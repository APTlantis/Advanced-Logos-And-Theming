# Logo conversion utilities

Run with the Python environment in `../.venv`. These commands are independent of theme generation.

```powershell
python scripts\Convert-to-ICO.py --input image.png --output icon.ico
python scripts\Convert-to-SVG.py --input image.png --output wrapped.svg
python scripts\Convert-to-SVG.py --input image.png --output traced.svg --mode trace --vtracer C:\path\vtracer.exe
python scripts\generate_atlas.py
```

ICO supports frame sizes, contain/crop fitting, background, filtering, overwrite and dry-run. SVG defaults to embedding original raster bytes and retains dimensions. BMP/TIFF normalize to browser-compatible PNG. Trace mode explicitly requires VTracer; it never falls back. Both tools expose full options through `--help` and reject unsafe batch-output placement/colliding names. Atlas reads `assets/logos.json` and writes `assets/palette-atlas.html`.

Converter exit codes: 0 means no failures, including skipped existing outputs; 1 means an input failed; 2 means invalid setup/dependency/arguments. Actions go to stdout and errors to stderr. `--dry-run` performs no writes.

SESM metadata embedding belongs to [SESM-Metadata-Embedder](../../SESM-Metadata-Embedder/README.md). Its registry and explicit asset-root invocation are documented there. The pre-migration combined help is retained in `legacy-tools/logo-tools-help.md` and the verified archives; its old paths are historical.
