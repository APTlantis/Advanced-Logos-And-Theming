# Eight themed visual documentation volumes

**Documentation snapshot: 31 October 2026.** Open [the offline collection](index.html) to explore eight topic volumes, 192 editable slides, eight 15-page illustrated guides, and preserved native specimens. The engine remains a **0.1.0 local pilot**.

Each topic directory contains a 24-slide PPTX, matching slide PDF, separately typeset guide PDF, Markdown guide, native slide previews, independently rendered PDF pages, and figures. The `artifacts/` directory preserves complete generated target trees, including local dependencies, inventories, and original PowerPoint sample/template pairs.

| Theme | Volume |
| --- | --- |
| [rpm-blackgold](rpm-blackgold/index.html) | From artwork to applications |
| [apt-crystal](apt-crystal/index.html) | Finding the canonical 32 |
| [apt-factor](apt-factor/index.html) | Turning colors into interfaces |
| [dnf-caddy](dnf-caddy/index.html) | Themes on the web |
| [dnf-clojure](dnf-clojure/index.html) | Writing and editing in color |
| [dnf-cloudflare](dnf-cloudflare/index.html) | Exploring the visual collection |
| [dnf-flathub](dnf-flathub/index.html) | Artwork, conversion, and custody |
| [apt-swift](apt-swift/index.html) | Operating and maintaining safely |

## Reading and visual treatment

The decks lead with artwork, exact canonical swatches, actual per-target token counts, and a traced primary color. Twelve topic slides explain implemented behavior; four review slides address decisions, failures, evidence, and recovery. The final slides provide a recap and source references. Speaker notes carry substantive explanations and source hashes.

The guides expand the slides with prerequisites, algorithms and contracts, worked-example procedures, actual output galleries, recovery guidance, a glossary, and acceptance checklists. Chart values, fictional scenes, and generated UI content remain illustrative. Browser previews establish their measured rendering environment, not downstream native application acceptance.

The original PowerPoint theme, master, layout, and media package parts remain byte-for-byte preserved. Native ring artwork is reused on the covers. New slides intentionally adapt geometry and add editable diagrams, canonical swatches, data tables, and recorded colors beyond the twelve Office scheme slots. The canonical 32 and theme scheme are unchanged. `source/specifications/` records the design treatment and font policy.

## Evidence and boundaries

- [Delivery manifest](validation/delivery.json): final inventory and acceptance status.
- [Package checks](validation/package-checks.json): deck counts, editable objects, design preservation, PDFs, and input preservation.
- [Command evidence](validation/commands.json): bounded import, generation, Atlas, conversion, and finishing-preview exercises.
- [Focused tests](validation/focused-tests.log): pipeline and converter suite output.
- [Native PowerPoint](validation/native.json): repair-disabled read-only opening, rendering, PDF export, and text bounds.
- [Browser specimens](validation/specimen-browser.json): actual local artifacts, no external requests, and browser errors.
- [Visual review](validation/visual-review.json): inspection coverage and final observations.
- [Figure provenance](validation/figure-provenance.json): generated figure hashes and their recorded input basis.
- [Input baseline](validation/input-inventory.json): 2,848 original files across eight selected runs.

The default installed ImageMagick Q16 build exited with Windows status `-1073740791` when reading Crystal. Validation selected the already-installed Q16-HDRI build using a process-local PATH. The system PATH and installed dependencies were not changed. The sandbox input-access failure and initial executable failure are retained in separate command-attempt records. Final exercise and test results use the recorded successful environment.

Manual PowerPoint edit/save/reopen, downstream theme import or activation, installation, publication, live hosting verification, and fresh tracing-fidelity review are **not performed**. Historical acceptance records retain their original dates. This collection changes no server routes or public copies.

## Reproducibility and recovery

Authoring dependencies are separate from pipeline runtime dependencies: Python with python-pptx, Pillow, lxml, reportlab and pypdf; native PowerPoint for rendering/PDF export; Poppler for independent PDF rendering; bundled Node/Playwright plus installed Chromium for specimen captures. Arial and Courier New come from the supplied design. No dependency installation or vendor rebuild is required by the authoring scripts in this environment.

For a future edition, copy these scripts into a **new sibling collection** and review paths/date/content deliberately. `prepare.py` refuses an existing baseline. `build.py` refuses existing decks unless `--replace-drafts` explicitly selects the current authoring drafts. Keep the earlier ZIP and receipts. Do not use replacement flags on historical collections or replace an input baseline to hide changed sources.

Authoring order: `prepare.py`; `render_native.ps1 -Templates`; inspect source renders; `capture_specimens.cjs`; `build.py`; `render_native.ps1`; `verify_exercises.py --attempt=UNIQUE`; `verify_delivery.py --render-pdfs`; `contacts.py`; inspect final slides/pages; `finalize.py`. Browser tools use `VOLUME_NODE_MODULES` for the bundled Node package directory and `PLAYWRIGHT_BROWSERS_PATH` for installed browser binaries. Exercise validation requires the project interpreter and a working `magick` on its process PATH. Run scripts from the project root with the appropriate prepared environment.

The source snapshot is a raw, hashed reference collection, not a complete standalone copy of the repository or its historical evidence. Original relative links inside those source files retain their source context. The authored collection navigation and guides have their own checked portable links.

Project identity, ownership, lifecycle, and physical roots are unchanged. Direct project navigation is updated; parent manifests and drive indexes require no change. The original documentation-suite plan remains available and records how these volumes support its longer written program without claiming every proposed volume complete.
