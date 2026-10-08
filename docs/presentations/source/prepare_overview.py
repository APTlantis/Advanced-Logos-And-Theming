"""Capture local overview evidence; this does not regenerate any theme."""
import hashlib
import json
from pathlib import Path
import tomllib
import zipfile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "docs/presentations/source"
REF = ROOT / "output/blackgold/powerpoint/aptlantis-black-gold-sample.pptx"
PAL = tomllib.loads((ROOT / "output/blackgold/palette.toml").read_text())["palette"]["canonical"]
SEM = json.loads((ROOT / "output/blackgold/semantics.json").read_text())
TOK = {t: json.loads((ROOT / f"output/blackgold/{t}/tokens.json").read_text()) for t in ("windows_terminal", "siyuan", "typora", "powerpoint")}
with zipfile.ZipFile(REF) as z:
    theme = ET.fromstring(z.read("ppt/theme/theme1.xml"))
ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
scheme = {e.tag.split("}")[-1]: "#" + list(e)[0].get("val", list(e)[0].get("lastClr", "")) for e in theme.find("a:themeElements/a:clrScheme", ns)}

slides = []
def add(title, lead, groups=None, table=None, note="", sources=(), kind="standard"):
    slides.append(dict(title=title, lead=lead, groups=groups or [], table=table, notes=note, sources=list(sources), kind=kind))

add("Logos and Theming", "From an image’s identity to useful application themes", [
    ["A detailed project overview", "Architecture, color decisions, application contracts and recoverable consolidation."],
    ["Black-Gold edition · 8 October 2026", "Built with the pipeline’s own PowerPoint theme."]],
    note="This overview describes the implemented local pilot, not an installation or publication. The supplied Black-Gold sample determines all twelve Office theme colors, Arial typography and the 16:9 canvas. The source artwork shown here is the preserved PNG for the Black-Gold run, not a newly generated visual. The separate document-suite plan specifies future deep dives; those volumes are not presented as already written.", sources=["README.md", "output/blackgold/powerpoint/aptlantis-black-gold-sample.pptx", "output/blackgold/source/apt-zig-dark-logo.png"], kind="cover")
add("One pipeline, three kinds of decisions", "A color can be faithful to an image and still be wrong for a role.", [
    ["Extraction", "Which observed colors represent the image?"],
    ["Meaning", "Which colors can serve as surfaces, text, accents and status signals?"],
    ["Application behavior", "Which combinations remain useful in each target’s native constraints?"]],
    note="The architecture separates extraction from semantics and target adaptation. This avoids conflating an image-derived candidate with a warning color or assuming the darkest sample must become the background. A terminal, document editor and presentation can share provenance while requiring different text and state combinations. The canonical palette stays unchanged when application tokens are derived.", sources=["Project-Proposal.md", "apt_theme/extraction.py", "apt_theme/semantics.py", "apt_theme/adaptation.py"])
add("Consolidation preserves the history", "The new projects organize work that grew in several places.", table=[
    ["Former location", "Disposition"],
    ["Lang-Theme-Generator", "Engine and legacy generation history"],
    ["Aptlantis Logos", "Artwork, catalogs and converters"],
    [".cts_holding/palette-transformer", "Transformation tools and differing versions"],
    ["Documents working collection", "Historical outputs, source assets and configuration"]],
    note="The former D-drive locations and the Documents working folder were inventoried and archived. Hash-verified migration records preserve differing versions rather than silently choosing one. The current consolidated implementation is not an assertion that every historical exporter was ported: legacy tools and outputs remain historical material. Archive, inventory, acceptance and retirement records provide the recovery trail. Existing public asset copies and deployment state were kept separate.", sources=["migration/README.md", "migration/acceptance.json", "Project-README.md"])
add("Ownership is part of the design", "A shared workflow does not require one project to own everything.", table=[
    ["Owner", "Responsibility"],
    ["Logos-And-Theming", "Theme engine, artwork/catalogs, ICO/SVG converters, atlas"],
    ["SESM-Metadata-Embedder", "SVG metadata, configuration, schema checks, embedding tests"],
    ["City Hall", "Canonical standards and schemas"],
    ["Public asset copies", "Existing publication and deployment state"]],
    note="The metadata sibling receives explicit asset-root and configuration paths. Asset IDs, filenames and registry relationships belong to the preserved collection. Canonical standards remain under City Hall; a project guide or handbook snapshot does not replace those standards. Ordinary generation does not run converters, embed metadata, install themes or publish assets.", sources=["AGENTS.md", "Logos-And-Theming.manifest.toml", "../SESM-Metadata-Embedder/README.md"])
