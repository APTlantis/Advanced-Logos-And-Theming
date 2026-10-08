# Logos-And-Theming documentation suite plan

**Planning date:** 8 October 2026. **Status:** proposed authoring sequence; the volumes below are planned, not completed. **Owner:** Logos-And-Theming, with an independently owned SESM companion. **Presentation entry point:** [24-slide Black-Gold overview](../presentations/Logos-And-Theming-Overview.pptx).

The suite should explain both how to use the pipeline and why its decisions are separated. The overview deck introduces the whole project; focused volumes carry the algorithms, application contracts, operational details and recovery evidence that would overwhelm a presentation. The deck’s speaker notes add explanatory depth and dated source references without crowding its slides.

## Editorial contract

- Describe the implemented local pilot before proposing extensions. Label a feature **implemented**, **recorded evidence**, **native acceptance pending**, or **proposed**. Do not present installation, publication or future targets as completed.
- Preserve the distinction between original image bytes, observed candidates, immutable canonical colors, semantic roles and derived application tokens. Use one traced color example across these layers.
- Use the supplied 16-bit Zig TIFF and historical Black-Gold palette for extraction comparisons. Use the current `output/blackgold` run for this deck’s exact theme and token-count examples. These are different fixtures; do not silently substitute the PNG run for the TIFF comparison.
- Keep actual source paths, hashes, configuration, version and command with each case study. Capture a dated documentation snapshot; code, schemas and current project contracts remain authoritative.
- Show readable output and failures. Coverage and spacing are diagnostics, not aesthetic scores. A native import check is different from a visual review, edit/save/reopen, installation or publication.
- Use concise main chapters, substantial worked examples and reference appendices. Include offline figures and linked evidence. Do not repeat configuration tables in several volumes: cross-link one artifact/command reference.
- The current default is dark-only, image-derived hues, local generation and no automatic activation. Future work does not alter these defaults without an explicit design decision.

## Existing material to reuse

| Material | Current value | Treatment in the suite |
|---|---|---|
| Project README, command contract, validation notes | Current engine use and evidence limits | Keep concise and authoritative; elaborate in guides without changing contracts |
| `docs/POWERPOINT.md` | Runtime and sample-deck contract | Reuse in adapter and native acceptance chapters |
| `migration/` inventories, archives and acceptance records | Dated consolidation and regression evidence | Link records; do not rewrite historical results as a fresh test run |
| Black-Gold generated artifacts | Traceable practical examples | Capture hashes and identify run/version; preserve canonical values |
| SESM sibling README and tests | Independent metadata ownership and write rules | Author the companion in the sibling project; link rather than duplicate ownership |
| Existing Writerside handbook | Broader artwork, standards, palettes, SVG and theme reference | Review for reuse, then integrate current-engine chapters deliberately |

The existing handbook is at `D:\.library\Writerside-Projects\Aptlantis-Logos-and-Theming`. Its README identifies `E:\Aptlantis-LogosAndTheming` as the reviewed **5 October 2026** source snapshot. It is useful reference material, but its snapshot predates the consolidated engine and the later regression repairs. Refreshing that snapshot and publishing its website are separate work; this plan performs neither. City Hall retains canonical standards authority.

## Reading routes

| Reader | Start | Continue |
|---|---|---|
| Project stakeholder | Overview deck | 02 case studies; 10 system handbook |
| Theme operator | 01 operator runbook | 09 artifact reference; 06 native acceptance |
| Color/design contributor | 02 case studies | 03 extraction; 04 semantics; 05 adapters |
| Developer adding a target | 09 artifact reference | 05 adapter guide; 06 acceptance; relevant design chapters |
| Asset/metadata maintainer | 07 asset lineage | SESM companion; 08 recovery |
| Auditor or future maintainer | 08 recovery | 09 contracts/evidence; 02 regressions; dated source catalog |

## Planned volumes

### 01 · Operator runbook

**Question:** How do I make, review and revise a theme without losing prior work? **Audience:** operators and occasional maintainers. **Owner:** Logos-And-Theming. **Proposed home:** `docs/guides/operator-runbook.md`. **Priority:** first. **Effort:** medium.

Chapter outline:

1. Setup: Python environment, ImageMagick, target-specific PowerPoint runtime; what setup installs locally.
2. First image-to-theme run: explicit output, target selection and an expected directory tree.
3. Inspect candidates, canonical 32, semantics and the HTML review before deciding a theme looks right.
4. Change a semantic background or status role in TOML; show the override and its resulting provenance.
5. Import an old palette without changing its canonical values; interpret historical role assignments.
6. Compare a previous palette; retain revisions in separate directories; use overwrite safely.
7. Handle input/configuration failure, review findings and strict results; understand staging/replacement recovery.
8. Hand off native files for application testing; generation is not activation.

