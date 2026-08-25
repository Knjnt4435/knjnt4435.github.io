from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_HTML = (
    ROOT / "index.html",
    ROOT / "demo/index.html",
    ROOT / "agents_logs/index.html",
    ROOT / "pathway_explorer/index.html",
)
REQUIRED = (
    *PUBLIC_HTML,
    ROOT / ".nojekyll",
    ROOT / "robots.txt",
    ROOT / "sitemap.xml",
    ROOT / "demo/imgs/169951-842348732_medium.mp4",
    ROOT / "demo/imgs/optovlab_logo.svg",
    ROOT / "demo/imgs/optovlab_figure1.svg",
    ROOT / "demo/imgs/optovlab_figure2.jpg",
    ROOT / "demo/imgs/optovlab_figure3.jpg",
)
PUBLIC_ROOTS = (
    ROOT / "index.html",
    ROOT / "demo",
    ROOT / "agents_logs",
    ROOT / "pathway_explorer",
    ROOT / "robots.txt",
    ROOT / "sitemap.xml",
)
FORBIDDEN_SUFFIXES = {".csv", ".db", ".jsonl", ".pdf", ".sqlite", ".xlsx"}
FORBIDDEN_TEXT = (
    re.compile(r"/home/qianzhang", re.IGNORECASE),
    re.compile(r"211[.]81[.]48[.]70"),
    re.compile(r"\b(?:api[_-]?key|password|secret)\s*[:=]", re.IGNORECASE),
    re.compile(r"\bsk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"\bas_sk_[A-Za-z0-9_-]{12,}"),
    re.compile(r"\bastra\b", re.IGNORECASE),
)


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        del tag
        for name, value in attrs:
            if name in {"href", "poster", "src"} and value:
                self.references.append(value)


def iter_public_files() -> list[Path]:
    files: set[Path] = set()
    for entry in PUBLIC_ROOTS:
        if entry.is_file():
            files.add(entry)
        elif entry.is_dir():
            files.update(path for path in entry.rglob("*") if path.is_file())
    return sorted(files)


def resolve_local_reference(page: Path, value: str) -> Path | None:
    value = value.strip()
    if not value or value.startswith(("#", "data:", "mailto:", "tel:")):
        return None
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or value.startswith("//"):
        return None
    path = unquote(parsed.path)
    if not path:
        return None
    target = (page.parent / path).resolve()
    if path.endswith("/"):
        target /= "index.html"
    return target


def main() -> None:
    errors: list[str] = []
    for path in REQUIRED:
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")

    public_files = iter_public_files()
    for path in public_files:
        relative = path.relative_to(ROOT)
        if path.name == ".DS_Store" or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f"forbidden public artifact: {relative}")
        if path.stat().st_size > 25 * 1024 * 1024:
            errors.append(f"public file exceeds 25 MiB: {relative}")
        if path.suffix.lower() in {".html", ".svg", ".xml"}:
            text = path.read_text(encoding="utf-8")
            for pattern in FORBIDDEN_TEXT:
                if pattern.search(text):
                    errors.append(f"forbidden text in {relative}: {pattern.pattern}")

    for page in PUBLIC_HTML:
        if not page.is_file():
            continue
        parser = ReferenceParser()
        parser.feed(page.read_text(encoding="utf-8"))
        for value in parser.references:
            target = resolve_local_reference(page, value)
            if target is None:
                continue
            try:
                target.relative_to(ROOT)
            except ValueError:
                errors.append(f"reference escapes repository: {page.name} -> {value}")
                continue
            if not target.exists():
                errors.append(
                    f"broken local reference: {page.relative_to(ROOT)} -> {value}"
                )

    report = {
        "status": "failed" if errors else "ok",
        "public_files": len(public_files),
        "public_bytes": sum(path.stat().st_size for path in public_files),
        "errors": errors,
    }
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
