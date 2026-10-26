# Logos-And-Theming

Local image-to-theme engine and artwork utilities. Package **0.1.0**, **local pilot**. As of **2026-10-25**, exporter expansion is paused while existing outputs are refined. This stabilization adds clearer code boundaries and a separate SVG finishing workflow; the fifteen theme targets remain unchanged.

Start with [architecture](docs/ARCHITECTURE.md), [the stabilization audit](docs/STABILIZATION-AUDIT.md), [command contracts](docs/COMMAND-CONTRACT.md) and [output naming](docs/OUTPUT-NAMING.md). [Project records](Project-README.md) distinguish implementation from native acceptance.

## Setup and theme generation

Python 3.12+ and ImageMagick are required for image generation. Setup creates the project-local environment from locked dependencies; runtime generation needs no Node or network access.

```powershell
.\Setup.ps1
.\Invoke-AptTheme.ps1 generate artwork.png --name dnf-Example --output output\example-new --strict
.\Invoke-AptTheme.ps1 import palette.toml --theme-version 2 --output output\example-import --targets windows_terminal --json
```

Use a fresh output directory. `--overwrite` permits replacement of an existing pipeline run; a non-pipeline nonempty directory is refused. Completed builds are staged and failed replacement restores the prior run. Successful replacement removes the prior run, so retain dated destinations when history is needed.

Artwork versions 1–5 use `apt`, `dnf`, `rpm`, `yum`, `eopkg`. Explicit and inferred identity must agree; unknown identity needs `--theme-version`. Package version is separate. Source bytes and SHA-256 are preserved; canonical 32 colors, semantic assignments and derived dark target tokens remain separate artifacts. No new hue families are introduced.

## Existing theme targets

All fifteen generate by default. Select a comma-separated subset with `--targets`:

`windows_terminal,siyuan,typora,powerpoint,alacritty,notepad_plus_plus,sublime_text,svg,syntax_highlighting,data_visualization,website,kmindz,markdown,codemirror5,codemirror6`

Each selected target emits native payloads, provenance-bearing palette TOML, swatch PNG, tokens and validation. Run-root `palette.toml`, `palette.png`, diagnostics, provenance, `review.html` and `run.json` remain stable. Resolve target filenames through `run.json.artifact_manifests`; freely named files use the resolved version prefix, while required native package members stay fixed. [Native contracts and limits](docs/OUTPUT-REFERENCE.md).

Native editor, PowerPoint, SVG, browser and Matplotlib acceptance are distinct. Generation does not install or activate a theme. Declared contrast checks do not establish visual suitability in every native application.

## Finish selected PNGs as SVG

```powershell
# Read-only selection/schema preview.
.\Invoke-AptTheme.ps1 finish docs\examples\finish-selected.toml --output .build\svg-review --json
# Explicitly write to that still-fresh destination.
.\Invoke-AptTheme.ps1 finish docs\examples\finish-selected.toml --output .build\svg-review --write --json
```

Choose faithful raster wrapping, explicit VTracer tracing, or editable palette geometry from matching recorded data. The command invokes the independently governed sibling SESM embedder and canonical safe-profile validator. Source runs remain unchanged. The receipt separates schema validation, safe-profile warnings and native acceptance. [Full finishing contract](docs/SVG-FINISHING.md).

## Independent utilities

```powershell
.\.venv\Scripts\python.exe scripts\Convert-to-ICO.py --input image.png --output icon.ico
.\.venv\Scripts\python.exe scripts\Convert-to-SVG.py --input image.png --output wrapped.svg
.\.venv\Scripts\python.exe scripts\Convert-to-SVG.py --input image.png --output traced.svg --mode trace --vtracer C:\path\vtracer.exe
.\Invoke-AptTheme.ps1 atlas output --output .build\atlas-review
```

SVG wrapping preserves raster bytes; tracing requires VTracer 1.0.0-alpha.4 and never silently falls back. [Converter options](scripts/help.md). Atlas snapshots selected runs without regenerating themes; browser selections remain read-only. [Atlas contract](docs/CHROMATIC-ATLAS.md).

The older `scripts/generate_atlas.py` is the asset/catalog atlas and writes `assets/palette-atlas.html`; it is separate from the theme-run `atlas` command.

## Verification and recovery

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Use [current testing guidance](docs/TESTING-REFERENCE.md) and the [acceptance record](evidence/stabilization-2026-10-25.json). Managed-sandbox `WinError 5` failures must be distinguished from a reliable outside-sandbox run. Browser rendering and installed-wheel checks do not establish native installation, import or publication.

[Migration/recovery](migration/README.md) preserves archive and restoration evidence. `tools/migrate.py`, `tools/verify.py` and `tools/governance.py` are historical mutating workflows, not general preflight checks. Existing artwork, output collections, historical specimens and public copies must not be casually regenerated.

Earlier overview bytes are retained in [the dated documentation snapshot](docs/history/stabilization-2026-10-25/README.md). Historical presentations and migration acceptance records retain their original scope; current contracts are authoritative. No installation, activation, public-copy updates or publication are part of stabilization.