add("The six-stage flow", "Every boundary produces something inspectable.", table=[
    ["Stage", "Decision / output"],
    ["1 · Image", "Preserved bytes, hash, normalized pixels"],
    ["2 · Candidates", "Up to 192 observed representatives and population weights"],
    ["3 · Canonical 32", "Stable IDs, four palette formats, selection diagnostics"],
    ["4 · Semantic roles", "Assignments, hue suitability and collision findings"],
    ["5 · Target adaptation", "Derived tokens, aliases, origins and omissions"],
    ["6 · Themes + review", "Native files, validation and self-contained HTML"]],
    note="The original image and its hash are retained independently from its normalized decoding. Candidate and selection diagnostics make the extraction reviewable. Semantic assignments are stored separately, and target tokens retain the origin of transformations. Processing completion and aesthetic approval are different conclusions: review findings can remain in completed output.", sources=["README.md", "docs/COMMAND-CONTRACT.md", "apt_theme/cli.py"])
add("Use a specialist tool at each stage", "The pipeline combines strengths instead of asking one tool to infer everything.", table=[
    ["Tool", "Job"],
    ["ImageMagick", "Decoding, orientation, ICC-aware sRGB normalization"],
    ["NumPy + scikit-learn", "Sampling and population-weighted OKLab clustering"],
    ["ColorAide", "Color conversion, contrast and sRGB gamut handling"],
    ["Python + PowerShell", "Pipeline contracts, configuration and local orchestration"],
    ["Artifact Tool / Open XML", "Editable PowerPoint content and package checks"]],
    note="ImageMagick handles image interpretation rather than semantic role assignment. KMeans uses sample weights and fixed seeds; cluster representatives are observed colors nearest centers, not exported centroids. ColorAide handles perceptual conversions and derivation. The PowerPoint target also requires the documented local Node/Artifact Tool runtime; the other targets do not. Dependency availability is part of setup, not a reason to choose a weaker algorithm silently.", sources=["apt_theme/extraction.py", "apt_theme/colors.py", "docs/POWERPOINT.md", "pyproject.toml"])
add("Normalize pixels; preserve the original", "Normalization creates a working representation without replacing the source.", [
    ["Interpret the image", "Apply orientation and ICC-aware sRGB conversion through ImageMagick."],
    ["Respect transparency", "Exclude fully transparent pixels; weight partial opacity by alpha."],
    ["Bound the computation", "Default sampling limit: 65,536 pixels. Fixed seed and stable ordering."]],
    note="The current implementation uses a bounded working sample after normalization; preserve the original high-bit-depth bytes for provenance and future comparisons. Transparent RGB values must not pollute the palette. Sampling introduces a deliberate computational bound: this is a representative estimate of the image, not an exhaustive proof that every pixel has been assigned ideally. Malformed input and an insufficient supply of distinct exportable colors fail clearly.", sources=["apt_theme/extraction.py", "profiles.toml", "tests/test_pipeline.py"])
add("Candidates are observed colors", "A cluster center guides selection; it does not become an invented export color.", [
    ["Perceptual coordinates", "Convert sampled sRGB colors to OKLab for clustering."],
    ["Population matters", "Weight clusters by image population and partial opacity."],
    ["Representative selection", "Choose an observed color nearest each cluster center, then order stably."]],
    note="The candidate stage requests up to 192 representatives. It reduces a large image to a bounded set while retaining population information. Near-black export noise is coalesced during canonical selection when enough meaningful observed alternatives remain. Fixed seeds and stable ordering support deterministic regeneration; they do not mean a color ID is immutable across different images or future selection algorithms.", sources=["apt_theme/extraction.py", "output/blackgold/candidates.json", "output/blackgold/selection.json"])
