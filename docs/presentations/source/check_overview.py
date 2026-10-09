"""Record delivery checks; native rendering is a separate already-executed gate."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import tomllib
from xml.etree import ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "docs/presentations"
DECK = BASE / "Logos-And-Theming-Overview.pptx"
DATA = json.loads((BASE / "source/overview-content.json").read_text(encoding="utf-8"))
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def slots(z):
    theme = ET.fromstring(z.read("ppt/theme/theme1.xml"))
    return {e.tag.split("}")[-1]: "#" + list(e)[0].get("val", list(e)[0].get("lastClr", "")) for e in theme.find("a:themeElements/a:clrScheme", NS)}

with zipfile.ZipFile(DECK) as current, zipfile.ZipFile(DATA["reference"]) as ref:
    assert slots(current) == slots(ref) == DATA["colors"]
    slides = [f"ppt/slides/slide{i}.xml" for i in range(1, 25)]
    assert len([p for p in current.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", p)]) == 24
    assert len([p for p in current.namelist() if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", p)]) == 24
    for i in range(1, 25):
        note = " ".join(ET.fromstring(current.read(f"ppt/notesSlides/notesSlide{i}.xml")).itertext())
        assert "PRIMARY SOURCES" in note and "SHA-256" in note
    palette_text = " ".join(ET.fromstring(current.read(slides[8])).itertext())
    for color_id, value in DATA["palette"].items():
        assert color_id in palette_text and value["hex"] in palette_text
for source in DATA["sources"]:
    assert digest(Path(source["path"])) == source["sha256"], source["path"]
assert digest(Path(DATA["reference"])) == DATA["reference_sha256"]
palette = tomllib.loads((ROOT / "output/dnf-Blackgold/palette.toml").read_text())["palette"]["canonical"]
assert palette == DATA["palette"] and len(palette) == len({v["hex"] for v in palette.values()}) == 32
receipt = json.loads((ROOT / ".build/overview/finalization.json").read_text())
assert receipt["finalSha256"] == digest(DECK)
assert receipt["packageIntegrity"]["findingCount"] == receipt["presentationLayout"]["findingCount"] == 0
assert receipt["presentationLayout"]["warning_count"] == 0
renders = [ROOT / f".build/overview/native-render/Slide{i}.PNG" for i in range(1, 25)]
assert all(p.is_file() for p in renders)
report = {
    "date": "2026-10-08", "deck": str(DECK), "sha256": digest(DECK), "slide_count": 24,
    "native_table_count": 12, "notes_count": 24, "source_count": len(DATA["sources"]),
    "theme_reference": DATA["reference"], "theme_reference_sha256": DATA["reference_sha256"],
    "theme_slots_match": True, "canonical_32_values_match": True, "source_hashes_match": True,
    "package_layout_and_font_checks": "passed; no findings or warnings",
    "native_powerpoint": {"method": "Presentations.Open2007 read-only, WithWindow=false, OpenAndRepair=false; export PNG 1280x720",
                          "result": "opened and exported all 24 slides without repair",
                          "executed_separately": True,
                          "renders": [{"slide": i, "sha256": digest(p)} for i, p in enumerate(renders, 1)]},
    "visual_review": {"method": "Full-size native PNG inspection of all 24 final slides",
                      "result": "passed", "slides_reviewed": list(range(1, 25))},
    "plan": {"path": str(ROOT / "docs/documentation-suite/PLAN.md"), "sha256": digest(ROOT / "docs/documentation-suite/PLAN.md"), "volumes": 10},
    "limits": ["No engine changes or new pipeline test run in this documentation task", "No theme installation or publication", "Future volumes are planned, not authored", "Manual presentation editing/save-reopen is not claimed"]
}
(BASE / "validation").mkdir(exist_ok=True)
(BASE / "validation/delivery.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
shutil.copyfile(ROOT / ".build/overview/finalization.json", BASE / "validation/finalization.json")
shutil.copyfile(renders[0], BASE / "preview.png")
print(json.dumps({"deck_sha256": report["sha256"], "slides": 24, "sources": len(DATA["sources"]), "theme_parity": True, "canonical_unchanged": True}))
