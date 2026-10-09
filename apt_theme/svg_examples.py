"""Editable SVG compositions for diagrams, editorial work, icons, maps and illustration.

All paints come from exported tokens. Local symbols, paths, patterns and clips
remain vector geometry; examples contain no script or external resources.
"""
import html
import base64
import math
import textwrap
import xml.etree.ElementTree as ET
from contextlib import contextmanager

ICONS = {
    "source": "M5 3H15L21 9V25H5ZM15 3V9H21M9 14H17M9 19H17",
    "palette": "M15 3C7 3 3 8 3 15S9 27 16 27C22 27 20 22 18 21C16 20 19 17 23 17C29 17 27 3 15 3ZM9 10H10M16 8H17M22 11H23M8 17H9",
    "code": "M10 7L3 15L10 23M20 7L27 15L20 23M18 4L12 26",
    "layers": "M15 3L28 10L15 17L2 10ZM3 16L15 23L27 16M3 22L15 29L27 22",
    "terminal": "M3 5H27V25H3ZM7 10L12 15L7 20M16 20H23",
    "document": "M7 3H23V27H7ZM11 9H19M11 14H19M11 19H17",
    "check": "M15 2L26 6V16C26 23 15 28 15 28S4 23 4 16V6ZM9 14L13 18L21 10",
    "archive": "M3 4H27V10H3ZM6 10V27H24V10M11 15H19M15 15V20",
    "search": "M21 13A8 8 0 1 1 5 13A8 8 0 1 1 21 13M19 19L28 28",
    "pin": "M15 2C4 2 3 13 8 19L15 28L22 19C27 13 26 2 15 2ZM19 11A4 4 0 1 1 11 11A4 4 0 1 1 19 11",
    "network": "M12 3H18V9H12ZM2 21H8V27H2ZM22 21H28V27H22ZM5 21V15H25V21M15 9V15",
    "image": "M3 4H27V26H3ZM3 22L11 13L17 20L22 15L27 22M22 9H23",
}


class Canvas:
    def __init__(self, tokens, title, description):
        from .visual_targets import Board
        self.board = Board(tokens, title, description, 1200, 800)
        self.defs = ET.SubElement(self.root, "defs")
        for name, path in ICONS.items():
            symbol = ET.SubElement(self.defs, "symbol", id=f"icon-{name}", viewBox="0 0 30 30")
            ET.SubElement(symbol, "path", d=path, fill="none", **{"stroke-width": "1.8", "stroke-linecap": "round", "stroke-linejoin": "round"})
        marker = ET.SubElement(self.defs, "marker", id="arrow", viewBox="0 0 10 10", refX="9", refY="5",
                               markerWidth="7", markerHeight="7", orient="auto-start-reverse")
        ET.SubElement(marker, "path", d="M1 1L9 5L1 9Z", fill=self.color("border"))

    def __getattr__(self, name):
        return getattr(self.board, name)

    @contextmanager
    def layer(self, name, label):
        previous = self.board.root
        self.board.root = ET.SubElement(previous, "g", id=name, **{"aria-label": label})
        try:
            yield
        finally:
            self.board.root = previous

    def path(self, d, key="border", fill="none", **attrs):
        return ET.SubElement(self.root, "path", d=d, stroke=self.color(key),
                             fill=self.color(fill) if fill != "none" else "none",
                             **{"stroke-width": "2", "stroke-linejoin": "round", **{k:str(v) for k,v in attrs.items()}})

    def circle(self, x, y, r, key="panel", **attrs):
        return ET.SubElement(self.root, "circle", cx=str(x), cy=str(y), r=str(r), fill=self.color(key),
                             **{k:str(v) for k,v in attrs.items()})

    def icon(self, name, x, y, size=30, key="primary"):
        return ET.SubElement(self.root, "use", href=f"#icon-{name}", x=str(x), y=str(y),
                             width=str(size), height=str(size), stroke=self.color(key), fill="none")

    def card(self, x, y, w, title, detail, icon, key="primary", h=94):
        self.rect(x, y, w, h, rx=10, stroke=self.color(key), **{"stroke-width": 2})
        self.icon(icon, x+16, y+18, 30, key)
        self.text(x+58, y+36, title, "foreground", 18)
        self.text(x+16, y+72, detail, "muted", 13)

    def footer(self, label):
        self.line(36, 746, 1164, 746, **{"stroke-width":"1"})
        self.text(36, 775, label, "muted", 14)
        self.text(1164, 775, "ILLUSTRATIVE / EDITABLE VECTOR", "muted", 12, **{"text-anchor":"end"})


