# Logos-And-Theming proposal

Owner: Herb. Date: 2026-10-08. State: implemented local pilot.

## Problem and intended result

Separate tools had mixed image selection, fixed semantic meanings and application mappings. A cyan warning in the supplied Zig palette exposed positional semantic assignment. Consolidate the image-to-theme workflow and related small logo utilities while independently governing SESM metadata editing.

## Design and boundaries

ImageMagick normalizes images; NumPy/scikit-learn select observed colors in OKLab; ColorAide supplies color math. A canonical 32-color palette is independent of semantic meaning. Application adapters preserve hue identity, report missing conventional hues and derive readable states through lightness/chroma adjustment. One command emits four native target formats and an offline report.

Dark modes only. No new hue families, automatic application installation, public deployment, marketplace publication, fonts/slide layouts, or untested additional exporters. ICO/SVG conversion and atlas remain explicit utilities. SESM metadata belongs to the sibling project.

## Acceptance and recovery

Use the source TIFF/Black-Gold reference, deterministic palette/output checks, actual exported contrast pairs, native-format parsing, converter preservation and separate metadata validation. Archive and completely restore/hash-check all old project content before retiring locations. Update direct and portfolio discovery records. Preserve dated handbook evidence and public asset bytes.

Native application import and visual acceptance are pending operator testing. See migration/acceptance.json for measured local evidence and migration completion.
