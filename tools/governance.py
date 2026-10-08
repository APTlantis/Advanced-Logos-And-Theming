"""Write approved project records and narrowly update active discovery paths."""
import ast
import json
import re
import tomllib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT.parent / "SESM-Metadata-Embedder"


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def manifest(root, description, group=False):
    name = root.name
    path = json.dumps(str(root))
    return f'''[manifest]
schema = "APTlantis Entity Manifest"
schema_version = "2.4"
manifest_type = "project"
canonical_name = "{name}.manifest.toml"
last_updated = "2026-10-08"
maintainer = "Herb"

[entity]
id = "{name.lower()}"
title = "{name}"
kind = "{'project-group' if group else 'project'}"
class = "{'project-group' if group else 'project'}"
status = "active"
description = {json.dumps(description)}

[project]
type = "command-tool"
portfolio_class = "{'project-group' if group else 'project'}"
stage = "local-pilot"
version = "0.1.0"

[governance]
primary_standard = "CTS"
primary_standard_path = "D:/.city_hall/CTS/README.md"
additional_standards = ["WGS", "PPS"]
additional_standard_paths = ["D:/.city_hall/WGS/README.md", "D:/.city_hall/PPS/README.md"]
inherits_from = "D:/CTS/CTS.manifest.toml"

[lifecycle]
state = "active"
created = "2026-10-08"
last_updated = "2026-10-08"
last_reviewed = "2026-10-08"
maintainer = "Herb"

[paths]
root = {path}

[documentation]
project_proposal = "Project-Proposal.md"
project_readme = "Project-README.md"
readme = "README.md"

[relationships]
parent = "D:/CTS"
related_projects = ["{'Logos-And-Theming' if name != 'Logos-And-Theming' else 'SESM-Metadata-Embedder'}"]
child_projects = []

[verification]
tests_verified = true
artifact_verified = true
release_verified = false
installation_verified = false
evidence = "{'../Logos-And-Theming/' if name != 'Logos-And-Theming' else ''}migration/acceptance.json"

[agent]
read_first = ["AGENTS.md", "{name}.manifest.toml", "Project-Proposal.md", "Project-README.md"]
authoritative_docs = ["{name}.manifest.toml", "README.md", "AGENTS.md"]
safe_to_modify = true
notes = "Local source and artifact validation do not establish native installation, visual acceptance or release readiness."
'''


