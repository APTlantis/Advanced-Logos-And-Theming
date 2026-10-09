"""Shared deterministic data and denser authored SVG charts."""
import json
import xml.etree.ElementTree as ET

MARKERS = ["o", "s", "^", "D", "v", "+"]
DASHES = ["none", "12 6", "3 5", "12 5 3 5", "18 5", "6 4"]
HATCHES = ["/", "\\", "|", "-", "+", "x"]


def example_data():
    return {
        "categories": ["Intake", "Parse", "Sample", "Cluster", "Select", "Map",
                       "Adapt", "Export", "Check", "Render", "Review", "Archive"],
        "bars": [28, 44, 36, 62, 53, 71, 46, 58, 39, 67, 51, 75],
        "lines": [[18 + i * 8 + (j * (i + 2) + j // 4 * 3) % 22 for j in range(24)] for i in range(6)],
        "heatmap": [[(r * 3 + c * 2 + c // 3) % 9 for c in range(12)] for r in range(8)],
        "periods": [f"Week {i}" for i in range(1, 25)],
        "series_labels": ["Intake", "Extraction", "Mapping", "Export", "Validation", "Review"],
        "heatmap_columns": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "heatmap_rows": ["North", "South", "East", "West", "Central", "Coastal", "Urban", "Rural"],
        "markers": MARKERS, "dash_patterns": DASHES, "hatches": HATCHES,
        "units": "Illustrative units", "intensity_units": "Illustrative level (0–8)", "illustrative": True,
    }


def marker(board, x, y, index, color):
    attrs = {"fill": board.color(color)}
    symbol = MARKERS[index]
    if symbol == "o":
        ET.SubElement(board.root, "circle", cx=str(x), cy=str(y), r="4", **attrs)
    elif symbol == "s":
        board.rect(x - 4, y - 4, 8, 8, color)
    elif symbol == "+":
        board.line(x - 5, y, x + 5, y, color, **{"stroke-width": "2"})
        board.line(x, y - 5, x, y + 5, color, **{"stroke-width": "2"})
    else:
        offsets = {"^": [(-5, 4), (0, -5), (5, 4)],
                   "v": [(-5, -4), (0, 5), (5, -4)],
                   "D": [(0, -5), (5, 0), (0, 5), (-5, 0)]}[symbol]
        ET.SubElement(board.root, "polygon", points=' '.join(f'{x+dx},{y+dy}' for dx, dy in offsets), **attrs)


def charts(tokens, directory, name):
    from .targets import slug
    from .visual_targets import Board
    slots = {"figure.facecolor": "background", "savefig.facecolor": "background",
             "axes.facecolor": "panel", "axes.edgecolor": "border", "axes.labelcolor": "foreground",
             "text.color": "foreground", "xtick.color": "muted", "ytick.color": "muted",
             "grid.color": "border", "legend.facecolor": "panel", "legend.edgecolor": "border"}
    style = "# Image-derived dark style; authored SVG and Matplotlib renders are separate.\n"
    style += ''.join(f'{slot}: {tokens[token]["hex"][1:]}\n' for slot, token in slots.items())
    colors = [tokens[f"series_{i}"]["hex"][1:] for i in range(1, 7)]
    style += "axes.prop_cycle: cycler('color', " + repr(colors) + ") + cycler('linestyle', ['-', '--', ':', '-.', '-', '--'])\n"
    style += "axes.grid: True\ngrid.alpha: 1.0\ngrid.linewidth: 0.6\nlines.linewidth: 2.5\nfont.size: 11\nsavefig.transparent: False\n"
    (directory / (slug(name) + ".mplstyle")).write_text(style, encoding="utf-8")
    scale = [tokens[f"sequential_{i}"]["hex"] for i in range(9)]
    (directory / "scales.json").write_text(json.dumps({"sequential": scale,
        "acceptance_limits": "Single source hue, ordered lightness; no perceptual-uniformity or CVD claim."}, indent=2)+"\n", encoding="utf-8")
    data = example_data()
    (directory / "example-data.json").write_text(json.dumps(data, indent=2)+"\n", encoding="utf-8")

    def axes(board):
        board.rect(85, 115, 825, 305)
        for value in (0, 20, 40, 60, 80):
            y = 420 - value * 3.5
            board.line(85, y, 910, y, **{"stroke-width": "1"})
            board.text(65, y + 5, value, "muted", 15, **{"text-anchor": "end"})
        board.text(85, 508, data["units"], "muted", 15)

    b = Board(tokens, "Category comparison / 12 bars", "Illustrative data • zero baseline • values and patterns supplement color")
    axes(b)
    defs = ET.SubElement(b.root, "defs")
    for i in range(6):
        pattern = ET.SubElement(defs, "pattern", id=f"hatch-{i}", width="10", height="10", patternUnits="userSpaceOnUse")
        paths = ["M0 10L10 0", "M0 0L10 10", "M5 0V10", "M0 5H10", "M5 0V10M0 5H10", "M0 0L10 10M0 10L10 0"]
        ET.SubElement(pattern, "path", d=paths[i], fill="none", stroke=b.color("panel"), **{"stroke-width": "1.5"})
    step = 825 / len(data["bars"])
    for i, value in enumerate(data["bars"]):
        x = 85 + (i + .5) * step
        b.rect(x - 22, 420 - value * 3.5, 44, value * 3.5, f"series_{i%6+1}", **{"data-value": value})
        ET.SubElement(b.root, "rect", x=str(x-22), y=str(420-value*3.5), width="44", height=str(value*3.5), fill=f"url(#hatch-{i%6})")
        b.text(x, 410 - value * 3.5, value, "foreground", 15, **{"text-anchor": "middle"})
        b.text(x, 449, data["categories"][i], "foreground", 12, **{"text-anchor": "middle"})
    b.save(directory / "bars.svg")

    b = Board(tokens, "Change over time / 6 series", "Illustrative data • 24 weekly observations per series • distinct markers and patterns")
    axes(b)
    for i, values in enumerate(data["lines"]):
        points = [(95+j*805/(len(values)-1), 420-v*3.5) for j, v in enumerate(values)]
        ET.SubElement(b.root, "polyline", points=' '.join(f'{x},{y}' for x,y in points), fill="none",
            stroke=b.color(f"series_{i+1}"), **{"stroke-width":"2.5", "stroke-dasharray":DASHES[i], "data-series": data["series_labels"][i]})
        for x, y in points:
            marker(b, x, y, i, f"series_{i+1}")
        lx = 95 + i * 137
        b.line(lx, 480, lx+22, 480, f"series_{i+1}", **{"stroke-dasharray":DASHES[i], "stroke-width":"2.5"})
        marker(b, lx+11, 480, i, f"series_{i+1}")
        b.text(lx+28, 485, data["series_labels"][i], "foreground", 12)
    for j in (0, 3, 7, 11, 15, 19, 23):
        b.text(95+j*805/23, 449, data["periods"][j], "muted", 13, **{"text-anchor":"middle"})
    b.save(directory / "lines.svg")

    b = Board(tokens, "Ordered intensity / 8 × 12 heatmap", "Illustrative monthly levels • single hue • exact values in the accompanying table")
    width, height = 780 / len(data["heatmap_columns"]), 256 / len(data["heatmap_rows"])
    for r, row in enumerate(data["heatmap"]):
        b.text(112, 144+r*height, data["heatmap_rows"][r], "foreground", 14, **{"text-anchor":"end"})
        for c, value in enumerate(row):
            cell = b.rect(130+c*width, 123+r*height, width-3, height-3, f"sequential_{value}", **{"data-value": value})
            ET.SubElement(cell, "title").text = f'{data["heatmap_rows"][r]}, {data["heatmap_columns"][c]}: {value}'
    for c, label in enumerate(data["heatmap_columns"]):
        b.text(130+(c+.5)*width, 403, label, "muted", 14, **{"text-anchor":"middle"})
    for i in range(9):
        b.rect(130+i*60, 440, 60, 22, f"sequential_{i}")
        b.text(160+i*60, 488, i, "foreground", 14, **{"text-anchor":"middle"})
    b.text(700, 456, "Illustrative level", "foreground", 16)
    b.text(130, 520, "0 = lowest intensity; 8 = highest intensity. Values: heatmap-values.html", "muted", 14)
    b.save(directory / "heatmap.svg")
    header = ''.join(f'<th scope="col">{label}</th>' for label in data["heatmap_columns"])
    rows = ''.join('<tr><th scope="row">'+label+'</th>'+''.join(f'<td>{v}</td>' for v in row)+'</tr>'
                   for label, row in zip(data["heatmap_rows"], data["heatmap"]))
    (directory / "heatmap-values.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><title>Heatmap values</title>'
        '<link rel="stylesheet" href="examples.css"><main><a href="examples.html">All charts</a><h1>Heatmap values</h1>'
        '<p>Illustrative monthly levels, 0–8.</p><div class="scroll"><table><caption>Values used by both renderers</caption>'
        '<thead><tr><th scope="col">Region</th>'+header+'</tr></thead><tbody>'+rows+'</tbody></table></div></main></html>', encoding="utf-8")
    return ["bars.svg", "lines.svg", "heatmap.svg"]