add("The Black-Gold canonical 32", "These IDs describe colors. They do not assign meanings.", note="This editable native table contains the exact canonical hex values from the preserved Black-Gold run. Colors range from dark anchors through muted browns, golds and cool accents to a light foreground. Pure black remains an image color; its presence does not make it the background role. Target exports must not rewrite these values. Role assignments and all derived colors are separate artifacts.", sources=["output/blackgold/palette.toml", "output/blackgold/selection.json"], kind="palette")
role_names = ("background", "foreground", "primary", "secondary", "warning", "cyan")
add("Semantic mapping makes intent explicit", "Assignments can be reviewed and overridden independently of extraction.", table=[["Role", "Source ID", "Canonical color"]] + [[r, SEM["roles"][r], PAL[SEM["roles"][r]]["hex"]] for r in role_names],
    note="Surfaces and text are selected by lightness and readability. Identity accents use prominence; status and ANSI roles use hue suitability rather than an accent’s position in a list. TOML semantic overrides resolve reviewed choices. The Black-Gold warning is warm #FBD484, not cyan. A legitimate warning color still needs contrast on its actual exported background and should not be the only way a warning is communicated.", sources=["apt_theme/semantics.py", "output/blackgold/semantics.json", "profiles.toml"])
add("Image identity can conflict with conventions", "Do not create an unrelated hue just to fill a familiar label.", [
    ["A warm warning is available", "Black-Gold maps warning to color_29 · #FBD484."],
    ["Magenta is unavailable", "The nearest image hue is used and the mismatch is reported."],
    ["Aliases are information", "Different named roles may share a color; collisions must stay visible."]],
    note="The actual semantics.json contains an unavailable_conventional_hue finding for magenta, using color_06 with a hue distance of roughly79.4degrees. Other runs can have different missing hues and collisions. No universal completeness claim is made for all images. Missing conventional hues are review findings, not permission to introduce new hue families. Applications may require a textual label, symbol or other additional distinction.", sources=["output/blackgold/semantics.json", "apt_theme/semantics.py"])
add("Derivation changes use, not origin", "Canonical colors remain untouched when applications need readable variations.", [
    ["Start from a source ID", "Record the role, source color and requested perceptual values."],
    ["Adjust for an actual need", "Change lightness or reduce chroma for text, surfaces and states."],
    ["Keep hue intent", "Fit sRGB by reducing chroma at fixed lightness and hue; record the result."]],
    note="Target origins record source IDs, purpose, requested OKLCH, whether the result was derived and whether gamut mapping was needed. Hue preservation describes the requested derivation in perceptual space; conversion to finite sRGB values can introduce quantization differences, especially in low-chroma colors. The pipeline should be judged on actual exported combinations as well as transformations. Token budgets do not require arbitrary shades.", sources=["apt_theme/colors.py", "apt_theme/adaptation.py", "output/blackgold/powerpoint/tokens.json"])
add("The background regression taught a boundary", "The darkest extracted color is not automatically the best dark surface.", [
    ["What looked wrong", "Repeated near-black anchors pulled themes toward flat black backgrounds."],
    ["What changed", "Coalesce the noise floor; map an identity surface near the configured lightness."],
    ["The Black-Gold result", "Background color_04 · #0A1924. Pure black stays in the canonical palette."]],
    note="Current defaults use semantic background_mode=identity with target lightness0.20; darkest remains an explicit alternative, and overrides take precedence. The Black-Gold selection reports18near-black candidates,1canonical floor representative and17coalesced. The quality lesson is not that black is always wrong: extraction, identity and surface assignment must be independently reviewable. Weighted coverage and minimum spacing provide diagnostics, not a mathematical proof of aesthetic quality.", sources=["docs/COMMAND-CONTRACT.md", "migration/dark-surface-regression.json", "output/blackgold/selection.json"])
add("Four targets, four native contracts", "The adapter serves real application settings rather than a generic color count.", table=[
    ["Target", "Budget", "Native output"],
    ["Windows Terminal", "20", "Scheme JSON: 16 ANSI + 4 application roles"],
    ["SiYuan", "64", "Dark CSS, metadata, README, previews, ZIP"],
    ["Typora", "40", "CSS for document, code, sidebar and states"],
    ["PowerPoint", "24", "12-slot color XML + editable sample deck"]],
    note="Budgets are working guides for distinct named tokens, not counts of UI settings. A single token can serve many settings. PowerPoint has12native Office color slots despite the adapter’s larger working token vocabulary. Additional targets such as IDEs, web frameworks and desktop applications remain deferred until native output and acceptance contracts are established.", sources=["profiles.toml", "docs/COMMAND-CONTRACT.md", "apt_theme/exporters.py"])
