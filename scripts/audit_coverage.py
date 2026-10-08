#!/usr/bin/env python3
"""Audit chapter coverage against the local record universe, without editing chapters."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
MIN_HAN = 6000
MIN_UNIQUE = 450
SUPPLEMENTAL_CHAPTERS = {
    "00_surveys": {
        "min_chinese_characters": 4500,
        "min_references": 23,
        "required_web_references": ["https://long-horizon-agents.github.io/"],
    },
    "17_hot_words": {
        "min_chinese_characters": 4500,
        "min_references": 22,
        "required_web_references": [
            "https://typesafe.ai/blog/introducing-system-one-models-and-jev",
            "https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills",
            "https://agentskills.io/specification",
        ],
    },
}
MIN_IDS = {
    "01_basics": 25,
    "02_memory": 35,
    "03_skills_and_self_improvement": 40,
    "04_training_data": 25,
    "05_rl_and_distillation": 40,
    "06_evaluation": 50,
    "07_safety": 35,
    "08_collaboration": 22,
    "09_multimodal_gui": 35,
    "10_world_models": 40,
    "11_embodied": 50,
    "12_science": 25,
    "13_efficiency": 35,
    "14_model_science": 35,
    "15_frontier_reports": 35,
    "16_generation": 40,
}
HAN = re.compile("[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\U00020000-\U0002fa1f\U00030000-\U000323af]")
TOKEN = re.compile(r"(?<![A-Za-z0-9_.-])\d{4}\.[A-Za-z0-9][A-Za-z0-9._-]*")
NUMERIC_ID = re.compile(r"\d{4}\.\d{4,5}")
URL = re.compile(r"https?://[^\s<>\"'`\[\]\u3000-\u303f\u3400-\u9fff\uff00-\uffef]+")
INLINE_LINK = re.compile(r"(?<!!)\[([^\]\n]*)\]\(\s*(<[^>\n]+>|(?:[^\s()]|\([^()\n]*\))+)(?:\s+[^\n)]*)?\s*\)")
REFERENCE = re.compile(r"(?<!!)\[([^\]\n]+)\](?:\[([^\]\n]*)\])?")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(content):
    return hashlib.sha256(content).hexdigest()


def blank(text):
    return re.sub(r"[^\n]", " ", text)


def reference_key(label):
    return " ".join(label.split()).casefold()


def eligible_lines(text):
    text = re.sub(r"<!--.*?(?:-->|$)", lambda match: blank(match.group()), text, flags=re.DOTALL)
    lines = text.splitlines()
    fence = None
    definitions = {}
    for index, line in enumerate(lines):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= fence[1] and not marker[2].strip():
                fence = None
            lines[index] = ""
        elif marker:
            fence = (marker[1][0], len(marker[1]))
            lines[index] = ""
        elif re.match(r"^(?: {4,}|\t+)\S", line):
            lines[index] = ""
        else:
            definition = re.match(r"^ {0,3}\[([^\]]+)\]:\s*(<[^>]+>|\S+)", line)
            if definition:
                definitions.setdefault(reference_key(definition[1]), definition[2].strip("<>"))
                lines[index] = ""
    return lines, definitions


def clean_url(url):
    url = url.rstrip(".,;:!?，。；：！？）")
    while url.endswith(")") and url.count(")") > url.count("("):
        url = url[:-1]
    return url


def canonical_id(token, universe):
    token = unquote(token).rstrip(".")
    if token in universe:
        return token
    token = re.sub(r"\.(?:pdf|html)$", "", token, flags=re.IGNORECASE)
    if re.fullmatch(r"\d{4}\.\d{4,5}v\d+", token):
        token = re.sub(r"v\d+$", "", token)
    return token


def repository_identifier(url, universe):
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower()
    if not any(host == domain or host.endswith("." + domain) for domain in ("arxiv.org", "alphaxiv.org")):
        return None
    match = re.match(r"/(?:abs|pdf|html)/(.+?)/?$", unquote(parsed.path))
    if not match:
        return None
    identifier = canonical_id(match[1], universe)
    if re.fullmatch(r"[A-Za-z.-]+/\d{7}v\d+", identifier):
        identifier = re.sub(r"v\d+$", "", identifier)
    return identifier


def line_content(line, definitions):
    line = re.sub(r"!\[[^\]\n]*\](?:\([^\n]*?\)|\[[^\]\n]*\])?", "", line)
    reference_urls = []

    def replace_reference(match):
        if match.end() < len(line) and line[match.end()] == "(":
            return match.group()
        label = match[2] if match[2] else match[1]
        target = definitions.get(reference_key(label))
        if target:
            reference_urls.append(target)
            return match[1]
        return match.group()

    resolved = REFERENCE.sub(replace_reference, line)
    visible = INLINE_LINK.sub(lambda match: match[1], resolved)
    targets = [match[2].strip("<>") for match in INLINE_LINK.finditer(resolved)]
    targets.extend(reference_urls)
    targets.extend(clean_url(match.group()) for match in URL.finditer(visible))
    visible = URL.sub("", visible)
    visible = re.sub(r"<[^>]*>", "", visible)
    identifier_text = unquote(visible + " " + " ".join(targets))
    targets = sorted({target for target in targets if target.startswith(("http://", "https://"))})
    return visible, identifier_text, targets


def scan_chapter(text, universe):
    lines, definitions = eligible_lines(text)
    occurrences = defaultdict(set)
    nonlocal_mentions = set()
    nonlocal_repository = defaultdict(set)
    external_web_urls = set()
    local_urls = set()
    chinese_characters = 0
    for number, line in enumerate(lines, 1):
        visible, identifier_text, urls = line_content(line, definitions)
        chinese_characters += len(HAN.findall(visible))
        for match in TOKEN.finditer(identifier_text):
            identifier = canonical_id(match.group(), universe)
            if identifier in universe:
                occurrences[identifier].add(number)
            elif NUMERIC_ID.fullmatch(identifier) or re.fullmatch(r"\d{4}\.[A-Za-z0-9][A-Za-z0-9_-]*[A-Za-z_-][A-Za-z0-9_-]*", identifier):
                nonlocal_mentions.add(identifier)
        for url in urls:
            identifier = repository_identifier(url, universe)
            if identifier in universe:
                occurrences[identifier].add(number)
                local_urls.add(url)
            elif identifier:
                nonlocal_repository[identifier].add(url)
            else:
                external_web_urls.add(url)
    nonlocal_mentions.difference_update(nonlocal_repository)
    return {
        "chinese_characters": chinese_characters,
        "citation_lines": {identifier: sorted(numbers) for identifier, numbers in sorted(occurrences.items())},
        "local_urls": sorted(local_urls),
        "nonlocal_repository_references": [
            {"id": identifier, "urls": sorted(urls)} for identifier, urls in sorted(nonlocal_repository.items())
        ],
        "nonlocal_identifier_mentions": sorted(nonlocal_mentions),
        "external_web_urls": sorted(external_web_urls),
    }


def load_inputs(root):
    taxonomy_bytes = (root / "data/taxonomy.json").read_bytes()
    records_bytes = (root / "data/papers.jsonl").read_bytes()
    taxonomy = json.loads(taxonomy_bytes)
    records = [json.loads(line) for line in records_bytes.decode("utf-8").splitlines() if line.strip()]
    require(len(records) == taxonomy["expected_paper_count"], "记录数不符合taxonomy快照约定")
    require(len({record["id"] for record in records}) == len(records), "本地语料ID重复")
    categories = taxonomy["categories"]
    keys = [category["key"] for category in categories]
    require(len(keys) == len(set(keys)), "taxonomy类别键重复")
    chapters = [category for category in categories if category.get("chapter")]
    require([category["key"] for category in chapters] == list(MIN_IDS), "taxonomy的16章与阈值配置不一致")
    for category in chapters:
        require(category["chapter"] == "chapters/" + category["key"] + ".md", "非法章节路径")
    for record in records:
        require(isinstance(record["id"], str) and record["id"], "非法本地ID")
        require(record["new"] in keys, "记录主类不在taxonomy中: " + record["id"])
        require(record["abstract"] is None or isinstance(record["abstract"], str), "abstract必须是字符串或null")
    hashes = {
        "data/taxonomy.json": sha256(taxonomy_bytes),
        "data/papers.jsonl": sha256(records_bytes),
    }
    return categories, sorted(records, key=lambda record: record["id"]), hashes


def audit(root):
    categories, records, hashes = load_inputs(root)
    by_id = {record["id"]: record for record in records}
    universe = set(by_id)
    primary_catalog = defaultdict(set)
    missing_abstract = set()
    for record in records:
        primary_catalog[record["new"]].add(record["id"])
        if not (record["abstract"] or "").strip():
            missing_abstract.add(record["id"])
    chapter_results = []
    all_cited = set()
    all_primary_cited = set()
    failure_messages = []
    for category in categories:
        if not category.get("chapter"):
            continue
        key = category["key"]
        path = root / category["chapter"]
        exists = path.is_file()
        content = path.read_bytes() if exists else b""
        hashes[category["chapter"]] = sha256(content) if exists else None
        scanned = scan_chapter(content.decode("utf-8"), universe)
        cited = set(scanned["citation_lines"])
        own = cited & primary_catalog[key]
        cross = cited - own
        all_cited.update(cited)
        all_primary_cited.update(own)
        failures = []
        if not exists:
            failures.append("章节文件缺失")
        if scanned["chinese_characters"] < MIN_HAN:
            failures.append("汉字数 {} < {}".format(scanned["chinese_characters"], MIN_HAN))
        if len(cited) < MIN_IDS[key]:
            failures.append("本地唯一ID数 {} < {}".format(len(cited), MIN_IDS[key]))
        failure_messages.extend(key + ": " + failure for failure in failures)
        result = dict(scanned, key=key, name=category["name"], path=category["chapter"], exists=exists,
                      local_citation_ids=sorted(cited), local_citation_count=len(cited),
                      local_numeric_ids=sorted(identifier for identifier in cited if NUMERIC_ID.fullmatch(identifier)),
                      local_slug_ids=sorted(identifier for identifier in cited if not NUMERIC_ID.fullmatch(identifier)),
                      primary_citation_ids=sorted(own), primary_citation_count=len(own),
                      cross_category_citation_ids=sorted(cross), cross_category_citation_count=len(cross),
                      cross_category_primary_counts=dict(sorted(Counter(by_id[identifier]["new"] for identifier in cross).items())),
                      cross_category_secondary_tag_ids=sorted(identifier for identifier in cross if key in by_id[identifier].get("secondary_tags", [])),
                      primary_catalog_count=len(primary_catalog[key]),
                      primary_coverage_ratio=round(len(own) / len(primary_catalog[key]), 6) if primary_catalog[key] else None,
                      primary_not_in_own_chapter_ids=sorted(primary_catalog[key] - cited),
                      cited_missing_abstract_ids=sorted(cited & missing_abstract),
                      thresholds={"min_chinese_characters": MIN_HAN, "min_local_ids": MIN_IDS[key]},
                      passed=not failures, failures=failures)
        chapter_results.append(result)
    if len(all_cited) < MIN_UNIQUE:
        failure_messages.append("全正文去重本地ID数 {} < {}".format(len(all_cited), MIN_UNIQUE))
    unseen = universe - all_cited
    for chapter in chapter_results:
        key = chapter["key"]
        chapter["primary_not_in_any_chapter_ids"] = sorted(primary_catalog[key] & unseen)
        chapter["primary_not_in_any_chapter_count"] = len(chapter["primary_not_in_any_chapter_ids"])
        candidates = sorted(chapter["primary_not_in_own_chapter_ids"], key=lambda identifier: (
            identifier in missing_abstract,
            by_id[identifier].get("classification_status") == "needs_review",
            identifier not in unseen,
            identifier,
        ))[:3]
        chapter["primary_gap_candidates"] = [{
            "id": identifier, "title": by_id[identifier]["title"],
            "classification_status": by_id[identifier].get("classification_status"),
            "abstract_missing": identifier in missing_abstract,
            "unseen_in_all_chapters": identifier in unseen,
        } for identifier in candidates]
    record_coverage = []
    for record in records:
        identifier = record["id"]
        referenced = [chapter for chapter in chapter_results if identifier in chapter["citation_lines"]]
        record_coverage.append({
            "id": identifier, "title": record["title"], "primary_category": record["new"],
            "id_kind": "numeric" if NUMERIC_ID.fullmatch(identifier) else "slug",
            "abstract_missing": identifier in missing_abstract,
            "cited_in_any_chapter": bool(referenced),
            "cited_in_primary_chapter": identifier in all_primary_cited,
            "citing_chapters": [chapter["key"] for chapter in referenced],
            "cross_category_chapters": [chapter["key"] for chapter in referenced if chapter["key"] != record["new"]],
            "citation_lines": {chapter["key"]: chapter["citation_lines"][identifier] for chapter in referenced},
        })
    catalog_coverage = [{
        "key": category["key"], "primary_catalog_count": len(primary_catalog[category["key"]]),
        "cited_anywhere_count": len(primary_catalog[category["key"]] & all_cited),
        "cited_in_primary_chapter_count": len(primary_catalog[category["key"]] & all_primary_cited),
        "unseen_count": len(primary_catalog[category["key"]] & unseen),
    } for category in categories]
    external_ids = {entry["id"] for chapter in chapter_results for entry in chapter["nonlocal_repository_references"]}
    external_web = {url for chapter in chapter_results for url in chapter["external_web_urls"]}
    supplemental_results = []
    for key, thresholds in SUPPLEMENTAL_CHAPTERS.items():
        relative_path = "chapters/" + key + ".md"
        path = root / relative_path
        content = path.read_bytes() if path.is_file() else b""
        hashes[relative_path] = sha256(content) if path.is_file() else None
        scanned = scan_chapter(content.decode("utf-8"), universe)
        reference_count = len(scanned["citation_lines"]) + len(scanned["nonlocal_repository_references"])
        required_web = set(thresholds.get("required_web_references", []))
        cited_web = required_web & set(scanned["external_web_urls"])
        reference_count += len(cited_web)
        failures = []
        if not path.is_file():
            failures.append("补充导读章节缺失")
        if scanned["chinese_characters"] < thresholds["min_chinese_characters"]:
            failures.append("补充导读字数不足")
        if reference_count < thresholds["min_references"]:
            failures.append("补充导读引用数不足")
        if required_web - cited_web:
            failures.append("缺少必需的一手来源")
        failure_messages.extend(key + ": " + failure for failure in failures)
        supplemental_results.append(dict(scanned, key=key, path=relative_path,
                                         reference_count=reference_count,
                                         web_reference_count=len(cited_web), thresholds=thresholds,
                                         passed=not failures, failures=failures))
    return {
        "schema_version": 2,
        "scope": "本地覆盖率只统计16个专题正文；综述导读与Hot Words单列，不增加原始语料覆盖率。不读取目录表作为正文，不等于精读、事实核验或结果复现。",
        "matching_policy": "精确本地ID宇宙匹配numeric/slug；numeric版本号及pdf/html后缀规范化；排除注释、围栏/缩进代码、图片和未使用的链接定义；使用过的reference链接归到正文使用行。",
        "character_policy": "统计可见正文中的CJK汉字（含扩展区），保留标题/表格/引用标签/inline code内容；排除链接目标、HTML标签、注释、围栏/缩进代码及链接定义。",
        "external_policy": "本地/库外按data/papers.jsonl成员资格区分，不按年份推断。库外含历史文献，也可能是近期新条目或拼写错误；不计本地覆盖阈值，不联网核验年代。",
        "thresholds": {"min_chinese_characters_per_chapter": MIN_HAN, "min_local_ids_per_chapter": MIN_IDS, "min_global_unique_local_ids": MIN_UNIQUE},
        "source_sha256": hashes,
        "summary": {
            "catalog_records": len(records), "chapter_count": len(chapter_results),
            "supplemental_chapter_count": len(supplemental_results),
            "all_reading_chapter_count": len(chapter_results) + len(supplemental_results),
            "thematic_chinese_characters": sum(chapter["chinese_characters"] for chapter in chapter_results),
            "supplemental_chinese_characters": sum(chapter["chinese_characters"] for chapter in supplemental_results),
            "unique_local_ids_cited": len(all_cited), "local_ids_not_cited_anywhere": len(unseen),
            "local_coverage_ratio": round(len(all_cited) / len(records), 6) if records else None,
            "unique_primary_ids_cited_in_own_chapter": len(all_primary_cited),
            "unique_cross_category_only_ids": len(all_cited - all_primary_cited),
            "chapter_local_id_sum_before_global_dedup": sum(chapter["local_citation_count"] for chapter in chapter_results),
            "cited_numeric_ids": sum(bool(NUMERIC_ID.fullmatch(identifier)) for identifier in all_cited),
            "cited_slug_ids": sum(not NUMERIC_ID.fullmatch(identifier) for identifier in all_cited),
            "records_missing_abstract": len(missing_abstract),
            "cited_records_missing_abstract": len(all_cited & missing_abstract),
            "uncited_records_missing_abstract": len(unseen & missing_abstract),
            "nonlocal_repository_ids": len(external_ids), "external_web_urls": len(external_web),
            "chapters_passing_thresholds": sum(chapter["passed"] for chapter in chapter_results),
            "passed": not failure_messages,
        },
        "failures": failure_messages,
        "global_cited_local_ids": sorted(all_cited),
        "global_unseen_local_ids": sorted(unseen),
        "global_cross_category_only_ids": sorted(all_cited - all_primary_cited),
        "global_cited_missing_abstract_ids": sorted(all_cited & missing_abstract),
        "chapters": chapter_results, "supplemental_chapters": supplemental_results,
        "catalog_coverage": catalog_coverage,
        "record_coverage": record_coverage,
    }


def cell(value):
    return " ".join(str(value).split()).replace("&", "&amp;").replace("|", "&#124;").replace("<", "&lt;").replace(">", "&gt;").replace("`", "&#96;").replace("[", "&#91;").replace("]", "&#93;")


def render_markdown(report):
    summary = report["summary"]
    lines = [
        "# 文献覆盖", "",
        "[首页](../README.md) · [文献目录](../catalog/README.md) · [机器可读报告](../data/coverage_report.json)", "",
        "本页汇总文献目录与正文引用的对应关系，提供专题覆盖、跨章引用与内容维护的统计入口。", "",
        "## 总览", "",
        "| 指标 | 数量 |", "| --- | ---: |",
        "| 文献记录 | {} |".format(summary["catalog_records"]),
        "| 研究专题 | {} |".format(summary["chapter_count"]),
        "| 跨专题章节 | {} |".format(summary["supplemental_chapter_count"]),
        "| 专题引用的文献记录（去重） | {} |".format(summary["unique_local_ids_cited"]),
        "| 专题引用占文献库比例 | {:.1%} |".format(summary["local_coverage_ratio"]),
        "| 专题正文汉字 | {} |".format(summary["thematic_chinese_characters"]),
        "| 跨专题正文汉字 | {} |".format(summary["supplemental_chinese_characters"]), "",
        "## 各专题覆盖", "",
        "引用记录按章去重，包含本专题主类和关联方向。主类覆盖率表示该类文献在所属专题中的引用比例。", "",
        "| 专题 | 正文汉字 | 引用记录 | 其中主类 | 其中跨类 | 主类文献数 | 主类覆盖率 | 检查 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for chapter in report["chapters"]:
        ratio = chapter["primary_coverage_ratio"]
        lines.append("| [{}](../{}) | {} | {} | {} | {} | {} | {} | {} |".format(
            chapter["key"], chapter["path"], chapter["chinese_characters"],
            chapter["local_citation_count"], chapter["primary_citation_count"],
            chapter["cross_category_citation_count"], chapter["primary_catalog_count"],
            "{:.1%}".format(ratio) if ratio is not None else "—",
            "PASS" if chapter["passed"] else "FAIL"))
    lines.extend([
        "", "## 跨专题章节", "",
        "[综述导读](../chapters/00_surveys.md)与[Hot Words](../chapters/17_hot_words.md)连接多个方向，单独统计论文和一手网页引用。", "",
        "| 章节 | 正文汉字 | 引用数 | 检查 |", "| --- | ---: | ---: | --- |",
    ])
    for chapter in report["supplemental_chapters"]:
        lines.append("| {} | {} | {} | {} |".format(
            chapter["key"], chapter["chinese_characters"], chapter["reference_count"],
            "PASS" if chapter["passed"] else "FAIL"))
    lines.extend([
        "", "## 统计方法", "",
        "- 以文献标识匹配正文引用，并按章和全库分别去重。",
        "- 正文汉字统计排除注释、代码块、链接目标和未使用的链接定义。",
        "- 文献库外的经典工作、补充论文和网页单独记录；目录本身不计入正文引用。",
        "- 逐条引用位置、元数据完整性、未引记录和输入校验值保存在机器可读报告中。", "",
        "## 检查结果", "",
    ])
    lines.extend("- " + cell(failure) for failure in report["failures"])
    if not report["failures"]:
        lines.append("专题与跨专题章节的数量检查通过。")
    lines.extend([
        "", "## 更新统计", "", "在项目根目录运行：", "", "```bash",
        "python3 scripts/audit_coverage.py",
        "python3 scripts/audit_coverage.py --check", "```", "",
        "生成命令更新本页及 `data/coverage_report.json`；`--check` 检查内容阈值与报告一致性，不修改文件。",
        "复杂链接和自定义 Markdown 扩展需要结合[质量检查](quality_review.md)复核。",
    ])
    return "\n".join(lines) + "\n"


def save(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        temporary.chmod(0o644)
        temporary.replace(path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="独立项目根目录")
    parser.add_argument("--check", action="store_true", help="只检查数量阈值与报告一致性，不写文件")
    args = parser.parse_args(argv)
    try:
        report = audit(args.root)
        outputs = {
            "docs/coverage.md": render_markdown(report),
            "data/coverage_report.json": json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        }
        stale = []
        for relative, content in outputs.items():
            path = args.root / relative
            if args.check:
                if not path.is_file() or path.read_bytes() != content.encode("utf-8"):
                    stale.append(relative)
            else:
                save(path, content)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, "ERROR: " + str(error) + "\n")
    print(json.dumps({"mode": "check" if args.check else "generate", "summary": report["summary"],
                      "failures": report["failures"], "stale_reports": stale}, ensure_ascii=False, indent=2))
    return 1 if args.check and (report["failures"] or stale) else 0


if __name__ == "__main__":
    sys.exit(main())
