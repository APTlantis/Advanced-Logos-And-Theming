"""Focused conversion and SESM integration checks."""

from __future__ import annotations

import base64
import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def module(filename: str):
    spec = importlib.util.spec_from_file_location(filename.replace("-", "_"), SCRIPTS / filename)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


ico = module("Convert-to-ICO.py")
svg = module("Convert-to-SVG.py")



class LogoToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="logo tools ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.png = self.root / "wide logo.png"
        subprocess.run(["magick", "-size", "80x40", "xc:none", "-fill", "#dd3344",
                        "-draw", "rectangle 20,5 60,35", str(self.png)], check=True, capture_output=True)

    def test_ico_frames_and_collision(self):
        target = self.root / "icon.ico"
        self.assertEqual(ico.main(["--input", str(self.png), "--output", str(target),
                                   "--sizes", "16,32,256", "--fit", "contain"]), 0)
        self.assertEqual(set(ico.ico_sizes(target)), {16, 32, 256})
        self.assertEqual(float(ico.run(["magick", str(target) + "[0]", "-format",
                                        "%[fx:p{0,0}.a]", "info:"])), 0.0)
        before = target.read_bytes()
        self.assertEqual(ico.main(["--input", str(self.png), "--output", str(target)]), 0)
        self.assertEqual(target.read_bytes(), before)
        with self.assertRaises(Exception):
            ico.parse_sizes("0,256")

    def test_svg_embed_preserves_bytes_and_dimensions(self):
        output = self.root / "wrapped.svg"
        self.assertEqual(svg.main(["--input", str(self.png), "--output", str(output)]), 0)
        root = ET.parse(output).getroot()
        self.assertEqual((root.get("width"), root.get("height")), ("80", "40"))
        image = next(element for element in root if element.tag.endswith("image"))
        self.assertEqual(base64.b64decode(image.get("href").split(",", 1)[1]), self.png.read_bytes())

    def test_svg_normalize_and_trace_dependency(self):
        output = self.root / "normalized.svg"
        self.assertEqual(svg.main(["--input", str(self.png), "--output", str(output),
                                   "--normalize", "--resize", "40x20"]), 0)
        self.assertEqual(ET.parse(output).getroot().get("width"), "40")
        missing = self.root / "no-trace.svg"
        self.assertEqual(svg.main(["--input", str(self.png), "--output", str(missing),
                                   "--mode", "trace", "--vtracer", "missing-vtracer.exe"]), 2)
        self.assertFalse(missing.exists())

    def test_batch_output_and_collision_guards(self):
        output = self.root / "batch output"
        self.assertEqual(svg.main(["--input", str(self.root), "--output-dir", str(output),
                                   "--no-recursive", "--dry-run"]), 2)
        outside = self.root.parent / (self.root.name + " SVG results")
        try:
            self.assertEqual(svg.main(["--input", str(self.root), "--output-dir", str(outside),
                                       "--no-recursive"]), 0)
            self.assertTrue((outside / "wide logo.svg").exists())
        finally:
            (outside / "wide logo.svg").unlink(missing_ok=True)
            outside.rmdir()
        other = self.root / "wide logo.jpg"
        other.write_bytes(b"not a real JPEG")
        with self.assertRaises(ValueError):
            ico.jobs(self.root, self.root.parent / "icons", False)

    def test_trace_output_contract_with_stub(self):
        output = self.root / "traced.svg"
        real_run = svg.run

        def run(command):
            if command[0] == "test-vtracer":
                if "--version" in command:
                    return "vtracer 1.0.0-alpha.4"
                destination = Path(command[command.index("--output") + 1])
                destination.write_text('<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0 L5 0 Z"/></svg>')
                return ""
            return real_run(command)

        with patch.object(svg, "run", side_effect=run):
            self.assertEqual(svg.main(["--input", str(self.png), "--output", str(output),
                                       "--mode", "trace", "--vtracer", "test-vtracer"]), 0)
        self.assertIn(b"<path", output.read_bytes())




if __name__ == "__main__":
    unittest.main()