def metadata_project():
    write(META / "AGENTS.md", '''# SESM-Metadata-Embedder instructions

Inherit D:/AGENTS.md and D:/CTS/AGENTS.md. Read the manifest, proposal and README.
Preserve SVG artwork and all non-SESM metadata. Preview by default; require explicit --write and --replace.
Require explicit --root for asset-relative registry keys and catalog lookup. Load configuration only when supplied.
Use canonical D:/.city_hall/SESM schema and safe-profile validator. Assets belong to ../Logos-And-Theming/assets.
Run tests after edits; schema success is separate from safe-profile validation and public adoption.
Do not copy to a public site or regenerate assets without explicit authorization.
''')
    write(META / "README.md", '''# SESM-Metadata-Embedder

Independent CTS project for inserting or replacing SESM 0.3.0 metadata in SVGs. Artwork and catalogs belong to `../Logos-And-Theming/assets`; this project owns the embedder, registry and tests.

Run Setup.ps1 once (Python 3.11+). Preview:

```powershell
.\\Invoke-SESM.ps1 --input ..\\Logos-And-Theming\\assets\\svg-embed-logos --root ..\\Logos-And-Theming\\assets --config sesm-metadata.toml
```

Add `--write` to insert blocks. Add both `--write --replace` to replace existing SESM blocks. Existing blocks are otherwise skipped. `--recursive` includes descendants; `--schema PATH` selects a reviewed alternative schema. `--root` is mandatory to keep catalog and registry identity independent of tool location. Shared defaults merge with source-backed fallback, followed by per-asset overrides.

Source text outside the SESM block is retained; dimensions, paths, other metadata and embedded raster bytes are preserved. Doctype/entity declarations and duplicate SESM blocks are rejected. Validation uses jsonschema and the canonical schema at D:/.city_hall/SESM/svg_asset.schema.json.

Run `.venv\\Scripts\\python.exe -m unittest discover -s tests -v`. ImageMagick is needed by the migrated test fixture, not metadata embedding. Run the separate canonical `Validate-SESM-Safe.py --safe-profile --json` for SVG content safety. Existing-block skips are not fresh metadata validation.

Exit 0 means no failures, 1 means at least one asset failed, 2 means invalid setup/dependencies/arguments. Actions go to stdout and errors to stderr. No site copying or publication occurs. Native site acceptance and release remain separate gates.
''')
    write(META / "Project-README.md", "# SESM-Metadata-Embedder\n\nIndependent SVG metadata project split from Aptlantis Logos on 2026-10-08. See README.md for explicit asset-root/configuration invocation, tests and evidence limits. Recovery archives and migration acceptance live in ../Logos-And-Theming/migration.\n")
    write(META / "Project-Proposal.md", "# SESM-Metadata-Embedder proposal\n\nOwner: Herb. Date: 2026-10-08.\n\nSeparate independently meaningful SVG metadata authoring from image conversion and theme production. Preserve the existing preview/write/replace contract, SVG identity and artwork, using explicit asset roots and canonical schema validation. This project owns tooling, configuration and tests; shared artwork remains in Logos-And-Theming. Acceptance requires preview without changes, replacement preserving non-SESM content, full-schema error handling and separate safe-profile validation. Public site copying and publication are outside this migration.\n")
    write(META / "requirements.txt", "jsonschema==4.26.0\n")
    write(META / "Setup.ps1", '''$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    if (-not (Test-Path -LiteralPath '.venv\\Scripts\\python.exe')) { python -m venv .venv }
    & .\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'SESM dependency setup failed.' }
} finally { Pop-Location }
''')
    write(META / "Invoke-SESM.ps1", '''param([Parameter(ValueFromRemainingArguments = $true)][string[]]$EmbeddingArguments)
$ErrorActionPreference = 'Stop'
$metadataPython = Join-Path $PSScriptRoot '.venv\\Scripts\\python.exe'
if (-not (Test-Path -LiteralPath $metadataPython)) { throw 'Run Setup.ps1 first.' }
& $metadataPython (Join-Path $PSScriptRoot 'scripts\\Embed-SESM.py') @EmbeddingArguments
exit $LASTEXITCODE
''')
    write(META / ".gitignore", ".venv/\n__pycache__/\n")
    embed = META / "scripts" / "Embed-SESM.py"
    text = embed.read_text(encoding="utf-8-sig")
    tree = ast.parse(text)
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "validate_schema")
    lines = text.splitlines(keepends=True)
    lines[function.lineno - 1:function.end_lineno] = ['''def validate_schema(value: object, schema: dict, path: str = "sesm") -> list[str]:
    from jsonschema import Draft202012Validator, FormatChecker
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [f"{path}: {error.message}" for error in validator.iter_errors(value)]
''']
    text = "".join(lines).replace('parser.add_argument("--root", type=Path, default=PROJECT_ROOT,', 'parser.add_argument("--root", type=Path, required=True,')
    write(embed, text)


def registrations():
    parent = ROOT.parent / "CTS.manifest.toml"
    text = parent.read_text(encoding="utf-8-sig")
    data = tomllib.loads(text)
    removed = {"Aptlantis Logos", "Lang-Theme-Generator"}
    children = [v for v in data["structure"]["children"] if v not in removed]
    projects = [v for v in data["classification"]["projects"] if v not in removed and v != "Logos-And-Theming"]
    groups = data["classification"]["project_groups"]
    for name in ("Logos-And-Theming", "SESM-Metadata-Embedder"):
        if name not in children:
            children.append(name)
    if "SESM-Metadata-Embedder" not in projects:
        projects.append("SESM-Metadata-Embedder")
    if "Logos-And-Theming" not in groups:
        groups.append("Logos-And-Theming")
    for key, values in (("children", children), ("projects", projects), ("project_groups", groups)):
        text = re.sub(r"(?m)^" + key + r" = \[[\s\S]*?\]", key + " = " + json.dumps(values), text, count=1)
    text = text.replace('last_updated = "2026-09-23"', 'last_updated = "2026-10-08"')
    lifecycle = text.split("[lifecycle]", 1)[1].split("[", 1)[0]
    if "last_updated" not in lifecycle:
        text = text.replace('[lifecycle]\n', '[lifecycle]\nlast_updated = "2026-10-08"\n', 1)
    note = '    "2026-10-08: Logos-And-Theming consolidates Aptlantis Logos, Lang-Theme-Generator and held palette-transformer; SESM-Metadata-Embedder is a separate sibling. Legacy trees are hash-verified in Logos-And-Theming/migration/archives.",\n'
    if note.strip() not in text:
        text = text.replace('known_gaps = [\n', 'known_gaps = [\n' + note)
    write(parent, text)
    index = Path(r"D:\INDEX.md")
    text = index.read_text(encoding="utf-8-sig")
    text = text.replace('`Aptlantis Logos`, ', '').replace('`Lang-Theme-Generator`, ', '')
    text = text.replace('Active projects: `Analyze-Projects`,', 'Active project group: `Logos-And-Theming`.\nActive projects: `SESM-Metadata-Embedder`, `Analyze-Projects`,')
    lines = [line for line in text.splitlines() if not (line.startswith('`Aptlantis Logos` is the current') or line.startswith('- The `Aptlantis Logos` directory rename'))]
    lines += ['', '## Logos and theming consolidation — 2026-10-08', '',
              '`D:\\CTS\\Logos-And-Theming` owns image-to-theme generation, shared artwork, ICO/SVG conversion and atlas tooling. `D:\\CTS\\SESM-Metadata-Embedder` independently owns SVG metadata embedding. Retired project trees and Git history are recoverable from `D:\\CTS\\Logos-And-Theming\\migration\\archives`; see its acceptance record before interpreting validation or lifecycle claims.']
    write(index, "\n".join(lines) + "\n")
    holding = Path(r"D:\CTS\.cts_holding\.cts_holding.manifest.toml")
    text = holding.read_text(encoding="utf-8-sig").replace('children = ["Flathub Toolkit", "Script Writers", "UTILITIES"]', 'children = []')
    text = text.replace('held_projects = ["Flathub Toolkit", "Script Writers", "UTILITIES"]', 'held_projects = []')
    text = text.replace('D:\\\\.library\\\\aptlantis_core', 'D:\\\\.city_hall')
    text = text.replace('last_updated = "2026-08-22"', 'last_updated = "2026-10-08"')
    text = text.replace('known_gaps = [\n', 'known_gaps = [\n    "2026-10-08: held palette-transformer consolidated into Logos-And-Theming; no physically present held projects remain after verified retirement. Older inventory entries were historical and absent.",\n')
    write(holding, text)


