"""Final local acceptance and retirement gate; preserves detailed command evidence."""
import hashlib
import json
import subprocess
import sys
import tempfile
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from apt_theme.colors import contrast, from_rgb
from apt_theme.extraction import load_palette
from apt_theme.semantics import hue_distance
from migrate import SOURCES, inventory, sha, ARCHIVES


def command(args, cwd=ROOT):
    proc = subprocess.run([str(v) for v in args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return {"command": [str(v) for v in args], "cwd": str(cwd), "exit_code": proc.returncode,
            "stdout": proc.stdout, "stderr": proc.stderr}


def hashes(root):
    return {str(p.relative_to(root)): sha(p) for p in root.rglob("*") if p.is_file()}


def main():
    records = []
    tests = command([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    records.append(tests)
    meta = ROOT.parent / "SESM-Metadata-Embedder"
    records.append(command([meta / ".venv/Scripts/python.exe", "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=meta))
    records.append(command([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT / "legacy-tools/palette-transformer"))
    records.append(command([sys.executable, "scripts/generate_atlas.py"]))
    records.append(command([sys.executable, r"D:\.city_hall\CTS\tools\cts_lint_contract.py", "docs/COMMAND-CONTRACT.md"]))
    assets = ROOT / "assets"
    records.append(command(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", meta / "Invoke-SESM.ps1",
                           "--input", assets / "svg-embed-logos", "--root", assets, "--config", meta / "sesm-metadata.toml"]))
    safe_files = sorted((assets / "svg-embed-logos").glob("*.svg"))
    if len(safe_files) != 16:
        raise ValueError("Expected 16 migrated component SVGs")
    for svg in safe_files:
        records.append(command([sys.executable, r"D:\.city_hall\SESM\Validate-SESM-Safe.py", svg, "--safe-profile", "--json"]))
    # Generate the exact delivered pilot through the PowerShell launcher.
    args = ["generate", str(assets / "sources/apt-aptlantis-dnf-Blackgold-16bit-logo.tif"), "--output", str(ROOT / "pilot/aptlantis-dnf-Blackgold"),
            "--name", "Aptlantis Zig Dark", "--compare", str(assets / "references/Aptlantis-Black-Gold/palette.toml"), "--overwrite", "--strict", "--json"]
    pilot = command(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ROOT / "Invoke-AptTheme.ps1", *args])
    records.append(pilot)
    if pilot["exit_code"]:
        raise ValueError("Pilot command failed: " + pilot["stderr"])
    envelope = json.loads(pilot["stdout"])
    schema = json.loads(Path(r"D:\.city_hall\CTS\CommandOutput.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(envelope)
    baseline = hashes(ROOT / "pilot/aptlantis-dnf-Blackgold")
    duplicate = command([ROOT / ".venv/Scripts/apt-theme.exe", *args])
    records.append(duplicate)
    second = hashes(ROOT / "pilot/aptlantis-dnf-Blackgold")
    deterministic = baseline == second
    changed_files = [key for key in set(baseline) | set(second) if baseline.get(key) != second.get(key)]
    colors, _ = load_palette(ROOT / "pilot/aptlantis-dnf-Blackgold/palette.toml")
    semantics = json.loads((ROOT / "pilot/aptlantis-dnf-Blackgold/semantics.json").read_text())
    warning = colors[semantics["roles"]["warning"]]
    warm_warning = hue_distance(warning["oklch"][2], 85) < 45
    native_checks = {}
    for target in ("windows_terminal", "siyuan", "typora", "powerpoint"):
        result = json.loads((ROOT / "pilot/aptlantis-dnf-Blackgold" / target / "tokens.json").read_text())
        # Recalculate ratios from final exported RGB, independently of the saved ratio field.
        recalculated = [contrast(result["tokens"][pair["foreground"]], result["tokens"][pair["background"]]) >= pair["required"] for pair in result["checks"]]
        native_checks[target] = {"named": result["named_count"], "unique": result["unique_count"],
                                 "declared_pairs": len(recalculated), "failures": sum(not passed for passed in recalculated)}
    manifest_schema = json.loads(Path(r"D:\.city_hall\WGS\EntityManifest-v2.4.schema.json").read_text(encoding="utf-8"))
    for path in (ROOT / "Logos-And-Theming.manifest.toml", meta / "SESM-Metadata-Embedder.manifest.toml", ROOT.parent / "CTS.manifest.toml", ROOT.parent / ".cts_holding/.cts_holding.manifest.toml"):
        Draft202012Validator(manifest_schema).validate(tomllib.loads(path.read_text(encoding="utf-8-sig")))
    parent = tomllib.loads((ROOT.parent / "CTS.manifest.toml").read_text(encoding="utf-8-sig"))
    references = "Logos-And-Theming" in parent["classification"]["project_groups"] and "SESM-Metadata-Embedder" in parent["classification"]["projects"]
    references = references and not ({"Aptlantis Logos", "Lang-Theme-Generator"} & set(parent["structure"]["children"]))
    workflow = Path(r"A:\aptlantis.net\docs\city-hall-logo-workflow.md").read_text(encoding="utf-8-sig")
    references = references and "Aptlantis Logos" not in workflow and '$metadataRoot' in workflow and '--root "$logoRoot"' in workflow
    references = references and str(meta / ".venv/Scripts/python.exe").replace("/", "\\") in workflow
    original = json.loads((ARCHIVES / "aptlantis-logos.json").read_text())["files"]
    archived_svgs = {p.removeprefix("svg-embed-logos/"): info for p, info in original.items() if p.startswith("svg-embed-logos/")}
    asset_preservation = archived_svgs == inventory(assets / "svg-embed-logos")
    for name, source in SOURCES.items():
        saved = json.loads((ARCHIVES / (name + ".json")).read_text())
        if saved["archive_sha256"] != sha(ARCHIVES / (name + ".zip")):
            raise ValueError(f"Archive changed after migration: {name}")
        if source.exists():
            if saved["files"] != inventory(source):
                raise ValueError(f"Source/archive changed after migration: {name}")
    ready = all(r["exit_code"] == 0 for r in records) and deterministic and warm_warning and references and asset_preservation and all(v["failures"] == 0 for v in native_checks.values())
    acceptance = {"reviewed_on": "2026-10-08", "timezone": "America/New_York", "ready_to_retire": ready,
        "commands": records, "deterministic_full_pilot": deterministic, "determinism_changed_files": changed_files, "canonical_count": len(colors),
        "warning_hex": warning["hex"], "warm_warning": warm_warning, "native_checks": native_checks,
        "active_references_updated": references, "svg_artwork_metadata_bytes_preserved": asset_preservation,
        "archive_full_restore": "verified during staging for all four trees", "browser_report": "loaded and visually inspected; source image decodes; all four target samples present; no horizontal overflow at 1288px",
        "native_application_import_and_visual_acceptance": "pending", "vtracer_actual_trace": "not exercised; migrated contract test uses a stub",
        "public_asset_copies": "not modified", "release": "not established"}
    acceptance["legacy_locations_retired"] = all(not p.exists() for p in SOURCES.values())
    (ROOT / "migration/acceptance.json").write_text(json.dumps(acceptance, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in acceptance.items() if k != "commands"}, indent=2))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
