"""Stable command entry point; no installation or activation of generated themes."""
import argparse
import json
import sys
import tomllib
from pathlib import Path

from .targets import DEFAULTS


def write_json(path, value):
    """Compatibility entry point for callers of the original CLI helper."""
    from .pipeline import write_json as write
    return write(path, value)


def build(args):
    """Compatibility entry point for generation/import callers."""
    from .pipeline import build as generate
    return generate(args)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version="apt-theme 0.1.0")
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("generate", "import"):
        p = commands.add_parser(command)
        p.add_argument("input", type=Path)
        p.add_argument("--output", type=Path, required=True)
        p.add_argument("--name")
        p.add_argument("--theme-version", type=int, choices=range(1, 6), help="artwork generation: 1=apt, 2=dnf, 3=rpm, 4=yum, 5=eopkg")
        p.add_argument("--targets", default=",".join(DEFAULTS))
        p.add_argument("--config", type=Path)
        p.add_argument("--compare", type=Path)
        p.add_argument("--overwrite", action="store_true")
        p.add_argument("--strict", action="store_true")
        p.add_argument("--json", action="store_true", help="machine-readable result on stdout")
    from . import atlas
    atlas.configure(commands.add_parser("atlas", help="read-only palette collection explorer"))
    from . import finishing
    finishing.configure(commands.add_parser("finish", help="finish explicitly selected PNGs as SVG with SESM"))
    args = parser.parse_args(argv)
    try:
        if args.command == "atlas":
            return atlas.run(args)
        if args.command == "finish":
            return finishing.run(args)
        print("Generating image-derived dark themes...", file=sys.stderr)
        result = build(args)
        failed = args.strict and result["contrast_failures"]
        envelope = {"status": "error" if failed else "warning" if result["contrast_failures"] or result["semantic_findings"] else "ok",
                    "tool": "apt-theme", "version": "0.1.0", "data": result,
                    "warnings": [json.dumps(finding) for finding in result["semantic_findings"]],
                    "errors": [{"code": "contrast_failed", "category": "validation", "message": "Declared contrast checks failed"}] if failed else []}
        print(json.dumps(envelope) if args.json else f"Generated {', '.join(result['targets'])}; {result['contrast_failures']} contrast failures. Review: {args.output / 'review.html'}")
        return 2 if args.strict and result["contrast_failures"] else 0
    except (ValueError, OSError, KeyError, TypeError, OverflowError, tomllib.TOMLDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        if args.json:
            print(json.dumps({"status": "error", "tool": "apt-theme", "version": "0.1.0", "data": None,
                              "warnings": [], "errors": [{"code": "processing_failed", "category": "runtime", "message": str(exc)}]}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
