"""Builds index.html from src/index.html with the web fonts embedded, so the page works on its own.

Usage: npm install && python3 build.py
"""
import base64
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
FONTS = ROOT / "node_modules" / "@fontsource-variable"
SRC = ROOT / "src" / "index.html"
OUT = ROOT / "index.html"


def unicode_range(css_file: pathlib.Path, block: str) -> str:
    css = css_file.read_text()
    m = re.search(r"/\* " + re.escape(block) + r" \*/.*?unicode-range:\s*([^;]+);", css, re.S)
    if not m:
        raise SystemExit(f"unicode-range not found for {block}")
    return m.group(1).strip()


def face(family, style, weight, woff2, urange):
    data = base64.b64encode(woff2.read_bytes()).decode()
    return (
        "@font-face{font-family:'%s';font-style:%s;font-weight:%s;font-display:swap;"
        "src:url(data:font/woff2;base64,%s) format('woff2');unicode-range:%s;}"
        % (family, style, weight, data, urange)
    )


bodoni = FONTS / "bodoni-moda"
jost = FONTS / "jost"
rules = []
for subset in ("latin-ext", "latin"):
    rules.append(face("Bodoni Moda", "normal", "400 900",
                      bodoni / "files" / f"bodoni-moda-{subset}-standard-normal.woff2",
                      unicode_range(bodoni / "standard.css", f"bodoni-moda-{subset}-standard-normal")))
    rules.append(face("Bodoni Moda", "italic", "400 900",
                      bodoni / "files" / f"bodoni-moda-{subset}-standard-italic.woff2",
                      unicode_range(bodoni / "standard-italic.css", f"bodoni-moda-{subset}-standard-italic")))
    rules.append(face("Jost", "normal", "100 900",
                      jost / "files" / f"jost-{subset}-wght-normal.woff2",
                      unicode_range(jost / "index.css", f"jost-{subset}-wght-normal")))

html = SRC.read_text()
assert "/*@FONTS@*/" in html
OUT.write_text(html.replace("/*@FONTS@*/", "\n".join(rules)))
print(f"{OUT.name} {OUT.stat().st_size / 1024:.0f} KB")
