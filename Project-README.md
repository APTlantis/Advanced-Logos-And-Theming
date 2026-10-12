# Logos-And-Theming

Typora refinement (2026-10-11): [fresh Black-Gold browser specimen](pilot/typora-markdown-2026-10-11/typora/examples.html), [Markdown stress document](pilot/typora-markdown-2026-10-11/typora/examples.md), and [native review steps](docs/TYPORA-REVIEW.md). Tables and common Markdown structures are styled using unchanged token colors; the current suite has 35 methods. Native Typora acceptance remains pending.


Current source overview: **2026-10-10**. CTS project group, **0.1.0 local pilot**, owned by Herb. The group owns the image-to-theme engine, shared artwork/catalogs, ICO/SVG converters and palette atlas. SESM metadata editing is independently governed by [SESM-Metadata-Embedder](../SESM-Metadata-Embedder/README.md).

Start with [PROJECT-READMAP.toml](PROJECT-READMAP.toml) and [evaluator context](docs/EVALUATOR-START.md). The read map reserves four mandatory governance records and selects source, tests and evidence within a 25-file budget. [README.md](README.md) supplies setup and usage; [Project-Proposal.md](Project-Proposal.md) states intent and boundaries.

The implemented pipeline extracts 32 observed canonical image colors, assigns semantic roles independently, then adapts dark-only native tokens without new hue families. Import preserves canonical RGB/IDs. All **eleven targets** generate by default: Windows Terminal, SiYuan, Typora, PowerPoint, Alacritty, Notepad++, Sublime Text, SVG, Prism syntax highlighting, Matplotlib data visualization and scoped website CSS. Each selected target also emits a provenance-bearing palette TOML and labeled swatch PNG.

[OUTPUT-REFERENCE.md](docs/OUTPUT-REFERENCE.md) covers exact files, budgets and algorithms. PowerPoint preserves the supplied 23-slide/14-layout template and emits PPTX/POTX without Node or private Codex generation dependencies. SVG supplies six detailed compositions; syntax supplies twelve offline Prism language pages; charts share deterministic 12-bar, six-by-24-line and eight-by-12-heatmap data. Website emits 89 mandatory tokens within its 112-token budget, scoped CSS and interactive specimens. Independent converter/atlas commands are described in README.md.

[TESTING-REFERENCE.md](docs/TESTING-REFERENCE.md) inventories **32 current methods** and future coverage; [VALIDATION.md](docs/VALIDATION.md) indexes dated results and native limitations. [Fresh evaluator preflight](migration/evaluator-preflight-2026-10-10.json) records this documentation pass. Earlier acceptance files remain evidence for their own artifacts; installation and release readiness remain unverified. Native application opening, edit/save/reopen, integration and visual acceptance require their stated separate gates.

The curated output index has recorded delivery evidence at [themes.aptlantis.net](https://themes.aptlantis.net/), served through a read-only output mount and explicit allowlist. [HOSTING.md](docs/HOSTING.md) describes operations. Current generator extensions do not automatically refresh existing/public runs; this preparation did not recheck public delivery.

[Migration and recovery](migration/README.md) documents verified archives, Git LFS hydration and restoration. Local assets and output are ignored by Git. [The overview deck](docs/presentations/Logos-And-Theming-Overview.pptx) and Writerside snapshot remain dated orientation material. [The documentation suite plan](docs/documentation-suite/PLAN.md) distinguishes authored references from proposed volumes.
