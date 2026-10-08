"""Image normalization, perceptual candidates and image-only canonical selection."""
import hashlib
import json
import subprocess
import tempfile
import tomllib
from pathlib import Path

import numpy as np
from PIL import ImageCms
from sklearn.cluster import KMeans
from threadpoolctl import threadpool_limits

from .colors import from_rgb, lab


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def rgb_labs(rgb):
    values = np.asarray(rgb, dtype=float) / 255
    linear = np.where(values <= .04045, values / 12.92, ((values + .055) / 1.055) ** 2.4)
    lms = linear @ np.array([[.4122214708, .2119034982, .0883024619],
                              [.5363325363, .6806995451, .2817188376],
                              [.0514459929, .1073969566, .6299787005]])
    return np.cbrt(lms) @ np.array([[.2104542553, 1.9779984951, .0259040371],
                                    [.793617785, -2.428592205, .7827717662],
                                    [-.0040720468, .4505937099, -.808675766]])


def extract(path, settings):
    path = Path(path)
    before = digest(path)
    def run(args):
        proc = subprocess.run(["magick", *args], capture_output=True)
        if proc.returncode:
            raise ValueError(proc.stderr.decode(errors="replace").strip())
        return proc.stdout
    info = run(["identify", "-format", "%w %h %[colorspace] %[profiles]", str(path) + "[0]"]).decode()
    width, height, space, *profiles = info.split()
    if space.upper() == "CMYK" and not any("icc" in p.lower() for p in profiles):
        raise ValueError("CMYK input requires an embedded ICC profile")
    with tempfile.TemporaryDirectory(prefix="apt-theme-") as temp:
        icc = Path(temp) / "sRGB.icc"
        icc.write_bytes(ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes())
        data = run([str(path) + "[0]", "-auto-orient", "-profile", str(icc),
                    "-colorspace", "sRGB", "-alpha", "on", "-depth", "8", "rgba:-"])
    pixels = np.frombuffer(data, dtype=np.uint8).reshape(-1, 4)
    pixels = pixels[pixels[:, 3] > 0]
    if not len(pixels):
        raise ValueError("Image has no visible pixels")
    limit = int(settings.get("sample_limit", 65536))
    seed = int(settings.get("seed", 32))
    if limit < 32:
        raise ValueError("sample_limit must be at least 32")
    visible_count = len(pixels)
    if len(pixels) > limit:
        indices = np.sort(np.random.default_rng(seed).choice(len(pixels), limit, replace=False))
        pixels = pixels[indices]
    rgb, inverse = np.unique(pixels[:, :3], axis=0, return_inverse=True)
    weights = np.bincount(inverse, weights=pixels[:, 3] / 255)
    if len(rgb) < 32:
        raise ValueError(f"Only {len(rgb)} distinct visible sRGB colors; canonical palette requires 32")
    requested = int(settings.get("candidates", 192))
    if requested < 32 or requested > 1024:
        raise ValueError("candidates must be between 32 and 1024")
    coords = rgb_labs(rgb)
    k = min(requested, len(rgb))
    with threadpool_limits(limits=1):
        model = KMeans(k, random_state=seed, n_init=3, max_iter=100).fit(coords, sample_weight=weights)
    representatives = []
    for cluster in range(k):
        members = np.flatnonzero(model.labels_ == cluster)
        if not len(members):
            continue
        nearest = members[np.argmin(np.sum((coords[members] - model.cluster_centers_[cluster]) ** 2, axis=1))]
        representatives.append(from_rgb(rgb[nearest], weight=float(weights[members].sum())))
    representatives.sort(key=lambda c: (c["oklch"][0], c["hex"]))
    if digest(path) != before:
        raise ValueError("Source image changed during extraction")
    return representatives, {"sha256": before, "original_dimensions": [int(width), int(height)],
        "normalization": "ImageMagick ICC-aware sRGB, first frame, auto orientation, 8-bit export",
        "visible_pixels": visible_count, "sampled_pixels": len(pixels), "unique_sample_colors": len(rgb),
        "alpha": "Fully transparent excluded; partial opacity weights population", "seed": seed}, coords, weights


def selection_pool(candidates):
    """Coalesce the sRGB near-black noise floor when alternatives exist.

    OKLab separates tiny encoded channel changes surprisingly far near zero.
    These must not consume several slots at the expense of visible image tones.
    Keep an observed darkest anchor; never alter candidate RGB values.
    """
    near_black = [i for i, c in enumerate(candidates) if max(c["rgb"]) <= 12]
    if len(near_black) <= 1 or len(candidates) - len(near_black) + 1 < 32:
        return candidates
    anchor = min(near_black, key=lambda i: (candidates[i]["oklch"][0], candidates[i]["hex"]))
    collapsed = dict(candidates[anchor])
    collapsed["weight"] = sum(candidates[i].get("weight", 1) for i in near_black)
    return [collapsed if i == anchor else c for i, c in enumerate(candidates)
            if i == anchor or i not in near_black]


