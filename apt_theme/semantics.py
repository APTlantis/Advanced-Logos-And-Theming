"""Semantic intent stays separate from canonical color identity."""
from .colors import contrast, distance

HUES = {"warning": 85, "error": 30, "success": 145, "info": 230,
        "red": 30, "green": 145, "yellow": 95, "blue": 265, "magenta": 325, "cyan": 205}


def hue_distance(a, b):
    return abs((a - b + 180) % 360 - 180)


def background_choice(colors, settings=None):
    settings = settings or {}
    if set(settings) - {"background_mode", "background_lightness"}:
        raise ValueError("Unknown semantic setting")
    mode = settings.get("background_mode", "identity")
    target = float(settings.get("background_lightness", .20))
    if mode not in ("identity", "darkest") or not .12 <= target <= .32:
        raise ValueError("background_mode must be identity or darkest; background_lightness must be in .12.. .32")
    darkest = min(colors, key=lambda k: (colors[k]["oklch"][0], k))
    dark = [k for k, c in colors.items() if .12 <= c["oklch"][0] <= .32]
    chromatic = [k for k in dark if colors[k]["oklch"][1] >= .015]
    if mode == "darkest":
        return darkest, "Explicit darkest-color policy"
    pool = chromatic or dark
    if not pool:
        return darkest, "No canonical color in the dark surface range; darkest fallback"
    largest = max(colors[k].get("weight", 1) for k in pool)
    ref = min(pool, key=lambda k: (abs(colors[k]["oklch"][0] - target)
              + .35 * max(0, colors[k]["oklch"][1] - .08)
              - .02 * (colors[k].get("weight", 1) / largest) ** .5, k))
    return ref, "Image-derived dark chromatic surface" if chromatic else "Image-derived dark neutral surface"


def assign(colors, overrides=None, settings=None):
    roles, notices = {}, []
    keys = list(colors)
    darkest = min(keys, key=lambda k: colors[k]["oklch"][0])
    background, reason = background_choice(colors, settings)
    if overrides and "background" in overrides:
        if overrides["background"] not in colors:
            raise ValueError("Invalid semantic background override")
        background = overrides["background"]
        reason = "Explicit semantic override"
    if "fallback" in reason:
        notices.append({"kind": "background_fallback", "source": background, "message": reason})
    brightest = max(keys, key=lambda k: contrast(colors[k], colors[background]))
    chromatic = [k for k in keys if colors[k]["oklch"][1] >= .04] or keys
    prominent = max(chromatic, key=lambda k: colors[k].get("weight", 1) ** .5 * colors[k]["oklch"][1])
    secondary = max(chromatic, key=lambda k: distance(colors[k], colors[prominent]))
    roles.update(background=background, foreground=brightest, primary=prominent, secondary=secondary)
    roles["panel"] = min(keys, key=lambda k: abs(colors[k]["oklch"][0] - (colors[background]["oklch"][0] + .035)))
    roles["muted"] = min(keys, key=lambda k: abs(contrast(colors[k], colors[background]) - 4.5))
    roles["selection"] = prominent
    roles["cursor"] = secondary
    for role, hue in HUES.items():
        ref = min(chromatic, key=lambda k: hue_distance(colors[k]["oklch"][2], hue) + 20 * abs(colors[k]["oklch"][0] - .7))
        roles[role] = ref
        delta = hue_distance(colors[ref]["oklch"][2], hue)
        if delta > 35:
            notices.append({"role": role, "kind": "unavailable_conventional_hue", "source": ref,
                            "hue_distance": delta, "message": "Closest image hue used; no new hue introduced"})
    roles["black"], roles["white"] = darkest, brightest
    chosen = []
    for role in ("keyword", "string", "number", "function", "type", "operator", "constant"):
        available = [k for k in chromatic if k not in chosen] or chromatic
        ref = max(available, key=lambda k: min([distance(colors[k], colors[s]) for s in chosen] or [.3])
                  + .15 * min(contrast(colors[k], colors[background]) / 7, 1))
        roles[role] = ref
        chosen.append(ref)
    roles["comment"] = roles["muted"]
    for role, ref in (overrides or {}).items():
        if role not in roles or ref not in colors:
            raise ValueError(f"Invalid semantic override {role} = {ref}")
        roles[role] = ref
    for ref in keys:
        matches = [r for r in ("warning", "error", "success", "info") if roles[r] == ref]
        if len(matches) > 1:
            notices.append({"kind": "semantic_collision", "source": ref, "roles": matches})
    return roles, notices
