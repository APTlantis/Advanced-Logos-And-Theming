# Changelog

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