add("Names and unique colors are different counts", "Black-Gold uses only the variations its current adapters need.", table=[["Target", "Budget", "Named", "Unique"]] + [[t.replace("_", " "), str(TOK[t]["budget"]), str(TOK[t]["named_count"]), str(TOK[t]["unique_count"])] for t in TOK],
    note="These values are a dated observation of the existing Black-Gold token files, not promises for every image. WindowsTerminal20/17,SiYuan62/40,Typora40/36,PowerPoint22/18. All four current Black-Gold validation files report no recorded contrast failures, which is narrower than universal readability or native application approval. Aliases and reuse can be intentional; extra colors should be generated only for actual needs.", sources=[f"output/blackgold/{t}/tokens.json" for t in TOK])
add("Terminal reduction protects identity", "A small vocabulary must support both meaning and readable text.", [
    ["Protect required roles", "Background, foreground, cursor, selection and the 16 ANSI slots."],
    ["Carry the image into text", "Retain visible gold and cool cyan/blue relationships through adaptation."],
    ["Expose compromise", "Report missing conventional hues, reused colors and actual contrast pairs."]],
    note="Terminal output has fewer component and typography options than a full editor. The adapter cannot rely on arbitrary syntax shades if the ANSI contract offers only16slots. Bright and ordinary ANSI variants need to be tested against the real background; selection foreground also needs checking against selection fill. Preserving a source hue is necessary but insufficient for a visually coherent terminal theme. Live terminal import and visual testing remain a separate acceptance step.", sources=["apt_theme/adaptation.py", "output/blackgold/windows_terminal/windows-terminal.json", "docs/VALIDATION.md"])
add("Editors need content and state coverage", "SiYuan and Typora require more than a page background and link color.", table=[
    ["Area", "What must hold together"],
    ["Document", "Body text, headings, links, quotes, tables"],
    ["Code", "Inline code, blocks and syntax roles"],
    ["Navigation", "Sidebar, muted text and active items"],
    ["Interaction", "Selection, focus, hover and common states"],
    ["Delivery", "Target CSS scopes; SiYuan package assets and metadata"]],
    note="The initial exports follow the target contracts documented in the project. Structural validation checks CSS references and package contents; the HTML review approximates representative combinations. Neither proves every selector behaves correctly in a particular installed application version. Native acceptance needs versioned import and visual checks for document, navigation, code and state combinations, including keyboard focus.", sources=["apt_theme/exporters.py", "docs/VALIDATION.md", "output/blackgold/siyuan/theme.css", "output/blackgold/typora/theme.css"])
add("PowerPoint: color theme and editable proof", "Twelve native slots become a reusable visual vocabulary.", [
    ["The pipeline sample", "Four editable slides: title, content, Office slots and a native chart."],
    ["This overview", "The same Black-Gold slots, Arial and canvas applied to project content."],
    ["Compatibility lesson", "XML can parse while QName-valued metadata still breaks PowerPoint."]],
    note="The previous package defect renamed the dcterms namespace prefix while leaving xsi:type=dcterms:W3CDTF undeclared. Correcting only core properties preserved the actual slide/theme/workbook bytes. The recorded repair checks opened six corrected workspace samples and a fresh deck with OpenAndRepair disabled. Native opening/export is evidence of compatibility; it does not prove that chart data editing and save-reopen have been manually accepted. This overview has native editable tables and explanatory text; it is a separate deliverable from the generated four-slide sample.", sources=["docs/POWERPOINT.md", "migration/powerpoint-metadata-repair.json", "apt_theme/powerpoint.py"])
