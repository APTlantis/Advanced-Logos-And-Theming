"""Offline visual review and labeled palette graphics."""
import base64
import html
import json
import math
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageCms, ImageDraw, ImageFont


def swatch(colors, path, title):
    width, columns, cell_height = 1024, 4, 72
    image = Image.new("RGB", (width, 80 + math.ceil(len(colors) / columns) * cell_height), "#111820")
    draw = ImageDraw.Draw(image)
    font_path = Path("C:/Windows/Fonts/consola.ttf")
    font = ImageFont.truetype(str(font_path), 15) if font_path.exists() else ImageFont.load_default(size=15)
    draw.text((16, 20), title[:95], font=font, fill="white")
    for i, (key, c) in enumerate(colors.items()):
        x, y = (i % columns) * width // columns, 80 + i // columns * cell_height
        draw.rectangle((x + 12, y + 5, x + 65, y + 58), fill=c["hex"])
        draw.text((x + 74, y + 10), key, font=font, fill="white")
        draw.text((x + 74, y + 32), c["hex"], font=font, fill="#b9c5d0")
    image.save(path)


def tiles(colors):
    return '<div class="swatches">' + "".join(
        f'<div><span style="background:{c["hex"]}"></span><code>{html.escape(key)}<br>{c["hex"]}</code></div>'
        for key, c in colors.items()) + "</div>"


def table(rows):
    if not rows:
        return "<p>None.</p>"
    columns = list(rows[0])
    return "<div class=scroll><table><thead><tr>" + "".join(f"<th>{html.escape(k)}</th>" for k in columns) + "</tr></thead><tbody>" + "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(row.get(k, '')))}</td>" for k in columns) + "</tr>" for row in rows) + "</tbody></table></div>"


def review(directory, name, colors, candidates, roles, notices, results, diagnostics, image=None, comparison=None):
    directory = Path(directory)
    pieces = [f"<h1>{html.escape(name)}</h1><p>Dark, image-derived themes. Native application import and visual acceptance remain pending.</p>"]
    if image:
        with tempfile.TemporaryDirectory(prefix="apt-preview-") as temp:
            profile = Path(temp) / "sRGB.icc"
            profile.write_bytes(ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes())
            rendered = subprocess.run(["magick", str(image) + "[0]", "-auto-orient", "-profile", str(profile),
                                       "-colorspace", "sRGB", "-thumbnail", "700x700>", "-depth", "8",
                                       "-strip", "-define", "png:exclude-chunks=all", "png:-"], capture_output=True)
            if rendered.returncode:
                raise ValueError(rendered.stderr.decode(errors="replace"))
        pieces.append('<img class=source alt="Source artwork" src="data:image/png;base64,' + base64.b64encode(rendered.stdout).decode() + '">')
    pieces += ["<h2>Canonical 32</h2>", tiles(colors), "<h2>Selection diagnostics</h2>",
               "<pre>" + html.escape(json.dumps(diagnostics, indent=2)) + "</pre>"]
    if comparison:
        pieces += ["<h2>Previous selection</h2>", tiles(comparison)]
    pieces += ["<details><summary>Candidate colors</summary>", tiles({f"candidate_{i:03}": c for i, c in enumerate(candidates, 1)}), "</details>",
               "<h2>Semantic mapping</h2>", table([{"role": r, "canonical": ref, "hex": colors[ref]["hex"]} for r, ref in roles.items()]),
               "<h2>Semantic findings</h2>", "<pre>" + html.escape(json.dumps(notices, indent=2)) + "</pre>"]
    for result in results:
        t = result["tokens"]
        pieces += [f'<h2>{html.escape(result["target"])}</h2><p>{result["named_count"]} named tokens; {result["unique_count"]} unique colors; budget {result["budget"]}; {result["contrast_failures"]} contrast failures.</p>']
        style = f'background:{t["background"]["hex"]};color:{t["foreground"]["hex"]};padding:24px;border-radius:8px'
        if result["target"] == "windows_terminal":
            from .targets import ANSI
            sample = "<code>PS C:\\Aptlantis&gt; apt-theme generate logo.tif</code><br>"
            for role in ANSI:
                for key in (role, "bright" + role.title()):
                    sample += f'<span style="color:{t[key]["hex"]}">{key}: build output, 0123456789</span><br>'
            sample += f'<span style="background:{t["selection"]["hex"]}">Selected terminal text</span>'
        else:
            sample = f'<h3 style="color:{t["primary"]["hex"]}">Aptlantis documentation</h3><p>Body text and a <a style="color:{t["primary"]["hex"]}" href="#">link</a>.</p>'
            sample += f'<pre style="background:{t["panel"]["hex"]};padding:16px">'
            for role in ("keyword", "function", "string", "number", "comment"):
                key = role + "_on_panel" if role + "_on_panel" in t else role
                sample += f'<span style="color:{t[key]["hex"]}">{role}: const gold = "Aptlantis"; // 32 colors</span>\n'
            sample += "</pre>"
            sample += f'<span style="background:{t["selection"]["hex"]};color:{t["selection_text"]["hex"]}">Selected document text</span>'
            if "native_slots" in result:
                sample += table([{"Office slot": s, "token": token, "hex": t[token]["hex"]} for s, token in result["native_slots"].items()])
                sample += f'<p><a href="powerpoint/{html.escape(result["sample_deck"]["file"], quote=True)}">Open the editable four-slide sample deck</a>. Chart values are illustrative. Native PowerPoint acceptance remains pending.</p>'
        pieces += [f'<div style="{style}">{sample}</div>', tiles(t),
                   "<details><summary>Contrast, provenance and omissions</summary>",
                   table([{**c, "ratio": round(c["ratio"], 3)} for c in result["checks"]]),
                   "<pre>" + html.escape(json.dumps({"origins": {k: c["origin"] for k, c in t.items()},
                        "aliases": result["aliases"], "omitted_canonical": result["omitted_canonical"]}, indent=2)) + "</pre></details>"]
    document = """<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Theme review</title><style>
body{background:#101820;color:#e8edf3;font:16px/1.5 system-ui;margin:0 auto;padding:32px;max-width:1200px}
h1,h2{color:#e9be68}.source{max-width:100%;max-height:550px}.swatches{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:10px;margin:20px 0}
.swatches>div{display:flex;gap:12px;align-items:center}.swatches span{width:48px;height:48px;border:1px solid #647080;flex-shrink:0}
table{border-collapse:collapse;width:100%}td,th{text-align:left;padding:8px;border-bottom:1px solid #405060}.scroll{overflow:auto}
pre{white-space:pre-wrap;overflow-wrap:anywhere}summary{cursor:pointer;padding:14px}details{margin:20px 0}a{color:#a4ccdf}
</style>""" + "".join(pieces) + "</html>"
    (directory / "review.html").write_text(document, encoding="utf-8")
