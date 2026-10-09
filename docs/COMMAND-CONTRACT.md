# apt-theme command contract

Version: 0.1.0. Input: one image (`generate`) or 32-color TOML (`import`). Output: explicitly named directory.

Every selected target also emits `apt-<language>-<output-type>-palette.toml` and `apt-<language>-<output-type>-swatch.png` beside its native outputs. Names use the theme/input stem with the Aptlantis/apt prefix normalized, and the current target ID with hyphens. Both commands emit actual target token values, provenance and canonical/derived labels; the full canonical 32 remain independent. See [OUTPUT-REFERENCE.md](OUTPUT-REFERENCE.md) for the schema and examples. The review page links both files; existing runs require an explicit new generation to gain them.

## Invocation

`apt-theme {generate|import} INPUT --output DIRECTORY [--name NAME] [--targets windows_terminal,siyuan,typora,powerpoint,alacritty,notepad_plus_plus,sublime_text,svg,syntax_highlighting,data_visualization] [--config TOML] [--compare TOML] [--overwrite] [--strict] [--json]`

The `powerpoint` target writes `<slug>.xml` (12 Office color slots), `<slug>-sample.pptx` (the supplied 23 editable slides), `<slug>-template.potx` (the same slides and 14 layouts), and `template-provenance.json`. It adapts the hash-verified bundled reference using Python ZIP/XML handling, with no Node.js/Artifact Tool generation dependency. A missing or modified reference is a processing error (exit 1). Generation does not open or install it. See [POWERPOINT.md](POWERPOINT.md).

PowerShell launcher: `Invoke-AptTheme.ps1` forwards arguments and exit codes. `Setup.ps1` installs only a project-local environment. Generation never downloads dependencies or modifies installed themes.

## Streams and exit codes

Progress and errors use stderr. Human completion or the `--json` run summary uses stdout. Exit 0: generation completed, possibly with review findings. Exit 1: processing/input/configuration failure. Exit 2: strict-mode contrast failure after writing all completed artifacts. Argparse also uses 2 for invalid command syntax.

Machine output uses the CTS envelope (`status`, `tool`, `version`, `data`, `warnings`, `errors`). Its `data` summary schema is `aptlantis.theme-run.v1`, with name, variant, source SHA-256, targets, contrast-failure count, semantic findings and explicit native-acceptance/installation status. JSON stdout has no progress text. Processing failures also emit an error envelope when `--json` is selected.

## Outputs and compatibility

Canonical TOML uses `[theme]` and `[palette.canonical]`, with per-color hex, RGB, OKLCH and population weight. `semantics.json` is separate. Original source bytes and SHA-256 are retained. Application tokens and validation are JSON. The HTML report embeds artwork and needs no network connection.

The existing `syntax_highlighting` target now emits `prism.css`, twelve `syntax-<language>.html` pages, a themed `examples.html` index, bundled Prism 1.30.0 runtime/grammars/license/hash manifest under `vendor/prism`, and preserved examples under `sources`. `syntax-example.html` remains the JavaScript compatibility entry. Grammar execution occurs in the browser; generation needs no Node or network access. `tokens.json` lists the twelve primary example pages.

The existing `data_visualization` target retains its style, scales, SVG filenames and `example-data.json` value keys (`categories`, `bars`, `lines`, `heatmap`, `illustrative`). Added label/pattern metadata supports 12 bars, six 24-point lines and an 8×12 heatmap. `heatmap-values.html` supplies exact values. The optional Matplotlib renderer consumes the same data and writes separate PNG/SVG renders and evidence. Native import and host integration remain separate gates; see [visual contracts](VISUAL-TARGETS.md).

The existing `svg` target emits six 1200×800 compositions plus a themed offline gallery. The original `technical-flow.svg`, `editorial-infographic.svg` and `orbit-map.svg` names remain; `icon-sheet.svg`, `wayfinding-map.svg` and `product-illustration.svg` add broader vector uses. `tokens.json` lists all six examples. XML geometry, text, local symbols and presentation paints remain editable. CLI arguments, budgets and canonical palette contracts are unchanged.

TOML configuration accepts `[profiles]`, `[extraction]`, `[semantics]` and `[overrides]`. Semantic settings are `background_mode = "identity"` (default) or `"darkest"`, and `background_lightness = 0.20` (range .12–.32). Explicit background overrides take precedence and participate in foreground/secondary-text mapping. Canonical selection coalesces the near-black sRGB noise floor when enough observed alternatives remain. Imports preserve the supplied canonical values. Re-generation can change canonical IDs; review ID-based overrides when changing images or selection versions. Existing outputs are not automatically rewritten.

The new canonical format does not masquerade as the old language-template format with positional semantic sections. Import accepts the old grouped palette structure, UTF-8 BOM, hex/RGB/OKLCH representations and references; exactly 32 entries are required. Hex is authoritative. Legacy scripts and their original contracts remain archived.

## Write behavior and recovery

Existing directories require `--overwrite`; non-pipeline nonempty directories are rejected. The source cannot live under the output. Build in a sibling staging directory, then replace the completed run. A failed replacement restores the previous output. No partial artifacts are published on processing failure. The previous generated run is removed after successful replacement; retain revisions with different output directories.

## Examples

`apt-theme generate logo.tif --output output/dark --strict`

`apt-theme import palette.toml --output output/import --targets windows_terminal --json`

`apt-theme generate logo.tif --output output/review --compare previous.toml --config profiles.toml`

Editor contracts are in [EDITOR-TARGETS.md](EDITOR-TARGETS.md). SVG/Prism/Matplotlib contracts, examples, budgets and acceptance limits are in [VISUAL-TARGETS.md](VISUAL-TARGETS.md). All ten targets are generated by default. Matplotlib is needed only for the optional validation renderer, never during generation.