def technical(tokens, directory):
    b = Canvas(tokens, "01 / Technical workflow", "Swimlanes, decisions, revision loops and preservation boundaries")
    lanes = [(120, "SOURCE", "Original bytes retained"), (285, "ENGINE", "Canonical identity stays separate"),
             (450, "REVIEW", "Local artifacts before application acceptance")]
    with b.layer("swimlanes", "Three workflow lanes"):
        for y, title, detail in lanes:
            b.rect(36, y, 1128, 148, "elevated", rx=12)
            b.text(54, y+29, title, "foreground", 14)
            for i, line in enumerate(textwrap.wrap(detail, 25)):
                b.text(54, y+56+i*20, line, "muted", 12)
    with b.layer("connectors", "Workflow connectors and revision loop"):
        for y in (170, 335, 500):
            for x in (490, 745):
                b.path(f"M{x} {y}H{x+22}", **{"marker-end":"url(#arrow)"})
        b.path("M1000 191H1096V277H356V309", **{"marker-end":"url(#arrow)"})
        b.path("M1000 356H1096V440H356V474", **{"marker-end":"url(#arrow)"})
        b.path("M1000 568V605H920V640", **{"marker-end":"url(#arrow)"})
        b.path("M601 568V623H601V670H326V568", **{"stroke-dasharray":"7 6", "marker-end":"url(#arrow)"})
        b.text(385, 647, "Revise semantic mapping; retain canonical colors", "muted", 14)
    with b.layer("workflow-nodes", "Nine workflow nodes"):
        rows = [
            (144, [("Artwork", "TIFF / PNG / SVG source", "image"), ("Normalize", "Orientation and color profile", "source"), ("Provenance", "Source hash and preserved bytes", "archive")]),
            (309, [("Canonical 32", "Observed RGB values and IDs", "palette"), ("Semantic roles", "Source references and findings", "layers"), ("Target tokens", "Dark adaptation; source hue", "code")]),
            (474, [("Native export", "Target contract and artifacts", "document"), ("Local checks", "Parsing, contrast and previews", "check"), ("Operator review", "Application import is separate", "search")]),
        ]
        for y, cards in rows:
            for i, (title, detail, icon) in enumerate(cards):
                b.card(260+i*255, y, 230, title, detail, icon, f"series_{i+1}")
    with b.layer("decision", "Review decision and preserved evidence"):
        b.path("M920 640L962 677L920 714L878 677Z", "primary", "panel")
        b.text(920, 682, "Ready?", "foreground", 13, **{"text-anchor":"middle"})
        b.path("M962 677H1000", **{"marker-end":"url(#arrow)"})
        b.text(1008, 669, "Record findings", "foreground", 15)
        b.text(1008, 694, "No auto activation", "muted", 13)
        b.text(54, 701, "All stages keep dated recovery evidence", "foreground", 16)
    b.footer("TECHNICAL / Architecture, runbooks and process documentation")
    b.save(directory / "technical-flow.svg")


