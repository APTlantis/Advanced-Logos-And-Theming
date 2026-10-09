"""SVG presentation attributes, Prism CSS and Matplotlib style contracts.

Examples are deterministic, offline, illustrative and use only exported tokens.
"""
import html
import json
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
PRISM = {
    "comment prolog doctype cdata": "comment", "punctuation operator": "operator",
    "property tag boolean constant symbol": "constant", "number": "number",
    "selector attr-name builtin class-name": "type", "string char attr-value": "string",
    "keyword atrule": "keyword", "function": "function", "regex important": "primary",
    "inserted": "diff_added", "deleted": "diff_deleted",
}


class Board:
    def __init__(self, tokens, title, description, width=960, height=540):
        self.tokens = tokens
        self.root = ET.Element("svg", xmlns=SVG_NS, width=str(width), height=str(height),
                               viewBox=f"0 0 {width} {height}", role="img", **{"aria-labelledby": "title desc"})
        ET.SubElement(self.root, "title", id="title").text = title
        ET.SubElement(self.root, "desc", id="desc").text = description
        self.rect(0, 0, width, height, "background")
        self.text(36, 52, title, "foreground", 26)
        self.text(36, 84, description, "muted", 15)

    def color(self, key):
        return self.tokens[key]["hex"]

    def rect(self, x, y, w, h, key="panel", **attrs):
        return ET.SubElement(self.root, "rect", x=str(x), y=str(y), width=str(w), height=str(h),
                             fill=self.color(key), **{k: str(v) for k, v in attrs.items()})

    def text(self, x, y, value, key="foreground", size=18, **attrs):
        node = ET.SubElement(self.root, "text", x=str(x), y=str(y), fill=self.color(key),
                             **{"font-family": "Arial, sans-serif", "font-size": str(size),
                                **{k: str(v) for k, v in attrs.items()}})
        node.text = str(value)
        return node

    def line(self, x1, y1, x2, y2, key="border", **attrs):
        return ET.SubElement(self.root, "line", x1=str(x1), y1=str(y1), x2=str(x2), y2=str(y2),
                             stroke=self.color(key), **{"stroke-width": "3", **attrs})

    def save(self, path):
        ET.indent(self.root)
        ET.ElementTree(self.root).write(path, encoding="utf-8", xml_declaration=True)


from .svg_examples import diagrams
from .syntax_examples import syntax
from .chart_examples import charts


def export_visual(result, directory, name):
    tokens, target = result["tokens"], result["target"]
    if target == "svg":
        result["examples"] = diagrams(tokens, directory)
        result["acceptance_limits"] = "Standalone SVG presentation attributes; SVG editor import/font substitution pending."
    elif target == "syntax_highlighting":
        result["examples"] = syntax(tokens, directory)
        result["acceptance_limits"] = "Bundled Prism 1.30.0 core and twelve language grammars; offline browser highlighting. Host integration and native editor behavior require separate review."
    else:
        result["examples"] = charts(tokens, directory, name)
        result["acceptance_limits"] = "Matplotlib mplstyle plus explicit JSON scale; SVG examples are authored independently. Optional Matplotlib renderer requires separate verification; no CVD or category-separation guarantee."
    if target in ('syntax_highlighting', 'svg'):
        return
    links = ''.join(f'<li><a href="{file}">{file}</a></li>' for file in result["examples"])
    (directory / "examples.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><title>Visual examples</title>'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="examples.css"><main><h1>'+html.escape(name)+' / '+target+'</h1><p>'+html.escape(result["acceptance_limits"])+
        '</p><ul>'+links+'</ul>' + ('<p><a href="heatmap-values.html">Heatmap value table</a></p><div class="scroll"><object data="bars.svg" type="image/svg+xml" aria-label="Bar chart"></object><object data="lines.svg" type="image/svg+xml" aria-label="Line chart"></object><object data="heatmap.svg" type="image/svg+xml" aria-label="Heatmap"></object></div>' if target == 'data_visualization' else '') + '</main></html>', encoding="utf-8")

    from .targets import css_tokens
    (directory / 'examples.css').write_text(css_tokens(tokens) + "body{background:var(--apt-background);color:var(--apt-foreground);font:17px/1.6 Arial;margin:0}main{max-width:1100px;margin:auto;padding:24px}a{color:var(--apt-primary)}a:focus-visible{outline:3px solid var(--apt-primary)}.scroll{overflow:auto}object{display:block;width:100%;min-width:700px;aspect-ratio:960/540;margin:24px 0}table{border-collapse:collapse}th,td{border:1px solid var(--apt-border);padding:8px;text-align:right}th{background:var(--apt-panel)}", encoding='utf-8')
