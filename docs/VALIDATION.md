# Validation and evidence limits

Date: 2026-10-08, America/New_York.

Alacritty, Notepad++ and Sublime Text exporters are covered by the 20-test focused pipeline/converter suite, including native TOML/XML/JSON parsing, canonical immutability and deterministic default regeneration with all seven targets. Tests passed outside the Windows sandbox after sandbox filesystem restrictions blocked temporary path resolution. See `migration/editor-target-acceptance.json` and [editor contracts](EDITOR-TARGETS.md). Native loading, installation and rendering of these three targets remain pending; existing pilot and historical acceptance records remain unchanged.

PowerPoint's reported repair warning was reproduced in native PowerPoint with repair disabled. The malformed timestamp QName in `docProps/core.xml` was corrected without changing slide, theme or workbook parts. All six repaired current decks and a fresh exporter run opened and rendered in native PowerPoint without repair, retaining four slides, one table and one chart. See `migration/powerpoint-metadata-repair.json`. This extends the earlier static evidence; chart editing/save/reopen and application installation remain unverified.

The dark-surface regression fix is recorded in `migration/dark-surface-regression.json`. The prior `pilot/zig-dark` output remains intact; `pilot/zig-surface-fix` contains a separate corrected run with its previous canonical palette as the comparison. Canonical palette changes apply only on new image generation; importing an existing palette preserves its colors while applying the revised background mapping. Existing output collections require explicit regeneration. Coverage scores may worsen when redundant near-black shades are removed; they are not an aesthetic ranking.

The pilot source is the preserved `assets/sources/apt-zig-dark-16bit-logo.tif`. Its comparison palette is `assets/references/Aptlantis-Black-Gold/palette.toml`. Native files, reports and source hashes are in `pilot/zig-dark`.

Focused tests cover observed-color selection, NumPy/ColorAide conversion agreement, opacity handling, monochrome and insufficient-color inputs, hue-preserving gamut mapping, semantic overrides, target budgets, canonical immutability, import, deterministic regeneration, strict-mode findings, overwrite safeguards, JSON/XML/CSS parsing and SiYuan package contents. Converter tests cover ICO frames, SVG dimensions/raster preservation, collision safety and explicit tracing. Tracing integration is exercised with a stub; actual VTracer tracing remains unverified.

The separate SESM suite covers preview, config precedence, schema errors, preservation outside metadata and replacement/duplicate handling. The canonical safe-profile validator is a separate gate. Migration archives are restored completely and hashes checked for every file, including Git history and differing source versions.

`migration/acceptance.json` records final commands and results. Passing static and browser-report checks does not prove native application import, installation, application rendering, marketplace acceptance or release readiness. No themes are installed or published by this work.

The later PowerPoint sample-deck extension is recorded separately in `migration/powerpoint-sample-acceptance.json`. Tests compare embedded theme values against the standalone XML, check four slides, native table and chart objects, workbook cells, scheme references and deterministic deck bytes. The skill's package/layout/chart-workbook/font validators and Artifact Tool import/render review are separate from opening and editing the deck in native PowerPoint, which remains pending. Historical migration evidence is preserved.
