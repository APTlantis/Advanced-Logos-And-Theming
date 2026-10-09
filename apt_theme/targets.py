"""Role-aware target adaptation and native exporters."""
import json
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from .colors import contrast, derive, readable

DEFAULTS = {"windows_terminal": 20, "siyuan": 64, "typora": 40, "powerpoint": 24,
            "alacritty": 20, "notepad_plus_plus": 32, "sublime_text": 40,
            "svg": 40, "syntax_highlighting": 32, "data_visualization": 48}
ANSI = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")
SYNTAX = ("keyword", "string", "number", "function", "type", "operator", "constant", "comment")


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "aptlantis-theme"


def adapt(colors, roles, target, budget):
    tokens, checks = {}, []
    background = colors[roles["background"]]
    def add(name, role, purpose, lightness=None, chroma=1, minimum=None, bg="background"):
        source = colors[roles[role]]
        c = dict(source) if lightness is None and chroma == 1 else derive(source, lightness, chroma)
        if minimum:
            check_bg = tokens.get(bg, background)
            if target not in ("windows_terminal", "alacritty") and bg == "background":
                surfaces = [tokens[k] for k in ("background", "panel", "elevated") if k in tokens]
                check_bg = max(surfaces or [background], key=lambda item: item["oklch"][0])
            c = readable(c, check_bg, minimum)
        c["origin"] = {"source": roles[role], "purpose": purpose,
                       "requested_oklch": c.get("requested_oklch", source["oklch"]),
                       "gamut_mapped": c.get("gamut_mapped", False),
                       "derived": c["hex"] != source["hex"]}
        tokens[name] = c
        if minimum:
            ratio = contrast(c, tokens.get(bg, background))
            checks.append({"foreground": name, "background": bg, "ratio": ratio,
                           "required": minimum, "pass": ratio + 1e-9 >= minimum})
    add("background", "background", "app background")
    add("foreground", "foreground", "body text", minimum=4.5)
    if target in ("windows_terminal", "alacritty"):
        add("cursor", "cursor", "cursor", minimum=3)
        add("selection", "selection", "selection background", lightness=.30, chroma=.55)
        checks.append({"foreground": "foreground", "background": "selection",
                       "ratio": contrast(tokens["foreground"], tokens["selection"]),
                       "required": 4.5, "pass": contrast(tokens["foreground"], tokens["selection"]) >= 4.5})
        for role in ANSI:
            add(role, role, "ANSI text", minimum=4.5)
            add("bright" + role.title(), role, "bright ANSI text",
                lightness=max(tokens[role]["oklch"][0], min(.99, tokens[role]["oklch"][0] + .08)), minimum=4.5)
        mandatory = 20
    else:
        add("panel", "background", "panel background", lightness=max(.18, min(.35, background["oklch"][0] + .04)), chroma=.7)
        add("elevated", "background", "elevated background", lightness=max(.24, min(.40, background["oklch"][0] + .08)), chroma=.7)
        checks[:] = [check for check in checks if check["foreground"] != "foreground"]
        add("foreground", "foreground", "body text across surfaces", minimum=4.5)
        add("muted", "muted", "secondary text", minimum=4.5)
        add("primary", "primary", "link and active accent", minimum=4.5)
        add("secondary", "secondary", "secondary accent", minimum=4.5)
        add("selection", "selection", "selection background", lightness=.30, chroma=.55)
        add("selection_text", "foreground", "selection text", minimum=4.5, bg="selection")
        add("border", "muted", "control boundary", minimum=3)
        for role in ("warning", "error", "success", "info"):
            add(role, role, "status text", minimum=4.5)
        for role in SYNTAX:
            add(role, role, "code text", minimum=4.5)
        mandatory = len(tokens)
        if target in ("svg", "data_visualization"):
            for i, role in enumerate(("primary", "secondary", "keyword", "string", "number", "type"), 1):
                add(f"series_{i}", role, "diagram/chart mark", minimum=3, bg="panel")
            if target == "data_visualization":
                for i in range(9):
                    add(f"sequential_{i}", "primary", "ordered single-hue scale stop",
                        lightness=.35 + i * .065, chroma=.7)
            mandatory = len(tokens)
        if target in ("notepad_plus_plus", "sublime_text", "syntax_highlighting"):
            # Native editor properties consume these optional semantic variants.
            for key, role in (("invalid", "error"), ("diff_added", "success"),
                              ("diff_deleted", "error"), ("diff_changed", "warning"),
                              ("tag", "keyword"), ("attribute", "type"),
                              ("escape", "constant"), ("label", "function")):
                if len(tokens) < budget:
                    add(key, role, key.replace("_", " ") + " text", minimum=4.5)
        if target in ("siyuan", "typora"):
            # These state tokens are consumed by selectors, not budget filler.
            for state in ("hover", "pressed", "subdued"):
                for role in ("primary", "secondary", "warning", "error", "success", "info"):
                    if len(tokens) < budget:
                        base = tokens[role]
                        add(role + "_" + state, role, f"{role} {state} text",
                            lightness=base["oklch"][0] + {"hover": .055, "pressed": -.055, "subdued": -.10}[state],
                            chroma=.75 if state == "subdued" else 1, minimum=4.5)
            if target == "siyuan":
                for role in ("foreground", "muted", "primary", *SYNTAX):
                    for surface in ("panel", "elevated"):
                        if len(tokens) < budget:
                            add(role + "_on_" + surface, role, f"{role} text on {surface}", minimum=4.5, bg=surface)
        # Actual fallback selectors use base tokens on nested backgrounds.
        for surface in ("panel", "elevated"):
            for name in ("foreground", "muted", "primary", *SYNTAX):
                token = name + "_on_" + surface if name + "_on_" + surface in tokens else name
                ratio = contrast(tokens[token], tokens[surface])
                checks.append({"foreground": token, "background": surface, "ratio": ratio,
                               "required": 4.5, "pass": ratio >= 4.5})
    if budget < mandatory:
        raise ValueError(f"{target} budget {budget} cannot retain {mandatory} mandatory tokens")
    used = {c["origin"]["source"] for c in tokens.values()}
    aliases = {}
    for key, c in tokens.items():
        aliases.setdefault(c["hex"], []).append(key)
    return {"target": target, "budget": budget, "named_count": len(tokens),
            "unique_count": len(aliases), "tokens": tokens, "checks": checks,
            "omitted_canonical": [key for key in colors if key not in used],
            "aliases": [v for v in aliases.values() if len(v) > 1],
            "contrast_failures": sum(not c["pass"] for c in checks)}


