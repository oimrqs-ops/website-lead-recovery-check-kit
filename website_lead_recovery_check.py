#!/usr/bin/env python3
"""Focused public-site lead recovery checks for HTML files or public URLs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse
from urllib.request import urlopen


CONTACT_HINTS = ("contact", "contato", "fale", "talk", "email", "whatsapp")
BOOKING_HINTS = ("book", "booking", "reserve", "schedule", "agendar", "agenda")
CTA_HINTS = ("quote", "contact", "book", "schedule", "reserve", "talk", "demo", "orcamento", "contato", "agendar")


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str
    severity: str = "fail"


class LeadHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._in_title = False
        self.meta_description = ""
        self.has_viewport = False
        self.canonical = ""
        self.links: list[dict[str, str]] = []
        self.forms = 0
        self.buttons: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {k.lower(): (v or "") for k, v in attrs}
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            name = attr.get("name", "").lower()
            if name == "description":
                self.meta_description = attr.get("content", "").strip()
            elif name == "viewport":
                self.has_viewport = True
        elif tag == "link" and attr.get("rel", "").lower() == "canonical":
            self.canonical = attr.get("href", "").strip()
        elif tag == "a":
            self.links.append(
                {
                    "href": attr.get("href", "").strip(),
                    "text": "",
                    "class": attr.get("class", "").strip(),
                }
            )
        elif tag == "form":
            self.forms += 1
        elif tag == "button":
            self.buttons.append("")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        text = re.sub(r"\s+", " ", data).strip()
        if not text:
            return
        if self._in_title:
            self.title += text
        if self.links:
            self.links[-1]["text"] = (self.links[-1]["text"] + " " + text).strip()
        if self.buttons:
            self.buttons[-1] = (self.buttons[-1] + " " + text).strip()


def load_source(source: str) -> tuple[str, str]:
    parsed = urlparse(source)
    if parsed.scheme in {"http", "https"}:
        with urlopen(source, timeout=10) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace"), source
    path = Path(source)
    return path.read_text(encoding="utf-8"), str(path.resolve())


def any_link_matches(links: Iterable[dict[str, str]], predicate) -> bool:
    return any(predicate(link) for link in links)


def audit_html(html: str, source_label: str) -> dict:
    parser = LeadHTMLParser()
    parser.feed(html)

    checks = [
        CheckResult("title", bool(parser.title.strip()), "Missing page title"),
        CheckResult("meta_description", bool(parser.meta_description), "Missing meta description"),
        CheckResult("viewport", parser.has_viewport, "Missing mobile viewport meta"),
        CheckResult("canonical", bool(parser.canonical), "Missing canonical link"),
        CheckResult("contact_form", parser.forms > 0, "No contact form found"),
        CheckResult(
            "mailto_link",
            any_link_matches(parser.links, lambda link: link["href"].startswith("mailto:")),
            "No mailto link found",
        ),
        CheckResult(
            "tel_link",
            any_link_matches(parser.links, lambda link: link["href"].startswith("tel:")),
            "No tel link found",
        ),
        CheckResult(
            "whatsapp_link",
            any_link_matches(parser.links, lambda link: "wa.me" in link["href"] or "whatsapp" in link["href"]),
            "No WhatsApp link found",
        ),
        CheckResult(
            "contact_path",
            any_link_matches(parser.links, lambda link: any(h in (link["href"] + " " + link["text"]).lower() for h in CONTACT_HINTS)),
            "No clear contact path found",
        ),
        CheckResult(
            "booking_path",
            any_link_matches(parser.links, lambda link: any(h in (link["href"] + " " + link["text"]).lower() for h in BOOKING_HINTS)),
            "No booking/schedule path found",
            severity="warn",
        ),
        CheckResult(
            "cta_copy",
            any(any(h in text.lower() for h in CTA_HINTS) for text in [*parser.buttons, *(link["text"] for link in parser.links)]),
            "No strong visible CTA copy found",
            severity="warn",
        ),
    ]

    passed = sum(1 for item in checks if item.passed)
    failed = sum(1 for item in checks if not item.passed and item.severity == "fail")
    warnings = sum(1 for item in checks if not item.passed and item.severity == "warn")

    return {
        "source": source_label,
        "title": parser.title.strip(),
        "meta_description": parser.meta_description,
        "canonical": parser.canonical,
        "forms": parser.forms,
        "link_count": len(parser.links),
        "checks": [item.__dict__ for item in checks],
        "summary": {
            "checks": len(checks),
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
        },
    }


def write_report(report: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = report["summary"]
    lines = [
        "# Website Lead Recovery Report",
        "",
        f"- source: `{report['source']}`",
        f"- title: `{report['title'] or 'missing'}`",
        f"- forms: `{report['forms']}`",
        f"- links: `{report['link_count']}`",
        f"- checks: `{summary['checks']}`",
        f"- passed: `{summary['passed']}`",
        f"- failed: `{summary['failed']}`",
        f"- warnings: `{summary['warnings']}`",
        "",
        "## Findings",
        "",
    ]
    for item in report["checks"]:
        status = "PASS" if item["passed"] else ("WARN" if item["severity"] == "warn" else "FAIL")
        detail = "OK" if item["passed"] else item["detail"]
        lines.append(f"- `{status}` {item['name']}: {detail}")
    lines.append("")
    lines.append("## Next pass")
    lines.append("")
    lines.append("- Fix the failed lead-path items first.")
    lines.append("- Re-run after each change to confirm CTA/contact recovery.")
    lines.append("- Use screenshots or a browser QA pass for the final handoff.")

    (out_dir / "lead-recovery-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out_dir / "lead-recovery-summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run focused website lead recovery checks.")
    parser.add_argument("source", help="Local HTML path or public URL")
    parser.add_argument("--out", default="out", help="Output directory")
    args = parser.parse_args()

    html, source_label = load_source(args.source)
    report = audit_html(html, source_label)
    write_report(report, Path(args.out))

    summary = report["summary"]
    print(
        f"checks={summary['checks']} passed={summary['passed']} "
        f"failed={summary['failed']} warnings={summary['warnings']}"
    )
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
