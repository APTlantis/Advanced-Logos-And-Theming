# Stabilization audit — 2026-10-25

Review covers current Python engine/exporters, converter scripts, Atlas/artifact discovery, package resources, tests, operational tools and documentation. It does not audit every generated theme visually, reopen every native application, or reinterpret historical archives as current source.

## Findings and disposition

| Priority | Evidence and implication | Disposition / acceptance |
| --- | --- | --- |
| High | Managed-sandbox temporary-file access caused widespread failures; the same original 59 tests pass outside that sandbox. | Record environment failure separately. Establish the outside-sandbox baseline before editing application behavior. |
| High | `cli.py` combined argument presentation with source preservation, adaptation, reporting and replacement. | Move orchestration to `pipeline.py`; retain CLI callable wrappers. Require complete fixture byte equality. |
| High | `targets.py` combined adaptation with native output serialization and dispatch. | Move writer dispatch/CSS helpers to `exporters.py`; preserve existing specialized exporters and wrapper signatures. No exporter rewrite. |
| High | Pipeline and Atlas duplicated directory replacement and rollback; artifact consumers separately validated manifest paths. | Share transactions and manifest validation. Keep consumer-specific ownership/lineage checks. Test failed commit recovery and collision rejection. |
| High | The sibling embedder's fallback role/kind/tags described every asset as a logo. | Supply explicit per-asset SESM records for finishing. Retain sibling ownership and canonical validation. Palette boards must not be labeled as logos. |
| Medium | Overview documents accumulated chronological additions, conflicting test counts, and superseded compatibility-copy naming. | Establish one current architecture/command guide. Preserve former overview bytes in a dated documentation snapshot; mark older detailed reference text as historical where applicable. |
| Medium | Existing ignore rules hide newly introduced engine modules and docs. | Add narrow exceptions for the new maintained files and this acceptance record, leaving artwork/output/archive exclusions intact. |
| Medium | SVG script implementation was unavailable as package code to an installed finishing command. | Move implementation into `svg_converter.py`, retain direct script invocation, and verify installed-wheel finishing. |
| High | Installed-wheel comparison found an extra exported `sources/__pycache__/palette.cpython-313.pyc`: pip compiles the bundled Python example and unfiltered source copying exported its cache. | Exclude Python cache directories/bytecode when copying syntax examples. Add a cache-contaminated fixture regression and require installed-wheel output to match all 356 baseline files exactly. |
| Medium | Canonical SESM safety checks inspect diagnostic strings as well as descriptive fields; internal identity evidence labels such as `source.run` trigger its command-authority rule. | Put internal identity-resolution diagnostics in the receipt. Embed compact exact identity and descriptive provenance; do not weaken the validator or change the standard. |

## Boundaries retained

Canonical 32 values/IDs, dark-only adaptation, hue families, fifteen target IDs, native fixed names, CM5/CM6/Markdown integration interfaces, version prefixes and manifest schema are preserved. The frozen PowerPoint reference and existing native packages remain under their original contracts.

No root relocation, broad directory migration, dependency upgrade, source deletion, archive retirement, theme activation, installation into target applications, or publication occurred. Direct project records and the read map are updated; parent manifests and the D-drive index need no change because identity, ownership, registration and physical roots remain the same.

## Tool classification

| Tools | Operational status |
| --- | --- |
| CLI generate/import/atlas/finish and converter scripts | Maintained operator entry points; writes require their documented explicit destinations/options |
| `check_stabilization.py` | Fresh generation/import fixture capture or comparison; refuses existing fixture destinations |
| `check_finishing.cjs` | Browser QA of a finishing receipt; writes only the explicitly selected evidence destination |
| `check_*`, `verify_*_package.py`, optional render helpers | Verification tooling; inspect each helper's dataset/output assumptions before reuse |
| `migrate.py`, `verify.py`, `governance.py` | Historical migration/governance workflows, not harmless checks; can overwrite outputs/records |
| PowerPoint metadata repair, normalization and vendor rebuild tools | Explicit maintenance operations that mutate their documented destinations; never run as general preflight |

## Evidence and remaining work

The acceptance record is [stabilization-2026-10-25.json](../evidence/stabilization-2026-10-25.json). It distinguishes fixture comparisons, regression tests, wheel verification, real SESM validation, browser rendering and unperformed gates.

The captured import and generation fixtures each contain 356 files across fifteen targets. Structural comparisons require zero changed paths/hashes. Four explicit local examples cover a logo, canonical palette, target swatch and an existing preview PNG; existing inputs/runs are hashed and remain unchanged.

VTracer was initially unavailable on PATH. The operator supplied a local executable; version 1.0.0-alpha.4 was confirmed, and an actual Ada-logo trace completed through the finishing command and canonical SESM validator. Offline Chromium verified path-based rendering and zero pixel changes from metadata insertion. The inspected original/trace comparison shows visible posterization and loss of fine texture with the existing defaults; it does not establish pixel fidelity or suitability for every logo. The exact binary hash, settings, measurements and comparison artifact are recorded in acceptance. Native SVG editor import remains unperformed. Individual output refinement remains operator-led follow-up work.
