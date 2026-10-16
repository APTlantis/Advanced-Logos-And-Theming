import copy
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from apt_theme.colors import from_rgb
from apt_theme.output_names import named_exports
from apt_theme.semantics import assign
from apt_theme.targets import DEFAULTS, adapt, export


class OutputNameTests(unittest.TestCase):
    def test_flat_collection_across_themes_and_targets(self):
        colors = {f"color_{i:02}": from_rgb([i * 7, i * 6, i * 4]) for i in range(1, 33)}
        before = copy.deepcopy(colors)
        roles, _ = assign(colors)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            collected = set()
            for name in ("Aptlantis-Ada", "apt-Swift"):
                language = name.split("-")[-1].lower()
                for target, budget in DEFAULTS.items():
                    directory = root / language / target
                    result = adapt(colors, roles, target, budget)
                    export(result, directory, name, colors, "a" * 64)
                    stem = f"apt-{language}-{target.replace('_', '-')}"
                    manifest = json.loads((directory / (stem + "-files.json")).read_text())
                    self.assertEqual(manifest["files"], result["named_exports"]["files"])
                    for record in manifest["files"]:
                        self.assertNotIn(record["file"], collected)
                        collected.add(record["file"])
                        data = (directory / record["file"]).read_bytes()
                        self.assertEqual(data, (directory / record["native_file"]).read_bytes())
                        self.assertEqual(hashlib.sha256(data).hexdigest(), record["sha256"])
                    if target == "kmindz":
                        self.assertTrue((directory / (stem + ".json")).is_file())
                    elif target in ("markdown", "codemirror5", "typora", "website", "siyuan"):
                        self.assertTrue((directory / (stem + ".css")).is_file())
                    elif target == "codemirror6":
                        self.assertTrue((directory / (stem + ".mjs")).is_file())
                    if target == "siyuan":
                        with zipfile.ZipFile(directory / (stem + ".zip")) as package:
                            self.assertIn("theme.css", package.namelist())
                            self.assertIn("theme.json", package.namelist())
            self.assertEqual(before, colors)

    def test_collision_is_rejected_before_copying(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            (directory / "example.json").write_text("two")
            # Punctuation-normalized roles must not silently overwrite each other.
            (directory / "example_.json").write_text("three")
            with self.assertRaisesRegex(ValueError, "collision"):
                named_exports({"target": "svg"}, directory, "Ada")
            self.assertFalse((directory / "apt-ada-svg-example.json").exists())
