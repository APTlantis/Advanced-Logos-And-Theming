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
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np

from apt_theme.cli import main
from apt_theme.colors import derive, distance, from_rgb, lab
from apt_theme.extraction import extract, load_palette, rgb_labs, select
from apt_theme.semantics import assign, hue_distance
from apt_theme.targets import DEFAULTS, adapt, export

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
