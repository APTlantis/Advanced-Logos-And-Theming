# SiYuan component styling

Current refinement: 2026-11-02. This is one restrained dark style, with no intensity preset. Canonical palette values and global semantic assignments remain unchanged. `apt_theme/siyuan.py` owns component mappings and authored offline specimens; `targets.py` owns palette adaptation and budgets, and `exporters.py` retains native packaging.

## Mapping contract

Palette tokens, semantic aliases, and native component selectors are separate. The default budget remains 64; the current default uses 62 named tokens. Budgets from the existing 22-token minimum use deterministic base-token fallbacks. Aliases do not count as new palette colors. `tokens.json.siyuan` records the versioned mapping, actual selectors, token references, status collision, and pending native acceptance.

The document title uses foreground; subordinate headings use secondary/type and muted roles. Primary is reserved for links, focus, and active controls. Metadata, references, inline code, and syntax receive separate existing roles. Warning/error collisions are adjusted only in the SiYuan target with hue-preserving lightness/chroma changes; unresolved collisions are recorded rather than concealed. Global semantic findings can still report the original canonical-role collision.

Native CSS variables cover surfaces, foregrounds, menus, toolbars, status cards, code, and tables. Explicit selectors cover the document tree, tabs, controls, editor blocks, embeds, and database headers/cards. Notebook headings are distinguished from document labels; folder indicators use the native `navigation-file`/`data-count` contract. Selection overrides folder colors. Highlight.js compound classes such as `.hljs-title.function_` and additional literal/attribute/diff classes remain editor-scoped.

All component rules are scoped beneath `html[data-theme-mode='dark']`. No global element styling, `!important`, font replacement, fixed table layout, sticky headers, or editor geometry redesign is included. Tables retain alignment, resizing, and native display, while adding header and alternating-row surfaces. Explicit inline document colors retain precedence. Plugin-owned iframe content is not styled.

## Output and acceptance

Native package members remain `theme.css`, `theme.json`, `README.md`, `icon.png`, and `preview.png`. An additional version-prefixed `examples.html` is an external standalone browser specimen and is excluded from the native ZIP. The generic review page links it through the artifact manifest.

Selectors were inspected in installed SiYuan 3.8.9 desktop assets. This establishes source compatibility, not native rendering. Contrast checks name component foreground/surface pairs, nested surfaces, selection, primary fills, and focus/boundary indicators. Explicit user colors and arbitrary third-party content are outside generated-color contrast guarantees.

The three-theme pilot preserves `apt-Codex`, `apt-BlueSlate`, and `rpm-BlackGold`; source runs are read-only. Open [the offline review](../pilot/theme-refinement-2026-11-02-review/index.html) for before/after specimens and package links. Reproduce into a fresh destination:

```powershell
.\.venv\Scripts\python.exe tools/prepare_theme_refinement.py pilot/theme-refinement-new
```

[Dated evidence](../evidence/theme-refinement-2026-11-02/acceptance.json) separates source tests, authored browser rendering, installed-wheel checks, and native acceptance. Theme installation/activation, live KMind import/apply, live SiYuan rendering, and publication remain pending. Existing runs, artwork, historical evidence, and public asset copies are not updated.
