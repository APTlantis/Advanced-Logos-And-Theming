# Full website theme

Target ID: `website`. Browser output contract: standard [CSS custom properties](https://www.w3.org/TR/css-variables-1/), scoped to `.apt-site`, and opt-in `.apt-*` component selectors. This is a reusable dark browser theme, not a framework adapter or a production website. Reference DOM and interactions are in the exported HTML specimens.

## Palette extension today

The current sequence is image extraction → **unchanged canonical 32** → semantic role references → target-specific adaptation → native output plus review artifacts. `apt_theme/targets.py` and `apt_theme/colors.py` implement adaptation. The old `legacy-tools/palette-transformer` is preserved independently; the active pipeline does not execute it or its website profile. Its numeric planning budget was retained, but its generic color-count expansion is not the new website contract.

Import an existing run's canonical `palette.toml` to assess another target without extracting the image again. Both import and image generation produce named target palettes, swatches, provenance, aliases and contrast checks. Lightness/chroma changes retain source hue, with gamut mapping and quantization recorded separately. Semantic role assignments can change between engine versions; importing preserves canonical values, not every historical mapping.

```powershell
.\Invoke-AptTheme.ps1 import output\dnf-D\palette.toml --output pilot\my-d-website --name Aptlantis-D --targets website --strict
.\Invoke-AptTheme.ps1 generate 'C:\path\logo.png' --output pilot\my-image-website --targets website --strict
```

Choose a fresh destination. The usual overwrite and non-pipeline-directory guards apply. Insufficient observed image colors still fail extraction; this exporter does not invent canonical colors to rescue an unsuitable image.

## Files and usage

| File | Contract |
| --- | --- |
| `website/theme.css` | Scoped colors, typography/layout and components; no external dependencies |
| `website/landing.html` | Responsive navigation, hero, cards, surfaces, footer and disclosures |
| `website/components.html` | Buttons and labeled states, forms, native dialog, messages, table, code and selection |
| `website/examples.html` | Neutral review index with findings and downloads |
| `website/README.md` | Integration and acceptance limits |
| `website/tokens.json`, `validation.json` | Actual named colors, origins, aliases and contrast pairs |
| `website/apt-<language>-website-palette.toml`, `apt-<language>-website-swatch.png` | Target palette and transformer-layout swatch |

Load `theme.css`; use `class="apt-site"` on the body or a containing element. Opt in with `apt-nav`, `apt-hero`, `apt-card`, `apt-input`, `apt-dialog`, `apt-table`, `apt-footer`, `apt-button apt-primary` / `apt-secondary`, and `apt-message apt-success` / `apt-warning` / `apt-error` / `apt-info`. Inputs are styled inside the namespace. `apt-muted`, `apt-text-<status>` and `apt-code-<role>` provide text treatments. The specimen HTML defines exact markup. Preview-only `data-state` attributes pin button states for comparison; ordinary controls use hover/active/disabled selectors. Demo forms prevent submission and save nothing. Dialogs use native `showModal()` and support Escape.

The default budget is **112 named tokens**; the current contract needs **89**: 22 shared roles, 28 surface roles, 24 action-state roles, 12 status-message roles and three link/focus roles. Every token has a CSS consumer. Budgets below 89 fail rather than dropping required states; larger budgets add no filler. Unique RGB counts are separate and depend on the source palette.

## Suitability and evidence limits

Review surface character, dominant accents, text hierarchy and repeated/aliased status hues. Missing conventional red/green/blue does not cause invented hue families. Status messages retain explicit labels. A valid export is not an aesthetic approval or a reason to keep every logo in every output family.

Checks cover opaque foreground/background pairs, surface text, labeled action states, status messages, links, focus and control boundaries. Current Chromium specimens additionally check actual visible text contrast, desktop/mobile overflow, dialog opening/Escape, focus outline, hover/pressed states, form behavior and offline requests. They do not establish production framework integration, screen-reader acceptance, color-vision safety, all native select popup states, or contrast after host CSS overrides/transparency. No application installation, activation or publication occurs.

Fresh comparison: [D, CoffeeScript and Assembly](../pilot/website-review-2026-10-09-v2/index.html). All three preserve canonical RGB/IDs and existing output bytes, have 89 named tokens and zero declared contrast failures. D and Assembly lack conventional success/info hues; CoffeeScript lacks a conventional info hue. Visual suitability remains operator review. Earlier pilot iterations remain preserved. Measured source/output hashes and browser checks: [acceptance record](../migration/website-target-acceptance-2026-10-09.json).

Reproduce the three-palette pilot with `python tools/review_website_palettes.py`; an existing destination is refused unless `--refresh` explicitly requests the guarded pipeline overwrite. Browser checks use `node tools/check_website_previews.cjs PLAYWRIGHT_MODULE CHROMIUM_EXECUTABLE`. Original output trees are hash-checked before and after import and never refreshed by this helper.
