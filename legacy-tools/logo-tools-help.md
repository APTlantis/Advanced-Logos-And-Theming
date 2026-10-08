# Logo script commands

Run from `D:\CTS\Aptlantis Logos` with Python 3.11+ and ImageMagick 7 available as `magick`. On the current host, use the installed Python 3.13 executable below. Set `$python` once before using the examples; sandbox execution may need filesystem approval:

```powershell
$python = "C:\Users\Administrator\AppData\Local\Programs\Python\Python313\python.exe"
```

These scripts use Python's standard library; Pillow and OpenCV are no longer required. Trace mode additionally needs the VTracer **1.0.0-alpha.4** Windows CLI on PATH or supplied with `--vtracer`. The pinned release's Windows ZIP SHA-256 is `8eadb5529864265f003f791ad9cb128e1b9b8b8af8c21016f38b04706bcf3531`.
The Windows CLI is available from the [VTracer 1.0.0-alpha.4 release](https://github.com/visioncortex/vtracer/releases/tag/1.0.0-alpha.4); verify the ZIP hash before extracting.

## ICO

```powershell
& $python "scripts\Convert-to-ICO.py" --input "svg-trace-logos\cts.svg" --output "$env:TEMP\cts.ico" --sizes 16,32,48,256
& $python "scripts\Convert-to-ICO.py" --input "png" --output "$env:TEMP\logo-icons" --recursive --fit contain --background none --dry-run
```

Supported inputs: PNG, JPEG, BMP, TIFF, WebP, GIF, and SVG. Animated formats use the first frame. Default frames are 16, 32, 48, 64, 128, and 256 pixels; sizes must be unique integers from 1 to 256. `--fit contain` preserves the image with padding; `--fit crop` fills the square. `--background`, `--filter` (Lanczos, Mitchell, Catrom, Point), and SVG `--density` control rendering. `--overwrite` replaces an existing output. Batch paths retain their subdirectory structure, and colliding output names are rejected. Completed ICOs are checked for requested frames and ImageMagick decode.

## SVG

```powershell
& $python "scripts\Convert-to-SVG.py" --input "png\apt-caddy-logo.png" --output "$env:TEMP\caddy.svg"
& $python "scripts\Convert-to-SVG.py" --input "png" --output-dir "$env:TEMP\logo-svg" --no-recursive --dry-run
& $python "scripts\Convert-to-SVG.py" --input "png\apt-caddy-logo.png" --mode trace --vtracer "C:\path\vtracer.exe" --max-colors 8 --simplify 2
```

Default `embed` mode preserves the original PNG, JPEG, WebP, or GIF bytes in an SVG data URL, along with original dimensions. BMP and TIFF are normalized to PNG for browser-compatible embedding. The old `auto` option is a deterministic alias for `embed`. Use `--normalize` to re-encode through ImageMagick; it is required for embed-mode `--resize`, `--blur`, `--colors`, or a nontransparent `--background`. Directory processing retains the legacy recursive default; `--no-recursive` limits it to one level.

`--mode trace` requires VTracer and never falls back to embedding. Its controls include `--curves`, `--hierarchical`, `--filter-speckle`, `--color-precision`, `--path-precision`, `--max-colors`, and `--simplify`. `--mono` enables black and white tracing; `--threshold` and `--invert` apply only there. The older OpenCV trace output is not reproduced; `--simplify` now sets VTracer's curve tolerance.

## SESM

```powershell
& $python "scripts\Embed-SESM.py" --input "svg-embed-logos\cts.svg" --config "sesm-metadata.toml"
& $python "scripts\Embed-SESM.py" --input "svg-trace-logos\cts.svg" --config "sesm-metadata.toml" --write
& $python "scripts\Embed-SESM.py" --input "svg" --recursive
& $python "D:\.city_hall\SESM\Validate-SESM-Safe.py" "svg-embed-logos\cts.svg" --safe-profile --json
```

Preview is the default and does not write. `--write` inserts a single SESM block; an existing block is skipped unless both `--write --replace` are supplied. Other XML text, geometry, and metadata are preserved. The canonical schema defaults to `D:\.city_hall\SESM\svg_asset.schema.json`; `--schema` can select another. Run the separate canonical safe-profile validator before claiming `sesm-safe`.

The optional `sesm-metadata.toml` has `[defaults]` and `[assets."project-relative/path.svg"]` tables. Nested TOML tables map directly to SESM objects. Precedence is source-backed fallback, shared defaults, then per-asset fields. Without `--config`, the fallback includes a stable asset ID, logo role, title, path, and descriptions from `logos.json` when present. It does not guess themes, links, timestamps, or integrity. To author broader fields, add `theme`, `ui`, `llm`, `crawl`, `links`, `provenance`, or `integrity` under a per-asset table with verified values. `--root` changes the path-key base and catalog root.

All three tools print actions to stdout and errors to stderr. Exit 0 means no failures (including skipped existing outputs); 1 means at least one input failed; 2 means invalid setup, dependency, or arguments. `--dry-run` on converters and default preview on the SESM embedder report planned writes without creating output directories.

## City Hall component logo adoption

The SESM registry now covers all 16 assets in `svg-embed-logos`, while preserving the CTS trace entry and existing CTS descriptions. These SVGs contain embedded raster artwork. Names and summaries use reviewed City Hall component records with canonical manifest references; unknown authorship and licensing are omitted. IDs, artwork, dimensions, and embedded raster bytes are preserved.

Run `Embed-SESM.py --input svg-embed-logos --config sesm-metadata.toml --write --replace`, then validate every SVG with the canonical safe-profile validator before copying to the site. The site workflow is documented in `A:\aptlantis.net\docs\city-hall-logo-workflow.md`. The site build consumes copied public files and does not read this source project.

Verification for this metadata edit: seven existing logo-tool tests passed; all 16 metadata blocks passed the embedder schema check and canonical safe-profile validator without warnings. Exact comparison outside the SESM blocks confirmed unchanged artwork and dimensions. Public copies matched the source bytes. This does not establish release readiness or public deployment.
