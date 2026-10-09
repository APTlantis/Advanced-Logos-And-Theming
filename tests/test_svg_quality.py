"""SVG editability, local references, paint provenance and deterministic output."""
import copy
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from apt_theme.colors import from_rgb
from apt_theme.semantics import assign
from apt_theme.targets import adapt
from apt_theme.svg_examples import diagrams
from apt_theme.visual_targets import Board


class SVGQualityTests(unittest.TestCase):
    def setUp(self):
        self.colors = {f"color_{i:02}": from_rgb([i*7, i*6, i*5]) for i in range(1,33)}
        roles, _ = assign(self.colors, {})
        self.tokens = adapt(self.colors, roles, "svg", 28)["tokens"]

    def test_local_references_and_editable_vector_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            examples = diagrams(self.tokens, directory)
            self.assertEqual(len(examples), 6)
            self.assertTrue({"technical-flow.svg", "editorial-infographic.svg", "orbit-map.svg"} <= set(examples))
            for filename in examples:
                root = ET.parse(directory / filename).getroot()
                self.assertEqual(root.get("viewBox"), "0 0 1200 800")
                self.assertEqual(root.get("aria-labelledby"), "title desc")
                self.assertIsNotNone(root.find("{*}title"))
                self.assertIsNotNone(root.find("{*}desc"))
                ids = [node.get("id") for node in root.iter() if node.get("id")]
                self.assertEqual(len(ids), len(set(ids)))
                self.assertGreaterEqual(len(root.findall("{*}g")), 2)
                self.assertEqual(len(root.findall("{*}defs/{*}symbol")), 12)
                for node in root.iter():
                    tag = node.tag.rsplit('}',1)[-1]
                    self.assertNotIn(tag, ("script", "image", "foreignObject", "animate", "set"))
                    for key, value in node.attrib.items():
                        self.assertFalse(key.lower().startswith("on"))
                        if key.endswith("href"):
                            self.assertTrue(value.startswith('#'), (filename,value))
                            self.assertIn(value[1:], ids)
                        for ref in re.findall(r"url\(#([^)]*)\)", value):
                            self.assertIn(ref, ids, (filename,ref))
            illustration = ET.parse(directory / "product-illustration.svg").getroot()
            self.assertIsNotNone(illustration.find("{*}defs/{*}clipPath"))
            self.assertIsNotNone(illustration.find("{*}defs/{*}radialGradient"))

    def test_paints_remain_exported_tokens_at_minimum_budget(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            examples = diagrams(self.tokens, directory)
            for filename in examples:
                root = ET.parse(directory / filename).getroot()
                paints = {node.get(key) for node in root.iter() for key in ("fill","stroke","stop-color")
                          if node.get(key,"").startswith('#')}
                self.assertLessEqual(paints, {color['hex'] for color in self.tokens.values()})
            css = (directory / "examples.css").read_text()
            self.assertFalse(set(re.findall(r"var\((--[\w-]+)\)",css)) - set(re.findall(r"(--[\w-]+)\s*:",css)))

    def test_determinism_and_unchanged_chart_canvas(self):
        before = copy.deepcopy(self.tokens)
        with tempfile.TemporaryDirectory() as temp:
            a, b = Path(temp)/"first", Path(temp)/"second"
            a.mkdir(); b.mkdir()
            diagrams(self.tokens, a); diagrams(self.tokens, b)
            self.assertEqual({p.name:p.read_bytes() for p in a.iterdir()}, {p.name:p.read_bytes() for p in b.iterdir()})
        self.assertEqual(self.tokens, before)
        self.assertEqual(Board(self.tokens,"Chart","Description").root.get("viewBox"),"0 0 960 540")


if __name__ == "__main__":
    unittest.main()
