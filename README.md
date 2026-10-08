# Logos-And-Theming

An image-to-theme pipeline and related logo utilities. Canonical palettes contain 32 observed colors. Semantic meaning and application adaptation are separate stages. Only dark themes are generated.

Project overview: [24-slide Black-Gold presentation](docs/presentations/Logos-And-Theming-Overview.pptx), with explanatory speaker notes. Further reading is planned in the [documentation suite plan](docs/documentation-suite/PLAN.md). Deck provenance and validation are in [presentations/README.md](docs/presentations/README.md).

## One command

Python 3.12+ and ImageMagick 7 are required for the locked environment (verified with Python 3.13). Run `Setup.ps1` once to create a local environment and install the engine. Activate `.venv\Scripts\Activate.ps1`, then:

```powershell
apt-theme generate assets\sources\apt-zig-dark-16bit-logo.tif --output output\zig-dark --name 'Aptlantis Zig Dark'
```

Without activation:

```powershell
.\Invoke-AptTheme.ps1 generate assets\sources\apt-zig-dark-16bit-logo.tif --output output\zig-dark
```

Default exports: Windows Terminal scheme JSON, SiYuan dark theme ZIP, Typora CSS, PowerPoint theme-color XML plus an editable four-slide sample deck, Alacritty TOML, Notepad++ XML and Sublime Text color-scheme JSON. New editor contracts, setup and acceptance limits are in [EDITOR-TARGETS.md](docs/EDITOR-TARGETS.md). Open `review.html` in a browser; it is self-contained and works offline. The preserved historical four-target example is [pilot/zig-dark/review.html](pilot/zig-dark/review.html).

Use `--targets windows_terminal,typora` for selected exports, `--config profiles.toml` for budgets/semantic overrides, `--compare PATH` to compare an existing 32-color palette, and `--strict` to fail on declared contrast failures. `--overwrite` replaces only a generated run or an empty output directory. Outputs never install or activate application themes.

```powershell
apt-theme import assets\references\Aptlantis-Black-Gold\palette.toml --output output\imported-zig
```

Imports preserve RGB values and original IDs; legacy role mappings remain in provenance while the new mapper assigns roles separately. Hex is authoritative when multiple representations are present. New canonical TOML contains colors without roles; `semantics.json` contains role references. Each target's `tokens.json` contains canonical sources, derivations, aliases, omissions and checks.

## Color choices

ImageMagick applies orientation and embedded ICC conversion to sRGB. The original input is copied and hashed. The export working space is 8-bit sRGB; the original 16-bit TIFF is retained. Sampling uses at most 65,536 visible pixels with a fixed seed, ignores fully transparent pixels, and weights partial opacity. Animated inputs use their first frame. Unprofiled CMYK is rejected; unprofiled RGB is treated as sRGB.

Population-weighted OKLab clustering creates up to 192 observed candidates. Canonical selection combines perceptual medoids, dark/light anchors, duplicate suppression and population-aware diversity. When at least 32 representatives remain, candidate colors whose 8-bit sRGB channels are all at most 12 are coalesced into one observed dark anchor with their combined population. This prevents tiny near-black channel changes from consuming several canonical slots. Sparse inputs retain their distinct colors. Near-duplicate medoids are replaced rather than occupying category quotas. Reports measure coverage over the actual sample, not every pixel and not human aesthetic quality.

Semantic assignment chooses hue suitability instead of positional accent IDs. Background selection is independent of the darkest/ANSI black anchor: by default it prefers an observed chromatic surface in OKLCH lightness .12–.32, near .20, with population and excessive saturation considered. Neutral dark surfaces serve grayscale palettes; no dark-range candidate produces a reported darkest-color fallback. Configure `[semantics] background_mode = "darkest"` to request the previous pipeline behavior, adjust `background_lightness` within .12–.32, or use an explicit `[overrides] background` ID. The choice and reason appear in `selection.json` and the report. Existing imported colors remain unchanged. Unavailable conventional status/ANSI hues and collisions are reported. Application adaptation adjusts lightness and chroma while preserving source hue. Gamut mapping reduces chroma at fixed lightness/hue. Final RGB quantization can slightly shift measured hue; requested OKLCH remains recorded. A narrow image palette can produce ANSI aliases; no unrelated hue is added.

Budgets are named token limits, not unique-color promises: Terminal 20, SiYuan 64, Typora 40, PowerPoint 24, Alacritty 20, Notepad++ 32, Sublime Text 40. Planning ranges are Alacritty 16–24, Notepad++ 24–40 and Sublime Text 32–56; required tokens set the actual minimum. Editor defaults currently emit 30 tokens, with reuse and no budget filler. Mandatory tokens cannot be dropped to satisfy an impossible budget. Tokens are reused across properties; aliases and counts below budget are intentional and visible. Checks use WCAG 2 contrast ratios: 4.5:1 text, 3:1 declared control boundaries/cursor. APCA and color-vision simulations are not implemented. Contrast evidence covers declared pairings, not every application's runtime state.

## Use the exports

- **Windows Terminal:** add the exported JSON object to `schemes` in settings, then choose its name. `black` is adjusted for readable text on a dark background. Missing magenta may alias an available image hue.
- **SiYuan:** extract `package.zip` into a theme folder beneath your workspace's `conf/appearance/themes`, then choose it in Appearance. Metadata targets SiYuan 3.7.0+ and dark mode only. Review native rendering before daily use.
- **Typora:** place the exported CSS in the folder opened by Preferences → Appearance → Open Theme Folder, restart Typora, then select the theme. The export styles content and common editor surfaces; platform-specific native controls may retain application styling.
- **PowerPoint:** open the generated `*-sample.pptx` to review typography, the 12 native color slots and an editable chart with illustrative data. The deck embeds the same scheme as the XML. To reuse the colors separately, copy the XML into `%APPDATA%\Microsoft\Templates\Document Themes\Theme Colors`, then select its named color scheme under Design → Variants → Colors. The XML supplies colors only; the sample deck uses Arial and simple 16:9 layouts. See [PowerPoint setup and acceptance](docs/POWERPOINT.md).

## Related utilities

```powershell
python scripts\Convert-to-ICO.py --input image.png --output icon.ico
python scripts\Convert-to-SVG.py --input image.png --output wrapped.svg
python scripts\Convert-to-SVG.py --input image.png --output traced.svg --mode trace --vtracer C:\path\vtracer.exe
python scripts\generate_atlas.py
```

Converters retain their existing options and collision checks; SVG defaults to embedded raster artwork. Tracing requires VTracer and never silently falls back. Atlas output belongs to `assets/palette-atlas.html`. Related conversion commands are independent of theme generation. SESM metadata embedding belongs to the sibling [SESM-Metadata-Embedder](../SESM-Metadata-Embedder/README.md).

## Verification and migration

Run `.venv\Scripts\python.exe -m unittest discover -s tests -v`. Migrated transformer tests remain under `legacy-tools/palette-transformer/tests`. Legacy exporters and older scripts are preserved for reference, not advertised as new pipeline targets.

See [validation](docs/VALIDATION.md), [command contract](docs/COMMAND-CONTRACT.md), and [migration/recovery](migration/README.md). Native application import and visual acceptance are separate from parsing, contrast, packaging and browser-report checks.
