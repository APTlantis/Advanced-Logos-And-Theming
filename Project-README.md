# Logos-And-Theming

The SVG, general syntax-highlighting and data-visualization extension is implemented with three diagram styles, an offline Prism token fixture, and bar/line/heatmap examples. Contracts and acceptance limits: [docs/VISUAL-TARGETS.md](docs/VISUAL-TARGETS.md). Local evidence: `migration/visual-target-acceptance.json`; earlier pilot and recovery evidence remain preserved.

CTS project group for image-derived dark themes and related logo tooling. The package and utilities share this directory; SESM embedding remains a separate sibling project.

Detailed overview: [Black-Gold slide deck](docs/presentations/Logos-And-Theming-Overview.pptx). Planned deep dives, ownership and authoring sequence: [documentation suite plan](docs/documentation-suite/PLAN.md).

Implementation and setup: README.md. Intent: Project-Proposal.md. Contracts: docs/COMMAND-CONTRACT.md. Verification: docs/VALIDATION.md and migration/acceptance.json. Recovery: migration/README.md and hash-verified archives.

Default dark surfaces now preserve an image hue instead of automatically using the darkest canonical color. Background and near-black selection policies, explicit opt-ins and the separately preserved comparison run are documented in README.md and migration/dark-surface-regression.json.

The PowerPoint metadata repair is documented in docs/POWERPOINT.md and migration/powerpoint-metadata-repair.json, including native opening without repair, recoverable originals and a utility for correcting older copies.

Current targets are Windows Terminal, SiYuan, Typora, PowerPoint colors with a 23-slide preview and a reusable 14-layout template, Alacritty, Notepad++, Sublime Text, SVG, Prism syntax highlighting and Matplotlib data visualization. New editor contracts and acceptance limits are in docs/EDITOR-TARGETS.md; older Notepad++/JetBrains outputs remain historical. Local structural and contrast evidence does not establish application installation, visual acceptance, distribution or release readiness. PowerPoint setup and the sample deck acceptance boundary are in docs/POWERPOINT.md.

The supplied presentation template is bundled byte-for-byte in `apt_theme/templates`. The exporter preserves its editable objects and workbooks while adapting Office color slots. It requires no Node or private Codex dependency. Evidence: `migration/powerpoint-template-acceptance.json`; setup and recovery: `docs/POWERPOINT.md`.

The output index is served at `https://themes.aptlantis.net/` by the A-drive Caddy server using a read-only D-drive mount and an explicit theme-folder allowlist. Operations: `docs/HOSTING.md`; delivery evidence: `migration/theme-hosting-acceptance.json`.
