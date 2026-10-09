# Testing, validation and future coverage

Source review: **2026-10-09**, engine **0.1.0**. This reference explains the checks that exist, why they matter, how to run them safely, what evidence they produce and what useful coverage remains to add. It is a strategy/reference, not a claim that every proposed check has passed. [VALIDATION.md](VALIDATION.md) indexes dated results; [OUTPUT-REFERENCE.md](OUTPUT-REFERENCE.md) explains the artifacts being tested.

## Contents

- [Quality model and evidence levels](#quality-model-and-evidence-levels)
- [Current automated suite](#current-automated-suite)
- [Browser, plotting and packaging checks](#browser-plotting-and-packaging-checks)
- [Native application acceptance](#native-application-acceptance)
- [Migration, governance and delivery checks](#migration-governance-and-delivery-checks)
- [Choosing checks for a change](#choosing-checks-for-a-change)
- [Proposed tests and priorities](#proposed-tests-and-priorities)
- [Evidence recording and maintenance](#evidence-recording-and-maintenance)

## Quality model and evidence levels

The central risks are source loss, changed canonical identity, unsuitable role assignment, unreadable derived tokens, invalid native formats, missing package resources and rendering that differs from the intended composition. A good test states an observable property and catches a plausible failure; a screenshot or a parser alone cannot answer all of these questions.

| Level | What it answers | What it cannot establish |
|---|---|---|
| Color/math and contract tests | Do algorithms, IDs, fields, budget limits and declared checks behave as expected? | Aesthetic quality or actual host behavior |
| Preservation/determinism tests | Did bytes/values remain unchanged, and does repetition agree in this environment? | Cross-version/platform determinism or recovery after every OS failure |
| Native-format/package inspection | Does JSON/TOML/XML/ZIP parse and contain expected parts/resources? | Host import, rendering or editing |
| Offline Chromium | Do tested pages create tokens, preserve source, navigate and render offline? | All browsers, assistive technology or native editor import |
| Matplotlib Agg | Does the real plotting library load the style and render the shared fixture? | Interactive GUI, other backends or notebook integration |
| Native application opening/rendering | Can a specified app/version open/render an identified file without repair? | Manual edit/save/reopen, installation, every frontend or release |
| Native round trip / installation | Do recorded workflows survive edits/reopen or installation? | Marketplace acceptance, publication or all deployments |
| Delivery/recovery | Are particular hosted files served and archives restorable with matching hashes? | Current generator quality or continued future availability |

Every run should preserve input SHA-256, target subset, config/settings, command, environment versions, exit/stdout/stderr and output identities. A historical passing result is valid evidence for that historical artifact. Later generator changes need their own evidence; earlier records should remain unchanged.

## Current automated suite

There are **29 unittest methods**: 16 pipeline, five converter, five syntax/chart quality and three SVG quality tests. The inventory below names methods exactly as implemented. Each method may contain many assertions; 29 does not mean 29 isolated risks or 29 native workflows.

Run from the repository root with the project environment and ImageMagick available:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

This uses temporary fixtures and does not install themes or regenerate the hosted collection. ImageMagick is exercised by image/converter tests. The all-target export test uses the packaged PowerPoint reference and local Prism assets, but does not open native applications. To focus during diagnosis:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_pipeline.py -v
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_logo_tools.py -v
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_visual_quality.py -v
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_svg_quality.py -v
```

Managed Windows sandbox path-resolution/temp-file errors have prevented previous runs. Distinguish those infrastructure failures from assertions: retain the failure and rerun in an authorized environment that can access the project/temp paths. Do not modify product behavior to conceal an environment failure. Passing one rerun proves that environment's run, not that the sandbox problem has disappeared.

### Pipeline tests: algorithm, adaptation and transaction contracts

Source: [`tests/test_pipeline.py`](../tests/test_pipeline.py), `PipelineTests`. Most tests share a synthetic exactly-32 gold/cyan palette; it makes missing conventional hues and hue-aware mappings observable without depending on a large artwork file.

| Method | Assertions and reason | Practical limit |
|---|---|---|
| `test_math_and_vector_conversion` | NumPy RGB→OKLab agrees with ColorAide on primaries, white and a dark sample to 1e-7; catches matrix/transfer errors | Small fixed sample, no exhaustive color-space/property test |
| `test_selection_observed_exact32_and_determinism` | Exactly 32 observed hex values retained and repeated selection identical | Exactly-32 fixture, not all image clustering/sampling paths |
| `test_semantics_hue_suitability_overrides_and_findings` | Warm warning selection, missing conventional hue finding, valid override and rejection of missing ID | Does not certify all semantic roles on every hue family |
| `test_near_black_noise_does_not_consume_visible_color_slots` | Redundant ≤12-channel black candidates collapse to one, weights preserved, selection observed/deterministic; sparse grayscale retained | Synthetic candidates rather than diverse photographed noise |
| `test_surface_identity_is_separate_from_black_anchor` | Identity surface differs from absolute black; black ANSI anchor remains; darkest/override/grayscale/bright fallback and invalid mode checked | Does not prove the chosen surface is aesthetically best |
| `test_gamut_and_hue_derivation` | Saturated-red lightness derivation gamut-maps, records original requested hue and measured hue stays within 1.5° | One difficult source, not exhaustive quantization/hue behavior |
| `test_native_exports_and_canonical_immutability` | All ten defaults export within budget, with zero declared failures on fixture and unchanged canonical dictionary; format-specific checks below | Static/native-file inspection, no native app opening |
| `test_import_roundtrip_determinism_and_overwrite` | Import retains ID→hex values, existing destination refused without flag, explicit replacement produces identical full file hashes, review contains no HTTPS link | Repeated import in one environment; no fault injection during final rename |
| `test_strict_mode_still_writes_failed_results` | Bright background override triggers exit 2 and leaves complete native files/run with failures | Checks intended contrast-failure path, not every error path |
| `test_powerpoint_template_failure_preserves_previous_output` | Mocked template failure during overwrite leaves prior run/operator note byte-identical | Failure before final replacement, not every filesystem interruption |
| `test_powerpoint_reference_hash_guard` | Missing/corrupt bundled reference rejected | Reference bytes only, not arbitrary valid-looking replacement validation |
| `test_powerpoint_timestamp_type_namespace_is_preserved` | Undeclared W3CDTF QName rejected; normalization repairs namespace and is idempotent | Core metadata case, not complete Open XML conformance |
| `test_powerpoint_metadata_repair_preserves_other_package_bytes` | Repair creates new copy, preserves source/slide/workbook bytes, validates timestamps and refuses existing destination | Small synthetic package; native opening separate |
| `test_transparency_monochrome_and_insufficient_colors` | Fully transparent magenta excluded; partial alpha weights exact; visible count preserved; grayscale findings and <32-color error | Small PNG fixture; ICC/CMYK/orientation/multiframe cases still need more tests |
| `test_invalid_input_config_and_nonpipeline_overwrite` | Bad TOML/unknown config rejected; nonpipeline directory's important file survives explicit overwrite | Guard cases, not complete malformed configuration matrix |
| `test_json_envelope_and_bom_configuration` | BOM config/palette accepted; stdout parses as one envelope with tool, target subset and empty errors | Success envelope; external CTS schema validation is separate |

The all-target method is an integration contract check, with these additional assertions:

| Target | Existing checks |
|---|---|
| Windows Terminal | 21 JSON properties, hex serialization, warm yellow/cyan hue suitability |
| Alacritty | Five TOML groups, eight normal/eight bright fields, selection/yellow values |
| Notepad++ | XML root, exact three lexers, unique style IDs per lexer, valid foreground hex, selection mapping and Python keyword class |
| Sublime Text | Selection foreground and 16 valid-hex scope rules |
| SiYuan/Typora | CSS variable references declared and balanced braces; SiYuan ZIP exact five members and dark metadata |
| PowerPoint | Twelve standalone slots match embedded theme; valid core QName; 23 slides/14 layouts; reference hash; slide/relationship/workbook bytes preserved; known chart substitutions; native table retained; POTX differs only by main content type |
| SVG/syntax/charts | Expected example counts; SVG namespace/title/token-only fill/stroke; Prism classes/local scripts/no authored token spans; nine ordered single-source scale stops and style cycle |
| Budget floors | 28 SVG, 37 chart and 22 syntax minimums accepted; one below rejected; terminal budget 19 rejected |

The suite verifies exported declared failures on the fixture but largely uses the production contrast function. A genuinely independent reference calculation and broader palette corpus would strengthen confidence. Balanced CSS braces do not constitute a full CSS parser or host selector validation.

### Converter tests: real ImageMagick, stubbed tracing

Source: [`tests/test_logo_tools.py`](../tests/test_logo_tools.py), `LogoToolTests`. A transparent 80×40 logo fixture is created with actual ImageMagick in a path containing spaces.

| Method | What and why | Limit |
|---|---|---|
| `test_ico_frames_and_collision` | Requested 16/32/256 frames decode; contain-fit corner remains transparent; existing output skipped byte-identically; invalid size rejected | Does not check every fit/filter/frame size or Windows icon display |
| `test_svg_embed_preserves_bytes_and_dimensions` | Wrapper dimensions 80×40; decoded base64 exactly equals original PNG bytes | PNG wrapper path, not all MIME/orientation inputs |
| `test_svg_normalize_and_trace_dependency` | Explicit normalization resize changes width; unavailable tracer returns setup error and no output | Real normalization but no actual VTracer process |
| `test_batch_output_and_collision_guards` | Unsafe nested batch destination rejected in dry-run; spaced external destination works; same-stem competing inputs rejected | Representative placement/name guards, not all Windows path aliases |
| `test_trace_output_contract_with_stub` | Stubbed version/output contract produces SVG path output through trace mode | A stub tests orchestration, not tracing fidelity or binary CLI compatibility |

There is no dedicated automated atlas test in the 29-method suite. Historical broad verification executes atlas generation, which proves the script completed against those assets, not link safety, accessibility, catalog escaping or rendering correctness.

### Syntax/chart resource and output tests

Source: [`tests/test_visual_quality.py`](../tests/test_visual_quality.py), `VisualQualityTests`.

| Method | What and why | Limit |
|---|---|---|
| `test_pinned_vendor_dependencies_and_integrity` | Prism version 1.30.0, required components before dependents, valid hashes and corrupted asset rejection | Integrity/dependency metadata, not browser tokenization |
| `test_source_languages_and_substantial_examples` | Twelve samples, 25–50 lines; JSON/TOML parse and Python compiles | Other samples not compiled/run; Python compile does not execute it |
| `test_shared_chart_values_and_svg_marks` | 12 bars, six 24-point lines, eight 12-cell rows; distinct markers/dashes; emitted fixture exact; bar attributes, line coordinates and heatmap values match | Uses fixed data and coordinate formula; not generalized arbitrary dataset layout |
| `test_source_is_escaped_and_generated_assets_match` | HTML sample script escaped, copied sources byte-identical, vendor integrity, JavaScript compatibility page identical | Dynamic nonexecution/source preservation verified separately in browser |
| `test_generated_css_references_are_declared` | Generated Prism/gallery custom-property uses resolve | No full CSS/host selector acceptance or accessibility audit |

### SVG contract tests

Source: [`tests/test_svg_quality.py`](../tests/test_svg_quality.py), `SVGQualityTests`, using the minimum 28-token budget.

| Method | What and why | Limit |
|---|---|---|
| `test_local_references_and_editable_vector_contract` | Six compositions, legacy filenames retained, 1200×800 canvas, title/desc/ARIA, unique IDs, groups, twelve symbols; no active/raster/external content; local IDs resolve; illustration clip/gradient present | Structure/editability affordances, not native editor operations or arbitrary-SVG sanitization |
| `test_paints_remain_exported_tokens_at_minimum_budget` | Literal fill/stroke/gradient stops all belong to tokens; gallery CSS variables resolve | Opacity/interpolation/display pixels may differ from literal colors; decorative contrast not certified |
| `test_determinism_and_unchanged_chart_canvas` | Two fresh SVG outputs byte-identical, input token dictionary unchanged, shared chart primitive still 960×540 | Same environment; fonts/rendering differences not covered by byte equality |

## Browser, plotting and packaging checks

These tools are additional acceptance checks, not automatically part of unittest discovery. Use fresh output directories; they add screenshots/rendered files/evidence to the supplied run. Running them on an old acceptance pilot would mutate that pilot. Node is only needed for browser verification; Matplotlib only for its renderer. Do not use Python `-O` for these checks: tools use `assert`, which optimization disables.

### Fresh local fixture

From the repository root, choose a new name in place of `docs-quality-review-2026-10-09` if it already exists:

```powershell
.\Invoke-AptTheme.ps1 import pilot\visual-quality-2026-10-09\palette.toml --output pilot\docs-quality-review-2026-10-09 --name 'Black-Gold review' --targets svg,syntax_highlighting,data_visualization --strict --json
```

This preserves the reviewed canonical colors and original palette input bytes while generating current examples. It intentionally does not exercise image extraction or every application exporter. The command is a repeatable recipe; this documentation edit does not claim that example directory has been generated.

### Offline Chromium

Tool: [`render_visual_previews.cjs`](../tools/render_visual_previews.cjs). Invocation contract:

```text
node tools/render_visual_previews.cjs RUN PLAYWRIGHT_MODULE [CHROMIUM_EXECUTABLE]
```

Supply the installed Playwright module path and optionally the actual browser executable. See [visual validation commands](VISUAL-TARGETS.md) for the recorded local runtime paths. Browser/context versions are written into evidence. The tool discovers present SVG/syntax/chart target directories through their `tokens.json.examples`; it does not require all three targets.

Checks include:

- HTTP/HTTPS blocked; no attempted requests or console/page errors permitted. This is the tool's web-request boundary, not an OS firewall proof for every protocol/process.
- SVG text bounds against viewBox, and overlapping text boxes for the composition target; screenshots at actual canvas size. Loaded gallery images, local paths, exact download bytes and 390px gallery layout are verified.
- Twelve actual Prism grammars registered and producing tokens, code text preserved after highlighting, representative leaf-token computed colors matching exported roles, only vendor executable scripts, and no sample-code execution flag.
- Index/previous/next links resolve; keyboard Tab/Enter reaches the language index; source downloads match file hashes; focusable code has contained overflow at 390px.
- All 96 heatmap table cells equal the shared fixture; optional root gallery is checked when present. JavaScript-disabled markup remains readable.

Evidence and PNG screenshots are written into the run. Inspect screenshots as well as assertions: a text bounding-box test can miss occlusion by graphics, weak hierarchy, tiny text, some overlaps or poor composition. Current Chromium success is not Firefox/WebKit/native SVG importer acceptance or a screen-reader test. Representative computed token colors do not exhaust every grammar token/context.

### Actual Matplotlib Agg renders

Tool: [`render_matplotlib_examples.py`](../tools/render_matplotlib_examples.py).

```text
python tools/render_matplotlib_examples.py RUN [ISOLATED_DEPENDENCIES]
```

The optional dependency directory is inserted before import. Agg is selected explicitly. The tool reads emitted tokens/data/scale/style, loads the style in a context, asserts axes surface and six series colors, renders all three kinds, and rejects any captured Matplotlib diagnostics. It applies hatches, six markers/dash patterns, direct values, labels, line legend and labeled heatmap colorbar from the same fixture.

Actual bar heights, plotted line y-values and image cells must equal the fixture. Labels/titles/ticks/legend/colorbar bounds must lie inside the figure canvas. Output is `data_visualization/matplotlib-{bars,lines,heatmap}.{png,svg}`, plus root `matplotlib-render-evidence.json` recording version/backend, data hash, counts, style assertions, diagnostics and bounds. The renderer provides label fallbacks for older fixture metadata; that compatibility does not make older pilots richer.

The 2026-10-09 recorded pass used Matplotlib 3.11.2/Agg and visually reviewed previews. Current checks do not automatically compare raster images to approved baselines, reject every in-plot overlap, test other backends or validate arbitrary new value ranges. Parser diagnostics/bounds pass is narrower than universal chart accessibility.

### Wheel resource and installed-package verification

Tool: [`verify_visual_package.py`](../tools/verify_visual_package.py).

```text
python tools/verify_visual_package.py WHEEL INSTALL_DIRECTORY PALETTE OUTPUT [TARGETS]
```

Build a wheel first, then install it with pip `--no-deps --target` into a new isolated directory. These are Python-package verification operations, not application theme installation. Example using an existing environment with build dependencies available:

```powershell
.\.venv\Scripts\python.exe -m pip wheel . --no-deps --no-build-isolation --wheel-dir output\docs-wheel-check
.\.venv\Scripts\python.exe -m pip install --no-deps --target output\docs-wheel-install output\docs-wheel-check\aptlantis_theme_pipeline-0.1.0-py3-none-any.whl
.\.venv\Scripts\python.exe tools\verify_visual_package.py output\docs-wheel-check\aptlantis_theme_pipeline-0.1.0-py3-none-any.whl output\docs-wheel-install pilot\visual-quality-2026-10-09\palette.toml output\docs-wheel-run svg,syntax_highlighting,data_visualization
```

Use fresh names if any paths exist; these commands are recipes, not authorization to overwrite an arbitrary folder. Build isolation is disabled in this recipe to use already available build tooling; it does not test a clean dependency resolver. The isolated install still uses the invoking interpreter's dependencies.

The verifier compares 31 vendor/source resources across checkout, wheel and installation, plus every top-level engine `.py` file. It imports from the installed directory and asserts that `apt_theme.__file__` belongs there, rechecks vendor hashes, invokes strict palette import and writes `wheel-verification.json` with wheel/resource/engine hashes and Python version. Default targets are syntax/chart; the optional argument includes SVG. PowerPoint reference packaging has separate dated evidence; this visual-resource verifier does not explicitly enumerate the PPTX/receipt or exercise PowerPoint unless requested through target selection. Sdist and fully dependency-isolated installation are useful future gates.

`tools/vendor_prism.py` is a maintainer resource-refresh tool with network activity, not an offline verification/generation step. A vendor update should verify tagged upstream provenance, license, dependency order, copied resources, browser behavior and packaging together.

## Native application acceptance

Native checks must name app/version, OS, exact artifact hashes, method and scenario. Generating a file does not authorize installation/activation/publication. Where these workflows require user changes, use an explicitly authorized, reversible test setup. Record “pending” when a scenario has not been performed. An error/repaired opening must never be reported as clean import.

| App/type | Useful acceptance scenarios | Current evidence boundary |
|---|---|---|
| Windows Terminal | Load scheme, ANSI normal/bright test, cursor, selection, opaque/transparent settings, terminal application overrides, restore config | Native application acceptance remains pending in generated records |
| SiYuan | Load dark theme in versioned test workspace; docks/lists/dialogs, editor/code/selection, hover/active/disabled, search/settings, target frontend | Packaging/selectors are checked; native installation/frontend acceptance pending |
| Typora | Load CSS, representative Markdown, code language scopes, sidebar/dialog, selection/link/input, export/print where claimed | Static CSS/report evidence; host acceptance pending |
| PowerPoint | Open PPTX and POTX with repair disabled; render all 23 slides; create through 14 layouts; edit text/table/chart/workbook; save/reopen and re-render | Opening/rendering recorded in template acceptance; manual round trips/layout creation pending |
| Alacritty | Import TOML, normal/bright ANSI, cursor text/background, selection, parent/later import overrides | Static native configuration checked; host load/render pending |
| Notepad++ | Load XML; Python/C++/JSON samples, style precedence, selection both with/without enableSelectFgColor, braces/folds/gutter/change history | Three lexers/globals checked statically; native behavior pending |
| Sublime Text | Load scheme; installed grammar scopes, caret/gutter/find/selection/inactive selection, invalid/diffs; confirm UI theme boundary | Scope JSON checked; host behavior pending |
| SVG | Open six files in Inkscape/Illustrator/Office where claimed; symbol/pattern/clip/gradient/fonts; edit/export/save/reopen | Chromium render verified; native importer/editor/print acceptance pending |
| Prism | Embed bundle in intended host, file paths/CSP, token nesting, fonts, selection, keyboard and assistive technology | Offline Chromium fixture verified; specific site/editor integration pending |
| Matplotlib | Intended notebook/backend, style precedence/restore, data ranges, export DPI/fonts and grayscale printing | Agg static fixture renders verified; interactive/other integration pending |
| ICO | Inspect Windows file/executable icon rendering at multiple scales; cache refresh and transparency | Frames decode through ImageMagick; native shell display pending |

For a PowerPoint round trip, keep the generated original hash, edit a duplicate, change a table cell and chart data, create slides from every layout, save to a new file, close/reopen with repair disabled, inspect the edits and capture renders. Package bytes are expected to change on an Office save; test preserved meaning, links and editable objects rather than requiring byte identity after native edits.

Native opening of particular PowerPoint files has already been recorded; do not reset that evidence to “never tested” because generated JSON conservatively says pending. Conversely, do not promote it to successful chart editing or installation. [POWERPOINT.md](POWERPOINT.md) and the receipt identify the exact boundary.

## Migration, governance and delivery checks

These are separate operational gates, not routine unit-test runners.

| Tool / record | What it does | Why to treat it separately |
|---|---|---|
| [`tools/verify.py`](../tools/verify.py) | Broad historical retirement gate: current suite, sibling SESM and legacy suite, atlas, CTS contract lint/schema, SESM asset validation, all-target pilot overwrite/determinism, contrast recalculation, manifest/reference/archive checks; writes `migration/acceptance.json` | Executes atlas/metadata/pilot writes, including `--overwrite`, and depends on sibling/City Hall/A-drive paths. Hardcoded historical dates/policies make it unsuitable as a harmless generic regression command. Read/review scope before using; do not run it merely to check documentation. |
| [`tools/migrate.py`](../tools/migrate.py), [migration recovery](../migration/README.md) | Source inventory, archive/staging/restore identities and consolidation operations | Migration is mutating recovery work, not a unit test. Do not rerun retirement operations for routine exporter edits. |
| [`tools/governance.py`](../tools/governance.py) | Writes project/portfolio discovery records | Record generator, not read-only manifest validation. Avoid replacing newer records from historical templates. |
| CTS/WGS schema/lint tools | Check command/manifest contract syntax and expected envelopes | Requires canonical City Hall tooling; proves structural conformance, not runtime adoption or release |
| Sibling SESM suite and safe-profile validator | Validate independent metadata tooling/schema/preservation and exact asset profile | Outside theme engine ownership; not automatically part of the 29 tests |
| [Hosting evidence](../migration/theme-hosting-acceptance.json) | Recorded allowlist, local delivery/download/security behavior of served collection | Serving reviewed files is a different gate from generator correctness or new pilot publication |
| [Git publication evidence](../migration/git-publication.json) | Recorded remote/recovery identities and LFS checks | Git state/publication does not establish native visual acceptance |

Archive validation should restore a full archive into a fresh bounded directory and compare inventory/path/size/hash, including hidden/history files where the archive promises them. A matching ZIP hash alone proves archive identity, not restore success. Do not mutate original files to run a preservation test. Public output copies require their separate authorized delivery workflow.

## Choosing checks for a change

| Change | Appropriate verification |
|---|---|
| Extraction/color math/semantic policy | Focused pipeline tests; image corpus/fixtures; new dated import and image-generation comparisons; canonical/source preservation and final contrast |
| Native field mapping/CSS selectors | Pipeline export tests; actual file parsing/mapping assertions; affected native application scenarios |
| PowerPoint adaptation/reference | Pipeline tests, hash guard/part comparison/package checks; no-repair native opening/renders; edit/layout round trips if behavior changes |
| Prism source/grammar/CSS | Visual tests plus pipeline safeguards; vendor integrity/dependency order; all twelve offline browser examples, download/text/color/navigation; installed wheel |
| Chart fixture/style/layout | Visual tests plus shared-values/Agg/browser checks; inspect patterns/legend/scale/table and clipping; canonical budget/contrast |
| SVG composition/gallery | SVG tests plus pipeline/converter tests; all six browser views/downloads/narrow layouts; visual review; installed-wheel SVG generation |
| Converter invocation/normalization | Converter suite; actual binary integration where changed, preservation and collision checks; native display if claiming it |
| Package rules/dependencies | Build/inspect wheel and sdist; isolated installed generation; reference/resource hashes; clean dependency environment when available |
| Documentation only | Verify claims against code/evidence, exact paths/links/anchors, target/method counts, parse TOML records, contract lint where changed; no need to regenerate reviewed themes |

After code changes, project instructions require focused pipeline and converter tests. Broaden with the affected runtime/native gates when the risk warrants them. Do not repeatedly regenerate or run unrelated mutating retirement tools once relevant checks pass.

## Proposed tests and priorities

Everything in this section is **proposed**, not counted in the 29-method suite. Priorities favor failures that could destroy work or produce misleading acceptance over tests that mirror implementation details.

### Priority 1: preservation and native correctness

| Proposal | Test design / pass condition | Reason and cost |
|---|---|---|
| Final replacement fault injection | Inject failure after old output rename and during stage rename; prior inventory restored exactly; no partial new destination | Exercises currently untested rollback branch; small bounded filesystem test |
| Source/destination safety matrix | Source-inside-output, same path, files vs dirs, duplicate targets, malformed budgets/settings, symlink/junction aliases where supported; errors preserve all originals | Overwrite guard is high impact; small tests plus versioned Windows integration |
| Actual no-repair native smoke matrix | Versioned test artifacts opened by intended apps; no repair/errors; native field behavior recorded | Parser success misses host behavior; needs apps and authorized test profiles |
| PowerPoint edit/save/reopen | Duplicate template artifact; edit chart/workbook/table/text and instantiate every layout; clean reopen and expected edits/render | Closes specific known pending gate; manual or bounded app automation |
| Package completeness across all assets | Wheel+sdist explicit inventory of engine, PPTX receipt/reference, Prism/sources; corrupt/missing resources fail without replacing previous run | Visual verifier covers 31 resources but not the complete ship surface explicitly |
| Independent contrast reference | Compute luminance/ratios independently from exported RGB; corpus of palettes checks thresholds and declared pair names | Avoids production math validating itself; deterministic small numerical tests |

### Priority 2: input diversity, usability and rendering

| Proposal | Test design / pass condition | Reason and cost |
|---|---|---|
| ICC/CMYK/orientation/frame corpus | Small profiled/unprofiled CMYK, oriented image, 16-bit TIFF, multiframe GIF/TIFF, transparent-all and partial-alpha inputs; known normalized values/dimensions/error contracts and original hash | Exercises normalization claims beyond current PNG fixture; requires carefully provenance-recorded fixtures |
| Sample/cluster selection repeatability | Input above sample limit, repeat seeds, representative-membership assertion against normalized sample, weighted population and bounded resources | Current selection test starts with exactly32 candidates; larger clustering/sampling deserves direct coverage |
| Palette family corpus | Gold-only, cyan-only, grayscale, dark/bright/extreme saturated palettes; canonical unchanged, hue/fallback/collision diagnostics, valid budgets and final contrast | Narrow palettes are intentional; catches assumptions about conventional hues |
| Browser engine/font matrix | Chromium plus Firefox/WebKit, known fonts/fallback, 390px/large zoom; exact downloads/text; keyboard navigation and no network/errors | Rendering/file-download behavior and text geometry vary by browser/font; moderate optional runtime cost |
| Accessibility audit | Screen reader and keyboard code scrolling/navigation; meaningful labels, focus, zoom and overflow; chart exact table access | Existing keyboard/ARIA checks are partial, not an accessibility certification |
| Approved visual regression baselines | Versioned screenshots with pinned fonts/browser/DPI; thresholded diff plus human review; separate geometry assertions | Detects absent/occluded shapes and composition drift; avoid brittle anti-alias-only failures |
| Chart semantics and layout expansion | Verify zero baselines, direct labels, hatches/dashes/legend correspondence; table labels/values; numeric bounds and generalized long-label/range cases if supported | Current fixed fixture values are checked; style aesthetics/overlap and generalized data are narrower |
| SVG importer matrix | Six exact files imported/edited/exported in supported editors; local references and geometry survive; compare meaning/render within declared tolerance | Browser acceptance does not prove symbol/clip/gradient support in editors |
| Real VTracer integration | Pin binary/version/hash; execute traced fixture; inspect path presence/bounds/color and rendered comparison; retain source | Existing stub can miss real CLI incompatibility and quality loss |
| Atlas correctness | Temporary catalog/assets; link existence, escaped labels, missing assets, duplicate palette hex handling, encoding, DOM/keyboard/render checks | Atlas currently has no focused suite and directly writes a fixed path; testing may require an isolated root seam |

### Priority 3: maintainability, portability and delivery

| Proposal | Test design / pass condition | Reason and cost |
|---|---|---|
| CLI subprocess/envelope schema | Success/warning/processing failure/strict failure/argparse cases through launcher and console command; stdout JSON only, stderr progress, exit propagation | Current tests invoke `main` directly and only parse success envelope; uses real entry points |
| Clean installed environment | Supported Python versions, resolver installs pinned/allowed deps in fresh env, wheel CLI runs without checkout, no generator network requests | Isolated resource directory still shares interpreter dependencies; catches undeclared requirements |
| Resource/performance limits | Representative large images; recorded time/peak memory; graceful failures for truncated files and invalid settings | Sample limit bounds analysis sample, not total decode memory; thresholds should be environment-aware |
| Structured fuzz/property cases | Valid byte triples and palette/config mutations; invariant preservation, finite outputs and understandable failure envelopes | Broadens edges without storing many large files; only meaningful invariants should be enforced |
| Concurrency/recovery interruption | Explicitly define concurrent writer policy first, then test locking/refusal or safe serialization and interruption recovery | Current implementation does not promise concurrent/power-loss safety; don't create tests against an invented contract |
| Documentation drift checker | Assert all target IDs/budgets/artifact links and test methods appear in reference; validate local links/anchors and manifest documentation paths | Fast maintainability guard as system grows; report explanatory changes, not just counts |
| Delivery/recovery drill | Authorized staged update/rollback, allowlist and downloads/hash checks; fresh archive restore comparison | Operational confidence; separate from routine local tests and requires defined publication scope |

Do not add tests that simply duplicate every implementation formula or snapshot entire reports without an identified risk. For visual changes, combine stable contract assertions with reviewable previews; for preservation, use byte hashes; for native round trips, use object/value semantics. When generalizing a fixture or adding an exporter, first document the supported input/output contract and its limits.

## Evidence recording and maintenance

Key current and historical receipts:

| Record | Scope |
|---|---|
| [SVG quality, 2026-10-09](../migration/svg-quality-acceptance-2026-10-09.json) | 29 focused tests, six new detailed SVGs, offline Chromium/gallery/download/geometry/narrow checks, preserved earlier pilot hashes, installed-wheel SVG generation |
| [Syntax/chart quality, 2026-10-09](../migration/visual-quality-acceptance-2026-10-09.json) | Then-current26 suite, twelve real Prism examples, three richer authored charts, actual Agg PNG/SVG renders and 31 packaged resources |
| [PowerPoint template](../migration/powerpoint-template-acceptance.json) | Then-current21 suite, 23-slide/14-layout reference, package preservation, wheel inclusion and native no-repair opening/rendering; manual edits pending |
| [Earlier visual targets](../migration/visual-target-acceptance.json) | Earlier20 suite, earlier diagrams/authored-token syntax/smaller chart fixtures; superseded implementation, preserved evidence |
| [Editor targets](../migration/editor-target-acceptance.json) | Static native editor format checks; host acceptance pending |
| [PowerPoint metadata repair](../migration/powerpoint-metadata-repair.json) | Earlier four-slide copies, metadata-only repair and native opening/rendering |
| [Migration acceptance](../migration/acceptance.json) | Dated consolidation/retirement/source/archive/contract gate |

The counts differ because the suite grew. Do not edit an older receipt's count, screenshots or hashes to imply it ran today's code. The source suite's current inventory and the latest dated execution result are distinct facts.

For each fresh verification, record:

1. Date/timezone, source revision or file hashes, scope and commands with cwd, exit/stdout/stderr.
2. Interpreter/library/renderer/native app versions and environment limitations.
3. Input/config/reference/vendor hashes and output path/hash inventory; source/canonical preservation comparison.
4. Assertions, diagnostics, screenshots and human visual findings, including failures and repairs.
5. Which native scenarios, installation/publication/recovery operations remain pending.

Keep new evidence beside a new dated pilot or in a new dated migration receipt; do not rewrite historical acceptance. If a renderer modifies the current run, take its final hash inventory after rendering, and keep generator-only and renderer-added artifacts identifiable. Record deterministic generator hashes separately from screenshot/render bytes that can vary with renderer metadata/fonts.

This documentation does not perform native installation, theme activation, hosted regeneration, publication, archive retirement or a Writerside refresh. Parent discovery records remain unchanged because ownership, identity and roots are unchanged. Update this reference when methods/tools/contracts change, and keep [VALIDATION.md](VALIDATION.md) as the concise result/evidence entry point.