**Primary sources:** `README.md`, `Setup.ps1`, `Invoke-AptTheme.ps1`, `profiles.toml`, `docs/COMMAND-CONTRACT.md`, `apt_theme/cli.py`. **Worked example:** generate the preserved Zig TIFF into a new revision, then import a historical palette into another directory. **Dependencies:** 09’s command reference and a frozen fixture record. **Complete when:** every documented command is exercised in bounded temporary outputs; expected files, stream behavior and exit codes are recorded; a new reader can reach the review report without an undocumented dependency. Do not overwrite the current reviewed Black-Gold run for authoring.

### 02 · Regression case studies and design decisions

**Question:** Why can a technically plausible palette or valid-looking package still fail? **Audience:** designers, developers and stakeholders. **Owner:** Logos-And-Theming. **Proposed home:** `docs/case-studies/`. **Priority:** first. **Effort:** medium.

Two initial chapters:

1. **Near-black surfaces:** original symptom, repeated dark anchors, observed candidate population, revised canonical selection and identity surface mapping. Show old/new images and actual background values. Include import behavior and explicit darkest/override alternatives.
2. **PowerPoint repair:** undeclared timestamp QName, the gap between XML parsing and namespace-aware validation, minimal core-properties repair, unchanged slide/theme/workbook bytes and native no-repair opening.

**Primary sources:** `migration/dark-surface-regression.json`, `migration/powerpoint-metadata-repair.json`, `docs/VALIDATION.md`, recorded comparison runs, `apt_theme/extraction.py`, `apt_theme/semantics.py`, `apt_theme/powerpoint.py`. **Dependencies:** retained before/after fixtures and source hashes. **Complete when:** each chapter distinguishes observation, hypothesis, verified cause, implemented remedy and remaining uncertainty; figures use preserved outputs; dates and verification methods are explicit. Do not claim a coverage improvement or a successful chart-edit round trip unless separately measured.

### 03 · Extraction and canonical selection methods

**Question:** What does “representative 32” mean, and where are the tradeoffs? **Audience:** color engineers and maintainers. **Owner:** Logos-And-Theming. **Proposed home:** `docs/design/extraction-and-selection.md`. **Priority:** second. **Effort:** large.

Chapter outline:

1. Original bytes versus decoded working pixels: orientation, ICC, sRGB and bit-depth handling.
2. Alpha exclusion and opacity-weighted population; bounded sampling and its limits.
3. sRGB → OKLab/OKLCH; conversion agreement and numerical tolerances.
4. Population-weighted KMeans, fixed seeds and nearest-observed representatives; why centroids are not exported.
5. Selection of 32: perceptual clustering, dark/light anchors, diversity and coalescing the near-black noise floor.
6. Determinism, stable ordering, export uniqueness and insufficient-color failure.
7. Coverage, spacing, duplicates and visual comparisons with the historical method.
8. Parameter sensitivity and candidate improvements, explicitly separated from current behavior.

**Primary sources:** `apt_theme/extraction.py`, `apt_theme/colors.py`, `profiles.toml`, `tests/test_pipeline.py`, `selection.json` and candidate data. **Examples:** principal 16-bit Zig TIFF plus monochrome, alpha and insufficient-color fixtures. **Dependencies:** 02 and 09. **Complete when:** formulas/units agree with code, algorithm steps are reproducible, nearest-observed and alpha behavior are demonstrated, and comparisons show images alongside diagnostics. Aesthetic judgment must remain visible rather than replaced with a scalar score.

### 04 · Semantic mapping design guide

**Question:** How does an image color become a useful role without positional shortcuts? **Audience:** theme designers and mapper maintainers. **Owner:** Logos-And-Theming. **Proposed home:** `docs/design/semantic-mapping.md`. **Priority:** second. **Effort:** large.

Chapter outline:

1. Neutral canonical IDs versus roles; image prominence and perceptual suitability.
2. Identity surfaces, foreground and secondary text; background lightness and explicit overrides.
3. Primary/secondary accents and syntax roles; semantic reuse versus collisions.
4. Status and ANSI hue suitability; warm warning selection and unavailable conventional hues.
5. What to do when identity and convention conflict: report, override or add a non-color cue.
6. Override precedence and imported historical role information.
7. Case-by-case review checklist and evidence limits.

**Primary sources:** `apt_theme/semantics.py`, `semantics.json`, `profiles.toml`, command contract and semantic tests. **Example:** trace Black-Gold warning to `color_29/#FBD484`; explain its reported magenta fallback without inventing a magenta. **Dependencies:** 03, 09. **Complete when:** every documented mapping rule is checked against current source; overrides and collisions have actual examples; the guide does not imply all conventional hues are always available.

### 05 · Target adaptation and exporter developer guide

**Question:** How do I add a useful native target without destroying the theme? **Audience:** developers and application specialists. **Owner:** Logos-And-Theming. **Proposed home:** `docs/developer/target-adapters.md`. **Priority:** second. **Effort:** large.

