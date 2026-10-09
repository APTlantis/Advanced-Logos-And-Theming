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
    def __init__(self, tokens, title, description):
        self.tokens = tokens
        self.root = ET.Element("svg", xmlns=SVG_NS, width="960", height="540",
                               viewBox="0 0 960 540", role="img", **{"aria-labelledby": "title desc"})
        ET.SubElement(self.root, "title", id="title").text = title
        ET.SubElement(self.root, "desc", id="desc").text = description
        self.rect(0, 0, 960, 540, "background")
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


def diagrams(tokens, directory):
    examples = []
    labels = ("Artwork", "Canonical 32", "Semantics", "Native export")
    b = Board(tokens, "01 / Technical flow", "Orthogonal connectors and outlined nodes • conceptual pipeline")
    for i, label in enumerate(labels):
        x = 40 + i * 230
        b.rect(x, 195, 190, 120, rx=6, stroke=b.color(f"series_{i+1}"), **{"stroke-width": 3})
        b.text(x + 14, 231, f"0{i+1}", "foreground")
        b.text(x + 14, 270, label)
        if i < 3:
            b.line(x + 194, 255, x + 222, 255)
            b.text(x + 200, 246, "→", "foreground", 20)
    b.text(40, 410, "Source bytes → observed colors → role references → derived target tokens", "muted", 17)
    b.save(directory / "technical-flow.svg")
    examples.append("technical-flow.svg")
    b = Board(tokens, "02 / Editorial infographic", "Typographic hierarchy and a large numeral • palette architecture")
    b.text(48, 260, "32", "primary", 132)
    b.text(48, 305, "observed colors", "foreground", 24)
    for i, (heading, body) in enumerate((("Preserve", "Original bytes and canonical RGB"),
                                       ("Interpret", "Roles reference canonical IDs"),
                                       ("Adapt", "Lightness and chroma vary; source hue stays"))):
        y = 140 + i * 110
        b.line(345, y, 900, y, f"series_{i+1}")
        b.text(355, y + 35, heading, "foreground", 24)
        b.text(355, y + 66, body, "muted", 17)
    b.save(directory / "editorial-infographic.svg")
    examples.append("editorial-infographic.svg")
    b = Board(tokens, "03 / Orbit map", "Radial composition and numbered satellites • conceptual target families")
    positions = ((220, 160), (735, 160), (220, 370), (735, 370))
    for i, ((x, y), label) in enumerate(zip(positions, ("Documents", "Editors", "Diagrams", "Charts")), 1):
        b.line(480, 280, x, y, f"series_{i}")
        ET.SubElement(b.root, "circle", cx=str(x), cy=str(y), r="64", fill=b.color("panel"),
                      stroke=b.color(f"series_{i}"), **{"stroke-width": "3"})
        b.text(x, y-5, f"0{i}", "foreground", 24, **{"text-anchor": "middle"})
        b.text(x, y+24, label, "muted", 17, **{"text-anchor": "middle"})
    ET.SubElement(b.root, "circle", cx="480", cy="280", r="90", fill=b.color("panel"),
                  stroke=b.color("primary"), **{"stroke-width": "3"})
    b.text(480, 275, "Canonical", "foreground", 24, **{"text-anchor": "middle"})
    b.text(480, 309, "32 colors", "primary", 24, **{"text-anchor": "middle"})
    b.save(directory / "orbit-map.svg")
    return examples + ["orbit-map.svg"]


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
    if target == 'syntax_highlighting':
        return
    links = ''.join(f'<li><a href="{file}">{file}</a></li>' for file in result["examples"])
    (directory / "examples.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><title>Visual examples</title>'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><link rel="stylesheet" href="examples.css"><main><h1>'+html.escape(name)+' / '+target+'</h1><p>'+html.escape(result["acceptance_limits"])+
        '</p><ul>'+links+'</ul>' + ('<p><a href="heatmap-values.html">Heatmap value table</a></p><div class="scroll"><object data="bars.svg" type="image/svg+xml" aria-label="Bar chart"></object><object data="lines.svg" type="image/svg+xml" aria-label="Line chart"></object><object data="heatmap.svg" type="image/svg+xml" aria-label="Heatmap"></object></div>' if target == 'data_visualization' else '') + '</main></html>', encoding="utf-8")

    from .targets import css_tokens
    (directory / 'examples.css').write_text(css_tokens(tokens) + "body{background:var(--apt-background);color:var(--apt-foreground);font:17px/1.6 Arial;margin:0}main{max-width:1100px;margin:auto;padding:24px}a{color:var(--apt-primary)}a:focus-visible{outline:3px solid var(--apt-primary)}.scroll{overflow:auto}object{display:block;width:100%;min-width:700px;aspect-ratio:960/540;margin:24px 0}table{border-collapse:collapse}th,td{border:1px solid var(--apt-border);padding:8px;text-align:right}th{background:var(--apt-panel)}", encoding='utf-8')
