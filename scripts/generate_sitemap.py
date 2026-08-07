#!/usr/bin/env python3
"""Regenerates sitemap.xml from every .html page in the repo root.

Run manually with `python3 scripts/generate_sitemap.py`, or let the
"Update sitemap" GitHub Action run it automatically whenever an .html
file changes.
"""
import datetime
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape

BASE_URL = "https://www.kerkyra-joyas.com.ar"
ROOT = Path(__file__).resolve().parent.parent

# Pages that exist as .html files but shouldn't be listed in the sitemap
# (search-engine site-verification files, etc.).
EXCLUDE_PREFIXES = ("google",)


def git_lastmod(path: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cd", "--date=short", "--", str(path)],
            cwd=ROOT, capture_output=True, text=True, check=True,
        ).stdout.strip()
        if out:
            return out
    except subprocess.CalledProcessError:
        pass
    return datetime.date.today().isoformat()


def collect_pages():
    pages = []
    for path in sorted(ROOT.glob("*.html")):
        if path.name.lower().startswith(EXCLUDE_PREFIXES):
            continue
        is_home = path.name == "index.html"
        loc = f"{BASE_URL}/" if is_home else f"{BASE_URL}/{path.name}"
        pages.append({
            "loc": loc,
            "lastmod": git_lastmod(path),
            "changefreq": "weekly" if is_home else "monthly",
            "priority": "1.0" if is_home else "0.8",
            "is_home": is_home,
        })
    pages.sort(key=lambda p: (not p["is_home"], p["loc"]))
    return pages


def render(pages) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for p in pages:
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(p['loc'])}</loc>")
        lines.append(f"    <lastmod>{p['lastmod']}</lastmod>")
        lines.append(f"    <changefreq>{p['changefreq']}</changefreq>")
        lines.append(f"    <priority>{p['priority']}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main():
    pages = collect_pages()
    (ROOT / "sitemap.xml").write_text(render(pages))
    print(f"sitemap.xml updated with {len(pages)} page(s):")
    for p in pages:
        print(f"  - {p['loc']}")


if __name__ == "__main__":
    main()
