import copy
import io
import hashlib
import json
import re
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from unittest.mock import patch
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np

from apt_theme.cli import main
from apt_theme.colors import derive, distance, from_rgb, lab
from apt_theme.extraction import extract, load_palette, rgb_labs, select
from apt_theme.semantics import assign, hue_distance
from apt_theme.targets import DEFAULTS, adapt, export
from apt_theme.powerpoint import normalize_core_properties, validate_core_properties

ROOT = Path(__file__).resolve().parents[1]


def hashes(path):
    return {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in path.rglob("*") if p.is_file()}


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # A deliberately gold/cyan fixture with exactly 32 observed colors.
        values = []
        for i in range(16):
            values.append(from_rgb([10 + i * 15, 7 + i * 11, 2 + i * 4], weight=10 + i))
            values.append(from_rgb([3 + i * 5, 8 + i * 14, 12 + i * 15], weight=8 + i))
        self.colors = {f"color_{i:02}": c for i, c in enumerate(sorted(values, key=lambda c: c["oklch"][0]), 1)}

    def test_math_and_vector_conversion(self):
        samples = [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 255], [3, 11, 20]]
        np.testing.assert_allclose(rgb_labs(samples), [lab(from_rgb(rgb)) for rgb in samples], atol=1e-7)

    def test_selection_observed_exact32_and_determinism(self):
        values = list(self.colors.values())
        first = select(values)
        self.assertEqual(first, select(values))
        self.assertEqual(len(first), 32)
        self.assertEqual({c["hex"] for c in first.values()}, {c["hex"] for c in values})

    def test_semantics_hue_suitability_overrides_and_findings(self):
        roles, notices = assign(self.colors)
        warning = self.colors[roles["warning"]]
        self.assertLess(hue_distance(warning["oklch"][2], 85), 45)
        self.assertTrue(any(n["kind"] == "unavailable_conventional_hue" for n in notices))
        overrides, _ = assign(self.colors, {"warning": "color_01"})
        self.assertEqual(overrides["warning"], "color_01")
        with self.assertRaises(ValueError):
            assign(self.colors, {"warning": "missing"})

    def test_near_black_noise_does_not_consume_visible_color_slots(self):
        noise = [from_rgb(rgb, weight=100) for rgb in
                 ([0, 0, 0], [0, 0, 2], [0, 2, 6], [1, 1, 1], [4, 4, 4], [10, 10, 10])]
        candidates = noise + [c for c in self.colors.values() if max(c["rgb"]) > 12]
        candidates += [from_rgb(rgb, weight=20) for rgb in ([26, 55, 73], [52, 85, 119], [179, 116, 51])]
        palette = select(candidates)
        self.assertEqual(len(palette), 32)
        self.assertEqual(sum(max(c["rgb"]) <= 12 for c in palette.values()), 1)
        self.assertEqual(palette, select(candidates))
        self.assertTrue({c["hex"] for c in palette.values()} <= {c["hex"] for c in candidates})
        self.assertEqual(sum(c["weight"] for c in noise), next(c["weight"] for c in palette.values() if max(c["rgb"]) <= 12))
        # Exact/sparse palettes are preserved rather than padded with invented colors.
        sparse = [from_rgb([i * 8] * 3) for i in range(32)]
        self.assertEqual({c["hex"] for c in select(sparse).values()}, {c["hex"] for c in sparse})

    def test_surface_identity_is_separate_from_black_anchor(self):
        colors = {**self.colors, "absolute_black": from_rgb([0, 0, 0], weight=10000),
                  "blue_surface": from_rgb([12, 25, 38], weight=5000)}
        roles, _ = assign(colors)
        self.assertNotEqual(roles["background"], "absolute_black")
        self.assertEqual(roles["black"], "absolute_black")
        self.assertGreaterEqual(colors[roles["background"]]["oklch"][0], .12)
        self.assertGreaterEqual(colors[roles["background"]]["oklch"][1], .015)
        darkest, _ = assign(colors, settings={"background_mode": "darkest"})
        self.assertEqual(darkest["background"], "absolute_black")
        explicit, _ = assign(colors, {"background": "absolute_black"})
        self.assertEqual(explicit["background"], "absolute_black")
        # A grayscale image retains its neutral identity; a sparse bright palette
        # falls back visibly rather than silently inventing a dark hue.
        gray = {str(i): from_rgb([i * 8] * 3) for i in range(32)}
        gray_roles, _ = assign(gray)
        self.assertGreater(gray[gray_roles["background"]]["oklch"][0], 0)
        bright = {str(i): from_rgb([180 + i, 180 + i, 180 + i]) for i in range(32)}
        _, notices = assign(bright)
        self.assertTrue(any(n["kind"] == "background_fallback" for n in notices))
        with self.assertRaises(ValueError):
            assign(colors, settings={"background_mode": "unknown"})

    def test_gamut_and_hue_derivation(self):
        source = from_rgb([255, 0, 0])
        changed = derive(source, .85)
        self.assertTrue(changed["gamut_mapped"])
        self.assertEqual(changed["requested_oklch"][2], source["oklch"][2])
        self.assertLess(hue_distance(changed["oklch"][2], source["oklch"][2]), 1.5)

    def test_native_exports_and_canonical_immutability(self):
        before = copy.deepcopy(self.colors)
        roles, _ = assign(self.colors)
        for target, budget in DEFAULTS.items():
            result = adapt(self.colors, roles, target, budget)
            self.assertLessEqual(result["named_count"], budget)
            self.assertEqual(result["contrast_failures"], 0)
            destination = self.root / target
            export(result, destination, "Test Dark")
            if target == "windows_terminal":
                scheme = json.loads((destination / "windows-terminal.json").read_text())
                self.assertEqual(len(scheme), 21)
                self.assertTrue(all(re.fullmatch(r"#[0-9A-F]{6}", v) for k, v in scheme.items() if k != "name"))
                self.assertLess(hue_distance(result["tokens"]["yellow"]["oklch"][2], 85), 45)
                self.assertLess(hue_distance(result["tokens"]["cyan"]["oklch"][2], 205), 45)
            elif target == "powerpoint":
                root = ET.parse(next(destination.glob("*.xml"))).getroot()
                self.assertEqual(len(root), 12)
                ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
                      "c": "http://schemas.openxmlformats.org/drawingml/2006/chart"}
                with zipfile.ZipFile(next(destination.glob("*.pptx"))) as deck:
                    validate_core_properties(deck.read("docProps/core.xml"))
                    slides = [n for n in deck.namelist() if re.fullmatch(r"ppt/slides/slide\d+.xml", n)]
                    self.assertEqual(len(slides), 4)
                    theme = ET.fromstring(deck.read("ppt/theme/theme1.xml")).find("a:themeElements/a:clrScheme", ns)
                    self.assertEqual({s.tag: s[0].attrib for s in theme}, {s.tag: s[0].attrib for s in root})
                    # Followed-link colors must remain native theme bindings,
                    # including the swatch, rather than disappear into black.
                    for n in ("ppt/slides/slide2.xml", "ppt/slides/slide3.xml"):
                        self.assertTrue(any(c.get("val") == "folHlink" for c in ET.fromstring(deck.read(n)).findall(".//a:schemeClr", ns)))
                    self.assertTrue(any(ET.fromstring(deck.read(n)).find(".//a:tbl", ns) is not None for n in slides))
                    chart = ET.fromstring(deck.read(next(n for n in deck.namelist() if n.endswith("/chart1.xml"))))
                    self.assertEqual(len(chart.findall(".//c:ser", ns)), 6)
                    self.assertEqual({c.get("val") for c in chart.findall(".//c:ser//a:schemeClr", ns)}, {f"accent{i}" for i in range(1, 7)})
                    self.assertIsNotNone(chart.find("c:externalData", ns))
                    with zipfile.ZipFile(io.BytesIO(deck.read("ppt/embeddings/sample-data.xlsx"))) as book:
                        sheet = ET.fromstring(book.read("xl/worksheets/sheet1.xml"))
                        self.assertEqual(len(sheet.findall(".//{*}row")), 3)
            else:
                css = next(destination.glob("*.css")).read_text()
                declared = set(re.findall(r"(--[\w-]+)\s*:", css))
                refs = set(re.findall(r"var\((--[\w-]+)\)", css))
                self.assertFalse(refs - declared)
                self.assertEqual(css.count("{"), css.count("}"))
                if target == "siyuan":
                    with zipfile.ZipFile(destination / "package.zip") as bundle:
                        self.assertEqual(set(bundle.namelist()), {"theme.css", "theme.json", "README.md", "icon.png", "preview.png"})
                    self.assertEqual(json.loads((destination / "theme.json").read_text())["modes"], ["dark"])
        self.assertEqual(self.colors, before)
        with self.assertRaises(ValueError):
            adapt(self.colors, roles, "windows_terminal", 19)

    def fixture_palette(self):
        from apt_theme.extraction import palette_toml
        path = self.root / "palette.toml"
        path.write_text(palette_toml(self.colors, "Test Dark", "a" * 64), encoding="utf-8-sig")
        return path

    def test_import_roundtrip_determinism_and_overwrite(self):
        path = self.fixture_palette()
        output = self.root / "output"
        args = ["import", str(path), "--output", str(output)]
        self.assertEqual(main(args), 0)
        loaded, _ = load_palette(output / "palette.toml")
        self.assertEqual({k: c["hex"] for k, c in loaded.items()}, {k: c["hex"] for k, c in self.colors.items()})
        first = hashes(output)
        self.assertEqual(main(args), 1)
        self.assertEqual(main(args + ["--overwrite"]), 0)
        self.assertEqual(first, hashes(output))
        self.assertNotIn("https://", (output / "review.html").read_text())

    def test_strict_mode_still_writes_failed_results(self):
        path = self.fixture_palette()
        config = self.root / "bad-background.toml"
        config.write_text('[overrides]\nbackground = "color_32"\n')
        output = self.root / "strict"
        self.assertEqual(main(["import", str(path), "--config", str(config), "--output", str(output), "--strict"]), 2)
        self.assertTrue((output / "windows_terminal" / "windows-terminal.json").exists())
        self.assertGreater(json.loads((output / "run.json").read_text())["contrast_failures"], 0)

    def test_powerpoint_runtime_failure_preserves_previous_output(self):
        output = self.root / "previous"
        output.mkdir()
        (output / "run.json").write_text('{"preserved": true}')
        (output / "operator-note.txt").write_text("Previous generated output")
        before = hashes(output)
        with patch("apt_theme.powerpoint.runtime", side_effect=ValueError("PowerPoint runtime unavailable")):
            self.assertEqual(main(["import", str(self.fixture_palette()), "--output", str(output),
                                   "--targets", "powerpoint", "--overwrite"]), 1)
        self.assertEqual(hashes(output), before)

    def test_powerpoint_timestamp_type_namespace_is_preserved(self):
        # Reproduces the undeclared QName produced by the original serializer.
        damaged = b'<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:ns2="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><ns2:created xsi:type="dcterms:W3CDTF">2026-01-01T00:00:00Z</ns2:created><ns2:modified xsi:type="dcterms:W3CDTF">2026-01-01T00:00:00Z</ns2:modified></cp:coreProperties>'
        with self.assertRaisesRegex(ValueError, 'namespace'):
            validate_core_properties(damaged)
        repaired = normalize_core_properties(damaged)
        validate_core_properties(repaired)
        self.assertEqual(normalize_core_properties(repaired), repaired)
        self.assertIn(b'xmlns:dcterms="http://purl.org/dc/terms/"', repaired)

    def test_powerpoint_metadata_repair_preserves_other_package_bytes(self):
        from tools.repair_powerpoint_metadata import repair
        source, destination = self.root / 'before.pptx', self.root / 'after.pptx'
        core = b'<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dcterms:created xsi:type="dcterms:W3CDTF">2026-01-01T00:00:00Z</dcterms:created></cp:coreProperties>'
        with zipfile.ZipFile(source, 'w') as package:
            package.writestr('docProps/core.xml', core)
            package.writestr('ppt/slides/slide1.xml', b'<preserve>slides and colors</preserve>')
            package.writestr('ppt/embeddings/data.xlsx', b'embedded workbook bytes')
        before = source.read_bytes()
        repair(source, destination)
        self.assertEqual(source.read_bytes(), before)
        with zipfile.ZipFile(destination) as package:
            validate_core_properties(package.read('docProps/core.xml'))
            self.assertEqual(package.read('ppt/slides/slide1.xml'), b'<preserve>slides and colors</preserve>')
            self.assertEqual(package.read('ppt/embeddings/data.xlsx'), b'embedded workbook bytes')
        with self.assertRaises(ValueError):
            repair(source, destination)

    def test_transparency_monochrome_and_insufficient_colors(self):
        from PIL import Image
        image = Image.new("RGBA", (32, 2), (255, 0, 255, 0))
        for i, c in enumerate(self.colors.values()):
            image.putpixel((i, 0), tuple(c["rgb"]) + (128 if i % 2 else 255,))
        path = self.root / "transparent.png"
        image.save(path)
        candidates, provenance, _, weights = extract(path, {"sample_limit": 100})
        self.assertEqual(len(candidates), 32)
        self.assertEqual(provenance["visible_pixels"], 32)
        self.assertNotIn("#FF00FF", {c["hex"] for c in candidates})
        self.assertAlmostEqual(weights.sum(), 16 + 16 * 128 / 255)
        mono = Image.new("RGB", (32, 1))
        for i in range(32):
            mono.putpixel((i, 0), (i * 8,) * 3)
        mono.save(path)
        values, _, _, _ = extract(path, {})
        roles, notices = assign(select(values))
        self.assertTrue(notices)
        Image.new("RGB", (10, 10), "black").save(path)
        with self.assertRaisesRegex(ValueError, "requires 32"):
            extract(path, {})

    def test_invalid_input_config_and_nonpipeline_overwrite(self):
        path = self.root / "bad.toml"
        path.write_text("invalid syntax")
        self.assertEqual(main(["import", str(path), "--output", str(self.root / "bad")]), 1)
        valid = self.fixture_palette()
        config = self.root / "config.toml"
        config.write_text("[unknown]\nvalue = 1\n")
        self.assertEqual(main(["import", str(valid), "--config", str(config), "--output", str(self.root / "bad")]), 1)
        protected = self.root / "protected"
        protected.mkdir()
        (protected / "important.txt").write_text("keep")
        self.assertEqual(main(["import", str(valid), "--output", str(protected), "--overwrite"]), 1)
        self.assertTrue((protected / "important.txt").exists())

    def test_json_envelope_and_bom_configuration(self):
        palette = self.fixture_palette()
        config = self.root / "config.toml"
        config.write_text('[profiles.windows_terminal]\nbudget = 20\n', encoding="utf-8-sig")
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(["import", str(palette), "--config", str(config), "--targets", "windows_terminal", "--output", str(self.root / "json"), "--json"])
        self.assertEqual(code, 0)
        envelope = json.loads(stdout.getvalue())
        self.assertEqual(envelope["tool"], "apt-theme")
        self.assertEqual(envelope["data"]["targets"], ["windows_terminal"])
        self.assertEqual(envelope["errors"], [])


if __name__ == "__main__":
    unittest.main()
