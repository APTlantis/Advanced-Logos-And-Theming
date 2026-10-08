#!/usr/bin/env python3
"""Generate Notepad++, JetBrains editor, and Windows Terminal themes from palette32 TOML."""

import argparse
import colorsys
import hashlib
import json
import tomllib
from pathlib import Path
from xml.etree import ElementTree

from generate_theme import generate_jetbrains, generate_notepadpp

ROOT = Path(__file__).resolve().parent
DEFAULT_PALETTES = sorted((ROOT / "Gen2").glob("apt-*-palette32/palette.toml"))
BODY = 4.5


def luminance(color):
    rgb = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
    return sum(a * b for a, b in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(a, b):
    x, y = sorted((luminance(a), luminance(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


def read_palette(path):
    raw = path.read_bytes()
    doc = tomllib.loads(raw.decode("utf-8-sig"))
    colors = {key: item["hex"].upper() for group in doc["palette"].values()
              for key, item in group.items()}
    if len(colors) != 32 or len(set(colors.values())) != 32:
        raise ValueError(f"{path}: expected 32 distinct named colors")
    if doc["theme"].get("variant") != "dark":
        raise ValueError(f"{path}: only dark palettes are supported")
    for section in doc["roles"].values():
        for role, name in section.items():
            if name not in colors:
                raise ValueError(f"{path}: role {role} references missing color {name}")
    return doc, colors, hashlib.sha256(raw).hexdigest()


def choose(colors, preferred, background, minimum=BODY, groups=(), used=()):
    """Prefer the authored role, then a readable same-family color, then any readable color."""
    candidates = [preferred]
    candidates += [name for group in groups for name in colors if name.startswith(group + "_")]
    candidates += list(colors)
    seen = set()
    valid = []
    for name in candidates:
        if name in seen:
            continue
        seen.add(name)
        ratio = contrast(colors[name], background)
        if ratio >= minimum:
            valid.append((name, ratio))
    if not valid:
        raise ValueError(f"No palette color reaches {minimum}:1 against {background}")
    # The authored color wins if it passes. Otherwise prefer the first family
    # with a readable member closest in luminance to the authored value.
    if valid[0][0] == preferred and preferred not in used:
        return colors[preferred], preferred
    def hsv(color):
        return colorsys.rgb_to_hsv(*(int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)))

    target_l = luminance(colors[preferred])
    target_h, target_s, _ = hsv(colors[preferred])

    def score(pair):
        name = pair[0]
        hue, sat, _ = hsv(colors[name])
        hue_distance = min(abs(hue - target_h), 1 - abs(hue - target_h)) * 2
        neutral_role = target_s < 0.16 or preferred.startswith("structural_dark")
        color_distance = (abs(sat - target_s) * 1.5 if neutral_role
                          else hue_distance * 2 + abs(sat - target_s) * 0.7)
        return (color_distance + abs(luminance(colors[name]) - target_l) * 0.7
                + (0.4 if name in used else 0))

    name = min(valid, key=score)[0]
    return colors[name], name


def build_tokens(doc, colors):
    roles = doc["roles"]
    base = roles["base"]
    text = roles["text"]
    syntax = roles["syntax"]
    accent = roles["accent"]
    bg = colors[base["editor_bg"]]
    panel = colors[base["panel_bg"]]
    selection = colors[base["elevated_bg"]]
    picks = {}

    def pick(key, name, against=bg, groups=(), minimum=BODY):
        value, source = choose(colors, name, against, minimum, groups)
        picks[key] = source
        return value

    t = {
        "background": bg, "surface": colors[base["app_bg"]],
        "panel": panel, "border": colors[base["border_subtle"]],
        "selection": selection, "lineHighlight": colors[base["panel_bg"]],
    }
    t["textPrimary"] = pick("textPrimary", text["fg_primary"], groups=("text_light",))
    t["textMuted"] = pick("textMuted", text["fg_secondary"], groups=("text_light", "neutral"))
    t["accent"] = pick("accent", accent["primary"], groups=("accent", "text_light"))
    t["accentSecondary"] = pick("accentSecondary", accent["secondary"], groups=("accent", "text_light"))
    t["highlight"] = pick("highlight", accent["highlight"], groups=("data", "text_light"))
    for key in ("keyword", "string", "number", "comment", "function", "type", "constant", "operator"):
        t[key] = pick(key, syntax[key], groups=("text_light", "accent", "data", "neutral"))
    t["variable"] = t["textPrimary"]
    t["punctuation"] = t["textMuted"]
    t["selectionText"] = pick("selectionText", text["fg_primary"], selection, ("text_light",))
    t["panelText"] = pick("panelText", text["fg_primary"], panel, ("text_light",))
    return t, picks


def terminal(doc, colors, t, picks):
    bg = colors[doc["roles"]["base"]["app_bg"]]
    result = {"name": doc["targets"]["windows_terminal"]["scheme_name"],
              "background": bg, "foreground": t["panelText"],
              "cursorColor": t["textPrimary"], "selectionBackground": t["selection"]}
    readable = [(name, color) for name, color in colors.items() if contrast(color, bg) >= BODY]

    def hsv(color):
        return colorsys.rgb_to_hsv(*(int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)))

    def assign(key, pair):
        picks["terminal." + key] = pair[0]
        result[key] = pair[1]

    neutrals = sorted((pair for pair in readable if hsv(pair[1])[1] < 0.17),
                      key=lambda pair: luminance(pair[1]))
    if len(neutrals) < 2:
        neutrals = sorted(readable, key=lambda pair: (hsv(pair[1])[1], luminance(pair[1])))
    assign("black", neutrals[0])
    assign("brightBlack", neutrals[1] if len(neutrals) > 1 else neutrals[0])
    assign("white", max((pair for pair in readable if pair[0].startswith("text_light_")),
                        key=lambda pair: luminance(pair[1])))
    assign("brightWhite", max(readable, key=lambda pair: luminance(pair[1])))

    used = {picks["terminal." + key] for key in ("black", "brightBlack", "white", "brightWhite")}
    # ANSI names express hue families, while the palette TOML's terminal roles
    # are suggestions. A dark-blue "yellow" role must not become yellow text.
    targets = {"red": 345, "green": 120, "yellow": 55, "blue": 235,
               "purple": 300, "cyan": 185}
    chromatic = [pair for pair in readable if hsv(pair[1])[1] >= 0.15] or readable
    for key, target in targets.items():
        def score(pair):
            hue, sat, _ = hsv(pair[1])
            degrees = hue * 360
            distance = min(abs(degrees - target), 360 - abs(degrees - target)) / 180
            return distance * 3 + (1 - sat) * 0.65 + (0.35 if pair[0] in used else 0)

        normal = min(chromatic, key=score)
        assign(key, normal)
        used.add(normal[0])
        alternatives = [pair for pair in chromatic if pair[0] != normal[0]]
        bright = min(alternatives or chromatic, key=lambda pair: score(pair)
                     + (0.3 if luminance(pair[1]) < luminance(normal[1]) else 0))
        assign("bright" + key.title(), bright)
        used.add(bright[0])
    return result


def validate_outputs(t, scheme, xml, icls):
    npp = ElementTree.fromstring(xml)
    jetbrains = ElementTree.fromstring(icls)
    bg = t["background"]
    for role in ("textPrimary", "textMuted", "accent", "accentSecondary", "highlight",
                 "keyword", "string", "number", "comment", "function", "type", "constant",
                 "operator", "variable", "punctuation"):
        if contrast(t[role], bg) < BODY:
            raise ValueError(f"Unreadable editor role: {role}")
    if contrast(t["selectionText"], t["selection"]) < BODY:
        raise ValueError("Unreadable selection")
    for style in npp.findall(".//WordsStyle"):
        fg = style.get("fgColor")
        if fg:
            bg_style = style.get("bgColor") or bg[1:]
            if contrast("#" + fg, "#" + bg_style) < BODY:
                raise ValueError(f"Unreadable Notepad++ {style.get('name')}")
    for attribute in jetbrains.findall(".//attributes/option"):
        values = {option.get("name"): option.get("value") for option in attribute.findall("./value/option")}
        if "FOREGROUND" in values:
            attr_bg = values.get("BACKGROUND", bg[1:])
            if contrast("#" + values["FOREGROUND"], "#" + attr_bg) < BODY:
                raise ValueError(f"Unreadable JetBrains {attribute.get('name')}")
    for role in ("foreground", "black", "red", "green", "yellow", "blue", "purple", "cyan",
                 "white", "brightBlack", "brightRed", "brightGreen", "brightYellow", "brightBlue",
                 "brightPurple", "brightCyan", "brightWhite"):
        if contrast(scheme[role], scheme["background"]) < BODY:
            raise ValueError(f"Unreadable terminal role: {role}")


def generate(path, output):
    doc, colors, digest = read_palette(path)
    t, picks = build_tokens(doc, colors)
    scheme = terminal(doc, colors, t, picks)
    name = doc["source"]["language"]
    xml = generate_notepadpp(t, name)
    icls = generate_jetbrains(t, name)
    validate_outputs(t, scheme, xml, icls)
    folder = output / path.parent.name
    folder.mkdir(parents=True, exist_ok=True)
    files = {"notepadpp.xml": xml, "jetbrains.icls": icls,
             "windows-terminal.json": json.dumps(scheme, indent=2) + "\n"}
    for filename, content in files.items():
        (folder / filename).write_text(content, encoding="utf-8")
    provenance = {"source_palette": str(path.resolve()), "source_sha256": digest,
                  "theme_id": doc["theme"]["id"], "generator": "generate_theme32.py",
                  "minimum_text_contrast": BODY, "resolved_roles": picks,
                  "outputs": sorted(files)}
    (folder / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(f"{name}: {folder}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("palettes", nargs="*", type=Path, help="palette32 TOML files (default: Gen2 palettes)")
    parser.add_argument("--output", type=Path, default=ROOT / "Gen2" / "generated")
    args = parser.parse_args()
    inputs = args.palettes or DEFAULT_PALETTES
    if not inputs:
        parser.error("No Gen2 palette.toml files found")
    for path in inputs:
        generate(path, args.output)


if __name__ == "__main__":
    main()
