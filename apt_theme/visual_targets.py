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


def syntax(tokens, directory):
    from .targets import css_tokens
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
    for classes, key in PRISM.items():
        fallback = {"diff_added": "success", "diff_deleted": "error"}
        token = key if key in tokens else fallback[key]
        selectors = ", ".join(".token." + cls for cls in classes.split())
        css += f"{selectors} {{ color:var(--apt-{token.replace('_', '-')}); }}\n"
    (directory / "prism.css").write_text(css, encoding="utf-8")
    # Authored tokens deliberately avoid claiming a language grammar was executed.
    code = [('comment', '// Authored JavaScript token fixture; illustrative'), ('', '\n'),
            ('keyword', 'class'), ('', ' '), ('class-name', 'Palette'), ('punctuation', ' {'), ('', '\n  '),
            ('function', 'count'), ('punctuation', '() {'), ('', '\n    '), ('keyword', 'const'), ('', ' '),
            ('property', 'name'), ('operator', ' = '), ('string', '"Aptlantis"'), ('punctuation', ';'),
            ('', '\n    '), ('keyword', 'return'), ('', ' '), ('number', '32'), ('operator', ' + '),
            ('constant', 'OFFSET'), ('punctuation', ';'), ('', '\n  '), ('punctuation', '}'),
            ('', '\n'), ('punctuation', '}')]
    markup = ''.join(f'<span class="token {cls}">{html.escape(value)}</span>' if cls else html.escape(value)
                     for cls, value in code)
    page = ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Syntax example</title><style>' + css +
            'body{background:var(--apt-background);color:var(--apt-foreground);font:18px Arial;padding:32px}'
            '</style><h1>Syntax highlighting</h1><p>Prism CSS contract. Authored tokens; no grammar engine is bundled.</p>'
            '<pre class="language-javascript"><code class="language-javascript">' + markup + '</code></pre></html>')
    (directory / "syntax-example.html").write_text(page, encoding="utf-8")
    return ["syntax-example.html"]


