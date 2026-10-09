"""Inventory, archive, verify and stage the user-authorized consolidation.

Retirement is a separate invocation after validation and reference updates.
"""
import argparse
import ast
import hashlib
import json
import shutil
import stat
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {"aptlantis-logos": Path(r"D:\CTS\Aptlantis Logos"),
           "lang-theme-generator": Path(r"D:\CTS\Lang-Theme-Generator"),
           "palette-transformer": Path(r"D:\CTS\.cts_holding\palette-transformer"),
           "advanced-documents": Path(r"C:\Users\Administrator\Documents\Advanced-Logos-And-Theming")}
METADATA = ROOT.parent / "SESM-Metadata-Embedder"
ARCHIVES = ROOT / "migration" / "archives"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def inventory(root):
    if root.is_symlink() or root.is_junction():
        raise ValueError(f"Refusing reparse root {root}")
    result = {}
    for file in sorted(root.rglob("*")):
        if file.is_symlink() or file.is_junction():
            raise ValueError(f"Refusing reparse entry {file}")
        if file.is_file():
            result[file.relative_to(root).as_posix()] = {"sha256": sha(file), "bytes": file.stat().st_size}
    return result


def archive(name, root):
    listing = inventory(root)
    target = ARCHIVES / (name + ".zip")
    manifest = ARCHIVES / (name + ".json")
    if target.exists():
        saved = json.loads(manifest.read_text())
        if saved["files"] != listing or sha(target) != saved["archive_sha256"]:
            raise ValueError(f"Source or archive changed: {root}")
        return saved
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=3) as bundle:
        for relative in listing:
            bundle.write(root / relative, relative)
    # Restore every archived file, not just its CRC or a representative sample.
    with tempfile.TemporaryDirectory(prefix="apt-restore-") as temp:
        with zipfile.ZipFile(target) as bundle:
            bundle.extractall(temp)
        restored = inventory(Path(temp))
        if restored != listing:
            raise ValueError(f"Restored archive differs: {name}")
    if inventory(root) != listing:
        raise ValueError(f"Source changed while archiving: {root}")
    saved = {"source": str(root), "files": listing, "archive_sha256": sha(target), "full_restore_verified": True}
    manifest.write_text(json.dumps(saved, indent=2), encoding="utf-8")
    return saved


def copy_verified(source, target):
    if source.is_dir():
        shutil.copytree(source, target, dirs_exist_ok=True)
        if inventory(source) != inventory(target):
            raise ValueError(f"Copied tree differs: {target}")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if sha(source) != sha(target):
            raise ValueError(f"Copied file differs: {target}")


def split_tests(source, output, embedding):
    text = source.read_text(encoding="utf-8-sig")
    tree = ast.parse(text)
    lines = text.splitlines(keepends=True)
    remove = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            if node.name.startswith("test_sesm") != embedding:
                remove.append((node.lineno - 1, node.end_lineno))
    for start, end in sorted(remove, reverse=True):
        del lines[start:end]
    text = "".join(lines)
    if embedding:
        text = text.replace('ico = module("Convert-to-ICO.py")', '').replace('svg = module("Convert-to-SVG.py")', '')
        text = text.replace('catalogued = sesm.fallback(ROOT / "svg" / "apt-caddy-logo.svg", ROOT)',
                            'assets = ROOT.parent / "Logos-And-Theming" / "assets"\n        catalogued = sesm.fallback(assets / "svg" / "apt-caddy-logo.svg", assets)')
    else:
        text = text.replace('sesm = module("Embed-SESM.py")', '')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")


