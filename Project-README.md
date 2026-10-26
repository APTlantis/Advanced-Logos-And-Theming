# Logos-And-Theming

Reviewed **2026-10-25**. Owner: Herb. CTS project group, **0.1.0 local pilot**. Exporter expansion is paused for output refinement and codebase stabilization. Identity, physical root, ownership and release stage remain unchanged.

The group owns image-to-theme generation, artwork/catalogs, ICO/SVG conversion and atlas utilities. SVG metadata authoring remains independently governed by [SESM-Metadata-Embedder](../SESM-Metadata-Embedder/README.md). Finishing integrates that tool through its existing explicit root/configuration/write interface; it does not absorb the sibling project.

The pipeline preserves original source bytes and selects/imports exactly 32 canonical colors. Semantic roles and dark target adaptation remain separate, without new hue families. Fifteen existing targets retain their native contracts, naming, token budgets and package resources. `finish` is an independent command for explicitly selected existing PNGs, with preview by default and fresh staged output on `--write`.

## Read first

- [README](README.md): setup and operator entry points.
- [Architecture](docs/ARCHITECTURE.md) and [audit](docs/STABILIZATION-AUDIT.md): current code boundaries, findings and dispositions.
- [Command contract](docs/COMMAND-CONTRACT.md), [output naming](docs/OUTPUT-NAMING.md), [SVG finishing](docs/SVG-FINISHING.md): maintained interfaces.
- [Testing](docs/TESTING-REFERENCE.md), [validation](docs/VALIDATION.md) and [stabilization acceptance](evidence/stabilization-2026-10-25.json): separate verification gates.
- [Read map](PROJECT-READMAP.toml): governed evaluator navigation.

The stabilization baseline captured 356 files each from generation and import across all fifteen targets. Complete hashes are compared after refactoring. The new finishing checks cover source preservation, exact palette fills/order/lineage, real SESM schema/safe validation, warning handling and output recovery. Native SVG editor import, real VTracer fidelity and publication remain separate, unperformed gates unless explicitly recorded in acceptance.

`assets/` and `output/` are ignored local collections; `pilot/`, historical presentations, Theming Index, legacy implementations and verified recovery archives remain preserved. [Hosting operations](docs/HOSTING.md) govern public-copy changes separately. No public delivery status was rechecked during stabilization.

No parent registration or root navigation change is needed because project identity/ownership/roots are unchanged. Prior overview bytes are retained in [the dated snapshot](docs/history/stabilization-2026-10-25/Project-README.md).