def charts(tokens, directory, name):
    from .targets import slug
    slots = {"figure.facecolor": "background", "savefig.facecolor": "background",
             "axes.facecolor": "panel", "axes.edgecolor": "border", "axes.labelcolor": "foreground",
             "text.color": "foreground", "xtick.color": "muted", "ytick.color": "muted",
             "grid.color": "border", "legend.facecolor": "panel", "legend.edgecolor": "border"}
    # Matplotlibrc treats # as a comment; bare six-digit hex is its color syntax.
    style = "# Image-derived dark style. Illustrative samples do not prove Matplotlib rendering.\n"
    style += ''.join(f'{slot}: {tokens[token]["hex"][1:]}\n' for slot, token in slots.items())
    colors = [tokens[f"series_{i}"]["hex"][1:] for i in range(1, 7)]
    style += "axes.prop_cycle: cycler('color', " + repr(colors) + ") + cycler('linestyle', ['-', '--', ':', '-.', '-', '--'])\n"
    style += "axes.grid: True\ngrid.alpha: 1.0\ngrid.linewidth: 0.6\nlines.linewidth: 2.5\nfont.size: 11\nsavefig.transparent: False\n"
    (directory / (slug(name) + ".mplstyle")).write_text(style, encoding="utf-8")
    scale = [tokens[f"sequential_{i}"]["hex"] for i in range(9)]
    (directory / "scales.json").write_text(json.dumps({"sequential": scale,
        "acceptance_limits": "Single source hue, ordered lightness; no perceptual-uniformity or CVD claim."}, indent=2)+"\n", encoding="utf-8")
    data = {"categories": ["A", "B", "C", "D"], "bars": [28, 44, 36, 62],
            "lines": [[18, 34, 26, 52], [38, 28, 48, 42]],
            "heatmap": [[0, 1, 4, 6], [2, 5, 7, 8], [1, 3, 6, 4]], "illustrative": True}
    (directory / "example-data.json").write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")
    b = Board(tokens, "Category comparison / bars", "Illustrative units • zero baseline • direct value labels")
    b.rect(95, 115, 810, 310)
    for value in (0, 20, 40, 60, 80):
        y = 420 - value * 3.5
        b.line(95, y, 905, y, **{"stroke-width": "1"})
        b.text(60, y+5, value, "muted", 15)
    for i, value in enumerate(data["bars"]):
        x = 150 + i * 190
        b.rect(x, 420-value*3.5, 100, value*3.5, f"series_{i+1}")
        b.text(x+50, 405-value*3.5, value, "foreground", 18, **{"text-anchor": "middle"})
        b.text(x+50, 455, data["categories"][i], "foreground", 18, **{"text-anchor": "middle"})
    b.save(directory / "bars.svg")
    b = Board(tokens, "Change over time / lines", "Illustrative units • labeled series and distinct line patterns")
    b.rect(95, 115, 810, 310)
    for value in (0, 20, 40, 60, 80):
        y = 420-value*3.5
        b.line(95, y, 905, y, **{"stroke-width": "1"})
        b.text(60, y+5, value, "muted", 15)
    for i, values in enumerate(data["lines"], 1):
        points = [(145+j*215, 420-v*3.5) for j, v in enumerate(values)]
        ET.SubElement(b.root, "polyline", points=' '.join(f'{x},{y}' for x,y in points), fill="none",
                      stroke=b.color(f"series_{i}"), **{"stroke-width": "4", "stroke-dasharray": "none" if i == 1 else "12 8"})
        for (x,y), v in zip(points, values):
            b.rect(x-4, y-4, 8, 8, f"series_{i}")
        b.text(805, points[-1][1]-12, f"Series {i}", "foreground", 16)
    for i in range(4):
        b.text(145+i*215, 455, f"Period {i+1}", "muted", 16, **{"text-anchor": "middle"})
    b.save(directory / "lines.svg")
    b = Board(tokens, "Ordered intensity / heatmap", "Illustrative level 0–8 • single hue • values shown below cells")
    for r, row in enumerate(data["heatmap"]):
        b.text(40, 162+r*90, f"Row {r+1}", "muted", 16)
        for c, value in enumerate(row):
            x, y = 150+c*180, 115+r*90
            b.rect(x, y, 140, 50, f"sequential_{value}")
            b.text(x+70, y+73, value, "foreground", 17, **{"text-anchor": "middle"})
    for i in range(9):
        b.rect(150+i*70, 425, 70, 28, f"sequential_{i}")
        b.text(185+i*70, 480, i, "muted", 16, **{"text-anchor": "middle"})
    b.save(directory / "heatmap.svg")
    return ["bars.svg", "lines.svg", "heatmap.svg"]


def export_visual(result, directory, name):
    tokens, target = result["tokens"], result["target"]
    if target == "svg":
        result["examples"] = diagrams(tokens, directory)
        result["acceptance_limits"] = "Standalone SVG presentation attributes; SVG editor import/font substitution pending."
    elif target == "syntax_highlighting":
        result["examples"] = syntax(tokens, directory)
        result["acceptance_limits"] = "Prism CSS classes; authored visual fixture only. Grammar execution and host integration pending."
    else:
        result["examples"] = charts(tokens, directory, name)
        result["acceptance_limits"] = "Matplotlib mplstyle plus explicit JSON scale; SVG examples are authored independently. Matplotlib loading/rendering pending; no CVD or category-separation guarantee."
    links = ''.join(f'<li><a href="{file}">{file}</a></li>' for file in result["examples"])
    (directory / "examples.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><title>Visual examples</title>'
        '<h1>'+html.escape(name)+' / '+target+'</h1><p>'+html.escape(result["acceptance_limits"])+
        '</p><ul>'+links+'</ul></html>', encoding="utf-8")
