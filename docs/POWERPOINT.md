# PowerPoint colors and sample deck

Selecting `powerpoint` in either generation or palette import emits the existing 12-slot Office color XML and `<theme-name>-sample.pptx`. The four slides contain a title, typography and link colors, an editable native color-slot table, and an editable six-series chart. Chart values are explicitly illustrative and stored in an embedded XLSX workbook. The theme slots match the XML; the canonical palette is unchanged. Reused accents remain visible as aliases rather than invented colors.

The sample uses Arial and a 1280×720 (16:9) canvas. Text, swatches and chart series reference native theme colors, including the followed-link slot. It is a review deck rather than a reusable slide-master template. Changing theme colors in PowerPoint updates the bound objects; the table's hexadecimal labels describe the original generation and do not recalculate automatically.

## Local runtime

Python orchestrates the export. JavaScript authoring uses Node.js and `@oai/artifact-tool` (validated locally with version 2.8.89). On this machine, the Codex bundled Node runtime under `%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node` is detected automatically. Bundled dependencies are not modified or installed by the pipeline.

For another runtime location, set `APT_THEME_NODE` to the Node executable and `APT_THEME_ARTIFACT_TOOL` to the absolute `dist/artifact_tool.mjs` entry point in an existing complete Artifact Tool installation, with its dependencies alongside it. The package is a private runtime dependency; Python setup does not download it. If unavailable, generation fails clearly before replacing an existing output. Targets selected without `powerpoint` continue to require only the original Python/ImageMagick dependencies.

Source distributions and wheels include the JavaScript builder. Same-environment regeneration normalizes ZIP timestamps, metadata, creation IDs and scoped relationship IDs for deterministic bytes. Determinism across different runtime versions is not promised.

## Review and recovery

The 2026-10-08 metadata repair fix prevents an invalid namespace reference in core timestamp types. `migration/powerpoint-metadata-repair.json` records native PowerPoint opening with repair explicitly disabled and rendered previews for six corrected workspace decks, plus a fresh exporter check. Slide, theme and embedded workbook bytes were unchanged during repair. Native chart editing and save/reopen remain separate checks.

Previously generated copies outside the project can be corrected into a new file:

```powershell
.\.venv\Scripts\python.exe tools\repair_powerpoint_metadata.py 'C:\path\old-sample.pptx' --output 'C:\path\corrected-sample.pptx'
```

This utility modifies only core metadata and refuses an existing output or the input path. Workspace originals repaired during this fix are preserved under `migration/powerpoint-metadata-backups`, with before/after hashes in the evidence record. Historical migration/sample acceptance records retain their original hashes and limited proof claims; the repair record supersedes the metadata hash for the corrected current decks. Historical `pilot/zig-dark` is retained unchanged and predates the fix.

Open the sample deck from the PowerPoint folder or from `review.html`. The color XML remains independently reusable using the README instructions. Before application acceptance, open the deck in PowerPoint, inspect all four slides, edit chart data, change an accent color, save a test copy and reopen it. Record this separately from structural validation and Artifact Tool rendering. No automatic installation or activation occurs.

The output-directory overwrite safeguards and atomic replacement remain in force. Regenerate using the preserved input and the existing launcher; recovery of the consolidated projects remains documented in `migration/README.md`. This extension does not change asset paths, portfolio ownership or the verified historical archives.
