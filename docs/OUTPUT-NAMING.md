# Version-aware output naming

Current contract: 2026-10-18. This supersedes the 2026-10-16 compatibility-copy convention for future `generate` and `import` runs. Existing generated runs, Atlas snapshots, recovery archives, dated presentations and public copies remain untouched.

## Artwork generation identity

| Theme version | Prefix |
| --- | --- |
| 1 | `apt` |
| 2 | `dnf` |
| 3 | `rpm` |
| 4 | `yum` |
| 5 | `eopkg` |

These versions identify the artwork/theme generation. The engine package version and native package schema/version fields are independent.

Both commands accept `--theme-version {1,2,3,4,5}`. A recognized prefix in the display name, source filename, imported palette theme metadata, or bounded source directory/run metadata can establish the version. For an input in `source/`, inspect its parent run; otherwise inspect only the immediate source directory. No distant ancestors or output destination names are used. All evidence, including an explicit flag, must agree. Unknown versions fail with instructions to supply the flag; conflicts fail before extraction/export. The flag supplies missing identity and cannot relabel conflicting source evidence.

The display name remains as supplied. Without `--name`, import uses the palette's theme name when available; otherwise the input filename stem supplies the name. Filename slugs lowercase letters and normalize punctuation/underscores to hyphens, removing optional leading `Aptlantis` branding and one recognized generation prefix. Empty slugs and stacked prefixes are rejected. `Aptlantis-Ada` alone has no generation prefix.

```powershell
# V2 inferred from the supplied name; the input must not carry conflicting evidence.
.\Invoke-AptTheme.ps1 generate 'C:\artwork\logo.png' --output output\ada-v2-new --name 'dnf-Ada'

# An unprefixed imported palette requires explicit identity if its context has none.
.\Invoke-AptTheme.ps1 import 'C:\palettes\palette.toml' --output output\ada-v3-new --name 'Aptlantis-Ada' --theme-version 3
```

`run.json`, the run-root palette and each target palette record `theme_identity`: numeric `version`, `prefix`, normalized `slug`, and an `evidence` array identifying version sources. Original input bytes, canonical RGB/IDs, source hashes and legacy-role provenance are preserved.

## One authoritative artifact filename

Freely named target files use `<prefix>-<theme>-<target>[-<role>].<extension>`. Target IDs use hyphens in filenames, retaining IDs such as `notepad_plus_plus` in CLI/metadata. All writers and their HTML/CSS/JavaScript/README references use the same artifact inventory before writing; no compatibility-copy or text-replacement pass runs afterward.

Examples for V2 Ada:

| Artifact | Filename |
| --- | --- |
| Windows Terminal | `dnf-ada-windows-terminal.json` |
| Markdown primary CSS | `dnf-ada-markdown.css` |
| Markdown token CSS | `dnf-ada-markdown-tokens.css` |
| Markdown specimen | `dnf-ada-markdown-examples.html` |
| CodeMirror 5 CSS | `dnf-ada-codemirror5.css` |
| CodeMirror 6 module | `dnf-ada-codemirror6.mjs` |
| PowerPoint preview/template | `dnf-ada-powerpoint-sample.pptx`, `dnf-ada-powerpoint-template.potx` |
| SiYuan distributable | `dnf-ada-siyuan.zip` |
| Target palette/swatch | `dnf-ada-<target>-palette.toml`, `dnf-ada-<target>-swatch.png` |
| Target metadata | `dnf-ada-<target>-tokens.json`, `dnf-ada-<target>-validation.json` |
| Integration instructions | `dnf-ada-<target>-readme.md` |

SiYuan retains `theme.css`, `theme.json`, `README.md`, `icon.png` and `preview.png`, including inside its ZIP. Kmindz retains `KMINDS.json` under the supplied package contract. These fixed-name exceptions have no prefixed aliases and are identified in the manifest. Keep them in their target/theme directories when collecting multiple themes.

Run-root `run.json`, `palette.toml`, `palette.txt`, `palette.css`, `palette.png`, provenance/diagnostic JSON, `review.html` and `markdown-editors.html` remain stable. Original inputs under `source/`, vendor assets and nested upstream syntax source downloads keep their identities. Native Office package members remain unchanged except for the existing color adaptation.

The CM5 theme identifier is `<prefix>-<theme>` (for example `dnf-ada`), matching `.cm-s-dnf-ada`. Use the generated integration README. `.markdown-body`, shared `--apt-*` variables, `.apt-site`/component classes and CM6 `{theme, highlightStyle, extension}` exports are stable integration namespaces, not artwork generation prefixes.

## Manifest and consumer contract

`run.json.artifact_manifests` maps target IDs to relative `<target>/<prefix>-<theme>-<target>-files.json` paths. Each manifest uses schema `aptlantis.artifact-manifest.v2` and records theme identity, target, stem and file entries containing `file`, `logical_name`, `role`, `sha256` and nullable `fixed_name_reason`. `logical_name` is an inventory key, not an emitted compatibility filename. The manifest itself is indexed by the run and is not self-hashed.

Consumers locate files through manifest entries rather than constructing filenames or assuming generic `tokens.json`/`examples.html`. The manifest replaces `named_export_manifests` and the `native_file` copy mapping. Hashes cover actual final bytes. Naming collisions or an incomplete inventory reject the staged build. `review.html` links the files; copy complete target directories for previews and dependencies.

Atlas discovers `apt-*`, `dnf-*`, `rpm-*`, `yum-*` and `eopkg-*` immediate child runs by default. New runs use manifest paths for tokens and previews; historical runs retain generic-filename fallback. Physical directory identity remains intact. `--include` still selects explicit immediate-child patterns.

## Validation and recovery

Tests cover five generations across fifteen targets, canonical preservation, manifest hashes, local references, collisions, native ZIP members, CM5 identity, CLI errors and mixed legacy/new Atlas snapshots. Current Markdown/editor, Typora, visual-preview and optional Matplotlib review helpers resolve manifest filenames while retaining legacy input support. Dated migration/public-repair scripts remain historical workflows and are not applied to new runs. Actual browser checks and native application acceptance remain separate. See [current evidence](../migration/version-naming-acceptance-2026-10-18.json).

Use a fresh output directory. Existing overwrite/staging/recovery safeguards remain in force. Roll back by retaining the prior generated run and using its own manifest and integration instructions. No historical repair command or automatic public refresh is provided.
