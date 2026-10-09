# SVG, syntax highlighting and data visualization

SVG gallery environment: the page, cards, text, links and focus outlines use fixed neutral colors independent of every theme. Palette-derived backgrounds remain inside the SVG compositions. Surrounding pages may use any background. Fresh preview: [neutral SVG gallery](../pilot/svg-neutral-gallery-2026-10-09/svg/examples.html). Earlier galleries remain historical previews.

Structured-data galleries and heatmap value tables also use fixed neutral charcoal (`#181a1d`) with neutral text, links and borders. Chart SVG canvases, Matplotlib styles, tokens and canonical colors retain the exported theme. Future runs generate this viewing environment; the twelve galleries linked from the current output index received a CSS-only refresh with originals preserved under `migration/chart-gallery-backups/2026-10-09`. Evidence and rollback paths: `migration/chart-neutral-gallery-2026-10-09.json`. Fresh preview: [neutral chart gallery](../pilot/chart-neutral-gallery-2026-10-09/data_visualization/examples.html).

Contract review: 2026-10-09, America/New_York. The three visual targets derive dark outputs from the unchanged canonical 32 colors. The syntax/chart quality pass adds actual offline Prism grammars and richer shared chart fixtures. Fresh local evidence: `migration/visual-quality-acceptance-2026-10-09.json`. Earlier pilots remain dated evidence. No theme is installed, activated or published by this pass.

| Target ID | Recommended budget | Planning range | Required tokens | Default emitted |
| --- | ---: | ---: | ---: | ---: |
| `svg` | 40 | 32–56 | 28 | 28 |
| `syntax_highlighting` | 32 | 24–48 | 22 | 30 |
| `data_visualization` | 48 | 32–64 | 37 | 37 |

Budgets limit named tokens, not unique colors. There is no filler. SVG adds six mark colors to the shared 22-token surface/text set; data visualization also adds nine single-hue sequential stops. Syntax adds up to eight optional semantic variants with base-role fallbacks at lower budgets. The 32-token low end of the data planning range cannot retain its 37 mandatory tokens and is rejected. Optional colors may alias; series are not guaranteed to be perceptually distinct.

```powershell
.\Invoke-AptTheme.ps1 import pilot\editor-targets\palette.toml --output output\my-visuals --name 'My Visuals' --targets svg,syntax_highlighting,data_visualization --strict
```

Use `generate` with an image for a newly extracted palette. Import preserves existing RGB values and IDs. Every target has `tokens.json`, `validation.json` and an `examples.html` index; the main offline report links to these examples. Generate into a fresh directory. Explicit overwrite guards still apply, and historical runs and recovery archives remain preserved.

## SVG diagrams and infographics

Six standalone **1200×800** SVG compositions now exercise uses beyond charts. The earlier three filenames are retained:

| File | Use and detail |
| --- | --- |
| `technical-flow.svg` | Architecture/runbooks: three swimlanes, nine nodes, arrowheads, a review decision and revision loop |
| `editorial-infographic.svg` | Posters/explainers: large typography, conceptual palette tiles, three sections and supporting callouts |
| `orbit-map.svg` | Relationships/taxonomies: six target families, curved connectors, concentric guides, satellite marks and legend |
| `icon-sheet.svg` | UI/document assets: twelve reusable local symbols, 16/24/32-pixel demonstrations and three surface treatments |
| `wayfinding-map.svg` | Schematic campus/floor-plan guides: eight landmarks, two patterned routes, numbered steps, textured grid and orientation |
| `product-illustration.svg` | Feature artwork: layered device scene, clipped application surface, floating artifacts and same-token tonal glow |

Geometry and text remain editable XML in named groups. RGB presentation attributes, gradient stops and pattern paints use the existing exported tokens; budgets and canonical 32 colors are unchanged. Conceptual swatch tiles repeat the six mark tokens and do not represent actual canonical RGB values. The wayfinding layout is fictional and not to scale. The product scene is an illustration, not a functioning UI.

