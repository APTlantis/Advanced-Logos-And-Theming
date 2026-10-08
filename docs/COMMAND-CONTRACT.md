# apt-theme command contract

Version: 0.1.0. Input: one image (`generate`) or 32-color TOML (`import`). Output: explicitly named directory.

## Invocation

`apt-theme {generate|import} INPUT --output DIRECTORY [--name NAME] [--targets windows_terminal,siyuan,typora,powerpoint] [--config TOML] [--compare TOML] [--overwrite] [--strict] [--json]`

PowerShell launcher: `Invoke-AptTheme.ps1` forwards arguments and exit codes. `Setup.ps1` installs only a project-local environment. Generation never downloads dependencies or modifies installed themes.

## Streams and exit codes

Progress and errors use stderr. Human completion or the `--json` run summary uses stdout. Exit 0: generation completed, possibly with review findings. Exit 1: processing/input/configuration failure. Exit 2: strict-mode contrast failure after writing all completed artifacts. Argparse also uses 2 for invalid command syntax.

Machine output uses the CTS envelope (`status`, `tool`, `version`, `data`, `warnings`, `errors`). Its `data` summary schema is `aptlantis.theme-run.v1`, with name, variant, source SHA-256, targets, contrast-failure count, semantic findings and explicit native-acceptance/installation status. JSON stdout has no progress text. Processing failures also emit an error envelope when `--json` is selected.

## Outputs and compatibility

Canonical TOML uses `[theme]` and `[palette.canonical]`, with per-color hex, RGB, OKLCH and population weight. `semantics.json` is separate. Original source bytes and SHA-256 are retained. Application tokens and validation are JSON. The HTML report embeds artwork and needs no network connection.

The new canonical format does not masquerade as the old language-template format with positional semantic sections. Import accepts the old grouped palette structure, UTF-8 BOM, hex/RGB/OKLCH representations and references; exactly 32 entries are required. Hex is authoritative. Legacy scripts and their original contracts remain archived.

## Write behavior and recovery

Existing directories require `--overwrite`; non-pipeline nonempty directories are rejected. The source cannot live under the output. Build in a sibling staging directory, then replace the completed run. A failed replacement restores the previous output. No partial artifacts are published on processing failure. The previous generated run is removed after successful replacement; retain revisions with different output directories.

## Examples

`apt-theme generate logo.tif --output output/dark --strict`

`apt-theme import palette.toml --output output/import --targets windows_terminal --json`

`apt-theme generate logo.tif --output output/review --compare previous.toml --config profiles.toml`
