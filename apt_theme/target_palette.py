"""Per-target palette documents and transformer-style labeled swatches."""
import json
import math

from PIL import Image, ImageDraw, ImageFont


def artifact_stem(name, target):
    from .targets import slug
    language = slug(name)
    for prefix in ("aptlantis-", "apt-"):
        if language.startswith(prefix):
            language = language[len(prefix):]
            break
    return f"apt-{language or 'theme'}-{slug(target)}"


def toml_document(data):
    """Serialize our tables, lists and scalar metadata without losing precision."""
    lines = []
    def value(item):
        if isinstance(item, bool):
            return str(item).lower()
        if isinstance(item, str):
            return json.dumps(item, ensure_ascii=False)
        if isinstance(item, (int, float)):
            return repr(item)
        if isinstance(item, list):
            return "[" + ", ".join(value(v) for v in item) + "]"
        if isinstance(item, dict):
            return "{ " + ", ".join(f"{value(k)} = {value(v)}" for k, v in item.items()) + " }"
        raise TypeError(type(item))
    def table(items, path):
        if path:
            lines.append("[" + ".".join(value(k) for k in path) + "]")
        for key, item in items.items():
            if not isinstance(item, dict):
                lines.append(f"{value(key)} = {value(item)}")
        lines.append("")
        for key, item in items.items():
            if isinstance(item, dict):
                table(item, [*path, key])
    table(data, [])
    return "\n".join(lines)


def export_palette(result, directory, name, canonical, source_hash):
    tokens = result["tokens"]
    stem = artifact_stem(name, result["target"])
    files = {"palette": stem + "-palette.toml", "swatch": stem + "-swatch.png"}
    groups = {"canonical": {}, "derived": {}}
    for key, color in tokens.items():
        l, c, h = color["oklch"]
        groups["derived" if color["origin"]["derived"] else "canonical"][key] = {
            "hex": color["hex"], "rgb": color["rgb"], "oklch": {"l": l, "c": c, "h": h},
            "origin": color["origin"]}
    document = {
        "theme": {"name": name, "variant": "dark", "source_sha256": source_hash,
                  "final_colors": result["named_count"]},
        "transformation": {"schema": "aptlantis.target-palette.v1", "profile": result["target"],
                           "requested_count": result["budget"], "actual_count": result["named_count"],
                           "unique_hex_count": result["unique_count"], "canonical_count": len(canonical),
                           "token_order": list(tokens), "omitted_canonical": result["omitted_canonical"],
                           "aliases": result["aliases"]},
        "palette": groups,
        "roles": {"tokens": {key: key for key in tokens}},
        # Source entries are separate from the adapted palette and retain their IDs/values.
        "source_palette": {"canonical": canonical},
        "validation": {"checks": result["checks"], "contrast_failures": result["contrast_failures"],
                       "native_visual_acceptance": "pending"}}
    (directory / files["palette"]).write_text(toml_document(document), encoding="utf-8")
    width, cell_height = 1200, 100
    image = Image.new("RGB", (width, 70 + math.ceil(len(tokens) / 4) * cell_height), "#101923")
    draw = ImageDraw.Draw(image)
    font, heading = ImageFont.load_default(size=13), ImageFont.load_default(size=24)
    draw.text((20, 20), f"{name} / {result['target']} / {len(tokens)} colors", fill="#EDF0E7", font=heading)
    for i, (key, color) in enumerate(tokens.items()):
        x, y = (i % 4) * 300, 70 + (i // 4) * cell_height
        draw.rectangle((x + 10, y + 8, x + 290, y + 55), fill=color["hex"])
        draw.text((x + 10, y + 60), key, fill="#EDF0E7", font=font)
        kind = "derived" if color["origin"]["derived"] else "canonical"
        draw.text((x + 10, y + 80), f"{color['hex']}  {kind} / {color['origin']['source']}", fill="#B2BCC7", font=font)
    image.save(directory / files["swatch"])
    result["palette_artifacts"] = files
