import copy
import re
import tempfile
import unittest
from pathlib import Path

from apt_theme.extraction import load_palette
from apt_theme.semantics import assign
from apt_theme.targets import adapt, export
from apt_theme.colors import contrast


class WebsiteTests(unittest.TestCase):
    def palette(self):
        return load_palette(Path(__file__).resolve().parents[1] / 'pilot/visual-targets/palette.toml')[0]

    def test_website_provenance_budget_and_real_contrast_pairs(self):
        colors = self.palette()
        before = copy.deepcopy(colors)
        roles, _ = assign(colors)
        result = adapt(colors, roles, 'website', 112)
        self.assertEqual(colors, before)
        self.assertEqual(result['named_count'], 89)
        with self.assertRaisesRegex(ValueError, 'mandatory'):
            adapt(colors, roles, 'website', 88)
        self.assertEqual(adapt(colors, roles, 'website', 89)['tokens'], result['tokens'])
        for token in result['tokens'].values():
            self.assertIn(token['origin']['source'], colors)
            requested = token['origin']['requested_oklch']
            self.assertAlmostEqual(requested[2], colors[token['origin']['source']]['oklch'][2])
        for check in result['checks']:
            measured = contrast(result['tokens'][check['foreground']], result['tokens'][check['background']])
            self.assertAlmostEqual(check['ratio'], measured)
            self.assertEqual(check['pass'], measured >= check['required'])
        self.assertEqual(result['contrast_failures'], 0)

    def test_website_export_scoping_local_assets_and_safe_name(self):
        colors = self.palette()
        result = adapt(colors, assign(colors)[0], 'website', 112)
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp) / 'website'
            export(result, directory, '<script>bad()</script>', colors, '0' * 64)
            css = (directory / 'theme.css').read_text()
            declared = set(re.findall(r'(--[\w-]+)\s*:', css))
            used = set(re.findall(r'var\((--[\w-]+)\)', css))
            self.assertFalse(used - declared)
            self.assertEqual(len(declared), len(result['tokens']))
            self.assertFalse(declared - used, 'Every token must have an actual CSS consumer')
            for rule in css.split('}'):
                if '{' in rule:
                    self.assertTrue(all(s.strip().startswith('.apt-site') for s in rule.split('{')[0].split(',')))
            for example in result['examples']:
                page = (directory / example).read_text()
                self.assertNotIn('<script>bad()', page)
                self.assertNotIn('https://', page)
                self.assertIn('class="apt-site"', page)
            self.assertIn('showModal()', (directory / 'components.html').read_text())