add("The run leaves a reviewable trail", "A complete output directory explains where its colors came from.", table=[
    ["Artifact", "Purpose"],
    ["source/ + provenance.json", "Original image bytes, hash and decoding provenance"],
    ["candidates.json / selection.json", "Representatives, coverage and spacing diagnostics"],
    ["palette.toml / txt / css / png", "Exactly32 canonical colors in reusable forms"],
    ["semantics.json / tokens.json", "Roles, derivations, aliases and findings"],
    ["validation.json / review.html", "Checks and a self-contained visual review"]],
    note="The report shows candidates, canonical selection, semantic roles, target samples, derivation chains, omissions, contrast and duplicates. A previous palette can be supplied for comparison without claiming its selection is wrong. Palette IDs are references within a run. Store complete runs as revisions when retaining history: overwrite replaces the preceding completed generated run after successful staging.", sources=["docs/COMMAND-CONTRACT.md", "apt_theme/report.py", "output/blackgold/provenance.json"])
add("The command contract keeps runs bounded", "Generate and import are local, reviewable operations.", [
    ["Generate", "apt-theme generate IMAGE --output DIRECTORY"],
    ["Import and configure", "Import exactly32 colors; choose targets, TOML settings and semantic overrides."],
    ["Complete with findings", "0: completed · 1: processing failure · 2: strict contrast failure / invalid syntax"]],
    note="Default targets are WindowsTerminal,SiYuan,Typora,PowerPoint. Import preserves supplied colors and records historical role assignments while resolving current semantics. --compare supplies an old palette, --overwrite explicitly replaces a recognized generated output, --strict returns2for contrast failure after completed artifacts are written, and argparse also uses2for invalid syntax. Staging prevents publication of partial output on processing failure and restores the prior output if replacement fails. Generation never installs, opens or activates themes.", sources=["docs/COMMAND-CONTRACT.md", "Invoke-AptTheme.ps1", "apt_theme/cli.py"])
add("Related utilities stay independently callable", "Theme generation, conversion and metadata embedding have different jobs.", table=[
    ["Utility", "Preserved behavior"],
    ["ICO converter", "ImageMagick multi-frame icon conversion"],
    ["SVG converter", "Embedded raster by default; explicit VTracer tracing"],
    ["Atlas", "Artwork/catalog browsing and palette utility"],
    ["SESM embedder", "Preview by default; explicit write / replace and schema checks"]],
    note="Explicit VTracer requests must not silently fall back to embedded raster when tracing fails. SVG metadata operations preserve content outside the metadata block and embedded raster bytes. SESM requires an explicit asset root and uses configuration and canonical schema validation in its sibling project. These tools are not run automatically by ordinary theme generation. Preserve filenames, registry relationships and existing public copies.", sources=["README.md", "../SESM-Metadata-Embedder/README.md", "migration/acceptance.json"])
add("Recovery is a deliverable", "Consolidation was gated on recoverability, not just copying files.", [
    ["Inventory and archive", "Hash source, assets, historical outputs, configuration and Git history."],
    ["Verify destinations", "Check migrated tools, artwork bytes and restored archive content."],
    ["Retire only after gates", "Update references; check resolved paths and reject changed source inventories."]],
    note="Migration records are dated evidence. They preserve differing script versions and recovery paths. The retirement process checks that source files have not changed after inventory and resolves deletion targets. The existing documentation handbook uses a historical snapshot; refresh is separate work and must preserve the boundary between a reference publication and current project authority. Public deployment state is outside consolidation.", sources=["migration/README.md", "migration/acceptance.json", "Project-README.md"])
add("What the evidence proves—and leaves open", "Structural success, native compatibility and aesthetic quality are separate gates.", table=[
    ["Evidence", "Limit"],
    ["20focused tests recorded after repair", "Dated engineering evidence, not a new run today"],
    ["Black-Gold: no recorded contrast failures", "Only the combinations implemented in validation"],
    ["Corrected PowerPoint opens without repair", "Opening/export differs from manual edit acceptance"],
    ["Coverage, spacing and visual report", "Diagnostics do not prove aesthetic quality"],
    ["Other native applications / future targets", "Live acceptance remains separately recorded"]],
    note="This deck cites the recorded repair evidence and existing output validation, not newly rerun pipeline tests. The documentation task does not alter engine behavior. Native rendering and package validation of this overview will be recorded in its delivery evidence. Perceptual coverage is helpful for comparing selections, but cannot establish whether a background or semantic role feels right. Additional accessibility methods and broader application version testing need explicit future work.", sources=["migration/powerpoint-metadata-repair.json", "docs/VALIDATION.md", "output/blackgold/run.json"])