def css_tokens(tokens):
    return ":root {\n" + "\n".join(f"  --apt-{key.replace('_', '-')}: {c['hex']};" for key, c in tokens.items()) + "\n}\n"


def editor_css(tokens, siyuan=False):
    css = css_tokens(tokens)
    if siyuan:
        css += """html[data-theme-mode='dark'] {
 --b3-theme-background: var(--apt-background); --b3-theme-surface: var(--apt-panel);
 --b3-theme-surface-light: var(--apt-elevated); --b3-theme-on-background: var(--apt-foreground);
 --b3-theme-on-surface: var(--apt-foreground); --b3-theme-on-surface-light: var(--apt-muted);
 --b3-theme-primary: var(--apt-primary); --b3-theme-on-primary: var(--apt-background);
 --b3-theme-primary-light: var(--apt-selection); --b3-theme-secondary: var(--apt-secondary);
 --b3-theme-error: var(--apt-error); --b3-border-color: var(--apt-border);
 --b3-protyle-code-background: var(--apt-panel); --b3-protyle-code-linenumber-hl: var(--apt-muted);
 --b3-list-hover: var(--apt-elevated); --b3-list-background: var(--apt-selection);
 --b3-font-family: system-ui, sans-serif;
}
body, .protyle-wysiwyg { background: var(--apt-background); color: var(--apt-foreground); }
.layout__dockl, .layout__dockr, .layout__dockb, .b3-list { background: var(--apt-panel); color: var(--apt-foreground); }
.b3-dialog__container { background: var(--apt-elevated); color: var(--apt-foreground); }
"""
        css += ".protyle-wysiwyg [data-type='NodeCodeBlock'] { background:var(--apt-panel); color:var(--apt-foreground); }\n"
    else:
        css += """:root { --bg-color:var(--apt-background); --text-color:var(--apt-foreground);
 --side-bar-bg-color:var(--apt-panel); --control-text-color:var(--apt-foreground); }
html, body, #write { background:var(--apt-background); color:var(--apt-foreground); }
#write { max-width: 900px; margin: auto; padding: 2rem; line-height: 1.65; }
#typora-sidebar, .md-fences, .CodeMirror { background:var(--apt-panel); color:var(--apt-foreground); }
.modal-content, .dropdown-menu { background:var(--apt-elevated); color:var(--apt-foreground); }
.cm-s-inner .cm-keyword { color:var(--apt-keyword); }
.cm-s-inner .cm-string { color:var(--apt-string); }
.cm-s-inner .cm-number { color:var(--apt-number); }
.cm-s-inner .cm-comment { color:var(--apt-comment); }
.cm-s-inner .cm-def { color:var(--apt-function); }
.cm-s-inner .cm-operator { color:var(--apt-operator); }
.cm-s-inner .cm-variable-2 { color:var(--apt-type); }
.cm-s-inner .cm-atom { color:var(--apt-constant); }
"""
    css += """a, h1, h2, h3 { color:var(--apt-primary); }
::selection { background:var(--apt-selection); color:var(--apt-selection-text); }
blockquote { border-left:3px solid var(--apt-primary); color:var(--apt-muted); }
table, td, th, hr, input { border-color:var(--apt-border); }
code { background:var(--apt-panel); }
input, textarea, button { background:var(--apt-panel); color:var(--apt-foreground); }
"""
    for role in SYNTAX:
        css += f".hljs-{role} {{ color:var(--apt-{role}); }}\n"
    for role in ("primary", "secondary", "warning", "error", "success", "info"):
        for state, pseudo in (("hover", ":hover"), ("pressed", ":active"), ("subdued", "[aria-disabled='true']")):
            key = role + "_" + state
            if key in tokens:
                css += f".apt-{role}{pseudo} {{ color:var(--apt-{key.replace('_', '-')}); }}\n"
                if role == "primary":
                    css += f"a{pseudo}, .b3-button--outline{pseudo} {{ color:var(--apt-{key.replace('_', '-')}); }}\n"
                elif role == "secondary":
                    css += f"button{pseudo}, .b3-menu__item{pseudo} {{ color:var(--apt-{key.replace('_', '-')}); }}\n"
        css += f".apt-{role} {{ color:var(--apt-{role}); }}\n"
    for surface, selectors in (("panel", ".b3-list, .protyle-wysiwyg [data-type='NodeCodeBlock']"),
                               ("elevated", ".b3-dialog__container")):
        if siyuan:
            key = "foreground_on_" + surface
            if key in tokens:
                css += f"{selectors} {{ color:var(--apt-{key.replace('_', '-')}); }}\n"
            for role in ("muted", "primary", *SYNTAX):
                key = role + "_on_" + surface
                if key in tokens:
                    prefix = ".b3-list" if surface == "panel" else ".b3-dialog__container"
                    cls = f".hljs-{role}" if role in SYNTAX else f".apt-{role}"
                    css += f"{prefix} {cls} {{ color:var(--apt-{key.replace('_', '-')}); }}\n"
    return css


