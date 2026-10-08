#!/usr/bin/env python3
"""Validate guide structure, relative links, source logs and catalog consistency."""

import argparse
from collections import Counter
import datetime
import html
import json
from pathlib import Path
import re
import subprocess
import sys
import unicodedata
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
ONLINE_METADATA_STATUSES = {
    "metadata_fetched", "primary_page_reachable", "primary_arxiv_metadata_verified",
    "verified_local_title_match", "title_verified", "source_title_retrieved",
    "verified_title_and_abstract", "reviewed_selected_sections",
}


def headings(text):
    anchors = set()
    seen = Counter()
    for line in text.splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*$", line)
        if not match:
            continue
        heading = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", match.group(1))
        heading = re.sub(r"<[^>]*>", "", heading).lower()
        slug = re.sub(r"[^\w\- ]", "", heading).replace(" ", "-")
        count = seen[slug]
        seen[slug] += 1
        anchors.add(slug if count == 0 else "{}-{}".format(slug, count))
    anchors.update(re.findall(r'<a\s+(?:id|name)=["\']([^"\']+)', text))
    return anchors


def source_records(payload):
    if isinstance(payload, list):
        for item in payload:
            yield from source_records(item)
    elif isinstance(payload, dict):
        if isinstance(payload.get("url"), str):
            yield payload
        for value in payload.values():
            if isinstance(value, (dict, list)):
                yield from source_records(value)


