# Logos-And-Theming

The 2026-10-09 per-target palette extension emits `apt-<language>-<output-type>-palette.toml` and `apt-<language>-<output-type>-swatch.png` for every selected output in both image generation and import. The TOML records actual tokens, origins, validation and the independent canonical 32; the PNG follows the supplied transformer swatch layout. Offline review links expose both. Evidence: `migration/target-palette-acceptance-2026-10-09.json`; contract: [output reference](docs/OUTPUT-REFERENCE.md). Existing/public output runs remain preserved.

Comprehensive current references: [output apps/types, files and generation internals](docs/OUTPUT-REFERENCE.md) and [test inventory, rationale, execution, limits and proposed coverage](docs/TESTING-REFERENCE.md). These source-checked 2026-10-09 documents extend the concise target contracts and dated validation records; they do not refresh hosted themes or the older Writerside snapshot.

The SVG quality extension adds six detailed 1200×800 editable compositions spanning workflows, editorial graphics, relationship maps, icons, wayfinding and product illustration. The existing three SVG filenames remain; canonical colors and budgets are unchanged. Fresh local gallery: `pilot/svg-quality-2026-10-09/svg/examples.html`; evidence: `migration/svg-quality-acceptance-2026-10-09.json`. Browser checks do not establish native editor import, and no hosted outputs were regenerated.

The 2026-10-09 syntax/chart quality pass bundles Prism 1.30.0 and twelve real language examples, expands charts to 12 bars, six 24-point lines and an 8×12 heatmap, and shares values between authored SVG and Matplotlib. All 26 focused tests, offline Chromium checks, Agg renders and isolated wheel generation passed. Contracts and limits: [docs/VISUAL-TARGETS.md](docs/VISUAL-TARGETS.md). Current evidence: `migration/visual-quality-acceptance-2026-10-09.json`. Earlier visual-target pilots and recovery evidence remain preserved; hosted themes were not regenerated.

CTS project group for image-derived dark themes and related logo tooling. The package and utilities share this directory; SESM embedding remains a separate sibling project.

Detailed overview: [Black-Gold slide deck](docs/presentations/Logos-And-Theming-Overview.pptx). Planned deep dives, ownership and authoring sequence: [documentation suite plan](docs/documentation-suite/PLAN.md).

Implementation and setup: README.md. Intent: Project-Proposal.md. Contracts: docs/COMMAND-CONTRACT.md. Verification: docs/VALIDATION.md and migration/acceptance.json. Recovery: migration/README.md and hash-verified archives.

Default dark surfaces now preserve an image hue instead of automatically using the darkest canonical color. Background and near-black selection policies, explicit opt-ins and the separately preserved comparison run are documented in README.md and migration/dark-surface-regression.json.

The PowerPoint metadata repair is documented in docs/POWERPOINT.md and migration/powerpoint-metadata-repair.json, including native opening without repair, recoverable originals and a utility for correcting older copies.

Current targets are Windows Terminal, SiYuan, Typora, PowerPoint colors with a 23-slide preview and a reusable 14-layout template, Alacritty, Notepad++, Sublime Text, SVG, Prism syntax highlighting and Matplotlib data visualization. New editor contracts and acceptance limits are in docs/EDITOR-TARGETS.md; older Notepad++/JetBrains outputs remain historical. Local structural and contrast evidence does not establish application installation, visual acceptance, distribution or release readiness. PowerPoint setup and the sample deck acceptance boundary are in docs/POWERPOINT.md.

The supplied presentation template is bundled byte-for-byte in `apt_theme/templates`. The exporter preserves its editable objects and workbooks while adapting Office color slots. It requires no Node or private Codex dependency. Evidence: `migration/powerpoint-template-acceptance.json`; setup and recovery: `docs/POWERPOINT.md`.

The output index is served at `https://themes.aptlantis.net/` by the A-drive Caddy server using a read-only D-drive mount and an explicit theme-folder allowlist. Operations: `docs/HOSTING.md`; delivery evidence: `migration/theme-hosting-acceptance.json`.