def export(result, directory, name):
    directory = Path(directory)
    directory.mkdir(parents=True)
    tokens, target = result["tokens"], result["target"]
    h = lambda key: tokens[key]["hex"]
    if target == "windows_terminal":
        scheme = {"name": name, "background": h("background"), "foreground": h("foreground"),
                  "cursorColor": h("cursor"), "selectionBackground": h("selection")}
        scheme.update({key: h(key) for role in ANSI for key in (role, "bright" + role.title())})
        (directory / "windows-terminal.json").write_text(json.dumps(scheme, indent=2) + "\n", encoding="utf-8")
    elif target == "alacritty":
        groups = {"primary": {"background": "background", "foreground": "foreground"},
                  "cursor": {"text": "background", "cursor": "cursor"},
                  "selection": {"text": "foreground", "background": "selection"},
                  "normal": {role: role for role in ANSI},
                  "bright": {role: "bright" + role.title() for role in ANSI}}
        content = "# Image-derived dark colors; import from your Alacritty config.\n"
        for group, mapping in groups.items():
            content += f"\n[colors.{group}]\n"
            content += "".join(f'{key} = "{h(token)}"\n' for key, token in mapping.items())
        (directory / (slug(name) + ".toml")).write_text(content, encoding="utf-8")
        result["native_slots"] = groups
    elif target in ("notepad_plus_plus", "sublime_text"):
        from .native_editors import export_editor
        export_editor(result, directory, name)
    elif target in ("svg", "syntax_highlighting", "data_visualization"):
        from .visual_targets import export_visual
        export_visual(result, directory, name)
    elif target == "powerpoint":
        ns = "http://schemas.openxmlformats.org/drawingml/2006/main"
        ET.register_namespace("a", ns)
        root = ET.Element(f"{{{ns}}}clrScheme", name=name)
        slots = {"dk1": "background", "lt1": "foreground", "dk2": "panel", "lt2": "muted",
                 "accent1": "primary", "accent2": "secondary", "accent3": "keyword",
                 "accent4": "string", "accent5": "number", "accent6": "type",
                 "hlink": "primary", "folHlink": "secondary"}
        for slot, token in slots.items():
            child = ET.SubElement(root, f"{{{ns}}}{slot}")
            ET.SubElement(child, f"{{{ns}}}srgbClr", val=h(token)[1:])
        ET.ElementTree(root).write(directory / (slug(name) + ".xml"), encoding="utf-8", xml_declaration=True)
        result["native_slots"] = slots
        from .powerpoint import sample_deck
        sample_deck(result, directory, name, slug(name))
    else:
        css = editor_css(tokens, target == "siyuan")
        filename = "theme.css" if target == "siyuan" else slug(name) + ".css"
        (directory / filename).write_text(css, encoding="utf-8")
        if target == "siyuan":
            from .report import swatch
            swatch(tokens, directory / "preview.png", name)
            from PIL import Image
            with Image.open(directory / "preview.png") as preview:
                preview.resize((160, 160)).save(directory / "icon.png")
            metadata = {"name": slug(name), "displayName": {"default": name}, "version": "0.1.0",
                        "minAppVersion": "3.7.0", "description": {"default": "Image-derived dark theme"},
                        "readme": {"default": "README.md"}, "modes": ["dark"], "frontends": ["all"],
                        "icon": "icon.png", "preview": "preview.png"}
            (directory / "theme.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
            (directory / "README.md").write_text(f"# {name}\n\nDark theme generated from the canonical image palette.\n\nCopy this folder into your SiYuan workspace's appearance/themes folder and select the theme. See validation.json before use. Native visual acceptance remains pending.\n", encoding="utf-8")
            with zipfile.ZipFile(directory / "package.zip", "w", zipfile.ZIP_DEFLATED) as archive:
                for file in ("theme.json", "theme.css", "README.md", "icon.png", "preview.png"):
                    info = zipfile.ZipInfo(file, (2026, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    archive.writestr(info, (directory / file).read_bytes())
    (directory / "tokens.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (directory / "validation.json").write_text(json.dumps({"checks": result["checks"],
        "contrast_failures": result["contrast_failures"], "native_visual_acceptance": "pending"}, indent=2) + "\n", encoding="utf-8")