add("A document suite, written in useful order", "Keep this deck as the entry point; put depth in focused, source-backed volumes.", [
    ["First · operate and explain", "Runbook, artifact reference and the two regression case studies."],
    ["Next · design and extend", "Extraction methods, semantic mapping, adapter contracts and native acceptance."],
    ["Then · preserve and integrate", "Asset lineage, SESM companion, recovery and the living handbook."]],
    note="The companion PLAN.md specifies audience, scope, chapter outlines, primary sources, ownership, dependencies and completion criteria for ten planned volumes. It also identifies the existing Writerside handbook and its2026-10-05snapshot as reusable reference material rather than current engine authority. The plan is not a commitment to publish or install anything. Future authoring should use dated source capture, reviewed examples and explicit proof limits. This24slideoverview is the presentation entry point.", sources=["docs/documentation-suite/PLAN.md", "D:/.library/Writerside-Projects/Aptlantis-Logos-and-Theming/README.md"])

assert len(slides) == 24
slides[8]["lead"] = "Perceptual clustering, light/dark anchors and diversity; IDs carry no meanings."
slides[8]["notes"] += " The selector clusters the candidate pool into thirty perceptual groups, protects the lightest and darkest anchors, skips representatives closer than0.03OKLab to the selected set and fills remaining positions with population-aware farthest candidates. Stable lightness/hex ordering assigns color IDs. This replaces fixed semantic category quotas."
names = {"windows_terminal": "Windows Terminal", "siyuan": "SiYuan", "typora": "Typora", "powerpoint": "PowerPoint"}
for row, target in zip(slides[14]["table"][1:], TOK):
    row[0] = names[target]
slides[22]["title"] = "What the evidence establishes"
slides[18]["table"][2][0] = "Candidates / selection"
slides[18]["table"][2][1] = "Representatives and selection diagnostics"
slides[22]["table"][1][0] = "20 focused tests after repair"
slides[22]["table"][2][0] = "Black-Gold contrast checks"
slides[22]["table"][3][0] = "PowerPoint no-repair opening"
slides[22]["table"][4][0] = "Coverage and visual report"
slides[22]["table"][5][0] = "Other native / future targets"
for slide in slides:
    for old, new in {"exactly32": "exactly 32", "Exactly32": "Exactly 32", "20focused": "20 focused", "WindowsTerminal": "Windows Terminal", "PowerPoint22/18": "PowerPoint 22/18", "SiYuan62/40": "SiYuan 62/40", "Typora40/36": "Typora 40/36", "ANSIvariants": "ANSI variants", "12native": "12 native", "16slots": "16 slots", "24slideoverview": "24-slide overview", "2026-10-05snapshot": "2026-10-05 snapshot", "79.4degrees": "79.4 degrees", "18near-black": "18 near-black", "1canonical": "1 canonical", "17coalesced": "17 coalesced", "color_06with": "color_06 with", "32entries": "32 entries", "0.03OKLab": "0.03 OKLab", "lightness0.20": "lightness 0.20", "roughly79.4": "roughly 79.4", "October5": "October 5"}.items():
        slide["notes"] = slide["notes"].replace(old, new)
        slide["groups"] = [[v.replace(old, new) for v in group] for group in slide["groups"]]
        if slide["table"]:
            slide["table"] = [[v.replace(old, new) for v in row] for row in slide["table"]]
    slide["sources"] = [s.replace("apt_theme/adaptation.py", "apt_theme/targets.py").replace("apt_theme/exporters.py", "apt_theme/targets.py").replace("output/blackgold/typora/theme.css", "output/blackgold/typora/aptlantis-black-gold.css") for s in slide["sources"]]
paths = sorted({s for slide in slides for s in slide["sources"]})
catalog = []
for p in paths:
    full = Path(p) if ":" in p else ROOT / p
    if not full.is_file():
        raise FileNotFoundError(full)
    catalog.append({"source": p, "path": str(full.resolve()), "sha256": hashlib.sha256(full.read_bytes()).hexdigest()})
data = {"date": "2026-10-08", "reference": str(REF), "reference_sha256": hashlib.sha256(REF.read_bytes()).hexdigest(), "colors": scheme, "palette": PAL, "slides": slides, "sources": catalog}
(OUT / "overview-content.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
print(f"Captured {len(slides)} slides and {len(catalog)} sources")