def editorial(tokens, directory):
    b = Canvas(tokens, "02 / Editorial infographic", "Large typography, section hierarchy, reusable marks and layered composition")
    with b.layer("hero", "Canonical identity hero"):
        b.rect(36, 120, 350, 586, rx=16)
        b.text(65, 145, "THE PALETTE", "muted", 15)
        b.text(60, 318, "32", "primary", 170)
        b.text(65, 391, "observed colors", "foreground", 28)
        for r in range(4):
            for c in range(8):
                b.rect(65+c*36, 424+r*32, 27, 24, f"series_{(r*8+c)%6+1}", rx=4)
        b.text(65, 579, "32 cells / conceptual palette", "muted", 14)
        b.text(65, 623, "Identity before adaptation", "foreground", 19)
        b.text(65, 652, "Actual RGB values: palette.toml", "muted", 14)
        b.text(65, 675, "Tiles repeat the six mark tokens", "muted", 13)
    with b.layer("editorial-sections", "Three editorial sections"):
        sections = [("01", "Preserve", "Original artwork and provenance", "Byte-preserved sources; dated evidence.", "source"),
                    ("02", "Interpret", "Meaning references the palette", "Semantic assignments remain separate.", "layers"),
                    ("03", "Adapt", "Readable dark application surfaces", "Lightness and chroma may vary; hue stays.", "code")]
        for i, (num, title, subtitle, detail, icon) in enumerate(sections):
            y=120+i*166
            b.rect(410, y, 754, 146, "panel", rx=12)
            b.text(438, y+53, num, f"series_{i+1}", 38)
            b.icon(icon, 1110, y+22, 30, f"series_{i+1}")
            b.text(525, y+44, title, "foreground", 27)
            b.text(525, y+79, subtitle, "foreground", 18)
            b.text(525, y+114, detail, "muted", 15)
            b.line(438, y+132, 1136, y+132, f"series_{i+1}", **{"stroke-width":"2"})
    with b.layer("editorial-notes", "Supporting editorial callouts"):
        for i, (title, detail) in enumerate([("10", "existing target formats"), ("3", "separate artifact layers"), ("0", "automatic installations")]):
            x=410+i*258
            b.rect(x, 638, 238, 68, "elevated", rx=9)
            b.text(x+16, 679, title, "foreground", 29)
            b.text(x+65, 678, detail, "muted", 13)
    b.footer("EDITORIAL / Explainers, posters and presentation figures")
    b.save(directory / "editorial-infographic.svg")


