"""Wrap raster images in SVG, or explicitly trace them with VTracer."""

from __future__ import annotations

import argparse
import base64
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

FORMATS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif", ".tiff"}
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".webp": "image/webp", ".gif": "image/gif"}
VTRACER_VERSION = "1.0.0-alpha.4"
SVG_NS = "http://www.w3.org/2000/svg"


def run(command: list[str]) -> str:
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}")
    return result.stdout.strip()


def dimensions(source: Path, magick: str) -> tuple[int, int]:
    value = run([magick, "identify", "-format", "%w %h", str(source) + "[0]"])
    width, height = map(int, value.split())
    if width < 1 or height < 1:
        raise ValueError("invalid image dimensions")
    return width, height


def image_command(source: Path, target: Path, args: argparse.Namespace) -> list[str]:
    command = [args.magick, str(source) + "[0]", "-auto-orient", "-filter", args.filter]
    if args.blur is not None:
        command += ["-blur", f"0x{args.blur}"]
    if args.resize:
        command += ["-resize", args.resize]
    if args.colors:
        command += ["-colors", str(args.colors)]
    if args.invert:
        command += ["-negate"]
    if args.background != "none":
        command += ["-background", args.background, "-alpha", "background", "-alpha", "remove"]
    return command + ["-depth", "8", f"PNG32:{target}"]


def embed_svg(data: bytes, mime: str, width: int, height: int) -> bytes:
    encoded = base64.b64encode(data).decode("ascii")
    root = ET.Element(f"{{{SVG_NS}}}svg", {
        "version": "1.1", "width": str(width), "height": str(height),
        "viewBox": f"0 0 {width} {height}",
    })
    ET.SubElement(root, f"{{{SVG_NS}}}image", {
        "x": "0", "y": "0", "width": str(width), "height": str(height),
        "href": f"data:{mime};base64,{encoded}",
    })
    ET.register_namespace("", SVG_NS)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"


def check_vtracer(executable: str) -> None:
    version = run([executable, "--version"])
    if VTRACER_VERSION not in version:
        raise RuntimeError(f"trace mode requires VTracer {VTRACER_VERSION}; found {version}")


def trace_command(source: Path, target: Path, args: argparse.Namespace) -> list[str]:
    command = [args.vtracer, "--input", str(source), "--output", str(target),
               "--preset", "bw" if args.mono else "poster",
               "--mode", args.curves, "--hierarchical", args.hierarchical,
               "--filter-speckle", str(args.filter_speckle),
               "--color-precision", str(args.color_precision),
               "--simplify", str(args.simplify),
               "--path-precision", str(args.path_precision)]
    if args.max_colors:
        command += ["--max-colors", str(args.max_colors)]
    if args.mono and args.threshold != "auto":
        command += ["--threshold", args.threshold]
    elif args.mono:
        command += ["--adaptive"]
    return command


def convert(source: Path, target: Path, args: argparse.Namespace) -> None:
    with tempfile.TemporaryDirectory(prefix="logo-svg-") as directory:
        temporary = Path(directory)
        prepared = temporary / "prepared.png"
        output = temporary / "output.svg"
        normalize = args.normalize or source.suffix.lower() not in MIME
        if args.mode == "trace" or normalize:
            run(image_command(source, prepared, args))
            width, height = dimensions(prepared, args.magick)
        else:
            width, height = dimensions(source, args.magick)
        if args.mode == "trace":
            run(trace_command(prepared, output, args))
            root = ET.parse(output).getroot()
            if not any(element.tag == f"{{{SVG_NS}}}path" for element in root.iter()):
                raise ValueError("VTracer output has no SVG paths")
            svg_bytes = output.read_bytes()
        else:
            raster = prepared if normalize else source
            mime = "image/png" if normalize else MIME[source.suffix.lower()]
            svg_bytes = embed_svg(raster.read_bytes(), mime, width, height)
            ET.fromstring(svg_bytes)
        target.parent.mkdir(parents=True, exist_ok=True)
        descriptor, name = tempfile.mkstemp(prefix=target.name + ".", suffix=".tmp", dir=target.parent)
        staged = Path(name)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(svg_bytes)
            staged.replace(target)
        finally:
            staged.unlink(missing_ok=True)