def stage():
    ARCHIVES.mkdir(parents=True, exist_ok=True)
    records = {}
    for name, root in SOURCES.items():
        print(f"Archiving and restoring {name}...", flush=True)
        records[name] = archive(name, root)
    logos, lang, transformer, docs = SOURCES.values()
    assets = ROOT / "assets"
    for folder in ("logos", "ico", "png", "svg", "svg-embed-logos", "palettes", "themes"):
        copy_verified(logos / folder, assets / folder)
    copy_verified(logos / "logos.json", assets / "logos.json")
    for folder in ("Gen2", "palettes", "themes", "project_images", "Docs"):
        copy_verified(lang / folder, assets / "legacy-lang-theme" / folder)
    for folder in ("Aptlantis-Black-Gold", "before-edit-refs"):
        copy_verified(docs / folder, assets / "references" / folder)
    copy_verified(docs / "apt-aptlantis-dnf-Blackgold-16bit-logo.tif", assets / "sources" / "apt-aptlantis-dnf-Blackgold-16bit-logo.tif")
    scripts = ROOT / "scripts"
    for name in ("Convert-to-ICO.py", "Convert-to-SVG.py", "generate_atlas.py", "help.md"):
        copy_verified(logos / "scripts" / name, scripts / name)
    atlas = scripts / "generate_atlas.py"
    text = atlas.read_text().replace("os.path.dirname(__file__), '..'", "os.path.dirname(__file__), '..', 'assets'")
    atlas.write_text(text, encoding="utf-8")
    # Independently runnable preserved transformer remains available as a utility.
    for file in transformer.glob("*.py"):
        copy_verified(file, ROOT / "legacy-tools" / "palette-transformer" / file.name)
    for name in ("profiles.toml", "requirements.txt", "README.md", "Transform-Palette.ps1"):
        copy_verified(transformer / name, ROOT / "legacy-tools" / "palette-transformer" / name)
    copy_verified(transformer / "tests", ROOT / "legacy-tools" / "palette-transformer" / "tests")
    copy_verified(transformer / "examples", ROOT / "legacy-tools" / "palette-transformer" / "examples")
    for name in ("generate_theme.py", "generate_theme32.py", "PaletteGenerator32.ps1"):
        copy_verified(lang / name, ROOT / "legacy-tools" / "lang-theme" / name)
    copy_verified(docs / "AptlantisPaletteGenerator.ps1", ROOT / "legacy-tools" / "documents" / "AptlantisPaletteGenerator.ps1")
    METADATA.mkdir(exist_ok=True)
    copy_verified(logos / "scripts" / "Embed-SESM.py", METADATA / "scripts" / "Embed-SESM.py")
    copy_verified(logos / "sesm-metadata.toml", METADATA / "sesm-metadata.toml")
    split_tests(logos / "tests" / "test_logo_tools.py", ROOT / "tests" / "test_logo_tools.py", False)
    split_tests(logos / "tests" / "test_logo_tools.py", METADATA / "tests" / "test_embedding.py", True)
    duplicates = {}
    for source_id, record in records.items():
        for relative, details in record["files"].items():
            if relative.endswith((".py", ".ps1")) and "/.venv/" not in "/" + relative and "/__pycache__/" not in "/" + relative:
                duplicates.setdefault(Path(relative).name, []).append({"source": source_id, "path": relative, "sha256": details["sha256"]})
    report = {"archives": {key: {"source": rec["source"], "file_count": len(rec["files"]), "archive_sha256": rec["archive_sha256"], "full_restore_verified": True} for key, rec in records.items()},
              "duplicate_scripts": {k: v for k, v in duplicates.items() if len(v) > 1},
              "active_implementation": "Reviewed D-drive converters and SESM; new theme engine; all differing scripts preserved in archives",
              "status": "staged; source retirement pending validation and reference updates"}
    (ROOT / "migration" / "inventory.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Migration staged; no sources removed.")


def retire():
    gate = json.loads((ROOT / "migration" / "acceptance.json").read_text())
    if gate.get("ready_to_retire") is not True:
        raise ValueError("Validation and references have not passed the retirement gate")
    # Validate every source before deleting the first source.
    for name, root in SOURCES.items():
        if not root.exists():
            continue
        expected = json.loads((ARCHIVES / (name + ".json")).read_text())
        if root.resolve() != Path(expected["source"]).resolve() or root.resolve() not in [p.resolve() for p in SOURCES.values()]:
            raise ValueError("Retirement path escaped the explicitly named sources")
        if inventory(root) != expected["files"] or sha(ARCHIVES / (name + ".zip")) != expected["archive_sha256"]:
            raise ValueError(f"Source or archive changed since snapshot: {root}")
    for name, root in SOURCES.items():
        if root.exists():
            def remove_readonly(function, path, error):
                Path(path).chmod(stat.S_IWRITE)
                function(path)
            shutil.rmtree(root, onexc=remove_readonly)
        print(f"Retired {root}", flush=True)
    report = ROOT / "migration" / "inventory.json"
    data = json.loads(report.read_text())
    data["status"] = "retired after verified archival, destination checks and reference updates"
    report.write_text(json.dumps(data, indent=2), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("stage", "retire"))
    args = parser.parse_args()
    {"stage": stage, "retire": retire}[args.action]()
