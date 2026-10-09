"""Resource integrity and shared chart data contracts; runtime checks live in browser tooling."""
import re
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from apt_theme.chart_examples import example_data
from apt_theme.syntax_examples import SOURCES, VENDOR, verify_vendor
from apt_theme.visual_targets import charts, syntax


class VisualQualityTests(unittest.TestCase):
    def test_pinned_vendor_dependencies_and_integrity(self):
        manifest = verify_vendor()
        self.assertEqual(manifest["version"], "1.30.0")
        metadata = json.loads((VENDOR / "components.json").read_text())
        ordered = manifest["load_order"]
        for language in manifest["languages"]:
            required = metadata["languages"][language].get("require", [])
            if isinstance(required, str):
                required = [required]
            for dependency in required:
                self.assertLess(ordered.index(f"prism-{dependency}.js"), ordered.index(f"prism-{language}.js"))
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            (directory / "manifest.json").write_text(json.dumps({"files": [{"file": "changed.js", "sha256": "0"*64}]}))
            (directory / "changed.js").write_text("changed")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                verify_vendor(directory)

    def test_source_languages_and_substantial_examples(self):
        examples = json.loads((SOURCES / "manifest.json").read_text())
        self.assertEqual(len(examples), 12)
        for example in examples:
            source = (SOURCES / example["file"]).read_text()
            self.assertGreaterEqual(len(source.splitlines()), 25)
            self.assertLessEqual(len(source.splitlines()), 50)
        json.loads((SOURCES / "palette.json").read_text())
        import tomllib
        tomllib.loads((SOURCES / "palette.toml").read_text())
        compile((SOURCES / "palette.py").read_text(), "palette.py", "exec")

    def test_shared_chart_values_and_svg_marks(self):
        data = example_data()
        self.assertEqual(len(data["bars"]), 12)
        self.assertEqual([len(row) for row in data["lines"]], [24]*6)
        self.assertEqual([len(row) for row in data["heatmap"]], [12]*8)
        self.assertEqual(len(set(data["markers"])), 6)
        self.assertEqual(len(set(data["dash_patterns"])), 6)
        keys = ["background", "panel", "foreground", "muted", "border", "link", "primary"]
        keys += [f"series_{i}" for i in range(1, 7)] + [f"sequential_{i}" for i in range(9)]
        tokens = {key: {"hex": "#C8A868", "rgb": [200, 168, 104]} for key in keys}
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            charts(tokens, directory, "Example")
            self.assertEqual(json.loads((directory / "example-data.json").read_text()), data)
            bars = ET.parse(directory / "bars.svg").getroot()
            self.assertEqual([int(n.get("data-value")) for n in bars.iter() if n.get("data-value")], data["bars"])
            lines = ET.parse(directory / "lines.svg").getroot().findall("{*}polyline")
            self.assertEqual(len(lines), 6)
            for line, values in zip(lines, data["lines"]):
                points = [tuple(map(float, p.split(','))) for p in line.get("points").split()]
                self.assertEqual([round((420-y)/3.5) for x, y in points], values)
            heatmap = ET.parse(directory / "heatmap.svg").getroot()
            self.assertEqual([int(n.get("data-value")) for n in heatmap.iter() if n.get("data-value") is not None],
                             [v for row in data["heatmap"] for v in row])

    def test_source_is_escaped_and_generated_assets_match(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            with patch("apt_theme.targets.css_tokens", return_value=""):
                tokens = {key: {} for key in ["foreground", "comment", "operator", "constant", "number", "type",
                                             "string", "keyword", "function", "primary", "diff_added", "diff_deleted"]}
                syntax(tokens, directory)
            page = (directory / "syntax-markup.html").read_text()
            self.assertIn('&lt;script&gt;', page)
            self.assertNotIn('<script>\n    // This script', page)
            for source in SOURCES.iterdir():
                self.assertEqual(source.read_bytes(), (directory / "sources" / source.name).read_bytes())
            verify_vendor(directory / "vendor/prism")
            self.assertEqual((directory / "syntax-example.html").read_bytes(), (directory / "syntax-javascript.html").read_bytes())

    def test_generated_css_references_are_declared(self):
        from apt_theme.semantics import assign
        from apt_theme.targets import adapt
        from apt_theme.colors import from_rgb
        colors = {f"color_{i:02}": from_rgb([i*7, i*6, i*5]) for i in range(1, 33)}
        roles, _ = assign(colors, {})
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            tokens = adapt(colors, roles, "syntax_highlighting", 32)["tokens"]
            syntax(tokens, directory)
            css = (directory / "prism.css").read_text() + (directory / "examples.css").read_text()
            declared = set(re.findall(r"(--[\w-]+)\s*:", css))
            used = set(re.findall(r"var\((--[\w-]+)\)", css))
            self.assertFalse(used - declared)


if __name__ == "__main__":
    unittest.main()