Chapter outline:

1. Target contract before code: required roles, component states, native file format and acceptance workflow.
2. Protecting roles before reduction; budgets versus named tokens versus unique colors.
3. Derived text/surface/state colors, hue intent, gamut fitting and quantization.
4. Origin records: source ID, requested values, derived/gamut flags, aliases and omissions.
5. Terminal’s 16 ANSI slots plus four application roles; identity under reduction.
6. SiYuan/Typora CSS scope and states; PowerPoint’s 12 native slots and sample content.
7. Export validation, deterministic artifacts, strict behavior and failure handling.
8. Proposed exporter review template for deferred IDE/web/desktop targets.

**Primary sources:** `apt_theme/targets.py`, `apt_theme/colors.py`, `apt_theme/powerpoint.py`, `docs/POWERPOINT.md`, token/validation artifacts and tests. **Dependencies:** 04, 06, 09. **Complete when:** an existing adapter is traced end-to-end and a proposed extension has a native contract, provenance design and meaningful acceptance checklist. Do not introduce a new exporter merely to demonstrate the guide.

### 06 · Native acceptance workbook

**Question:** Does a structurally valid export behave well in the real application? **Audience:** application testers and operators. **Owner:** Logos-And-Theming; native acceptance reviewers recorded per run. **Proposed home:** `docs/acceptance/`, one guide per target plus a results template. **Priority:** second, alongside 05. **Effort:** medium per target.

Shared chapters: application/version and OS; isolated import procedure; fixture/run hash; visual checklist; keyboard/state checks; reversible cleanup; results and unresolved findings.

| Target | Minimum scenarios |
|---|---|
| Windows Terminal | 16 ANSI samples, default/bright text, cursor, selection, gold/cyan identity |
| SiYuan | Package recognition, document/sidebar, code, selection, hover/focus and supplied previews |
| Typora | Theme discovery, document headings/tables/quotes, code, sidebar and interaction states |
| PowerPoint | Open with repair disabled, all slides, Office slots, native table/chart, edit data, save/reopen |

**Primary sources:** generated native artifacts, `docs/VALIDATION.md`, native application documentation and recorded repair evidence. **Dependencies:** 01, 05, frozen fixtures. **Complete when:** procedures are safe and versioned, structural and native evidence are separately recorded, and “pending” is used wherever a live scenario has not been executed. PowerPoint opening/export evidence already exists; chart editing/save/reopen is a distinct pending scenario. Authoring these procedures does not authorize installation or publication.

### 07 · Asset lineage and converter reference, with SESM companion

**Question:** How do artwork, catalogs, conversions and embedded metadata stay connected? **Audience:** asset maintainers. **Owner:** Logos-And-Theming for assets/converters; SESM-Metadata-Embedder for its companion. **Proposed homes:** `docs/assets/asset-lineage.md` and `D:\CTS\SESM-Metadata-Embedder\docs\embedding-guide.md`. **Priority:** third. **Effort:** medium.

Chapter outline: asset IDs and registries; original versus derivative files; ICO frame options; embedded-raster SVG versus explicit VTracer tracing; dimensions/raster byte preservation; atlas utility; provenance handoff to SESM; configuration precedence and explicit roots; preview/write/replace; canonical schema and safe-profile validation as separate gates; preservation outside the metadata block.

**Primary sources:** converter scripts/tests, asset catalogs, both project READMEs, SESM configuration/tests and canonical schema references. **Dependencies:** 09 and ownership map. **Complete when:** a single asset is traced from original to derivative to metadata without changing its ID or raster bytes; every converter option is source checked; preview output and write boundaries are explicit. Real VTracer integration must be labeled pending where only stub coverage exists. The sibling companion should be written in its own project on a later authorized authoring pass.

### 08 · Consolidation and recovery runbook

**Question:** Can a future maintainer recover the former collections and explain retirement? **Audience:** maintainers and auditors. **Owner:** Logos-And-Theming, linking sibling records. **Proposed home:** `docs/operations/recovery.md`. **Priority:** third. **Effort:** medium.

Chapter outline: original four-location inventory; archive identities and Git preservation; differing versions; migration manifests; complete restoration rehearsal; destination/hash checks; reference updates; source-changed and resolved-path deletion gates; public-copy boundaries; post-migration recovery and evidence freshness.

**Primary sources:** `migration/README.md`, inventory/archive hash catalogs, acceptance/retirement records and migration scripts. **Dependencies:** 07, 09. **Complete when:** a bounded restoration procedure and expected hash checks are documented, recovery destination avoids overwriting live projects, and every historical claim links dated evidence. A newly executed recovery rehearsal must be recorded separately from the original migration acceptance.

### 09 · Command, artifact and evidence reference

