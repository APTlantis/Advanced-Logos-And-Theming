"""Native output dispatch and shared editor CSS; adaptation lives in targets.py."""
import json
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from .targets import ANSI, SYNTAX, slug


def css_tokens(tokens):
    return ":root {\n" + "\n".join(f"  --apt-{key.replace('_', '-')}: {c['hex']};" for key, c in tokens.items()) + "\n}\n"


def editor_css(tokens, siyuan=False):
    if not siyuan:
        from .typora import theme_css
        return css_tokens(tokens) + theme_css(tokens)
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


def export(result, directory, name, canonical, source_hash, identity=None, theme_version=None):
    from .identity import resolve_identity
    from .output_names import ArtifactNames
    identity = identity or resolve_identity(name, theme_version)
    artifact = ArtifactNames(identity, result["target"], name)
    result["_artifact_names"] = artifact
    result["theme_identity"] = identity.record()
    directory = Path(directory)
    directory.mkdir(parents=True)
    tokens, target = result["tokens"], result["target"]
    h = lambda key: tokens[key]["hex"]
    if target == "kmindz":
        from .kmindz import export_kmindz
        export_kmindz(result, directory, name)
    elif target in ("markdown", "codemirror5", "codemirror6"):
        from .browser_themes import export_browser_theme
        export_browser_theme(result, directory, name)
    elif target == "website":
        from .website import export_website
        export_website(result, directory, name)
    elif target == "windows_terminal":
        scheme = {"name": name, "background": h("background"), "foreground": h("foreground"),
                  "cursorColor": h("cursor"), "selectionBackground": h("selection")}
        scheme.update({key: h(key) for role in ANSI for key in (role, "bright" + role.title())})
        (directory / artifact('windows-terminal.json')).write_text(json.dumps(scheme, indent=2) + "\n", encoding="utf-8")
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
        (directory / artifact(slug(name) + ".toml")).write_text(content, encoding="utf-8")
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
        ET.ElementTree(root).write(directory / artifact(slug(name) + ".xml"), encoding="utf-8", xml_declaration=True)
        result["native_slots"] = slots
        from .powerpoint import sample_deck
        sample_deck(result, directory, name, slug(name))
    else:
        css = editor_css(tokens, target == "siyuan")
        filename = artifact('theme.css') if target == "siyuan" else artifact(slug(name) + ".css")
        (directory / filename).write_text(css, encoding="utf-8")
        if target == "typora":
            from .typora import export_examples
            export_examples(result, directory, name, filename)
        if target == "siyuan":
            from .report import swatch
            swatch(tokens, directory / artifact('preview.png'), name)
            from PIL import Image
            with Image.open(directory / artifact('preview.png')) as preview:
                preview.resize((160, 160)).save(directory / artifact('icon.png'))
            metadata = {"name": identity.key, "displayName": {"default": name}, "version": "0.1.0",
                        "minAppVersion": "3.7.0", "description": {"default": "Image-derived dark theme"},
                        "readme": {"default": artifact('README.md')}, "modes": ["dark"], "frontends": ["all"],
                        "icon": artifact('icon.png'), "preview": artifact('preview.png')}
            (directory / artifact('theme.json')).write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
            (directory / artifact('README.md')).write_text(f"# {name}\n\nDark theme generated from the canonical image palette.\n\nCopy this folder into your SiYuan workspace's appearance/themes folder and select the theme. Review the run's target validation report before use. Native visual acceptance remains pending.\n", encoding="utf-8")
            with zipfile.ZipFile(directory / artifact('package.zip'), "w", zipfile.ZIP_DEFLATED) as archive:
                for file in (artifact('theme.json'), artifact('theme.css'), artifact('README.md'), artifact('icon.png'), artifact('preview.png')):
                    info = zipfile.ZipInfo(file, (2026, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    archive.writestr(info, (directory / file).read_bytes())
    from .target_palette import export_palette
    export_palette(result, directory, name, canonical, source_hash)
    artifact('tokens.json')
    artifact('validation.json')
    result["artifact_paths"] = dict(artifact.paths)
    result.pop("_artifact_names")
    (directory / artifact('tokens.json')).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (directory / artifact('validation.json')).write_text(json.dumps({"checks": result["checks"],
        "contrast_failures": result["contrast_failures"], "native_visual_acceptance": "pending"}, indent=2) + "\n", encoding="utf-8")
    artifact.finish(directory, result, name)