def orbit(tokens, directory):
    b = Canvas(tokens, "03 / Relationship map", "Concentric guides, six linked families, secondary nodes and a readable legend")
    cx, cy = 600, 386
    labels = [("Documents", "document", "Typography / tables"), ("Editors", "code", "Syntax / selections"),
              ("Terminals", "terminal", "ANSI / cursor"), ("Diagrams", "network", "Nodes / connectors"),
              ("Charts", "layers", "Series / scales"), ("Presentations", "image", "Native Office slots")]
    with b.layer("orbital-guides", "Concentric relationship guides"):
        for radius in (126, 190, 258):
            b.circle(cx, cy, radius, "background", stroke=b.color("border"), **{"stroke-width":"1", "stroke-dasharray":"4 8"})
        for angle in range(0,360,30):
            a=math.radians(angle)
            b.line(cx+128*math.cos(a), cy+128*math.sin(a), cx+258*math.cos(a), cy+258*math.sin(a), **{"stroke-width":"1", "opacity":".3"})
    with b.layer("relationships", "Six family connections"):
        positions=[]
        for i in range(6):
            a=math.radians(-90+i*60)
            x,y=cx+292*math.cos(a),cy+198*math.sin(a)
            positions.append((x,y))
            b.path(f"M{cx} {cy}Q{cx+(x-cx)*.7} {cy} {x} {y}", f"series_{i+1}", **{"stroke-width":"2.5"})
        for i, ((x,y), (title, icon, detail)) in enumerate(zip(positions, labels)):
            b.circle(x,y,71,"panel",stroke=b.color(f"series_{i+1}"), **{"stroke-width":"2.5"})
            b.icon(icon,x-16,y-40,32,f"series_{i+1}")
            b.text(x,y+16,title,"foreground",17,**{"text-anchor":"middle"})
            b.text(x,y+39,f"0{i+1}","muted",13,**{"text-anchor":"middle"})
            sx=x+(110 if x>=cx else -110)
            b.line(x+(71 if x>=cx else -71),y,sx,y,f"series_{i+1}",**{"stroke-width":"2"})
            b.circle(sx,y,5,f"series_{i+1}")
    with b.layer("identity", "Shared canonical identity"):
        b.circle(cx,cy,106,"elevated",stroke=b.color("primary"),**{"stroke-width":"3"})
        b.text(cx,cy-55,"CANONICAL","foreground",17,**{"text-anchor":"middle"})
        b.text(cx,cy+27,"32","primary",58,**{"text-anchor":"middle"})
        b.text(cx,cy+59,"one source identity","muted",14,**{"text-anchor":"middle"})
    with b.layer("family-legend", "Target-family legend"):
        for i, (title, icon, detail) in enumerate(labels):
            x=36+(i%3)*380; y=687+(i//3)*28
            b.rect(x,y-11,10,10,f"series_{i+1}",rx=2)
            b.text(x+19,y,title+" / "+detail,"foreground",13)
    b.footer("RELATIONSHIPS / System maps, taxonomies and dependency overviews")
    b.save(directory / "orbit-map.svg")


def icons(tokens, directory):
    b = Canvas(tokens, "04 / Reusable icon sheet", "Twelve local symbols • consistent strokes • three sizes • multiple surface treatments")
    with b.layer("icon-catalog", "Twelve labeled reusable icons"):
        for i, name in enumerate(ICONS):
            x=36+(i%4)*286; y=120+(i//4)*163
            b.rect(x,y,270,145,rx=12,stroke=b.color("border"),**{"stroke-width":"1"})
            b.icon(name,x+22,y+26,56,f"series_{i%6+1}")
            b.text(x+96,y+46,name.title(),"foreground",19)
            b.text(x+96,y+75,f"symbol: icon-{name}","muted",13)
            for j,size in enumerate((16,24,32)):
                b.icon(name,x+100+j*49,y+94,size,"foreground")
            b.text(x+22,y+124,f"{i+1:02}","muted",13)
    with b.layer("surface-treatments", "Examples of icon use on dark surfaces"):
        for i,(surface,label) in enumerate([("panel","Outlined tile"),("elevated","Raised surface"),("background","Open canvas")]):
            x=36+i*380
            b.rect(x,642,364,66,surface,rx=10,stroke=b.color("border"),**{"stroke-width":"1"})
            b.icon("check",x+20,658,34,"foreground")
            b.text(x+76,682,label,"foreground",19)
    b.footer("ICONS / UI assets, manuals, badges and diagram annotations")
    b.save(directory / "icon-sheet.svg")


def wayfinding(tokens, directory):
    b = Canvas(tokens, "05 / Wayfinding map", "Illustrative campus • paths, blocks, route markers, landmarks and a map key")
    with b.layer("map-base", "Campus blocks and pedestrian paths"):
        b.rect(36,120,820,586,rx=14)
        # A local same-token pattern provides texture without introducing paints.
        pattern=ET.SubElement(b.defs,"pattern",id="map-grid",width="28",height="28",patternUnits="userSpaceOnUse")
        ET.SubElement(pattern,"path",d="M28 0H0V28",fill="none",stroke=b.color("border"),opacity=".18",**{"stroke-width":"1"})
        ET.SubElement(b.root,"rect",x="36",y="120",width="820",height="586",rx="14",fill="url(#map-grid)")
        for d in ("M70 280H820", "M70 480H820", "M320 150V675", "M600 150V675"):
            b.path(d,"elevated",**{"stroke-width":"32", "stroke-linecap":"round"})
            b.path(d,"border",**{"stroke-width":"1", "stroke-dasharray":"5 8"})
        buildings=[(90,160,155,80,"Library","document"),(375,160,150,80,"Studio","image"),(655,160,145,80,"Archive","archive"),
                   (90,340,155,94,"Workshop","code"),(375,340,150,94,"Gallery","palette"),(655,340,145,94,"Review","check"),
                   (90,540,155,100,"Intake","source"),(655,540,145,100,"Commons","network")]
        for i,(x,y,w,h,label,icon) in enumerate(buildings):
            b.rect(x,y,w,h,"elevated",rx=8,stroke=b.color(f"series_{i%6+1}"),**{"stroke-width":"2"})
            b.icon(icon,x+15,y+13,25,"foreground")
            b.text(x+15,y+h-19,label,"foreground",17)
        b.path("M390 544Q460 520 525 563L515 635Q450 666 390 630Z","series_3","panel",**{"stroke-dasharray":"4 5"})
        for x,y in [(410,574),(474,560),(488,614),(421,627)]:
            b.circle(x,y,8,"series_3")
        b.text(406,605,"Garden","foreground",16)
    with b.layer("routes", "Two labeled illustrative routes"):
        b.path("M167 640V675H320V280H730V240","primary",**{"stroke-width":"5", "stroke-linecap":"round"})
        b.path("M170 434V480H600V280H450V240","series_3",**{"stroke-width":"4", "stroke-dasharray":"10 7"})
        for i,(x,y) in enumerate([(320,650),(320,480),(320,280),(600,280),(730,280)],1):
            b.circle(x,y,13,"panel",stroke=b.color("primary"),**{"stroke-width":"2"})
            b.text(x,y+5,i,"foreground",13,**{"text-anchor":"middle"})
        b.icon("pin",142,648,28,"primary")
        b.text(74,691,"START","foreground",12)
    with b.layer("map-key", "Map legend and orientation"):
        b.rect(880,120,284,586,"elevated",rx=14)
        b.text(904,165,"MAP KEY","foreground",18)
        b.line(907,208,951,208,"primary",**{"stroke-width":"5"})
        b.text(966,213,"Archive route","foreground",16)
        b.line(907,252,951,252,"series_3",**{"stroke-width":"4","stroke-dasharray":"10 7"})
        b.text(966,257,"Studio route","foreground",16)
        b.icon("pin",907,287,28,"foreground")
        b.text(966,310,"Entry point","foreground",16)
        b.circle(921,352,11,"panel",stroke=b.color("primary"),**{"stroke-width":"2"})
        b.text(966,357,"Route step","foreground",16)
        b.line(1022,520,1022,450,"primary",**{"marker-end":"url(#arrow)"})
        b.text(1022,432,"N","foreground",20,**{"text-anchor":"middle"})
        b.text(904,581,"Conceptual layout","foreground",18)
        b.text(904,610,"Positions are illustrative.","muted",14)
        b.text(904,637,"No distances or live routing.","muted",14)
        b.text(904,680,"NOT TO SCALE","muted",12)
    b.footer("WAYFINDING / Campus guides, floor plans and schematic maps")
    b.save(directory / "wayfinding-map.svg")


def illustration(tokens, directory):
    b = Canvas(tokens, "06 / Product illustration", "Layered vector scene • clipping • tonal glow • repeated symbols • editorial callouts")
    gradient=ET.SubElement(b.defs,"radialGradient",id="tonal-glow",cx="50%",cy="50%",r="50%")
    for offset,opacity in [("0%",".18"),("100%","0")]:
        ET.SubElement(gradient,"stop",offset=offset,**{"stop-color":b.color("primary"),"stop-opacity":opacity})
    clip=ET.SubElement(b.defs,"clipPath",id="screen-clip")
    ET.SubElement(clip,"rect",x="285",y="220",width="630",height="340",rx="8")
    with b.layer("scene-background", "Decorative vector scene"):
        ET.SubElement(b.root,"ellipse",cx="600",cy="386",rx="475",ry="274",fill="url(#tonal-glow)")
        for radius in (210,260,310):
            b.path(f"M{600-radius} 410C{600-radius} {410-radius} {600+radius} {410-radius} {600+radius} 410", "border", **{"opacity":".4","stroke-dasharray":"3 7"})
        for i in range(9):
            x=145+i*112
            b.circle(x,655,3,"primary")
        b.path("M206 617L384 703H1027L850 617Z","border","panel")
        for i in range(6):
            b.path(f"M{350+i*90} 630L{445+i*90} 687","border",**{"stroke-width":"1"})
    with b.layer("device", "Device frame and stand"):
        b.rect(261,180,678,404,"elevated",rx=20,stroke=b.color("border"),**{"stroke-width":"2"})
        b.rect(285,220,630,340,"background",rx=8)
        b.circle(600,200,3,"muted")
        b.path("M550 584L537 640H664L650 584Z","border","elevated")
        b.rect(494,637,210,13,"panel",rx=6,stroke=b.color("border"))
    with b.layer("screen-content", "Clipped illustrative application surface"):
        content=ET.SubElement(b.root,"g",**{"clip-path":"url(#screen-clip)"})
        previous=b.board.root; b.board.root=content
        try:
            b.rect(285,220,630,48,"panel")
            b.icon("palette",304,230,27,"primary")
            b.text(346,251,"Palette workspace","foreground",17)
            for x in (846,866,886): b.circle(x,243,3,"muted")
            b.rect(285,268,124,292,"panel")
            for i,(icon,label) in enumerate([("source","Source"),("layers","Roles"),("code","Tokens"),("check","Review")]):
                y=289+i*56
                b.icon(icon,303,y,24,"foreground")
                b.text(337,y+17,label,"foreground",13)
            b.text(433,302,"Adapted swatches","foreground",19)
            for r in range(3):
                for c in range(6):
                    b.rect(433+c*72,321+r*47,60,34,f"series_{(r*6+c)%6+1}",rx=5)
            b.text(433,485,"Conceptual screen / illustrative tiles","muted",13)
            b.rect(433,504,186,32,"elevated",rx=5)
            b.icon("check",443,510,20,"foreground")
            b.text(473,525,"Review artifacts","foreground",13)
        finally:
            b.board.root=previous
    with b.layer("floating-assets", "Floating source and export artifacts"):
        for x,y,icon,label,key in [(82,235,"image","Artwork","series_2"),(984,243,"document","Export","series_3"),
                                   (101,474,"archive","Recovery","series_4"),(982,484,"check","Review","series_5")]:
            b.rect(x,y,130,110,"panel",rx=14,stroke=b.color(key),**{"stroke-width":"2"})
            b.icon(icon,x+43,y+17,42,key)
            b.text(x+65,y+90,label,"foreground",17,**{"text-anchor":"middle"})
        b.path("M212 290H248","border",**{"stroke-dasharray":"4 5"})
        b.path("M946 292H984","border",**{"stroke-dasharray":"4 5"})
    b.footer("ILLUSTRATION / Product explainers, landing visuals and feature artwork")
    b.save(directory / "product-illustration.svg")


CATALOG = [
    ("technical-flow.svg", "Technical workflow", "Three swimlanes, nine nodes, revision loop and a review decision.", technical),
    ("editorial-infographic.svg", "Editorial infographic", "Typographic hierarchy, conceptual palette tiles and supporting callouts.", editorial),
    ("orbit-map.svg", "Relationship map", "Six families, curved links, concentric guides and a labeled legend.", orbit),
    ("icon-sheet.svg", "Reusable icons", "Twelve local symbols in multiple sizes and surface treatments.", icons),
    ("wayfinding-map.svg", "Wayfinding map", "Eight landmarks, two patterned routes, step markers and orientation.", wayfinding),
    ("product-illustration.svg", "Product illustration", "Layered device scene, clipped screen content and a same-hue tonal glow.", illustration),
]


def diagrams(tokens, directory):
    cards=[]
    for filename,title,description,draw in CATALOG:
        draw(tokens,directory)
        download=base64.b64encode((directory / filename).read_bytes()).decode("ascii")
        cards.append(f'<article><h2><a href="{filename}">{html.escape(title)}</a></h2><p>{html.escape(description)}</p>'
                     f'<a download="{filename}" href="data:image/svg+xml;base64,{download}">Download editable SVG</a>'
                     f'<div class="canvas" tabindex="0" aria-label="{html.escape(title)} preview"><a href="{filename}"><img src="{filename}" alt="{html.escape(title)} composition"></a></div></article>')
    # Gallery chrome is independent of the exported artwork palette.
    css="""
*{box-sizing:border-box}body{background:#181a1d;color:#eceef0;margin:0;font:17px/1.6 Arial,sans-serif}
main{max-width:1280px;padding:clamp(16px,3vw,36px);margin:auto}a{color:#dce1e6;text-decoration:underline;text-underline-offset:3px}h1,h2{line-height:1.25}
article{margin:32px 0;padding:20px;border:1px solid #60656d;border-radius:12px;background:#22252a}
.canvas{overflow:auto;margin-top:18px}img{display:block;width:100%;min-width:800px;aspect-ratio:3/2}
a:focus-visible,.canvas:focus-visible{outline:3px solid #eceef0;outline-offset:4px}
"""
    (directory / "examples.css").write_text(css,encoding="utf-8")
    (directory / "examples.html").write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"><title>SVG composition gallery</title>'
        '<link rel="stylesheet" href="examples.css"><main><h1>SVG composition gallery</h1>'
        '<p>Six uses for editable vector artwork: workflows, editorial figures, relationship maps, icons, wayfinding and product illustration.</p>'
        '<p>The gallery uses a fixed neutral charcoal viewing environment. Only the SVG artwork, including its own background, uses exported theme colors; an embedding page can use any background.</p><p>Illustrative content. Native editor import requires separate review.</p>'+
        ''.join(cards)+'</main></html>',encoding="utf-8")
    return [entry[0] for entry in CATALOG]