**Question:** What are the exact contracts another tool or maintainer can rely on? **Audience:** developers, operators and auditors. **Owner:** Logos-And-Theming. **Proposed home:** `docs/reference/`. **Priority:** first; foundation for other guides. **Effort:** medium.

Chapter outline: CLI flags/configuration keys; stdout/stderr and JSON envelope; exact exit-code distinctions; output tree and palette schema; semantic and origin record fields; import compatibility; staging/overwrite behavior; dependencies; validation pair coverage; evidence vocabulary and source catalog.

**Primary sources:** `docs/COMMAND-CONTRACT.md`, `apt_theme/cli.py`, target/report code, profiles, tests and actual outputs. **Dependencies:** none beyond source capture. **Complete when:** examples parse, every field/key is verified, required versus optional fields are clear, and reference tables do not contradict CLI behavior. Distinguish strict contrast exit 2 from argparse syntax exit 2. Preserve legacy grouped palette information as historical data rather than declaring its roles current.

### 10 · Living system handbook and curated case atlas

**Question:** Where should a reader understand the whole collection after entering through the deck? **Audience:** all readers. **Owner:** documentation project in coordination with Logos-And-Theming and SESM. **Proposed home:** existing Writerside handbook, after a reviewed source refresh. **Priority:** fourth. **Effort:** large integration effort.

Chapter outline: project/authority map; six-stage architecture; guided first run; choosing a focused volume; asset/metadata relationships; application contracts; recurring design tradeoffs; curated image-to-theme cases; evidence and recovery navigation; glossary and offline source catalog.

**Primary sources:** existing handbook topics/catalog/gap register and reviewed volumes 01–09. **Dependencies:** the core guides, a source comparison against the 5 October snapshot, and agreement on what material is linked versus incorporated. **Complete when:** source identities are recorded, stale paths/claims are resolved, canonical standards remain external authority, offline navigation/figures work, and documented inspection/render gates pass. Publication remains separate. A curated case atlas should expand only when each new image brings a distinct decision or failure mode.

## Authoring sequence and dependencies

| Wave | Deliverables | Why this order | Exit gate |
|---|---|---|---|
| 0 · Entry point | This deck + this plan | Establish the whole-picture narrative | Theme parity, source traceability, rendered deck reviewed |
| 1 · Practical foundation | 09 reference, 01 runbook, 02 cases | Make current use and recent lessons durable | Exercised examples and dated before/after evidence |
| 2 · Design and extension | 03 extraction, 04 semantics, 05 adapters, 06 acceptance | Explain increasingly application-specific choices | Code-aligned methods and versioned native procedures |
| 3 · Long-term custody | 07 assets/SESM, 08 recovery | Preserve independently owned tools and history | Byte/ID preservation and recoverable instructions |
| 4 · Integrated reading | 10 handbook and curated atlas | Integrate stable material rather than duplicate drafts | Reviewed snapshot, offline build and navigation checks |

Practical dependencies: **09 → 01/03/04/05**, **02 → 03/04**, **03 → 04 → 05**, **01 + 05 → 06**, **07 + 09 → 08**, then **01–09 → 10**. Native acceptance can progress incrementally while design volumes are drafted. A failed native scenario should become a tracked finding and, when useful, a new case study; it does not automatically authorize an implementation change.

## Common chapter and review template

Each volume should include: purpose and reader prerequisites; implemented behavior; one end-to-end example; decisions and tradeoffs; failure/recovery behavior; evidence limits; source/version/hash table; glossary; and a focused acceptance checklist. References may use relative paths within their owner project and absolute authority paths for sibling/canonical sources.

Before declaring a volume ready:

1. Verify assertions against current source, not just the previous guide.
2. Record examples and expected results in isolated outputs; avoid modifying reviewed runs.
3. Check diagrams, color samples and caption provenance. Embed essential visuals for offline use.
4. Check commands, links, configuration values and native filenames.
5. Separate static checks, rendered documentation, live application behavior and publication status.
6. Record review date, source hashes and unresolved findings. Refresh only the material that changed.

## Known gaps to keep visible

- Native import/visual acceptance for Windows Terminal, SiYuan and Typora is not established by CSS/JSON parsing or HTML previews.
- PowerPoint no-repair opening/rendering is recorded; chart data editing and save/reopen need separate acceptance.
- Real VTracer tracing remains different from stub-based tests.
- Additional application exporters, light variants and broader accessibility analysis are deferred; do not document them as existing features.
- The prior Writerside snapshot needs deliberate reconciliation with the current consolidated engine and subsequent repair records.
- Token budgets should be reviewed against actual component needs as targets evolve. Reaching a nominal count is not a completion criterion.

The next concrete authoring batch should be **09, 01 and 02**. It provides a source-checked reference, a usable workflow and explanations of the two failures that most clearly demonstrate the project’s complexity.
