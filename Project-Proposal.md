# Logos-And-Theming proposal

The 2026-10-09 documentation extension inventories every current target, generated artifact and construction path in [the output reference](docs/OUTPUT-REFERENCE.md), and explains the 29-method suite, runtime/native gates and prioritized future tests in [the testing reference](docs/TESTING-REFERENCE.md). It changes documentation and navigation only; historical evidence, product contracts and hosted outputs remain preserved.

The SVG quality extension broadens the existing target's examples to six detailed 1200×800 editable vector compositions: workflow, editorial infographic, relationship map, icon sheet, wayfinding map and product illustration. It retains existing filenames and color budgets, using local symbols, paths, patterns, clipping and a same-token tonal gradient. Native editor import remains a separate gate; current evidence: `migration/svg-quality-acceptance-2026-10-09.json`.

The 2026-10-09 quality pass strengthens the existing syntax and chart targets: bundled offline Prism 1.30.0 for twelve languages and deterministic 12-bar, 6×24-line and 8×12-heatmap examples shared with the optional Matplotlib renderer. Canonical 32-color identity and target budgets are unchanged. Fresh local evidence is in `migration/visual-quality-acceptance-2026-10-09.json`; no hosted outputs or installation state were changed.

The 2026-10-08 visual-target extension adds SVG presentation-attribute examples, Prism CSS and a Matplotlib style with explicit sequential scales. There are now ten default targets. Examples are illustrative; static, browser and Matplotlib Agg evidence are separate from native editor integration. See docs/VISUAL-TARGETS.md and migration/visual-target-acceptance.json.

Owner: Herb. Date: 2026-10-08. State: implemented local pilot.

## Problem and intended result

Separate tools had mixed image selection, fixed semantic meanings and application mappings. A cyan warning in the supplied Zig palette exposed positional semantic assignment. Consolidate the image-to-theme workflow and related small logo utilities while independently governing SESM metadata editing.

## Design and boundaries

ImageMagick normalizes images; NumPy/scikit-learn select observed colors in OKLab; ColorAide supplies color math. A canonical 32-color palette is independent of semantic meaning. Application adapters preserve hue identity, report missing conventional hues and derive readable states through lightness/chroma adjustment. One command emits ten target formats and an offline report.

Dark modes only. No new hue families, automatic application installation, public deployment, marketplace publication or exporters without documented native contracts. PowerPoint emits a reusable 12-slot color XML, a 23-slide editable preview and a POTX template with 14 native layouts, using the user-supplied template preserved on 2026-10-09. Generation uses Python Open XML adaptation and no Node/Codex runtime. ICO/SVG conversion and atlas remain explicit utilities. SESM metadata belongs to the sibling project.

## Acceptance and recovery

Use the source TIFF/Black-Gold reference, deterministic palette/output checks, actual exported contrast pairs, native-format parsing, converter preservation and separate metadata validation. Archive and completely restore/hash-check all old project content before retiring locations. Update direct and portfolio discovery records. Preserve dated handbook evidence and public asset bytes.

Alacritty, Notepad++ and Sublime Text native exporters were added on 2026-10-08 with documented contracts in docs/EDITOR-TARGETS.md. Native application import and visual acceptance of those exporters are pending operator testing. See migration/acceptance.json for measured local evidence and migration completion.
