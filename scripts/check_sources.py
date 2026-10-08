#!/usr/bin/env python3
"""Fetch first-party source metadata without claiming to verify paper results."""

import argparse
import concurrent.futures
import datetime
import hashlib
import html
import json
import re
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


class MetadataParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.metadata = {}
        self.in_title = False
        self.title_parts = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "meta":
            name = attributes.get("name", attributes.get("property", ""))
            self.metadata.setdefault(name, attributes.get("content", ""))
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)


def check_url(url):
    record = {
        "url": url,
        "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "scope": "metadata_and_reachability_only",
    }
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "LLM-Agent-Guide/1.0"})
        with urllib.request.urlopen(request, timeout=35) as response:
            body = response.read(4000000)
            record.update(http_status=response.status, final_url=response.url)
        record["sha256"] = hashlib.sha256(body).hexdigest()
        text = body.decode("utf-8", errors="replace")
        if url.startswith("https://api.github.com/"):
            payload = json.loads(text)
            for key in ("full_name", "description", "stargazers_count", "pushed_at", "html_url"):
                if key in payload:
                    record[key] = payload[key]
            record["title"] = payload.get("full_name", "GitHub API response")
        else:
            parser = MetadataParser()
            parser.feed(text)
            record["title"] = html.unescape(parser.metadata.get("citation_title") or "".join(parser.title_parts)).strip()
            record["published"] = parser.metadata.get("citation_date", "")
            record["arxiv_id"] = parser.metadata.get("citation_arxiv_id", "")
        if re.search(r"client challenge|access denied|just a moment|verify you are human", record.get("title", ""), re.IGNORECASE):
            record["status"] = "blocked_challenge_page"
        else:
            record["status"] = "metadata_fetched" if record.get("title") else "reachable_without_title"
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as error:
        record.update(status="fetch_failed", error=str(error))
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("urls", nargs="*")
    parser.add_argument("--markdown", nargs="*", type=Path, default=[])
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    urls = set(arguments.urls)
    for path in arguments.markdown:
        urls.update(re.findall(r"\]\((https?://[^\s)]+)\)", path.read_text(encoding="utf-8")))
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        records = list(executor.map(check_url, sorted(urls)))
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"total": len(records), "failed": sum(record["status"] == "fetch_failed" for record in records)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
