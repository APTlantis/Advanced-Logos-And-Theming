"""Create verified multi-resolution ICO files with ImageMagick 7."""

from __future__ import annotations

import argparse
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

FORMATS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp", ".gif", ".svg"}
DEFAULT_SIZES = (16, 32, 48, 64, 128, 256)


def parse_sizes(value: str) -> tuple[int, ...]:
    try:
        sizes = tuple(int(part.strip()) for part in value.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("sizes must be comma-separated integers") from exc
    if not sizes or len(set(sizes)) != len(sizes) or any(size < 1 or size > 256 for size in sizes):
        raise argparse.ArgumentTypeError("sizes must be unique integers from 1 to 256")
    return tuple(sorted(sizes, reverse=True))


def ico_sizes(path: Path) -> tuple[int, ...]:
    with path.open("rb") as stream:
        header = stream.read(6)
        if len(header) != 6:
            raise ValueError("truncated ICO header")
        reserved, kind, count = struct.unpack("<HHH", header)
        if reserved or kind != 1 or count == 0:
            raise ValueError("invalid ICO header")
        directory = stream.read(16 * count)
        if len(directory) != 16 * count:
            raise ValueError("truncated ICO directory")
        sizes = []
        for offset in range(0, len(directory), 16):
            width, height, _, _, _, _, length, position = struct.unpack_from("<BBBBHHII", directory, offset)
            width, height = width or 256, height or 256
            if width != height or not length or position + length > path.stat().st_size:
                raise ValueError("invalid ICO frame")
            sizes.append(width)
        return tuple(sizes)


def run(command: list[str]) -> str:
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}")
    return result.stdout.strip()


def convert(source: Path, target: Path, args: argparse.Namespace) -> None:
    with tempfile.TemporaryDirectory(prefix="logo-ico-") as directory:
        base = Path(directory) / "base.png"
        output = Path(directory) / "output.ico"
        input_spec = str(source) if source.suffix.lower() == ".svg" else str(source) + "[0]"
        command = [args.magick]
        if source.suffix.lower() == ".svg":
            command += ["-density", str(args.density)]
        command += [input_spec, "-auto-orient", "-filter", args.filter]
        if args.fit == "crop":
            command += ["-resize", "256x256^", "-gravity", "center", "-crop", "256x256+0+0", "+repage"]
        else:
            command += ["-resize", "256x256", "-background", args.background, "-gravity", "center", "-extent", "256x256"]
        run(command + ["-depth", "8", f"PNG32:{base}"])
        run([args.magick, str(base), "-define", "icon:auto-resize=" + ",".join(map(str, args.sizes)), str(output)])
        if sorted(ico_sizes(output)) != sorted(args.sizes):
            raise ValueError("ICO directory does not contain the requested sizes")
        decoded = run([args.magick, "identify", "-format", "%wx%h\n", str(output)]).splitlines()
        if sorted(decoded) != sorted(f"{size}x{size}" for size in args.sizes):
            raise ValueError("ICO frames could not all be decoded at the requested sizes")
        target.parent.mkdir(parents=True, exist_ok=True)
        descriptor, name = tempfile.mkstemp(prefix=target.name + ".", suffix=".tmp", dir=target.parent)
        staged = Path(name)
        try:
            with os.fdopen(descriptor, "wb") as stream, output.open("rb") as source_stream:
                shutil.copyfileobj(source_stream, stream)
            os.replace(staged, target)
        finally:
            staged.unlink(missing_ok=True)


def jobs(input_path: Path, output_path: Path | None, recursive: bool) -> list[tuple[Path, Path]]:
    if input_path.is_file():
        if input_path.suffix.lower() not in FORMATS:
            raise ValueError(f"unsupported input format: {input_path.suffix}")
        target = output_path or input_path.with_suffix(".ico")
        if target.is_dir():
            target /= input_path.stem + ".ico"
        if target.suffix.lower() != ".ico":
            raise ValueError("single-file output must end in .ico")
        return [(input_path, target)]
    if not input_path.is_dir():
        raise ValueError(f"input not found: {input_path}")
    if output_path is not None and output_path.exists() and not output_path.is_dir():
        raise ValueError("directory output must be a directory")
    root = output_path or input_path
    if root.resolve() != input_path.resolve() and root.resolve().is_relative_to(input_path.resolve()):
        raise ValueError("batch output directory must be outside the input tree")
    sources = input_path.rglob("*") if recursive else input_path.iterdir()
    result = []
    for source in sorted(sources):
        if source.is_file() and source.suffix.lower() in FORMATS:
            result.append((source, root / source.relative_to(input_path).with_suffix(".ico")))
    targets = [target.resolve() for _, target in result]
    if len(set(targets)) != len(targets):
        raise ValueError("multiple inputs map to one ICO output")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path, help="ICO file path or batch output directory")
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--sizes", type=parse_sizes, default=DEFAULT_SIZES)
    parser.add_argument("--fit", choices=("contain", "crop"), default="contain")
    parser.add_argument("--background", default="none", help="canvas color; default transparent")
    parser.add_argument("--filter", choices=("Lanczos", "Mitchell", "Catrom", "Point"), default="Lanczos")
    parser.add_argument("--density", type=int, default=384, help="SVG render DPI")
    parser.add_argument("--magick", default="magick", help="ImageMagick executable")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if not 72 <= args.density <= 1200:
        parser.error("--density must be 72..1200")
    try:
        planned = jobs(args.input, args.output, args.recursive)
        if not planned:
            raise ValueError("no supported inputs found")
        if not args.dry_run:
            run([args.magick, "-version"])
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
        except (ValueError, OSError, RuntimeError) as exc:
            failures += 1
            print(f"FAILED {source}: {exc}", file=sys.stderr)
    print(f"Processed {len(planned)} input(s); failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
