"""Role-aware target adaptation and native exporters."""
import re

from .colors import contrast, derive, readable

DEFAULTS = {"windows_terminal": 20, "siyuan": 64, "typora": 40, "powerpoint": 24,
            "alacritty": 20, "notepad_plus_plus": 32, "sublime_text": 40,
            "svg": 40, "syntax_highlighting": 32, "data_visualization": 48, "website": 112, "kmindz": 40, "markdown": 40, "codemirror5": 40, "codemirror6": 40}
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
        if target in ("markdown", "codemirror5", "codemirror6"):
            from .browser_themes import extend
            extend(tokens, checks, add)
            mandatory = len(tokens)
        if target == "kmindz":
            from .kmindz import extend
            extend(tokens, checks, add)
            mandatory = len(tokens)
        if target == "website":
            from .website import extend
            extend(tokens, checks, add)
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
    from .exporters import css_tokens as render
    return render(tokens)


def editor_css(tokens, siyuan=False):
    from .exporters import editor_css as render
    return render(tokens, siyuan)


def export(result, directory, name, canonical, source_hash, identity=None, theme_version=None):
    from .exporters import export as write
    return write(result, directory, name, canonical, source_hash, identity, theme_version)
