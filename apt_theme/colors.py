"""Shared color math; exported RGB is the authority for contrast."""
import math
from coloraide import Color


def from_rgb(rgb, **metadata):
    rgb = [int(v) for v in rgb]
    if len(rgb) != 3 or any(v < 0 or v > 255 for v in rgb):
        raise ValueError("RGB values must be three sRGB bytes in 0..255")
    lch = Color("srgb", [v / 255 for v in rgb]).convert("oklch").coords()
    lch = [float(v) if math.isfinite(v) else 0.0 for v in lch]
    return {"hex": "#" + "".join(f"{v:02X}" for v in rgb), "rgb": rgb,
            "oklch": lch, **metadata}


def lab(c):
    return Color(c["hex"]).convert("oklab").coords()


def distance(a, b):
    return math.dist(lab(a), lab(b))


def contrast(a, b):
    return Color(a["hex"]).contrast(Color(b["hex"]), method="wcag21")


def derive(source, lightness=None, chroma_scale=1.0):
    l, c, h = source["oklch"]
    l = l if lightness is None else min(.99, max(.01, lightness))
    requested = [l, c * chroma_scale, h]
    value = Color("oklch", requested)
    mapped = not value.in_gamut("srgb")
    # Fixed L/H chroma bisection: avoids channel clipping and hue changes.
    if mapped:
        lo, hi = 0.0, requested[1]
        for _ in range(36):
            mid = (lo + hi) / 2
            if Color("oklch", [l, mid, h]).in_gamut("srgb", tolerance=0):
                lo = mid
            else:
                hi = mid
        value = Color("oklch", [l, lo, h])
    rgb = [round(min(1, max(0, v)) * 255) for v in value.convert("srgb").coords()]
    return from_rgb(rgb, requested_oklch=requested, gamut_mapped=mapped)


def readable(source, background, minimum=4.5):
    if contrast(source, background) >= minimum:
        return dict(source)
    # Find the smallest useful lightness adjustment, retaining source hue.
    for step in range(1, 101):
        candidate = derive(source, source["oklch"][0] + step / 100)
        if contrast(candidate, background) >= minimum:
            return candidate
    return derive(source, .99)
