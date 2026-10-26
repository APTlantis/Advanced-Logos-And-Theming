Version-aware naming (2026-10-18): `apt`/`dnf`/`rpm`/`yum`/`eopkg` identify theme versions 1–5. New runs emit one authoritative freely named target file and indexed manifests, with documented native exceptions. [Contract](docs/OUTPUT-NAMING.md); [local evidence](migration/version-naming-acceptance-2026-10-18.json). Existing runs and public copies are preserved.

Atlas collection refresh (2026-10-16): all 19 `apt-*`/`dnf-*` runs, 608 canonical colors and 171 copied offline examples, including GFM and CodeMirror 5/6. [Collection and usage](docs/CHROMATIC-ATLAS.md).

Chromatic Atlas pilot (2026-10-16): read-only palette matrix, OKLab color-space projections and provenance inspector over current pipeline snapshots. [Contract and local usage](docs/CHROMATIC-ATLAS.md).

Markdown/editor extension (2026-10-16): fifteen defaults, including `markdown`, `codemirror5` and `codemirror6`, with real offline previews, scoped/native contracts and separate downstream acceptance. [Contract](docs/MARKDOWN-EDITORS.md).

Kmindz extension (2026-10-14): twelfth default target, dark `KMINDS.json` output from the supplied v1 template, with canonical preservation and separate native acceptance. [Contract](docs/KMINDZ-TARGET.md).

# Logos-And-Theming

Operator presentations (2026-10-17): [five themed decks](docs/presentations/operators-2026-10-17/README.md), 16 slides each, cover palette design, Chromatic Atlas, Markdown/CodeMirror, converters and safe operation. Native PowerPoint opening/rendering, PDF companions, offline source snapshots and 22 focused tests are recorded in the collection. Local template-preserving authoring was selected after the SlideForge wallet gate; no top-up, activation or publication occurred. These decks are dated documentation, with manual edit/save/reopen acceptance still unperformed.

Output naming (2026-10-16): all fifteen exporters provide named copies and SHA-256 file manifests for central collection; native package filenames and existing runs remain preserved. [Naming contract](docs/OUTPUT-NAMING.md).

Typora refinement (2026-10-11): [fresh Black-Gold browser specimen](pilot/typora-markdown-2026-10-11/typora/examples.html), [Markdown stress document](pilot/typora-markdown-2026-10-11/typora/examples.md), and [native review steps](docs/TYPORA-REVIEW.md). Tables and common Markdown structures are styled using unchanged token colors; the then-current suite had 35 methods. Native Typora acceptance remains pending.


Current source overview: **2026-10-10**. CTS project group, **0.1.0 local pilot**, owned by Herb. The group owns the image-to-theme engine, shared artwork/catalogs, ICO/SVG converters and palette atlas. SESM metadata editing is independently governed by [SESM-Metadata-Embedder](../SESM-Metadata-Embedder/README.md).

Start with [PROJECT-READMAP.toml](PROJECT-READMAP.toml) and [evaluator context](docs/EVALUATOR-START.md). The read map reserves four mandatory governance records and selects source, tests and evidence within a 25-file budget. [README.md](README.md) supplies setup and usage; [Project-Proposal.md](Project-Proposal.md) states intent and boundaries.

The implemented pipeline extracts 32 observed canonical image colors, assigns semantic roles independently, then adapts dark-only native tokens without new hue families. Import preserves canonical RGB/IDs. All **fifteen targets** generate by default: Windows Terminal, SiYuan, Typora, PowerPoint, Alacritty, Notepad++, Sublime Text, SVG, Prism syntax highlighting, Matplotlib data visualization, scoped website CSS, Kmindz, portable Markdown and CodeMirror 5/6 themes. Each selected target also emits a provenance-bearing palette TOML and labeled swatch PNG.

[OUTPUT-REFERENCE.md](docs/OUTPUT-REFERENCE.md) covers exact files, budgets and algorithms. PowerPoint preserves the supplied 23-slide/14-layout template and emits PPTX/POTX without Node or private Codex generation dependencies. SVG supplies six detailed compositions; syntax supplies twelve offline Prism language pages; charts share deterministic 12-bar, six-by-24-line and eight-by-12-heatmap data. Website emits 89 mandatory tokens within its 112-token budget, scoped CSS and interactive specimens. Independent converter/atlas commands are described in README.md.

[TESTING-REFERENCE.md](docs/TESTING-REFERENCE.md) retains dated method inventories and documents the current 53-method suite; [VALIDATION.md](docs/VALIDATION.md) indexes dated results and native limitations. [Fresh evaluator preflight](migration/evaluator-preflight-2026-10-10.json) records this documentation pass. Earlier acceptance files remain evidence for their own artifacts; installation and release readiness remain unverified. Native application opening, edit/save/reopen, integration and visual acceptance require their stated separate gates.

The curated output index has recorded delivery evidence at [themes.aptlantis.net](https://themes.aptlantis.net/), served through a read-only output mount and explicit allowlist. [HOSTING.md](docs/HOSTING.md) describes operations. Current generator extensions do not automatically refresh existing/public runs; this preparation did not recheck public delivery.

[Migration and recovery](migration/README.md) documents verified archives, Git LFS hydration and restoration. Local assets and output are ignored by Git. [The overview deck](docs/presentations/Logos-And-Theming-Overview.pptx) and Writerside snapshot remain dated orientation material. [The documentation suite plan](docs/documentation-suite/PLAN.md) distinguishes authored references from proposed volumes.
