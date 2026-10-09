# Logos-And-Theming proposal

The 2026-10-08 visual-target extension adds SVG presentation-attribute examples, Prism CSS and a Matplotlib style with explicit sequential scales. There are now ten default targets. Examples are illustrative; static, browser and Matplotlib Agg evidence are separate from native editor integration. See docs/VISUAL-TARGETS.md and migration/visual-target-acceptance.json.

Owner: Herb. Date: 2026-10-08. State: implemented local pilot.

## Problem and intended result

Separate tools had mixed image selection, fixed semantic meanings and application mappings. A cyan warning in the supplied Zig palette exposed positional semantic assignment. Consolidate the image-to-theme workflow and related small logo utilities while independently governing SESM metadata editing.

## Design and boundaries

ImageMagick normalizes images; NumPy/scikit-learn select observed colors in OKLab; ColorAide supplies color math. A canonical 32-color palette is independent of semantic meaning. Application adapters preserve hue identity, report missing conventional hues and derive readable states through lightness/chroma adjustment. One command emits ten target formats and an offline report.

Dark modes only. No new hue families, automatic application installation, public deployment, marketplace publication or exporters without documented native contracts. PowerPoint emits a reusable 12-slot color XML and an editable four-slide sample deck for visual review; full presentation templates remain deferred. ICO/SVG conversion and atlas remain explicit utilities. SESM metadata belongs to the sibling project.

## Acceptance and recovery

Use the source TIFF/Black-Gold reference, deterministic palette/output checks, actual exported contrast pairs, native-format parsing, converter preservation and separate metadata validation. Archive and completely restore/hash-check all old project content before retiring locations. Update direct and portfolio discovery records. Preserve dated handbook evidence and public asset bytes.

Alacritty, Notepad++ and Sublime Text native exporters were added on 2026-10-08 with documented contracts in docs/EDITOR-TARGETS.md. Native application import and visual acceptance of those exporters are pending operator testing. See migration/acceptance.json for measured local evidence and migration completion.
