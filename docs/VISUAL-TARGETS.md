# SVG, syntax highlighting and data visualization

Contract review: 2026-10-08, America/New_York. The three requested next targets are implemented. All derive dark outputs from the unchanged canonical 32 colors. No theme is installed, activated or published.

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

Three standalone 960×540 SVG files implement different compositions: `technical-flow.svg` uses orthogonal connectors and outlined nodes; `editorial-infographic.svg` uses a large numeral and typographic sections; `orbit-map.svg` uses a radial map. Geometry/text remain editable XML. RGB `fill`/`stroke` presentation attributes follow the [W3C SVG styling contract](https://www.w3.org/TR/SVG11/styling.html). There are no scripts, linked assets or required external fonts. Each file has an accessible title and description.

These are reusable examples rather than an editor-specific theme. Colors are recorded in `tokens.json`; edit attributes or import into an SVG editor. Browser rendering is checked separately. Illustrator, Inkscape, Office import, font substitution, printing and PDF conversion remain unverified. Diagram numbers use readable text tokens; decorative marks use 3:1 contrast against the panel.

## General syntax highlighting: Prism CSS

`prism.css` follows the [official Prism token classes](https://prismjs.com/tokens.html), mapping comments, punctuation, properties, tags, booleans, constants, symbols, numbers, selectors, attributes, builtins, classes, strings, characters, keywords, functions, regexes and inserted/deleted text. Classes intentionally share semantic tokens. Include this CSS after the host's base styles and use Prism language-marked `pre`/`code` markup with the appropriate grammar.

`syntax-example.html` embeds the exact CSS and authored JavaScript token spans for offline viewing. It checks appearance and token CSS, not language parsing. Prism JavaScript and grammars are not bundled or installed. Host overrides, plugins, grammar execution, large files, mixed languages and assistive-technology behavior require integration review. This is not a universal IDE format.

## Data visualization: Matplotlib style and scales

`<name>.mplstyle` follows the [official Matplotlib style-sheet/rcParams contract](https://matplotlib.org/stable/users/explain/customizing.html): figure/axes surfaces, text, ticks, borders, grids, legends and a six-entry color/line-style cycle. Load explicitly with `plt.style.use('path/to/name.mplstyle')` or a style context. Bare hex avoids the file format's `#` comment syntax.

`scales.json` is a separate pipeline artifact. Nine sequential stops share the primary source hue and increase OKLCH lightness. Pass these explicitly to `matplotlib.colors.ListedColormap`; the style does not install a colormap. `example-data.json` supplies illustrative values. `bars.svg`, `lines.svg` and `heatmap.svg` are dependency-free authored examples, separate from Matplotlib output.

Optional validation: `python tools/render_matplotlib_examples.py RUN [ISOLATED_DEPENDENCIES]`. This loads the style, asserts surface/cycle values and writes separate `matplotlib-bars`, `matplotlib-lines` and `matplotlib-heatmap` PNG/SVG files. Matplotlib is not an engine dependency. The measured pilot uses Matplotlib 3.11.2 in the isolated ignored `output/visual-validation-runtime` directory, with version/backend/diagnostics in `matplotlib-render-evidence.json`. No persistent style installation occurs.

Pair categorical colors with labels, shapes, hatching and line patterns because narrow palettes can alias. Text checks are 4.5:1; series/panel checks are 3:1. Sequential intensity stops intentionally do not guarantee 3:1 against the panel or adjacent stops. Heatmap values in the authored example appear outside the cells. No category-separation, perceptual-uniformity, color-vision simulation, APCA, statistical or interactive GUI acceptance is claimed.

## Progress and evidence

The user marked PowerPoint, Documentation/PDF, Alacritty, Notepad++, Sublime Text and Windows Terminal done. That planning status adds no application acceptance evidence. The three next items above now have local examples. Shell prompt, JetBrains, VS Code, Carbon, full website, React, WPF and WinUI remain future work; existing SiYuan/Typora adapters retain their earlier contracts. Duplicate plan rows refer to the same targets.

See [validation](VALIDATION.md), `migration/visual-target-acceptance.json` and the separate [pilot review](../pilot/visual-targets/review.html). Generator checks, browser previews, Matplotlib Agg renders and native editor import are distinct evidence gates. Parent/index registration needs no change because identity, ownership and discovery roots are unchanged.

The pilot's [offline visual gallery](../pilot/visual-targets/visual-examples.html) embeds all ten reviewed PNG previews. Seven authored examples passed Chromium text-bound/media/CSS checks; three actual Matplotlib Agg charts rendered separately. Browser evidence is in `pilot/visual-targets/browser-preview-evidence.json`. Reproduce browser checks with `node tools/render_visual_previews.cjs RUN PLAYWRIGHT_MODULE [CHROMIUM_EXECUTABLE]`, using an existing local browser/runtime. The gallery is a dated pilot artifact; generation writes target example indexes and the main report.
