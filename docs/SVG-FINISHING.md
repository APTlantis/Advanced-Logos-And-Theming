# Finish selected PNG assets as SVG

`apt-theme finish` processes an explicit TOML list without regenerating themes or modifying source runs. It defaults to a read-only preview. Writing creates a fresh directory containing finished SVGs, the exact SESM registry and `finish-receipt.json`.

## Usage

```powershell
# Validate selections, provenance, matching palette data, dependencies and SESM schema.
.\Invoke-AptTheme.ps1 finish docs\examples\finish-selected.toml --output .build\svg-review --json

# Write the selected deliverables into that still-fresh destination.
.\Invoke-AptTheme.ps1 finish docs\examples\finish-selected.toml --output .build\svg-review --write --json
```

The [four-asset example](examples/finish-selected.toml) requires the existing local artwork/BlackGold collection. Edit a copy to select your own files. Paths resolve relative to the plan, independently of the shell directory.

The separate [tracing example](examples/finish-trace.toml) selects one actual logo. Use `finish docs\examples\finish-trace.toml --output .build\trace-review --write --vtracer C:\path\vtracer.exe`. The recorded real VTracer review shows posterization and loss of fine texture at default settings; wrapping is the faithful choice when those details must remain intact.

```toml
schema = "aptlantis.finish-plan.v1"

[[assets]]
id = "dnf-example-logo"
input = "../artwork/logo.png"
role = "logo"
mode = "embed"
title = "Example logo"
theme_name = "dnf-Example"

[[assets]]
id = "dnf-example-terminal-palette"
run = "../output/dnf-Example"
target = "windows_terminal"
role = "theme-board"
mode = "palette"
```

Each entry needs a unique simple `id`, an SESM `role`, and exactly one `input` PNG or `run`. `mode` defaults to `embed`; `title` defaults to the selected source stem. `output` optionally overrides `<id>.svg` with a simple filename; case-insensitive collisions and Windows reserved names are rejected. Unknown fields are errors.

Run selections resolve actual files using `run.json.artifact_manifests`; historical generic paths remain supported. Without `target`, the selected run artifact is `palette.png`. With `target`, `logical` defaults to `swatch.png`; it can select another recorded PNG such as SiYuan's `preview.png` for embed/trace. These are manifest logical keys, not assumptions about emitted filenames. New manifest hashes and identities are checked before use.

For a standalone pipeline swatch PNG, `palette` may identify its matching canonical or target palette TOML. Palette mode requires valid structured data, expected swatch dimensions and exact recorded fill values. It never extracts colors from raster pixels. Run selections supply their own palette; target palette mode also checks the recorded token values/order/origins. Arbitrary unstructured PNGs use embed or trace.

Recorded theme identity is preserved and conflicts fail. Standalone assets may declare `theme_name` and, if necessary, `theme_version` (1–5). A version requires either an authored name or recorded theme data. Known generation evidence must agree. No theme, rights, descriptions or endorsement claims are invented for an arbitrary PNG.

## Conversion modes

| Mode | Result | Acceptance limit |
| --- | --- | --- |
| `embed` | Original PNG bytes in an SVG image element, retaining dimensions/transparency | Remains raster artwork inside an SVG container |
| `trace` | Paths produced by the converter's VTracer contract and default settings | Requires compatible VTracer 1.0.0-alpha.4; fidelity needs actual visual review |
| `palette` | Editable rectangles and text from recorded colors/order/labels, plus available lineage | Recreates a readable palette board; font metrics/layout may differ from the PNG |

Tracing uses the existing converter defaults. Use the standalone converter for its expanded tuning controls; this finishing interface does not add a second set of tracing settings. Missing tools never cause a fallback to another conversion method.

## SESM and provenance

Finishing invokes the independent sibling embedder with explicit root/configuration and `--write` against staged SVGs. It then runs the canonical schema/safe-profile validator. The supplied metadata overrides the embedder's logo defaults with the actual asset role, kind, tags, compact theme identity, PNG hash, conversion method and available palette lineage.

The receipt records all consulted source/configuration hashes, full identity-resolution evidence, recorded identity, conversion settings, tool versions/script hashes, final SVG hashes and separate schema/safe-profile results. Metadata insertion must preserve every artwork byte; the command verifies that property before committing.

Defaults use the sibling project beside the source checkout and `D:/.city_hall/SESM`. An installed wheel normally needs an explicit sibling path:

```powershell
apt-theme finish selection.toml --output results --write `
  --sesm-project D:\CTS\SESM-Metadata-Embedder `
  --sesm-standard D:\.city_hall\SESM `
  --sesm-python D:\CTS\SESM-Metadata-Embedder\.venv\Scripts\python.exe
```

The selected SESM interpreter requires `jsonschema`, as documented by that project. Finishing adds no Node/network requirement. `--magick` and `--vtracer` override tracing executables. The standard is read-only; changing it is outside this command's scope.

## Failure, warnings and recovery

Preview validates plan/data/schema and dependency availability without writing assets or an output directory. SVG content safety is only evaluated when SVGs are produced, so preview reports it as unperformed.

Writing stages the whole selection and commits only after every asset succeeds and all input/tool hashes are rechecked. Existing destinations, overlapping selected runs, unsafe paths, collisions, invalid data/schema/content and changed inputs fail without replacing a prior result. Source files and their original manifests are never rewritten. Use a new destination for every revision; finishing has no overwrite or replace option.

Schema success and safe-profile classification are separate. Warnings remain `sesm-unverified`, are recorded in the receipt and produce a warning envelope. Only clean canonical validation is `sesm-safe`; warnings are not silently promoted. Safety errors abort the batch. Metadata is descriptive context, not authority.

Exit 0 means preview/write completed, possibly with recorded warnings; exit 1 means processing failed; argparse uses 2 for invalid syntax. `--json` emits one CTS envelope on stdout; errors go to stderr. Browser rendering, native SVG editor import, target-application integration and publication remain separate gates.
