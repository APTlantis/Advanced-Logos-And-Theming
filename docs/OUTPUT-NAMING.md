# Output naming

Implemented 2026-10-16 for new `generate` and `import` runs. Collectable files use `apt-<theme>-<target>[-<role>].<extension>` in each target directory. Leading `Aptlantis-` or `apt-` is removed once from the theme name; punctuation and underscores become hyphens and letters become lowercase. The existing palette/swatch naming uses the same normalization.

| Target | Main named file for `--name Aptlantis-Ada` |
| --- | --- |
| Windows Terminal | `apt-ada-windows-terminal.json` |
| Alacritty | `apt-ada-alacritty.toml` |
| Notepad++ | `apt-ada-notepad-plus-plus.xml` |
| Sublime Text | `apt-ada-sublime-text.sublime-color-scheme` |
| Typora | `apt-ada-typora.css` |
| SiYuan | `apt-ada-siyuan.css`, `apt-ada-siyuan.zip` |
| PowerPoint | `apt-ada-powerpoint.xml`, `apt-ada-powerpoint-sample.pptx`, `apt-ada-powerpoint-template.potx` |
| Kmindz | `apt-ada-kmindz.json` |
| Markdown | `apt-ada-markdown.css` |
| CodeMirror 5 | `apt-ada-codemirror5.css` |
| CodeMirror 6 | `apt-ada-codemirror6.mjs` |
| Website | `apt-ada-website.css` |
| Prism | `apt-ada-syntax-highlighting.css` |
| Data visualization | `apt-ada-data-visualization.mplstyle` |
| SVG | `apt-ada-svg-technical-flow.svg` and the other composition roles |

Other authored top-level files receive a role suffix: `apt-ada-markdown-tokens.css`, `apt-ada-markdown-extras.css`, `apt-ada-markdown-syntax-prism.css`, `apt-ada-kmindz-validation.json`, `apt-ada-svg-examples.html`. Existing named palettes and swatches are retained as-is. The target ID remains `kmindz`, matching the existing exporter.

Each target's `apt-<theme>-<target>-files.json` lists named copies, native filenames and SHA-256 hashes. `run.json` indexes these manifests; `review.html` supplies download links. Named copies are byte-identical to their original entry points. Naming conflicts fail the staged build before any named files are copied. Different names that normalize to the same slug still identify the same filename namespace; choose distinct theme names for a combined collection.

## Copying to a central folder

For example, after generating Ada and Swift, collect only their primary Kmindz JSON files:

```powershell
New-Item -ItemType Directory -Force collected-kmindz | Out-Null
Get-ChildItem output -Recurse -File -Filter 'apt-*-kmindz.json' |
    Copy-Item -Destination collected-kmindz -ErrorAction Stop
```

Use the manifest when selecting individual roles. A broad `*.json` glob also selects tokens, validation and metadata. `Copy-Item` can overwrite existing same-name files, so use a fresh destination or check collisions before repeating a collection.

## Compatibility and application limits

Original top-level entry points remain alongside the named copies for existing tools, offline previews and native folder contracts. SiYuan's named ZIP retains required `theme.css`, `theme.json`, README and image names inside it. Vendor resources and nested syntax source downloads retain upstream names. Run-root canonical palettes, provenance, source bytes and run metadata retain their existing contracts.

Named files do not bundle dependencies. Markdown needs its token CSS and optional Prism/extras styles; CodeMirror needs its documented peer dependencies. HTML previews and generated README instructions retain their original relative paths: copy the complete target directory and its vendor tree to use them. The named HTML file alone is not a standalone preview. CSS scopes, CM5 theme identifiers and CM6 exports are unchanged.

Existing generated runs, Atlas snapshots, recovery archives and public copies are not renamed or regenerated. Generate into a fresh directory to obtain named files. Native application acceptance and public deployment remain separate from filename/hash and pipeline tests.
