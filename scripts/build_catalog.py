#!/usr/bin/env python3
"""Build a deterministic, auditable catalog from local metadata using stdlib only."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import quote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_KEYS = (
    "01_basics", "02_memory", "03_skills_and_self_improvement",
    "04_training_data", "05_rl_and_distillation", "06_evaluation", "07_safety",
    "08_collaboration", "09_multimodal_gui", "10_world_models", "11_embodied",
    "12_science", "13_efficiency", "14_model_science", "15_frontier_reports",
    "16_generation", "90_adjacent", "99_review",
)
BASE_FIELDS = ("title", "id", "url", "abstract", "one_line", "source_dates", "likes", "old")
EVIDENCE_FIELDS = {"local_title": "title", "local_one_line": "one_line", "local_abstract": "abstract"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def json_text(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def fingerprint(value):
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_config(taxonomy_path, overrides_path):
    taxonomy = read_json(taxonomy_path)
    overrides = read_json(overrides_path)
    keys = [category["key"] for category in taxonomy["categories"]]
    require(keys == list(EXPECTED_KEYS), "taxonomy 必须按约定保留全部18个固定键")
    for index, category in enumerate(taxonomy["categories"]):
        expected = "chapters/" + category["key"] + ".md" if index < 16 else None
        require(category["chapter"] == expected, "chapter 路径不符合固定键: " + category["key"])
    mapping = taxonomy["legacy_mapping"]
    require(len(mapping) == 23 and "18_Unassigned" in mapping, "必须保留23个旧映射键")
    require(set(mapping.values()) <= set(keys), "旧映射包含未知新类别")
    rule_ids = set()
    for rule in taxonomy["rules"]:
        require(rule["id"] not in rule_ids, "重复规则 ID: " + rule["id"])
        rule_ids.add(rule["id"])
        require(rule["target"] in keys and rule["target"] != "99_review", "非法规则目标")
        require(set(rule["fields"]) <= {"title", "one_line"}, "自动规则禁止检索摘要")
        re.compile(rule["pattern"], re.IGNORECASE)
    for guard in taxonomy["legacy_guards"]:
        require(guard["old"] in mapping, "非法旧类别防护")
        re.compile(guard["pattern"], re.IGNORECASE)
    require(overrides["schema_version"] == 1, "未知 overrides schema")
    override_ids = [entry["id"] for entry in overrides["overrides"]]
    require(len(override_ids) == len(set(override_ids)), "重复 override ID")
    return taxonomy, overrides


def load_source(source, assign, taxonomy):
    with source.open(encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    require(len(rows) == taxonomy["expected_paper_count"], "源记录数不等于冻结快照2050条记录")
    raw = "paper_id" in rows[0]
    old_by_id = {}
    if raw:
        assignments = read_json(assign or source.with_name("assign.json"))
        require(set(assignments) == set(taxonomy["legacy_mapping"]), "assign.json 的23键与映射不一致")
        for old, paper_ids in assignments.items():
            require(isinstance(paper_ids, list), "旧类别内容必须为 ID 列表")
            for paper_id in paper_ids:
                require(paper_id not in old_by_id, "旧归属重复: " + paper_id)
                old_by_id[paper_id] = old
    papers = []
    for row in rows:
        if raw:
            paper_id = row["paper_id"]
            require(paper_id in old_by_id, "旧归属缺失: " + paper_id)
            paper = {
                "title": row["title"], "id": paper_id, "url": row["url"],
                "abstract": row.get("abstract"), "one_line": row.get("one_line"),
                "source_dates": {field: row.get(field) for field in ("date", "published", "updated")},
                "likes": {field: row.get(field) for field in ("likes_30", "likes_90")},
                "old": old_by_id[paper_id],
            }
        else:
            require(all(field in row for field in BASE_FIELDS), "compact 输入缺少可重建元数据")
            paper = {field: row[field] for field in BASE_FIELDS}
        require(isinstance(paper["id"], str) and paper["id"], "非法论文 ID")
        require(isinstance(paper["title"], str) and paper["title"], "缺失标题: " + paper["id"])
        require(isinstance(paper["url"], str), "非法 URL: " + paper["id"])
        require(paper["old"] in taxonomy["legacy_mapping"], "未知旧分类: " + str(paper["old"]))
        for field in ("abstract", "one_line"):
            require(paper[field] is None or isinstance(paper[field], str), "非法文本元数据: " + field)
        require(isinstance(paper["source_dates"], dict) and isinstance(paper["likes"], dict), "日期/热度必须为对象")
        papers.append(paper)
    ids = [paper["id"] for paper in papers]
    require(len(ids) == len(set(ids)), "源论文 ID 重复，禁止静默覆盖")
    if raw:
        require(set(ids) == set(old_by_id), "assign.json 存在源数据之外的 ID")
    return sorted(papers, key=lambda paper: paper["id"])


def validate_overrides(papers, config, taxonomy):
    by_id = {paper["id"]: paper for paper in papers}
    entries = {}
    for entry in config["overrides"]:
        paper_id = entry["id"]
        require(paper_id in by_id, "override ID 不在源数据中: " + paper_id)
        paper = by_id[paper_id]
        require(entry["expected_old"] == paper["old"], "override 旧类漂移: " + paper_id)
        require(entry["expected_title"] == paper["title"], "override 标题漂移: " + paper_id)
        require(entry["new"] in EXPECTED_KEYS, "override 目标无效: " + paper_id)
        require(entry["new"] != "99_review", "证据不足请留待审，不标为已校正")
        require(bool(entry["reason"].strip()), "override 缺少变更理由: " + paper_id)
        require(entry["reviewer"] == "coding_assistant_local_review", "不得伪称人类专家审核")
        require(bool(entry["evidence_basis"]), "override 缺少证据: " + paper_id)
        tags = entry["secondary_tags"]
        require(len(tags) == len(set(tags)), "override 副标签重复: " + paper_id)
        require(set(tags) <= set(EXPECTED_KEYS) - {entry["new"], "99_review"}, "override 副标签无效")
        for evidence in entry["evidence_basis"]:
            field = EVIDENCE_FIELDS.get(evidence["source"])
            require(field is not None, "override 必须使用本地 title/one_line/abstract")
            require(bool(evidence["quote"]) and evidence["quote"] in (paper[field] or ""),
                    "override 引文不在本地原文中: " + paper_id)
        entries[paper_id] = entry
    changed = sum(entry["new"] != taxonomy["legacy_mapping"][entry["expected_old"]] for entry in entries.values())
    require(changed >= 20, "至少需要20条相对旧默认映射的显式定点修正")
    return entries


def rule_matches(paper, rules):
    matches = []
    for rule in rules:
        for field in rule["fields"]:
            match = re.search(rule["pattern"], paper.get(field) or "", re.IGNORECASE)
            if match:
                matches.append({
                    "rule_id": rule["id"], "target": rule["target"],
                    "rank": (2 if field == "title" else 1, rule["priority"]),
                    "reason": rule["reason"],
                    "evidence": {"source": "local_" + field, "quote": match.group(), "rule_id": rule["id"]},
                })
    return sorted(matches, key=lambda item: (-item["rank"][0], -item["rank"][1], item["rule_id"]))


def classify(paper, taxonomy, overrides):
    mapped = taxonomy["legacy_mapping"][paper["old"]]
    matches = rule_matches(paper, taxonomy["rules"])
    entry = overrides.get(paper["id"])
    tags = set()
    if entry:
        primary = entry["new"]
        tags.update(entry["secondary_tags"])
        status = "local_override_reviewed"
        reason = entry["reason"]
        evidence = entry["evidence_basis"]
        rule_ids = ["override:" + paper["id"]]
    elif matches:
        highest = matches[0]["rank"]
        winners = [match for match in matches if match["rank"] == highest]
        targets = {match["target"] for match in winners}
        tags.update(match["target"] for match in matches)
        evidence = [match["evidence"] for match in matches]
        rule_ids = list(dict.fromkeys(match["rule_id"] for match in matches))
        if len(targets) > 1:
            primary = "99_review"
            status = "needs_review"
            reason = "同层级最高优先级规则目标冲突，待复核：" + ", ".join(sorted(targets))
        else:
            primary = next(iter(targets))
            status = "rule_assigned_unreviewed"
            reason = "自动规则（未人工审核）：" + "；".join(match["reason"] for match in winners)
    else:
        primary = mapped
        status = "legacy_mapped_unreviewed"
        reason = "仅沿用旧到新默认映射，未人工审核；不代表逐篇核验。"
        evidence = [{"source": "legacy_assignment", "quote": paper["old"]}]
        rule_ids = ["legacy_mapping"]
        text = paper["title"] + "\n" + (paper["one_line"] or "")
        for guard in taxonomy["legacy_guards"]:
            if guard["old"] == paper["old"]:
                match = re.search(guard["pattern"], text, re.IGNORECASE)
                if not match:
                    primary = "99_review"
                    reason = guard["reason"]
                    rule_ids = ["legacy_guard:" + paper["old"]]
                else:
                    field = "title" if re.search(guard["pattern"], paper["title"], re.IGNORECASE) else "one_line"
                    evidence.append({"source": "local_" + field, "quote": match.group(), "rule_id": "legacy_guard"})
        if primary == "99_review":
            status = "needs_review"
            if mapped == "99_review":
                reason = "旧未分配/其他类，且标题与 one_line 无特定规则证据，进入待复核。"
    reason = "旧类 " + paper["old"] + " 默认映射 " + mapped + " → " + primary + "。" + reason
    return dict(paper, new=primary, legacy_mapped_primary=mapped,
                secondary_tags=sorted(tags - {primary, "99_review"}), reason=reason,
                evidence_basis=evidence, classification_status=status, classification_rule_ids=rule_ids)


def validate_results(papers, results, taxonomy):
    require(len(results) == len(papers), "重分类发生丢失")
    require({paper["id"] for paper in papers} == {paper["id"] for paper in results}, "重分类 ID 不一致")
    require(len({paper["id"] for paper in results}) == len(results), "主归属重复")
    for base, paper in zip(papers, results):
        require(all(base[field] == paper[field] for field in BASE_FIELDS), "源元数据发生变化: " + paper["id"])
        require(paper["new"] in EXPECTED_KEYS, "未知主类")
        require(paper["classification_status"] in taxonomy["statuses"], "未知审核状态")
        require((paper["new"] == "99_review") == (paper["classification_status"] == "needs_review"), "待审状态不一致")
        require(paper["new"] not in paper["secondary_tags"], "主类不能重复出现在副标签中")
        require(len(paper["secondary_tags"]) == len(set(paper["secondary_tags"])), "副标签重复")
        require(set(paper["secondary_tags"]) <= set(EXPECTED_KEYS) - {"99_review"}, "未知副标签")
        for evidence in paper["evidence_basis"]:
            if evidence["source"] == "legacy_assignment":
                require(evidence["quote"] == paper["old"], "旧归属证据不一致")
            else:
                require(evidence["quote"] in (paper[EVIDENCE_FIELDS[evidence["source"]]] or ""), "分类证据不可回溯")


def cell(value):
    return " ".join(str(value).split()).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("|", "&#124;").replace("`", "&#96;").replace("[", "&#91;").replace("]", "&#93;")


def paper_link(paper):
    title = cell(paper["title"])
    if urlsplit(paper["url"]).scheme not in {"http", "https"}:
        return title
    return "[" + title + "](" + quote(paper["url"], safe=":/?=&%#@+;,$!~*'-._") + ")"


def catalog_order(paper):
    likes = paper["likes"]
    popularity = max(likes.get("likes_30") or 0, likes.get("likes_90") or 0)
    return -popularity, paper["id"]


def render(papers, results, taxonomy, overrides):
    groups = defaultdict(list)
    for paper in results:
        groups[paper["new"]].append(paper)
    categories = {category["key"]: category for category in taxonomy["categories"]}
    status_counts = Counter(paper["classification_status"] for paper in results)
    outputs = {"data/papers.jsonl": "".join(json_text(paper) + "\n" for paper in results)}
    readme = [
        "# 文献目录", "",
        "按研究主题浏览 **" + str(len(results)) + " 条文献记录**。每条记录保留一个主归属，相关方向提供交叉阅读入口。",
        "首次阅读可从[综述导读](../chapters/00_surveys.md)或[专题索引](../README.md#topics)开始，再使用本目录查找具体文献。", "",
        "[Hot Words](../chapters/17_hot_words.md)解释JEV、harness、Agent Skills等概念的来源与研究联系，作为跨专题入口，不另设文献主类。", "",
        "## 分类索引", "",
        "前 16 类对应研究专题；相邻方向与待复核条目单列，便于区分研究范围与分类不确定性。",
        "类内按文献记录中的平台关注度排序，同分按 ID 排序；关联方向提供跨主题入口。", "",
        "| 研究方向 | 文献数 | 专题导读 |", "| --- | ---: | --- |",
    ]
    for category in taxonomy["categories"]:
        key = category["key"]
        chapter = "[阅读](../" + category["chapter"] + ")" if category["chapter"] else "—"
        readme.append("| [" + category["name"] + "](" + key + ".md) | " + str(len(groups[key])) + " | " + chapter + " |")
        lines = [
            "# " + category["name"], "", category["scope"], "",
            "[文献目录](README.md) · [分类方法](../docs/classification_audit.md)", "",
        ]
        if category["chapter"]:
            lines.extend(["[阅读专题导读](../" + category["chapter"] + ")", ""])
        if key in {"90_adjacent", "99_review"}:
            lines.extend(["[相邻方向与待复核说明](../docs/adjacent_topics.md)", ""])
        lines.extend([
            "本方向收录 **" + str(len(groups[key])) + " 条记录**。相关方向用于交叉检索，不重复计入各类数量。", "",
            "| ID | 文献 | 相关方向 |", "| --- | --- | --- |",
        ])
        for paper in sorted(groups[key], key=catalog_order):
            related = " · ".join(
                "[" + categories[tag]["name"] + "](" + tag + ".md)"
                for tag in paper["secondary_tags"]
            ) or "—"
            lines.append("| " + " | ".join([cell(paper["id"]), paper_link(paper), related]) + " |")
        outputs["catalog/" + key + ".md"] = "\n".join(lines) + "\n"
    readme.extend([
        "| **合计** | **" + str(len(results)) + "** | |", "",
        "## 使用与维护", "",
        "目录包含论文及研究项目页面，按主要研究问题归类。各专题进一步说明背景、方法联系与研究机会。",
        "摘要、来源日期及分类依据保存在 [data/papers.jsonl](../data/papers.jsonl)。",
        "发现引用或归属问题时，请按[贡献指南](../CONTRIBUTING.md)提供原始来源与修正理由。", "",
        "[文献收录与分类](../docs/methodology.md) · [分类方法与数据字段](../docs/classification_audit.md) · "
        "[质量检查](../docs/quality_review.md)",
    ])
    outputs["catalog/README.md"] = "\n".join(readme) + "\n"
    audit = [
        "# 分类方法与数据说明", "",
        "[文献目录](../catalog/README.md) · [贡献指南](../CONTRIBUTING.md) · [收录标准](methodology.md)", "",
        "## 分类原则", "",
        "以文献主要解决的研究问题确定主归属，以关联标签连接方法、对象和应用。每条记录只有一个主类，跨方向阅读不重复计数。",
        "分类由来源类别、题名与简述规则以及显式校正共同确定。规则负责建立一致的检索入口，校正配置记录跨领域工作中需要单独判断的归属。", "",
        "## 生成规则", "",
        "1. 应用显式校正配置，并核对记录标识、来源类别、题名和证据片段，避免配置错用。",
        "2. 匹配题名规则，再匹配简述规则；同一证据层内按规则优先级决定归属。自动规则不扫描完整摘要。",
        "3. 同层同优先级的不同目标发生冲突时转入待复核，其他有效关联保留为副标签。",
        "4. 未命中规则的记录使用来源分类转换；对证据要求较高的类别另行设置保护条件。",
        "5. 证据不足的条目进入待复核目录，相邻学科单独保留。二者均不表示负面质量判断。", "",
        "配置文件：[分类体系与规则](../data/taxonomy.json) · [显式校正](../data/classification_overrides.json)。", "",
        "## 主题边界", "",
        "- 评测按任务跨度、场景与能力组合组织；评分、验证、诊断及校准作为支撑方法。",
        "- 循环架构与推理计算组织以效率为主要入口；模型表征、优化机制与可解释性以模型科学为主要入口。",
        "- 多模态生成与世界模型分别关注内容构造与决策预测，不因使用相同生成结构而合并。",
        "- 技术报告按所披露的研究对象阅读；发布形式本身不是能力或可靠性的证明。", "",
        "## 数据完整性", "",
        "| 检查项 | 数量 |", "| --- | ---: |",
        "| 文献记录 | " + str(len(results)) + " |",
        "| 唯一标识 | " + str(len({paper["id"] for paper in results})) + " |",
        "| 主分类 | " + str(len(categories)) + " |",
        "| 重复主归属 | 0 |", "",
        "生成器检查标识唯一性、主类与关联标签合法性、元数据保留及证据片段一致性。完整记录保存在 JSONL 中，网页目录仅展示阅读所需信息。", "",
        "## 分类状态", "",
        "以下状态记录每条文献的分类路径，便于定位规则覆盖与人工校正。", "",
        "| 状态字段 | 记录数 |", "| --- | ---: |",
    ]
    for status in taxonomy["statuses"]:
        audit.append("| `" + status + "` | " + str(status_counts[status]) + " |")
    audit.extend([
        "", "## 数据字段", "",
        "| 字段 | 含义 |", "| --- | --- |",
        "| `id/title/url/abstract/one_line` | 来源标识、题名、链接、摘要与简述；缺失值保留为 null |",
        "| `source_dates/likes` | 来源日期与平台关注信号 |",
        "| `new/secondary_tags` | 主分类与关联主题 |",
        "| `old/legacy_mapped_primary` | 导入时的来源分类及转换结果，用于追踪数据来源 |",
        "| `reason/evidence_basis` | 分类依据与可匹配的来源片段 |",
        "| `classification_status/classification_rule_ids` | 分类状态与所用规则 |", "",
        "## 本地重建", "",
        "在项目根目录执行，仅需 Python 3 标准库：", "", "```bash",
        "python3 scripts/build_catalog.py --source data/papers.jsonl",
        "python3 scripts/build_catalog.py --source data/papers.jsonl --check", "```", "",
        "重建从保存的来源字段重新应用分类配置，不直接复用已计算的主归属。`--check` 仅在内存重建并逐字节比较，不改写文件。",
        "导入外部文献数据时可使用 `--source /path/corpus.jsonl --assign /path/assign.json`；`--output-dir` 支持在临时目录验证输出。",
        "生成范围包括语料 JSONL、分类目录和本说明，不改写研究章节。",
    ])
    outputs["docs/classification_audit.md"] = "\n".join(audit) + "\n"
    return outputs


def write_outputs(outputs, output_dir, check):
    mismatches = []
    for relative, content in outputs.items():
        destination = output_dir / relative
        if check:
            if not destination.is_file() or destination.read_bytes() != content.encode("utf-8"):
                mismatches.append(relative)
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=destination.parent, delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(content)
            temporary.chmod(0o644)
            temporary.replace(destination)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
    require(not mismatches, "生成文件与当前规则不一致: " + ", ".join(mismatches))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, help="旧 corpus_v2.jsonl 或可独立重建的 compact papers.jsonl")
    parser.add_argument("--assign", type=Path, help="原始输入的 assign.json；compact 输入不需要")
    parser.add_argument("--output-dir", type=Path, default=ROOT, help="输出根目录，默认脚本所在项目")
    parser.add_argument("--check", action="store_true", help="只校验并比较已生成文件，不写入")
    args = parser.parse_args(argv)
    original = ROOT.parent / "alphaxiv_survey" / "data" / "corpus_v2.jsonl"
    source = args.source or (original if original.is_file() else ROOT / "data" / "papers.jsonl")
    try:
        taxonomy, overrides = load_config(ROOT / "data/taxonomy.json", ROOT / "data/classification_overrides.json")
        papers = load_source(source, args.assign, taxonomy)
        entries = validate_overrides(papers, overrides, taxonomy)
        results = [classify(paper, taxonomy, entries) for paper in papers]
        validate_results(papers, results, taxonomy)
        outputs = render(papers, results, taxonomy, overrides)
        write_outputs(outputs, args.output_dir, args.check)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, "ERROR: " + str(error) + "\n")
    print(json.dumps({
        "mode": "check" if args.check else "build", "records": len(results),
        "unique_ids": len({paper["id"] for paper in results}), "lost": 0, "duplicate_primary": 0,
        "primary_counts": {key: sum(paper["new"] == key for paper in results) for key in EXPECTED_KEYS},
        "classification_status": dict(Counter(paper["classification_status"] for paper in results)),
        "override_primary_changes": sum(entry["new"] != taxonomy["legacy_mapping"][entry["expected_old"]] for entry in entries.values()),
        "generated_files": len(outputs), "compact_metadata_sha256": fingerprint(papers),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