def selection_diagnostics(candidates, colors):
    pool = selection_pool(candidates)
    return {"near_black_definition": "All 8-bit sRGB channels <= 12",
            "near_black_candidates": sum(max(c["rgb"]) <= 12 for c in candidates),
            "near_black_canonical": sum(max(c["rgb"]) <= 12 for c in colors.values()),
            "coalesced_candidates": len(candidates) - len(pool),
            "policy": "One observed near-black anchor when at least 32 representatives remain; preserve sparse inputs"}


def select(candidates, seed=32):
    if len({c["hex"] for c in candidates}) < 32:
        raise ValueError("Need at least 32 distinct candidate colors")
    candidates = selection_pool(candidates)
    coords = np.array([lab(c) for c in candidates])
    weights = np.array([c.get("weight", 1) for c in candidates])
    with threadpool_limits(limits=1):
        model = KMeans(30, random_state=seed, n_init=10).fit(coords, sample_weight=weights)
    selected = {int(np.argmin(coords[:, 0])), int(np.argmax(coords[:, 0]))}
    for center in model.cluster_centers_:
        ranking = np.argsort(np.sum((coords - center) ** 2, axis=1), kind="stable")
        ref = next(int(i) for i in ranking if int(i) not in selected)
        if min(np.linalg.norm(coords[ref] - coords[s]) for s in selected) >= .03:
            selected.add(ref)
    # Replace near-duplicate medoids with population-aware farthest candidates.
    while len(selected) < 32:
        remaining = [i for i in range(len(candidates)) if i not in selected]
        chosen = max(remaining, key=lambda i: min(np.linalg.norm(coords[i] - coords[s]) for s in selected)
                     * (.25 + .75 * (weights[i] / weights.max()) ** .5))
        selected.add(chosen)
    colors = [dict(candidates[i]) for i in sorted(selected, key=lambda i: (coords[i, 0], candidates[i]["hex"]))]
    return {f"color_{i:02}": c for i, c in enumerate(colors, 1)}


def metrics(coords, weights, palette):
    target = np.array([lab(c) for c in palette.values()])
    minimum = np.full(len(coords), np.inf)
    for c in target:
        minimum = np.minimum(minimum, np.linalg.norm(coords - c, axis=1))
    distances = np.linalg.norm(target[:, None] - target[None, :], axis=2)
    np.fill_diagonal(distances, np.inf)
    return {"weighted_mean_oklab_distance": float(np.average(minimum, weights=weights)),
            "max_sample_oklab_distance": float(minimum.max()),
            "minimum_palette_spacing": float(distances.min()), "coverage": "normalized visible pixel sample",
            "limitation": "Coverage and spacing do not establish aesthetic quality"}


def load_palette(path):
    data = tomllib.loads(Path(path).read_text(encoding="utf-8-sig"))
    colors = {}
    for family, entries in data.get("palette", {}).items():
        for key, value in entries.items():
            if not isinstance(value, dict):
                raise ValueError(f"Invalid color {key}")
            if "hex" in value:
                h = value["hex"].lstrip("#")
                if len(h) != 6:
                    raise ValueError(f"Invalid hex for {key}")
                c = from_rgb([int(h[i:i+2], 16) for i in (0, 2, 4)])
            elif "rgb" in value:
                rgb = value["rgb"]
                if len(rgb) != 3 or any(not isinstance(v, int) or not 0 <= v <= 255 for v in rgb):
                    raise ValueError(f"Invalid RGB for {key}")
                c = from_rgb(rgb)
            elif "oklch" in value:
                from coloraide import Color
                o = value["oklch"]
                c = from_rgb([round(v * 255) for v in Color("oklch", [o["l"], o["c"], o["h"]]).convert("srgb").coords()])
            else:
                raise ValueError(f"Color {key} needs hex, RGB or OKLCH")
            if key in colors:
                raise ValueError(f"Duplicate color ID {key}")
            colors[key] = {**c, "weight": float(value.get("weight", 1)), "legacy_family": family}
    if len(colors) != 32:
        raise ValueError(f"Imported canonical palette must contain exactly 32 colors, found {len(colors)}")
    if data.get("theme", {}).get("variant", "dark") != "dark":
        raise ValueError("Only dark themes are supported")
    for group, roles in data.get("roles", {}).items():
        if any(ref not in colors for ref in roles.values()):
            raise ValueError(f"Invalid legacy role reference in {group}")
    return colors, data


def palette_toml(colors, name, source_hash):
    lines = ["[theme]", f"name = {json.dumps(name)}", 'variant = "dark"',
             f"source_sha256 = {json.dumps(source_hash)}", "final_colors = 32", "", "[palette.canonical]"]
    for key, c in colors.items():
        l, ch, h = c["oklch"]
        lines.append(f'{key} = {{ hex = "{c["hex"]}", rgb = {c["rgb"]}, oklch = {{ l = {l:.10f}, c = {ch:.10f}, h = {h:.10f} }}, weight = {c.get("weight", 1):.8f} }}')
    return "\n".join(lines) + "\n"
