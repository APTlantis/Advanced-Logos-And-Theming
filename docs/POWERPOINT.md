# PowerPoint colors and reusable template

Selecting `powerpoint` during generation or palette import emits:

- `<theme-name>.xml`: the twelve native Office color slots.
- `<theme-name>-sample.pptx`: all 23 slides of the supplied presentation, editable.
- `<theme-name>-template.potx`: a reusable PowerPoint template with the same slides and 14 custom layouts.
- `template-provenance.json`: source identity, hash, counts and changed package parts.

The original `aptlantis-clogure-template.pptx` is preserved byte-for-byte under `apt_theme/templates`, with its receipt in `provenance.json`. Its SHA-256 is `ff78bc0f960314d5301f3533a18fe65d1a45c6c24e4139ff84e52cc675b6595d`. Wheels and source distributions include this reference. The exporter rejects a missing or modified reference rather than silently substituting another design. Text inside the supplied deck remains template content, not instructions to the pipeline.

## Output contract

The native Open XML package preserves slide text, geometry, master/layout relationships, placeholders, notes, typography, tables, four charts and embedded XLSX workbooks. Placeholder copy and sample data remain illustrative. Picture placeholders remain empty until the operator adds pictures. The title placeholder is retained for reuse rather than filled with the theme name.

The exporter replaces the twelve theme color definitions with the existing generated token values, maps explicit black shadow colors to `dk1` and the pale chart border to `lt1`, and preserves alpha/effect transforms. Existing scheme references remain native bindings. The dark background/text color map stays intact. Canonical palette values and IDs do not change; no new hue families are introduced. Theme slot aliases are intentional.

POTX differs from PPTX only in the main presentation content type. Both preserve all supplied example slides so users can choose or duplicate examples as well as create slides from the custom layouts. The compatibility `-sample.pptx` filename remains stable. ZIP entry order and timestamps are fixed for deterministic regeneration. The original reference is never rewritten.

## Runtime and use

Generation uses Python's standard-library ZIP/XML handling. Node.js, `@oai/artifact-tool`, `APT_THEME_NODE` and `APT_THEME_ARTIFACT_TOOL` are no longer required or consulted by the PowerPoint exporter. The former JavaScript sample builder is retained as legacy source only. Separate historical documentation-deck authoring scripts still have their own JavaScript dependencies; they are not run by `apt-theme`.

Open the PPTX for review/editing, or open the POTX in PowerPoint to create a presentation from it. The offline review links to both files. Generation does not install a template into Office, activate a theme or publish outputs.

A fresh local review can be generated without overwriting earlier runs:

```powershell
.\Invoke-AptTheme.ps1 import output\clogure\palette.toml --output output\clogure-template-review --name 'Aptlantis Clogure' --targets powerpoint --strict
```

That palette is a local ignored file; on a fresh clone use your own palette/image or restore the preserved assets. All normal output collision safeguards and atomic run replacement remain in force.

## Acceptance and recovery

`migration/powerpoint-template-acceptance.json` records the 2026-10-09 checks. Structural preservation, deterministic generation, package inclusion, native opening/rendering and manual editing are separate gates. Native PowerPoint opening uses read-only mode with repair disabled. Import/render success does not establish manual chart editing, adding slides through every layout, or save/reopen acceptance. Those remain operator checks. The existing contrast checks cover declared generated token pairs, not every possible combination a user can compose within a layout.

Recover the reference from the original Downloads file or a verified package, checking its SHA-256 above. Regenerate into a fresh run directory. Earlier four-slide outputs, metadata backups, archives and dated acceptance records remain historical evidence and are not overwritten by this extension.

The earlier timestamp metadata repair is documented in `migration/powerpoint-metadata-repair.json`. `tools/repair_powerpoint_metadata.py` remains available for older copies and modifies only core metadata into a new destination. The template exporter preserves the supplied valid core metadata and namespace declarations without reserializing them.

No identity, ownership or discovery-root changes occurred; parent portfolio and drive navigation records need no update.
