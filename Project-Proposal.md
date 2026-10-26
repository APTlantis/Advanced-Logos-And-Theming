# Logos-And-Theming proposal

Owner: Herb. Current stabilization decision: **2026-10-25**. Package 0.1.0 remains a local pilot. The original proposal and accumulated extension notes are preserved byte-for-byte in [the dated snapshot](docs/history/stabilization-2026-10-25/Project-Proposal.md).

## Purpose and current direction

Produce image-derived dark themes from an independent canonical 32-color palette, with separate semantic assignments and hue-preserving native target adaptation. Preserve original artwork/provenance and verified recovery evidence.

Pause new exporters and broad feature expansion. Review and improve the current structure in bounded batches while the operator tightens individual outputs. Retain all fifteen target IDs and application acceptance limits. Add a separate explicit-selection PNG-to-SVG finishing command that invokes the independently governed SESM embedder.

## Implementation boundaries

Keep the existing repository/package layout. Separate CLI presentation, orchestration, target adaptation and native output dispatch. Share bounded artifact validation and staged output commit/rollback without changing existing generate/import/Atlas contracts.

Finishing defaults to preview. Explicit writes use a fresh destination and preserve all source runs/manifests. Raster wrapping retains PNG bytes; tracing requires compatible VTracer; editable palette SVGs require matching recorded structured data. Accurate asset roles, compact theme identity and provenance are embedded using the canonical SESM schema and safe profile. Full tool/settings/source evidence stays in the receipt.

No canonical recoloring, new hue families, light themes, native theme installation/activation, public-copy changes, publication, bulk conversion or transfer of SESM ownership is included.

## Acceptance and recovery

Establish a reliable test environment before behavior changes. Compare complete deterministic generation/import fixtures across fifteen targets. Test CLI streams/statuses, native package members/resources, manifest discovery, source preservation, collision/overwrite guards and failed commit recovery.

Verify four representative finishing samples with real SESM validation, browser rendering and exact palette data checks. Preserve warning classifications and distinguish native import and real tracing fidelity from static/stub/browser evidence. Current results and limitations are recorded in [stabilization acceptance](evidence/stabilization-2026-10-25.json).

Preserve historical runs, original source bytes, migration archives and prior documentation snapshots. No entity relocation or parent registration change is proposed.
