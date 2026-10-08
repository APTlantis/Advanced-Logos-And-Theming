# Validation and evidence limits

Date: 2026-10-08, America/New_York.

The pilot source is the preserved `assets/sources/apt-zig-dark-16bit-logo.tif`. Its comparison palette is `assets/references/Aptlantis-Black-Gold/palette.toml`. Native files, reports and source hashes are in `pilot/zig-dark`.

Focused tests cover observed-color selection, NumPy/ColorAide conversion agreement, opacity handling, monochrome and insufficient-color inputs, hue-preserving gamut mapping, semantic overrides, target budgets, canonical immutability, import, deterministic regeneration, strict-mode findings, overwrite safeguards, JSON/XML/CSS parsing and SiYuan package contents. Converter tests cover ICO frames, SVG dimensions/raster preservation, collision safety and explicit tracing. Tracing integration is exercised with a stub; actual VTracer tracing remains unverified.

The separate SESM suite covers preview, config precedence, schema errors, preservation outside metadata and replacement/duplicate handling. The canonical safe-profile validator is a separate gate. Migration archives are restored completely and hashes checked for every file, including Git history and differing source versions.

`migration/acceptance.json` records final commands and results. Passing static and browser-report checks does not prove native application import, installation, application rendering, marketplace acceptance or release readiness. No themes are installed or published by this work.