def normalize_title(title):
    title = unicodedata.normalize("NFKC", html.unescape(title)).casefold()
    for command, symbol in {"pi": "π", "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "theta": "θ", "tau": "τ"}.items():
        title = re.sub(r"\\" + command + r"\b", symbol, title)
    return re.sub(r"[\W_]+", "", title)


def public_document_errors(path, text):
    errors = []
    formula_pattern = r"\\[\[\]()]|\$\$|(?<![\\$])\$(?![\s$])[^$\n]+\$(?![\d$])"
    if re.search(formula_pattern, text):
        errors.append("阅读文档包含数学公式，应改为自然语言解释: " + str(path))
    process_pattern = (
        r"主助手|编码助手|用户关心|(?:按|根据)用户(?:要求|反馈)|应用户"
        r"|用户指定(?:的)?(?:材料|论文|版本|模型)|本轮扩写|旧类\s|默认映射|未人工审核"
    )
    if re.search(process_pattern, text):
        errors.append("公开文档包含内部编辑或迁移措辞: " + str(path))
    source_process_pattern = (
        r"数据快照|快照日期|导读依据(?:本地)?摘要|本地语料精选"
        r"|(?:仅有|只有)\s*one_line|缺摘要[／/]"
        r"|(?:不代表|不等于|不声称|未完成).{0,18}(?:全文审阅|全文阅读|全文精读|独立复现)"
    )
    if re.search(source_process_pattern, text):
        errors.append("公开文档包含流程化来源声明: " + str(path))
    if path.parts[0] not in {"chapters", "catalog"}:
        return errors
    if re.search(r"^\*\*(?:新增|补充|方法)对照[：:]", text, re.MULTILINE):
        errors.append("论文导读保留编辑批次标签: " + str(path))
    if path.parts[0] == "catalog":
        if re.search(r"classification_status|evidence_basis|legacy_mapped_primary", text):
            errors.append("目录展示了内部分类字段: " + str(path))
        return errors
    if re.search(r"^## 来源与(?:阅读|收录)边界|（(?:已核验|本地摘要|仅简述)）|（`[^`]+`，在线）", text, re.MULTILINE):
        errors.append("专题包含流程化来源说明或核验标签: " + str(path))
    if not re.search(r"^## [^\n]*研究机会", text, re.MULTILINE):
        errors.append("专题缺少研究机会: " + str(path))
    if re.search(r"^## [^\n]*(?:阅读路线|分层阅读|学习路线|上手练习|怎样安排阅读顺序)", text, re.MULTILINE):
        errors.append("专题仍以阅读安排代替研究机会: " + str(path))
    if path.name == "00_surveys.md":
        required = {"https://long-horizon-agents.github.io/", "https://arxiv.org/abs/2609.11873v3"}
        urls = set(re.findall(r"\]\((https?://[^\s)]+)\)", text))
        if required - urls:
            errors.append("综述入口缺少必需的项目或路线图引用")
        return errors
    if re.search(r"^\|[^\n]*(?:文献地图|ID 与完整题名)|^分组阅读地图：", text, re.MULTILINE):
        errors.append("专题使用了脱离叙述的文献清单: " + str(path))
    if path.name == "06_evaluation.md":
        axes = [r"^#{2,3} [^\n]*" + axis + r"[：:]" for axis in ("更长", "更宽")]
        if not all(re.search(pattern, text, re.MULTILINE) for pattern in axes):
            errors.append("评测章缺少任务跨度与场景覆盖主线")
    if path.name not in {"00_surveys.md", "17_hot_words.md"}:
        for label, pattern in (("经典发展脉络", r"^## [^\n]*(?:发展|经典)[^\n]*$"),
                               ("前沿研究方向", r"^## [^\n]*前沿研究方向[^\n]*$")):
            section = re.search(pattern, text, re.MULTILINE)
            if not section:
                errors.append("专题缺少" + label + ": " + str(path))
                continue
            remainder = text[section.end():]
            introduction = re.split(r"^#{2,4} ", remainder, maxsplit=1, flags=re.MULTILINE)[0].strip()
            first_paragraph = introduction.split("\n\n", 1)[0]
            if len(re.findall(r"[\u4e00-\u9fff]", first_paragraph)) < 80:
                errors.append(label + "缺少问题总述: " + str(path))
            if re.match(r"(?:\*\*)?\[", first_paragraph):
                errors.append(label + "直接以论文开篇: " + str(path))
            if label == "前沿研究方向":
                body = re.split(r"^## ", remainder, maxsplit=1, flags=re.MULTILINE)[0]
                branches = list(re.finditer(r"^#{3,4} ([^\n]+)\n", body, re.MULTILINE))
                if not branches:
                    errors.append("前沿研究方向缺少分支: " + str(path))
                for branch in branches:
                    opening = body[branch.end():].lstrip().split("\n\n", 1)[0]
                    if (len(re.findall(r"[\u4e00-\u9fff]", opening)) < 60
                            or re.match(r"(?:\*\*)?\[|#|\|", opening)):
                        errors.append("前沿分支缺少问题铺垫: " + str(path) + ": " + branch[1])
    sections = list(re.finditer(r"^## .+$", text, re.MULTILINE))
    if not sections or "方向背景" not in sections[0].group():
        errors.append("专题未以方向背景开篇: " + str(path))
    elif len(sections) > 1:
        background = text[sections[0].end():sections[1].start()]
        if len(re.findall(r"[\u4e00-\u9fff]", background)) < 200:
            errors.append("专题背景说明不足: " + str(path))
    return errors


def validate(root):
    errors = []
    warnings = []
    markdown_files = sorted(root.rglob("*.md"))
    texts = {path.resolve(): path.read_text(encoding="utf-8") for path in markdown_files}
    checked_links = 0
    external_urls = set()
    for path, text in texts.items():
        errors.extend(public_document_errors(path.relative_to(root), text))
        content = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        if "<!--ALL_PAPERS_TABLE-->" in text or "TODO" in text:
            errors.append("未完成占位符: " + str(path.relative_to(root)))
        for match in re.finditer(r"\]\(([^\s)]+)(?:\s+\"[^\"]*\")?\)", content):
            target = match.group(1)
            parts = urlsplit(target)
            if parts.scheme in ("http", "https"):
                external_urls.add(target)
                continue
            if parts.scheme:
                continue
            checked_links += 1
            destination = (path.parent / unquote(parts.path)).resolve() if parts.path else path
            try:
                destination.relative_to(root)
            except ValueError:
                errors.append("链接逃出独立目录: {} -> {}".format(path.relative_to(root), target))
                continue
            if not destination.exists():
                errors.append("本地链接不存在: {} -> {}".format(path.relative_to(root), target))
            elif parts.fragment and destination.suffix == ".md":
                destination_text = texts.get(destination) or destination.read_text(encoding="utf-8")
                if unquote(parts.fragment) not in headings(destination_text):
                    errors.append("章节锚点不存在: {} -> {}".format(path.relative_to(root), target))
    taxonomy = json.loads((root / "data/taxonomy.json").read_text(encoding="utf-8"))
    rows = [json.loads(line) for line in (root / "data/papers.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    identifiers = [row["id"] for row in rows]
    if len(rows) != taxonomy["expected_paper_count"] or len(identifiers) != len(set(identifiers)):
        errors.append("论文总数或唯一性不符合快照约定")
    thematic_chapters = {category["chapter"] for category in taxonomy["categories"] if category.get("chapter")}
    required_chapters = thematic_chapters | {"chapters/00_surveys.md", "chapters/17_hot_words.md"}
    for chapter in sorted(required_chapters):
        path = root / chapter
        if not path.exists():
            errors.append("缺少阅读章节: " + chapter)
        elif len(re.findall(r"[\u4e00-\u9fff]", path.read_text(encoding="utf-8"))) < 1500:
            errors.append("章节中文叙事不足1500字: " + chapter)
    sources = []
    for path in sorted((root / "sources").glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            sources.extend(source_records(payload))
        except (ValueError, OSError) as error:
            errors.append("来源记录无效: {} {}".format(path.name, error))
    source_status_counts = Counter(record.get("status", "unspecified") for record in sources)
    unavailable_sources = [
        {"url": record["url"], "status": record.get("status", "")}
        for record in sources
        if re.search(r"failed|error|blocked|challenge|mismatch", record.get("status", ""), re.IGNORECASE)
    ]
    by_id = {row["id"]: row for row in rows}
    aliases_path = root / "sources/title_aliases.json"
    aliases = json.loads(aliases_path.read_text(encoding="utf-8")) if aliases_path.exists() else {}
    versions_path = root / "sources/title_versions.json"
    versions = json.loads(versions_path.read_text(encoding="utf-8")) if versions_path.exists() else {}
    verified_sample_ids = set()
    versioned_title_changes = set()
    for record in sources:
        if record.get("status") not in ONLINE_METADATA_STATUSES:
            continue
        match = re.search(r"arxiv\.org/(?:abs|html)/(\d{4}\.\d{4,5})(?:v\d+)?(?:$|[?#/])", record["url"])
        if not match or match.group(1) not in by_id or not record.get("title"):
            continue
        paper_id = match.group(1)
        online_title = record.get("online_title") or record["title"]
        alias = aliases.get(paper_id, {})
        alias_matches = (
            alias.get("local_title") == by_id[paper_id]["title"]
            and normalize_title(alias.get("online_title", "")) == normalize_title(online_title)
        )
        version_entry = versions.get(paper_id, {})
        requested_version = re.search(re.escape(paper_id) + r"v(\d+)", record["url"])
        version_number = requested_version.group(1) if requested_version else version_entry.get("current_version")
        version_title = version_entry.get("versions", {}).get(version_number, "")
        version_matches = (
            version_entry.get("local_title") == by_id[paper_id]["title"]
            and bool(version_title)
            and normalize_title(version_title) == normalize_title(online_title)
        )
        if normalize_title(online_title) == normalize_title(by_id[paper_id]["title"]) or alias_matches:
            verified_sample_ids.add(paper_id)
        elif version_matches:
            versioned_title_changes.add(paper_id)
        elif not re.search(r"failed|error|blocked|challenge", record.get("status", ""), re.IGNORECASE):
            errors.append("在线题名与本地语料不一致: {}: {}".format(paper_id, online_title))
    logged_urls = {record["url"] for record in sources}
    online_urls = {record["url"] for record in sources if record.get("status") in ONLINE_METADATA_STATUSES}
    editorial_urls = set()
    for path, text in texts.items():
        if "catalog" not in path.parts and path.name != "classification_audit.md":
            editorial_urls.update(re.findall(r"\]\((https?://[^\s)]+)\)", text))
    unchecked = sorted(editorial_urls - logged_urls)
    if unchecked:
        warnings.append("{} 个正文外链未在来源日志找到；详见报告 unchecked_editorial_urls".format(len(unchecked)))
    command = [sys.executable, str(root / "scripts/build_catalog.py"), "--source", str(root / "data/papers.jsonl"), "--check"]
    completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    if completed.returncode:
        errors.append("目录重建一致性检查失败: " + completed.stdout[-3000:])
    return {
        "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "passed" if not errors else "failed",
        "paper_count": len(rows),
        "unique_paper_ids": len(set(identifiers)),
        "chapter_count": len(required_chapters),
        "thematic_chapter_count": len(thematic_chapters),
        "supplemental_chapter_count": len(required_chapters - thematic_chapters),
        "markdown_files": len(markdown_files),
        "relative_links_checked": checked_links,
        "external_urls_including_catalog": len(external_urls),
        "source_records": len(sources),
        "source_status_counts": dict(source_status_counts),
        "unavailable_source_attempts": unavailable_sources,
        "distinct_corpus_titles_matched_online": len(verified_sample_ids),
        "known_versioned_title_changes": sorted(versioned_title_changes),
        "editorial_urls": len(editorial_urls),
        "editorial_urls_with_online_metadata": len(editorial_urls & online_urls),
        "editorial_urls_local_only_or_unverified": sorted(editorial_urls - online_urls),
        "unchecked_editorial_urls": unchecked,
        "catalog_check_output": completed.stdout.strip(),
        "classification_status_counts": dict(Counter(row["classification_status"] for row in rows)),
        "errors": errors,
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--report", type=Path)
    arguments = parser.parse_args()
    report = validate(arguments.root.resolve())
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if arguments.report:
        arguments.report.parent.mkdir(parents=True, exist_ok=True)
        arguments.report.write_text(rendered, encoding="utf-8")
    print(rendered)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
