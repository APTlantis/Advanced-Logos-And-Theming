# Changelog

## 2026-10-11 — Typora Markdown refinement

- Separated Typora CSS from SiYuan, adding striped tables and common Markdown structure styling without changing token colors or budgets.
- Added paired offline Markdown/browser specimens with tall/wide tables, packaged in the Python exporter.
- All 35 focused tests, three browser viewport checks and isolated wheel generation passed. Original Black-Gold output hashes and SiYuan CSS remain unchanged. Native Typora acceptance is pending; print/PDF is deferred.

## 2026-10-10 — Evaluator preparation

- Added the WGS/PPS `PROJECT-READMAP.toml`, with four mandatory records and source/test/evidence priorities within a 25-file budget; wired discovery through the manifest, agent instructions and overview.
- Reconciled current documentation to eleven targets and 32 test methods while preserving dated acceptance records, the overview deck and Writerside snapshot. Added `docs/EVALUATOR-START.md` and fresh preflight evidence.
- Existing 2026-10-09 extensions include bundled PowerPoint templates, offline Prism/chart/SVG examples, per-target palettes/swatches and scoped website CSS. Their individual contracts and dated evidence are indexed in the current README and validation guide.
- This preparation changes documentation only; it does not install, activate, regenerate hosted outputs, commit, publish or mark a release ready.

## 2026-10-08 — Terminal and editor exporters

- Added Alacritty TOML, Notepad++ XML (globals and Python/C++/JSON lexers) and Sublime Text 4 color-scheme JSON to default generation.
- Added native parsing and canonical-preservation coverage; documented budgets and application acceptance limits in docs/EDITOR-TARGETS.md. Native loading and rendering remain pending.


## 2026-10-08 — PowerPoint repair warning

- Fixed an undeclared `dcterms` prefix in the core timestamp `xsi:type` values created during deterministic metadata normalization. Added a dedicated QName validation check because slide/package schema checks did not catch it.
- Verified the original Clogure deck fails native PowerPoint opening with repair disabled; corrected and freshly generated decks open normally. Six current workspace decks were repaired with backups; only `docProps/core.xml` changed.
- Added `tools/repair_powerpoint_metadata.py` for corrected copies of previously generated decks without overwriting inputs. Native evidence is in `migration/powerpoint-metadata-repair.json`.

## 2026-10-08 — Dark-surface regression

- Removed the automatic darkest-color application background. Default mapping now selects an image-derived dark chromatic surface, with neutral/fallback behavior and explicit configuration.
- Coalesced redundant near-black candidate representatives before canonical selection when 32 observed alternatives remain. Preserved original candidate data and imported palette values.
- Added regression coverage for noisy near-black candidates, sparse grayscale palettes, background overrides and darkest-policy opt-in. Preserved the previous Zig output and generated a separate comparison run.

## 2026-10-08 — PowerPoint sample deck

- PowerPoint generation and palette import now emit an editable four-slide PPTX alongside the color XML, with native theme bindings, a color-slot table and an embedded chart workbook containing illustrative data.
- Included the deck in deterministic output checks and linked it from the local review report. Documented the Node.js/Artifact Tool runtime and separate native PowerPoint acceptance gate.

## 0.1.0 — 2026-10-08

- Added observed-color canonical selection, separate semantics, hue-preserving target adaptation and offline review.
- Added Windows Terminal, SiYuan, Typora and PowerPoint color exports with provenance and declared contrast checks.
- Consolidated artwork and conversion utilities; split SESM into its own project.
- Preserved old source trees in fully restored/hash-verified archives before retirement.
