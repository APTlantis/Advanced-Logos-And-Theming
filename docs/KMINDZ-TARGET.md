# KMind Zen target

Current compatibility refinement: 2026-11-02. Target ID `kmindz`, default budget 40, mandatory count 32. Both `generate` and `import` select the existing target; no new exporter or automatic application update is introduced.

## Native contract and provenance

The exact supplied `local-kmind-slate.kmind-theme.json` is bundled as `apt_theme/templates/kmindz-slate-v1.json`. `kmindz-contract.json` records its SHA-256 and the inspected installed `siyuan-kmind-zen` 0.46.0 JavaScript hash. The previous `kmindz-template.json` remains unchanged as historical contract evidence.

The installed host's `WYe` validator visits both `light` and `dark`, and `qYe` rejects an absent variant. Future exports therefore put identical dark styling in both slots, with `defaults.appearance = dark`. The light slot is a compatibility mirror, not a generated light theme. The actual host validator functions accept the new pilot themes and reject the previous single-slot shape; this is a source-level check, not native application import/apply acceptance.

Package/theme schema versions remain 1. Identity remains generation-aware `<prefix>-<slug>-canonical32`; names and descriptions come from the selected theme. Zero timestamps remain deterministic unspecified markers, supported by the inspected host normalizer. Geometry, fonts, line widths, depth predicates, priorities, and routes follow the supplied Slate dark variant. Canonical palette bytes and global semantics remain separate.

## Files and lookup

The physical download is `<prefix>-<theme>-kmindz.kmind-theme.json`. The logical artifact key remains `KMINDS.json`; `run.json` and the target file manifest resolve it to the physical filename. Historical generic `KMINDS.json` runs remain discoverable. No duplicate alias file is created. Review-page links use the recorded filename.

Other version-prefixed artifacts include the authored `preview.svg`, `format-provenance.json`, palette TOML/swatch, `tokens.json`, and `validation.json`. The thumbnail is an authored dark hierarchy preview, not a native KMind layout render. Format provenance describes the dark mirror and records pending native acceptance.

## Mapping and validation

The 22-token base has ten consumed hierarchy extensions. All paint fields, depth overrides, twelve rainbow entries, background, and authored preview use mapped target colors. Root and lower-depth text is checked against both normal and selected fills at 4.5:1; hierarchy edges are checked at 3:1. Budgets below 32 fail rather than dropping required mappings. No sample colors or new hue families are inserted into generated output.

Tests cover both required slots, mirrored styling, dark default, provenance, native extension, identity, palette preservation, deterministic serialization, geometry, selected contrast, and manifest discovery. The offline checker executes the exact color/route/theme validator functions from the identified installed host and checks the three pilot packages. Python generation remains independent of Node and network access; Node is optional QA tooling only.

## Review and acceptance limits

Open [the three-theme pilot](../pilot/theme-refinement-2026-11-02-review/index.html) for package downloads and SiYuan before/after specimens. Use a fresh destination for further generation. [Dated evidence](../evidence/theme-refinement-2026-11-02/acceptance.json) separates automated compatibility, browser previews, and installed-wheel use.

Native KMind import, Apply behavior, existing map overrides, layout/rainbow precedence, rendering, edit/save/reopen, and other plugin versions remain pending. Do not label these packages application-accepted until tested in the host. No themes are installed, activated, or published, and historical/public outputs remain unchanged.
