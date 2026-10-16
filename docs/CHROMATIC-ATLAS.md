# Chromatic Atlas local pilot

Source reviewed 2026-10-16. A standalone read-only view of existing Logos-And-Theming runs, separate from the legacy `scripts/generate_atlas.py` asset gallery. This pilot adds a collection-level `atlas` command; it does not add a theme target, regenerate themes, edit canonical palettes or publish assets.

## Generate and open

```powershell
.venv/Scripts/python.exe -m apt_theme.cli atlas output --output pilot/chromatic-atlas-new
```

By default immediate `apt-*` and `dnf-*` child runs are included. Both families retain their physical directory names in the workspace. Use `--include apt-BlackGold apt-Ada` for an explicit smaller collection. Each selected run must have a dark pipeline `run.json` and a 32-entry canonical `palette.toml`. Missing semantic assignments or declared target JSON files produce visible snapshot findings; malformed identities, RGB disagreements and unresolved origins reject the snapshot. Unknown target usage is not invented.

Open the generated `index.html` directly. All CSS, JavaScript and the normalized dataset are packaged locally; there are no external fonts, libraries, APIs or CDN requests. `atlas-data.js` contains the same data as `atlas.json` to support direct file opening. Alternatively, serve only the generated directory on loopback:

```powershell
.venv/Scripts/python.exe -m http.server 8127 --bind 127.0.0.1 --directory pilot/chromatic-atlas-new
```

Existing output requires `--overwrite`, and only an atlas-owned directory can be replaced. Source collection/ancestor/descendant overlap is rejected. A failed build leaves an existing snapshot intact. Refresh is explicit; the browser never reads the source collection or writes changes back to it.

## Workspace and interaction

The desktop explorer, main canvas and collapsible inspector follow the supplied ColorBoard concept. Smaller layouts stack the panels. The selection tray remains separate from canonical data.

- **Matrix:** all 32 canonical source IDs per palette, optional readable HEX labels, canonical/lightness/hue ordering, palette/semantic/HEX search, hue families and lightness/chroma limits.
- **Color space:** OKLab a × b and hue × lightness projections, keyboard-selectable points and the same selected IDs as the matrix. Overlapping coordinates are not jittered, so close/identical coordinates can overlap. The matrix and inspector remain available for exact identity selection.
- **Inspector:** exact canonical HEX/RGB/slot, computed OKLCH/OKLab, source receipt, recorded semantic assignments and exported-token descendants. Selecting a token shows actual/requested coordinates, gamut-mapping flag, origin and source hash.
- **Collection:** click selects, Ctrl/Command-click toggles colors across palettes and Shift-click selects the displayed range. Inspecting a tray item preserves the collection. Copy individual HEX or the collection list, or download a separate JSON selection. No browser storage or canonical editing is performed.

Nearest-neighbor values use Euclidean distance in all three OKLab coordinates, unscaled. The a × b projection omits lightness and must not be interpreted as full 3D distance. Hue/lightness projection omits colors below C = 0.02; those colors are labeled near-neutral instead of being assigned an artificial red hue. That threshold is an explicit display convention, not a color-science classification standard. Hue-only filters exclude near-neutral colors. Neighbors search the complete snapshot independently of filters and may include identical RGB values from different palettes.

Canonical slots are source identities, not cross-palette semantic equivalents. Exported token counts vary by target. Recorded token lineage is not proof of native selector/property consumption or downstream application acceptance. The app does not imply that sparse color-space regions should be filled by altering an existing palette.

## Data contract

`aptlantis.chromatic-atlas.v1` links separate `themes`, `canonical`, `tokens` and `sources` arrays. Canonical IDs combine the source run directory and original slot; token IDs add target and key. Tokens refer to `canonical_id`. Canonical values retain stored RGB/HEX, original recorded OKLCH and computed coordinates from the existing color engine. The `hue_defined` display flag uses the 0.02 chroma threshold.

Every read source includes its collection-relative path, kind and SHA-256. Source bytes are checked again before publishing the local snapshot. Source paths are provenance labels, not browser fetch endpoints. Snapshot findings are data-availability limits. The fixed snapshot does not claim currentness after source files change.

Temporary collection downloads use `aptlantis.atlas-selection.v1`, with selected canonical records and source snapshot schema. They do not replace a pipeline palette file. Dataset and selection JSON preserve exact canonical identities; rounded coordinates shown in the inspector are display values.

## Pilot evidence and boundaries

The dated pilot uses 19 runs (13 `apt-*`, six `dnf-*`), 608 canonical colors, 10,583 exported tokens and 342 hashed data source files. [Local snapshot](../pilot/chromatic-atlas-2026-10-16/index.html). [Acceptance evidence](../migration/chromatic-atlas-collection-acceptance-2026-10-16.json).

Nine exporter/CLI tests cover source identity, lineage, hashes, deterministic output, offline data forms, missing-data findings, malformed provenance, overwrite/recovery boundaries and safe inline serialization. The browser checker exercises real matrix/plot interactions, source inspection, nearest-neighbor calculations, copy/export, filters, selection persistence, desktop/mobile layout and direct file opening. Installed-wheel generation is checked with network and child processes blocked.

Reference inputs: `C:/Users/Administrator/Desktop/ColorBoard.md` and the supplied `chromatic-atlas.png`, `selected-color.png`, `workspace.png` screenshots. Their proposed interactions informed this bounded pilot; sample screenshot colors and slot assignments do not replace pipeline data. Full comparison dashboards, graph exploration, pan/zoom, saved evaluations and quality-laboratory features remain later work. Existing output assets, legacy atlas, public hosting, theme installation and activation remain outside this pilot.

## Complete collection and offline examples - 2026-10-16

The current local snapshot includes exactly these source run directories:

| Apt family | DNF family |
| --- | --- |
| apt-Ada | dnf-Ada |
| apt-BlackGold | dnf-Assembly |
| apt-Clojure | dnf-Julia |
| apt-CoffeeScript | dnf-QBasic |
| apt-Crystal | dnf-Scratch |
| apt-D | dnf-Zig |
| apt-Erlang | |
| apt-Factor | |
| apt-Nim | |
| apt-R | |
| apt-Racket | |
| apt-Spark | |
| apt-Swift | |

All 19 runs declare fifteen targets, including Markdown/GFM and CodeMirror 5/6. The inspector's **Examples** tab opens copied local previews: 171 entries across nine targets per theme. Native-format targets without browser examples retain their existing integration contracts. The Atlas keeps both Ada runs separate; physical `apt-Clojure` remains visible even where original metadata says `Clogure`. Metadata labels are retained in the snapshot and source files are unchanged.

Copies preserve complete target directories and their local dependencies. `examples-manifest.json` records each copied source path, local path and SHA-256 (5,548 files in this snapshot). Source files are checked after copying. The Atlas itself works via direct file opening. CodeMirror 6's ES-module example needs a local HTTP server serving this generated Atlas directory. No public hosting change is required.

The Markdown example uses the existing GFM-capable parser, sanitizer and Prism assets. Its coverage manifest distinguishes baseline GFM, conditional HTML structures and deferred math/Mermaid integrations; no complete GitHub-renderer conformance claim is added. Generated examples are copied, not regenerated.

The original 13-theme pilot is preserved at `pilot/chromatic-atlas-initial-2026-10-16`. The existing `pilot/chromatic-atlas-2026-10-16/index.html` link now opens the complete collection. Initial acceptance/browser records retain their historical 13-theme scope; the collection acceptance record supersedes them for the current snapshot. The full suite now has 53 methods.