def site_workflow():
    path = Path(r"A:\aptlantis.net\docs\city-hall-logo-workflow.md")
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace(r"C:\Users\Administrator\AppData\Local\Programs\Python\Python313\python.exe", str(META / ".venv/Scripts/python.exe").replace("/", "\\"))
    text = text.replace(r'D:\CTS\Aptlantis Logos\svg-embed-logos', r'D:\CTS\Logos-And-Theming\assets\svg-embed-logos')
    text = text.replace('The operator-authored `sesm-metadata.toml` in that project', 'The operator-authored `sesm-metadata.toml` in `D:\\CTS\\SESM-Metadata-Embedder`')
    text = text.replace("$logoRoot = 'D:\\CTS\\Aptlantis Logos'", "$logoRoot = 'D:\\CTS\\Logos-And-Theming\\assets'\n$metadataRoot = 'D:\\CTS\\SESM-Metadata-Embedder'")
    text = text.replace('"$logoRoot\\tests"', '"$metadataRoot\\tests"')
    text = text.replace('"$logoRoot\\scripts\\Embed-SESM.py"', '"$metadataRoot\\scripts\\Embed-SESM.py"')
    text = text.replace('--config "$logoRoot\\sesm-metadata.toml"', '--root "$logoRoot" --config "$metadataRoot\\sesm-metadata.toml"')
    note = 'Source discovery paths updated 2026-10-08 for the verified project migration. Existing public asset copies and the historical validation claims above are unchanged.'
    if note not in text:
        text += '\n' + note + '\n'
    write(path, text)


if __name__ == "__main__":
    if "--repair-site-python" in sys.argv:
        site_workflow()
        sys.exit(0)
    if "--repair-manifests" in sys.argv:
        write(ROOT / "Logos-And-Theming.manifest.toml", manifest(ROOT, "Image-derived dark theme pipeline and related logo utilities", True))
        write(META / "SESM-Metadata-Embedder.manifest.toml", manifest(META, "Independent SESM SVG metadata preview, insertion and replacement"))
        for path in (ROOT.parent / "CTS.manifest.toml", ROOT.parent / ".cts_holding/.cts_holding.manifest.toml"):
            text = path.read_text(encoding="utf-8-sig")
            if "last_updated" not in text.split("[lifecycle]", 1)[1].split("[", 1)[0]:
                write(path, text.replace('[lifecycle]\n', '[lifecycle]\nlast_updated = "2026-10-08"\n', 1))
        sys.exit(0)
    metadata_project()
    write(ROOT / "Logos-And-Theming.manifest.toml", manifest(ROOT, "Image-derived dark theme pipeline and related logo utilities", True))
    write(META / "SESM-Metadata-Embedder.manifest.toml", manifest(META, "Independent SESM SVG metadata preview, insertion and replacement"))
    registrations()
    site_workflow()
    print("Project governance and active discovery paths updated; dated handbook snapshots preserved.")