Files follow the [W3C SVG styling contract](https://www.w3.org/TR/SVG11/styling.html). Local `<symbol>`/`<use>` references, paths, markers, patterns, clips and a single-color opacity gradient require no scripts, raster images, remote resources or external fonts. Icons use inherited presentation strokes; symbol IDs are documented in the sheet. Each SVG has an accessible root title/description. The themed `examples.html` gallery embeds all six compositions, offers byte-preserving offline downloads and contains horizontal scrolling on narrow screens. The chart SVG canvas stays 960×540.

These are reusable examples rather than an editor-specific theme. Colors are recorded in `tokens.json`; edit attributes or import into an SVG editor. Browser rendering is checked separately. Illustrator, Inkscape, Office import, font substitution, printing and PDF conversion remain unverified; preservation of symbols, clips, patterns and gradients varies by importer. Body text uses readable text tokens; large decorative numerals/marks use the existing series tokens. Subtle guide lines, textures and gradient opacity are decorative and do not add contrast guarantees.

Fresh local SVG pilot: [gallery](../pilot/svg-quality-2026-10-09/svg/examples.html), [palette/token review](../pilot/svg-quality-2026-10-09/review.html), and `migration/svg-quality-acceptance-2026-10-09.json`. XML/local-reference/paint-provenance tests and offline Chromium previews are separate from native editor import. Earlier pilots and hosted outputs remain unchanged.

## General syntax highlighting: Prism CSS

`prism.css` follows the [official Prism token classes](https://prismjs.com/tokens.html), mapping comments, punctuation, properties, tags, booleans, constants, symbols, numbers, selectors, attributes, builtins, classes, strings, characters, keywords, functions, regexes and inserted/deleted text. Classes intentionally share semantic tokens. Include this CSS after the host's base styles and use Prism language-marked `pre`/`code` markup with the appropriate grammar.

Prism **1.30.0** core and grammars are bundled in `vendor/prism`, including the required C and C-like dependencies. Twelve substantial source examples cover JavaScript, TypeScript, Python, C#, C++, HTML (Prism `markup`), CSS, JSON, SQL, Bash, PowerShell and TOML. `examples.html` links to individual `syntax-<language>.html` pages; `syntax-example.html` remains a byte-identical JavaScript compatibility entry. Pages escape source text before local grammar execution, preserve readable source when JavaScript is disabled, and never execute the sample code. Each page offers previous/next navigation and a source download that retains the exact source bytes, including when opened through `file://`.

`prism.css` remains usable independently. To use the bundled runtime, load core followed by the grammars in `vendor/prism/manifest.json` order and apply the generated CSS. Examples additionally use `examples.css` for their layout. Vendor records include the upstream tag URLs, SHA-256 values and MIT license. Generation verifies those hashes, copies local assets and needs neither network nor Node. Maintainer-only acquisition: `python tools/vendor_prism.py`; review any vendor update deliberately. Python wheels include both vendor files and source examples.

The fresh pilot passed actual Chromium grammar execution, representative computed token colors, preserved source text, download hashes, keyboard navigation, 390-pixel layouts, and zero HTTP/HTTPS requests or browser errors. HTML includes embedded CSS and JavaScript grammar coverage. Git attributes disable newline conversion for pinned vendor assets, example sources and this dated pilot so recorded hashes survive Windows checkouts. Host overrides, plugins, large/untrusted files and assistive-technology behavior still require integration review. This is not a universal IDE format, and illustrative snippets are not application integration tests.

## Data visualization: Matplotlib style and scales

`<name>.mplstyle` follows the [official Matplotlib style-sheet/rcParams contract](https://matplotlib.org/stable/users/explain/customizing.html): figure/axes surfaces, text, ticks, borders, grids, legends and a six-entry color/line-style cycle. Load explicitly with `plt.style.use('path/to/name.mplstyle')` or a style context. Bare hex avoids the file format's `#` comment syntax.

`scales.json` is a separate pipeline artifact. Nine sequential stops share the primary source hue and increase OKLCH lightness. Pass these explicitly to `matplotlib.colors.ListedColormap`; the style does not install a colormap. `example-data.json` supplies deterministic illustrative values: **12 bars**, **six lines with 24 weekly points each**, and an **8×12 monthly heatmap**. Existing value keys remain; added metadata supplies category/period/region names, markers, patterns and units. The SVG and optional Matplotlib renderers consume the same fixture. `bars.svg`, `lines.svg` and `heatmap.svg` remain dependency-free authored examples, separate from Matplotlib output.

Bars start at zero and have direct values and repeating six-pattern hatches. Lines have six marker/pattern combinations and a legend. Heatmap cells use one ordered hue, row/column labels and a labeled scale; `heatmap-values.html` supplies all 96 values in an accessible table. SVG cell titles also identify values. The themed chart index embeds the three authored examples with contained scrolling on narrow screens. The Matplotlib line legend sits outside the plot. The renderer retains fallback labels for older runs without the added metadata.

Optional validation: `python tools/render_matplotlib_examples.py RUN [ISOLATED_DEPENDENCIES]`. This loads the style, asserts surface/cycle values and writes separate `matplotlib-bars`, `matplotlib-lines` and `matplotlib-heatmap` PNG/SVG files. Matplotlib is not an engine dependency. The measured pilot uses Matplotlib 3.11.2 in the isolated ignored `output/visual-validation-runtime` directory, with version/backend/diagnostics in `matplotlib-render-evidence.json`. No persistent style installation occurs.

Pair categorical colors with labels, shapes, hatching and line patterns because narrow palettes can alias. Text checks are 4.5:1; series/panel checks are 3:1. Sequential intensity stops intentionally do not guarantee 3:1 against the panel or adjacent stops. Heatmap values appear in the separate table, not as low-contrast text over cells. No category-separation, perceptual-uniformity, color-vision simulation, APCA, statistical or interactive GUI acceptance is claimed.

## Progress and evidence

Current local quality pilot: [review](../pilot/visual-quality-2026-10-09/review.html), [syntax gallery](../pilot/visual-quality-2026-10-09/syntax_highlighting/examples.html), [chart gallery](../pilot/visual-quality-2026-10-09/data_visualization/examples.html), and [render gallery](../pilot/visual-quality-2026-10-09/visual-examples.html). All 26 focused tests passed; Chromium checked 15 examples offline; Matplotlib Agg checked the plotted values and rendered six artifacts without diagnostics. All 31 wheel resources matched source hashes and isolated installed-wheel generation passed. Commands and hashes are in the new acceptance record. These results do not update any hosted theme folders or establish native editor acceptance.

The user marked PowerPoint, Documentation/PDF, Alacritty, Notepad++, Sublime Text and Windows Terminal done. That planning status adds no application acceptance evidence. The three next items above now have local examples. Shell prompt, JetBrains, VS Code, Carbon, full website, React, WPF and WinUI remain future work; existing SiYuan/Typora adapters retain their earlier contracts. Duplicate plan rows refer to the same targets.

See [validation](VALIDATION.md), `migration/visual-target-acceptance.json` and the separate [pilot review](../pilot/visual-targets/review.html). Generator checks, browser previews, Matplotlib Agg renders and native editor import are distinct evidence gates. Parent/index registration needs no change because identity, ownership and discovery roots are unchanged.

The pilot's [offline visual gallery](../pilot/visual-targets/visual-examples.html) embeds all ten reviewed PNG previews. Seven authored examples passed Chromium text-bound/media/CSS checks; three actual Matplotlib Agg charts rendered separately. Browser evidence is in `pilot/visual-targets/browser-preview-evidence.json`. Reproduce browser checks with `node tools/render_visual_previews.cjs RUN PLAYWRIGHT_MODULE [CHROMIUM_EXECUTABLE]`, using an existing local browser/runtime. The gallery is a dated pilot artifact; generation writes target example indexes and the main report.