def jobs(source: Path, output: Path | None, output_dir: Path | None, recursive: bool) -> list[tuple[Path, Path]]:
    if source.is_file():
        if source.suffix.lower() not in FORMATS:
            raise ValueError(f"unsupported input format: {source.suffix}")
        target = output or ((output_dir / (source.stem + ".svg")) if output_dir else source.with_suffix(".svg"))
        if target.suffix.lower() != ".svg":
            raise ValueError("single-file output must end in .svg")
        return [(source, target)]
    if not source.is_dir():
        raise ValueError(f"input not found: {source}")
    if output is not None:
        raise ValueError("--output is only for a single-file input; use --output-dir")
    if output_dir and output_dir.exists() and not output_dir.is_dir():
        raise ValueError("directory output must be a directory")
    root = output_dir or source
    if root.resolve() != source.resolve() and root.resolve().is_relative_to(source.resolve()):
        raise ValueError("batch output directory must be outside the input tree")
    files = source.rglob("*") if recursive else source.iterdir()
    result = [(file, root / file.relative_to(source).with_suffix(".svg"))
              for file in sorted(files) if file.is_file() and file.suffix.lower() in FORMATS]
    if len({target.resolve() for _, target in result}) != len(result):
        raise ValueError("multiple inputs map to one SVG output")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path, help="SVG file path for single input")
    parser.add_argument("--output-dir", type=Path, help="output directory")
    parser.add_argument("--mode", choices=("auto", "embed", "trace"), default="embed",
                        help="auto is a compatibility alias for embed")
    parser.add_argument("--no-recursive", action="store_false", dest="recursive",
                        help="only process the top level; legacy behavior recurses")
    parser.set_defaults(recursive=True)
    parser.add_argument("--normalize", action="store_true", help="re-encode input as PNG with ImageMagick")
    parser.add_argument("--resize", help="ImageMagick geometry, requires --normalize in embed mode")
    parser.add_argument("--background", default="none", help="ImageMagick canvas/background color")
    parser.add_argument("--filter", choices=("Lanczos", "Mitchell", "Catrom", "Point"), default="Lanczos")
    parser.add_argument("--blur", type=float, help="ImageMagick blur sigma")
    parser.add_argument("--colors", type=int, help="limit colors during raster preparation")
    parser.add_argument("--mono", action="store_true", help="black/white VTracer mode")
    parser.add_argument("--threshold", default="auto", help="mono threshold 0..255 or auto")
    parser.add_argument("--invert", action="store_true", help="invert raster before mono trace")
    parser.add_argument("--simplify", type=float, default=2.0, help="VTracer curve tolerance in pixels")
    parser.add_argument("--curves", choices=("pixel", "polygon", "spline"), default="spline")
    parser.add_argument("--hierarchical", choices=("stacked", "cutout"), default="cutout")
    parser.add_argument("--filter-speckle", type=int, default=4)
    parser.add_argument("--color-precision", type=int, default=6)
    parser.add_argument("--path-precision", type=int, default=2)
    parser.add_argument("--max-colors", type=int)
    parser.add_argument("--magick", default="magick")
    parser.add_argument("--vtracer", default="vtracer")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.output and args.output_dir:
        parser.error("choose --output or --output-dir")
    if args.mode == "auto":
        args.mode = "embed"
    if args.resize and args.mode == "embed" and not args.normalize:
        parser.error("--resize requires --normalize in embed mode")
    if args.mode == "embed" and not args.normalize and (
        args.blur is not None or args.colors is not None or args.background != "none"
    ):
        parser.error("image preparation controls require --normalize in embed mode")
    if args.mode != "trace" and (args.mono or args.invert or args.threshold != "auto"):
        parser.error("mono/threshold/invert require --mode trace")
    if args.threshold != "auto" and (not args.threshold.isdigit() or not 0 <= int(args.threshold) <= 255):
        parser.error("--threshold must be auto or 0..255")
    if args.threshold != "auto" and not args.mono:
        parser.error("--threshold requires --mono")
    if args.invert and not args.mono:
        parser.error("--invert requires --mono")
    if args.blur is not None and args.blur < 0 or args.simplify < 0:
        parser.error("blur and simplify must be nonnegative")
    if not 0 <= args.filter_speckle <= 128 or not 1 <= args.color_precision <= 8 or not 0 <= args.path_precision <= 8:
        parser.error("trace precision settings out of range")
    if args.colors is not None and not 2 <= args.colors <= 256:
        parser.error("--colors must be 2..256")
    if args.max_colors is not None and not 2 <= args.max_colors <= 256:
        parser.error("--max-colors must be 2..256")
    try:
        planned = jobs(args.input, args.output, args.output_dir, args.recursive)
        if not planned:
            raise ValueError("no supported inputs found")
        if not args.dry_run:
            run([args.magick, "-version"])
            if args.mode == "trace":
                check_vtracer(args.vtracer)
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    failures = 0
    for source, target in planned:
        if target.exists() and not args.overwrite:
            print(f"SKIP exists: {target}")
            continue
        if args.dry_run:
            print(f"WOULD CONVERT {source} -> {target}")
            continue
        try:
            convert(source, target, args)
            print(f"CONVERTED {source} -> {target}")
        except (ValueError, OSError, RuntimeError, ET.ParseError) as exc:
            failures += 1
            print(f"FAILED {source}: {exc}", file=sys.stderr)
    print(f"Processed {len(planned)} input(s); failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
