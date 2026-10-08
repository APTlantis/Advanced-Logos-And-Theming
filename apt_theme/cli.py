"""Stable command entry point; no installation or activation of generated themes."""
import argparse
import json
import shutil
import sys
import tempfile
import tomllib
from pathlib import Path

from .extraction import digest, extract, load_palette, metrics, palette_toml, select
from .report import review, swatch
from .semantics import assign
from .targets import DEFAULTS, adapt, export


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def build(args):
    source = args.input.resolve(strict=True)
    output = args.output.resolve()
    if output == source or output in source.parents:
        raise ValueError("Output cannot contain the input source")
    if output.exists() and not args.overwrite:
        raise ValueError("Output already exists; use --overwrite explicitly")
    if output.exists() and not output.is_dir():
        raise ValueError("Output must be a directory")
    if output.exists() and (output / "run.json").exists() is False and any(output.iterdir()):
        raise ValueError("Refusing to overwrite a non-pipeline directory")
    config = {}
    if args.config:
        config = tomllib.loads(args.config.read_text(encoding="utf-8-sig"))
    if set(config) - {"profiles", "extraction", "overrides"}:
        raise ValueError("Unknown configuration section")
    targets = args.targets.split(",")
    if len(set(targets)) != len(targets) or any(t not in DEFAULTS for t in targets):
        raise ValueError("Targets must be unique names from " + ", ".join(DEFAULTS))
    name = args.name or source.stem
    comparison, old = None, {}
    if args.command == "generate":
        candidates, provenance, coords, weights = extract(source, config.get("extraction", {}))
        colors = select(candidates, int(config.get("extraction", {}).get("seed", 32)))
        diagnostics = {"canonical": metrics(coords, weights, colors)}
    else:
        colors, old = load_palette(source)
        provenance = {"sha256": digest(source), "kind": "imported_palette", "legacy_roles": old.get("roles", {})}
        candidates = list(colors.values())
        diagnostics = {"kind": "import", "canonical_colors_preserved": True}
    if args.compare:
        comparison, _ = load_palette(args.compare)
        if args.command == "generate":
            diagnostics["previous"] = metrics(coords, weights, comparison)
        diagnostics["comparison_sha256"] = digest(args.compare)
    roles, notices = assign(colors, config.get("overrides", {}))
    results = [adapt(colors, roles, target, int(config.get("profiles", {}).get(target, {}).get("budget", DEFAULTS[target]))) for target in targets]
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="apt-build-", dir=output.parent) as temp:
        stage = Path(temp) / "result"
        stage.mkdir()
        source_dir = stage / "source"
        source_dir.mkdir()
        shutil.copy2(source, source_dir / source.name)
        if digest(source_dir / source.name) != provenance["sha256"]:
            raise ValueError("Source changed before preservation")
        (stage / "palette.toml").write_text(palette_toml(colors, name, provenance["sha256"]), encoding="utf-8")
        (stage / "palette.txt").write_text("\n".join(f'{key}\t{c["hex"]}' for key, c in colors.items()) + "\n", encoding="utf-8")
        (stage / "palette.css").write_text(":root {\n" + "\n".join(f'  --apt-{key.replace("_", "-")}: {c["hex"]};' for key, c in colors.items()) + "\n}\n", encoding="utf-8")
        swatch(colors, stage / "palette.png", name + " canonical 32")
        write_json(stage / "candidates.json", candidates)
        write_json(stage / "selection.json", diagnostics)
        write_json(stage / "semantics.json", {"roles": roles, "findings": notices})
        write_json(stage / "provenance.json", provenance)
        for result in results:
            export(result, stage / result["target"], name)
        review(stage, name, colors, candidates, roles, notices, results, diagnostics,
               source_dir / source.name if args.command == "generate" else None, comparison)
        failures = sum(r["contrast_failures"] for r in results)
        run = {"schema": "aptlantis.theme-run.v1", "name": name, "variant": "dark", "source_sha256": provenance["sha256"],
               "targets": targets, "contrast_failures": failures, "semantic_findings": notices,
               "native_application_acceptance": "pending", "installation": "not performed"}
        write_json(stage / "run.json", run)
        if output.exists():
            # The old result remains recoverable until the completed replacement is in place.
            backup = Path(temp) / "previous"
            output.rename(backup)
            try:
                stage.rename(output)
            except BaseException:
                backup.rename(output)
                raise
        else:
            stage.rename(output)
    return run


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version="apt-theme 0.1.0")
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("generate", "import"):
        p = commands.add_parser(command)
        p.add_argument("input", type=Path)
        p.add_argument("--output", type=Path, required=True)
        p.add_argument("--name")
        p.add_argument("--targets", default=",".join(DEFAULTS))
        p.add_argument("--config", type=Path)
        p.add_argument("--compare", type=Path)
        p.add_argument("--overwrite", action="store_true")
        p.add_argument("--strict", action="store_true")
        p.add_argument("--json", action="store_true", help="machine-readable result on stdout")
    args = parser.parse_args(argv)
    try:
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
