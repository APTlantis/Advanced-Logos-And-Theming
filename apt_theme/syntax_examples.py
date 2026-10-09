"""Offline Prism pages from preserved source text and pinned vendor resources."""
import hashlib
import base64
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
SOURCES = ROOT / "examples/syntax"
VENDOR = ROOT / "vendor/prism"


def verify_vendor(directory=VENDOR):
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    for record in manifest["files"]:
        actual = hashlib.sha256((directory / record["file"]).read_bytes()).hexdigest()
        if actual != record["sha256"]:
            raise ValueError(f"Prism asset hash mismatch: {record['file']}")
    return manifest


def page(title, body, scripts=""):
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>' + html.escape(title) + '</title><link rel="stylesheet" href="prism.css">'
            '<link rel="stylesheet" href="examples.css"></head><body><main>' + body +
            '</main>' + scripts + '</body></html>')


def syntax(tokens, directory):
    from .targets import css_tokens
    from .visual_targets import PRISM
    manifest = verify_vendor()
    shutil.copytree(VENDOR, directory / "vendor/prism")
    shutil.copytree(SOURCES, directory / "sources")
    css = css_tokens(tokens) + """
pre[class*='language-'], code[class*='language-'] {
 color:var(--apt-foreground); background:var(--apt-panel);
 font-family:Consolas, monospace; text-shadow:none; line-height:1.65;
 white-space:pre; tab-size:4;
}
pre[class*='language-'] { padding:24px; overflow:auto; }
pre[class*='language-'] ::selection, code[class*='language-']::selection {
 background:var(--apt-selection); color:var(--apt-selection-text);
}
.token.bold, .token.important { font-weight:bold; }
.token.italic { font-style:italic; }
"""
    mapping = dict(PRISM)
    mapping.update({"parameter variable": "foreground", "namespace": "type",
                    "annotation decorator": "function", "interpolation-punctuation": "operator"})
    for classes, key in mapping.items():
        fallback = {"diff_added": "success", "diff_deleted": "error"}
        token = key if key in tokens else fallback[key]
        selectors = ", ".join(".token." + cls for cls in classes.split())
        css += f"{selectors} {{ color:var(--apt-{token.replace('_', '-')}); }}\n"
    (directory / "prism.css").write_text(css, encoding="utf-8")
    (directory / "examples.css").write_text("""
*{box-sizing:border-box} body{margin:0;background:var(--apt-background);color:var(--apt-foreground);font:17px/1.6 Arial,sans-serif}
main{max-width:1100px;margin:auto;padding:clamp(16px,4vw,40px);min-width:0}
h1{line-height:1.2} a{color:var(--apt-primary)} a:focus-visible,pre:focus-visible{outline:3px solid var(--apt-primary);outline-offset:4px}
nav{display:flex;gap:12px;flex-wrap:wrap} pre{max-width:100%;border:1px solid var(--apt-border);border-radius:8px;font-size:15px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:16px;padding:0;list-style:none}
.cards li{background:var(--apt-panel);padding:20px;border:1px solid var(--apt-border);border-radius:8px}
.cards a{font-size:21px} .note{color:var(--apt-muted)}
""", encoding="utf-8")
    examples = json.loads((SOURCES / "manifest.json").read_text(encoding="utf-8"))
    scripts = ''.join(f'<script defer src="vendor/prism/{file}"></script>' for file in manifest["load_order"])
    pages = []
    cards = []
    for index, example in enumerate(examples):
        language = example["language"]
        filename = f"syntax-{language}.html"
        previous = examples[(index - 1) % len(examples)]["language"]
        following = examples[(index + 1) % len(examples)]["language"]
        source = (SOURCES / example["file"]).read_text(encoding="utf-8")
        download = base64.b64encode((SOURCES / example["file"]).read_bytes()).decode("ascii")
        body = ('<nav aria-label="Example navigation"><a href="examples.html">All languages</a>'
                f'<a href="syntax-{previous}.html">Previous</a><a href="syntax-{following}.html">Next</a></nav>'
                f'<h1>{html.escape(example["title"])} / syntax review</h1>'
                f'<p>{html.escape(example["description"])}</p>'
                '<p class="note">Prism 1.30.0 highlights this source locally. Example code is never executed.</p>'
                f'<a download="{example["file"]}" href="data:text/plain;base64,{download}">Download source</a>'
                f'<pre tabindex="0" aria-label="{example["title"]} source" class="language-{language}">'
                f'<code data-source="sources/{example["file"]}" class="language-{language}">{html.escape(source)}</code></pre>')
        rendered = page(example["title"] + " syntax review", body, scripts)
        (directory / filename).write_text(rendered, encoding="utf-8")
        if language == "javascript":
            (directory / "syntax-example.html").write_text(rendered, encoding="utf-8")
        pages.append(filename)
        cards.append(f'<li><a href="{filename}">{example["title"]}</a><p>{example["description"]}</p></li>')
    (directory / "examples.html").write_text(page("Syntax examples", '<h1>Syntax highlighting</h1>'
        '<p>Twelve language examples with bundled offline Prism grammars and downloadable source.</p>'
        '<p class="note">Illustrative code; host integration and native editor behavior require separate review.</p>'
        '<ul class="cards">' + ''.join(cards) + '</ul>'), encoding="utf-8")
    return pages
