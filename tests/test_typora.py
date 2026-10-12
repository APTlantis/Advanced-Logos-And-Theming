import copy
import hashlib
import tempfile
import unittest
from pathlib import Path

from apt_theme.colors import from_rgb
from apt_theme.semantics import assign
from apt_theme.targets import adapt, editor_css, export
from apt_theme.typora import specimens


class TyporaTests(unittest.TestCase):
    def test_exports_preserve_tokens_and_are_deterministic(self):
        colors = {f'color_{i:02}': from_rgb([i * 7, i * 6, i * 4]) for i in range(1, 33)}
        before = copy.deepcopy(colors)
        roles, _ = assign(colors)
        with tempfile.TemporaryDirectory() as temp:
            outputs = []
            for name in ('a', 'b'):
                result = adapt(colors, roles, 'typora', 40)
                original_tokens = copy.deepcopy(result['tokens'])
                directory = Path(temp) / name
                export(result, directory, 'Test Dark', colors, 'a' * 64)
                self.assertEqual(result['tokens'], original_tokens)
                self.assertEqual(result['named_count'], 40)
                self.assertEqual(result['contrast_failures'], 0)
                self.assertEqual(result['examples'], ['examples.html', 'examples.md'])
                document = (directory / 'examples.html').read_text(encoding='utf-8')
                self.assertIn('href="test-dark.css"', document)
                self.assertIn('id="write"', document)
                self.assertIn('browser simulation', document)
                self.assertTrue((directory / 'example-image.png').exists())
                outputs.append({p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.iterdir()})
            self.assertEqual(*outputs)
        self.assertEqual(colors, before)

    def test_native_layout_and_scoped_styles(self):
        tokens = {key: {'hex': '#123456'} for key in ('primary_hover', 'primary_pressed')}
        css = editor_css(tokens)
        for selector in ('#write h6', '#write table', '#write tbody tr:nth-child(even)',
                         '#write .md-def-footnote', '#write .md-toc', '#write img'):
            self.assertIn(selector, css)
        self.assertNotIn('.b3-', css)
        self.assertNotIn('position:sticky', css)
        self.assertNotIn('display:block', css)
        self.assertNotIn('table-layout:fixed', css)
        self.assertNotIn('text-align:', css)
        self.assertNotIn('white-space:', css)

    def test_packaged_specimens_cover_stress_cases(self):
        markdown, markup = specimens('<unsafe>')
        self.assertIn('&lt;unsafe&gt;', markup)
        self.assertIn('| 100 | Sample 100 | 700 |', markdown)
        self.assertIn('| C12 |', markdown)
        self.assertIn('---:', markdown)
        for text in ('[TOC]', '[^1]', '- [x]', '######', '```python', 'example-image.png'):
            self.assertIn(text, markdown)
        self.assertEqual(markup.count('<table '), 4)
