"""Semantic intent stays separate from canonical color identity."""
from .colors import contrast, distance

HUES = {"warning": 85, "error": 30, "success": 145, "info": 230,
        "red": 30, "green": 145, "yellow": 95, "blue": 265, "magenta": 325, "cyan": 205}


def hue_distance(a, b):
    return abs((a - b + 180) % 360 - 180)


def assign(colors, overrides=None):
    roles, notices = {}, []
    keys = list(colors)
    darkest = min(keys, key=lambda k: colors[k]["oklch"][0])
    brightest = max(keys, key=lambda k: contrast(colors[k], colors[darkest]))
    chromatic = [k for k in keys if colors[k]["oklch"][1] >= .04] or keys
    prominent = max(chromatic, key=lambda k: colors[k].get("weight", 1) ** .5 * colors[k]["oklch"][1])
    secondary = max(chromatic, key=lambda k: distance(colors[k], colors[prominent]))
    roles.update(background=darkest, foreground=brightest, primary=prominent, secondary=secondary)
    roles["panel"] = min(keys, key=lambda k: abs(colors[k]["oklch"][0] - (colors[darkest]["oklch"][0] + .035)))
    roles["muted"] = min(keys, key=lambda k: abs(contrast(colors[k], colors[darkest]) - 4.5))
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
                  + .15 * min(contrast(colors[k], colors[darkest]) / 7, 1))
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
