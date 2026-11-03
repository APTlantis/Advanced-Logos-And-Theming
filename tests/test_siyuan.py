"""Behavioral contracts for native-scoped SiYuan mappings."""
import copy
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from apt_theme.colors import from_rgb
from apt_theme.semantics import assign
from apt_theme.targets import adapt, export
from apt_theme.siyuan import mapping, theme_css


def ratio(a, b):
    def luminance(value):
        channels = [int(value[i:i+2], 16) / 255 for i in (1, 3, 5)]
        linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in channels]
        return sum(v * w for v, w in zip(linear, (.2126, .7152, .0722)))
    low, high = sorted((luminance(a), luminance(b)))
    return (high + .05) / (low + .05)


class SiYuanTests(unittest.TestCase):
    def setUp(self):
        self.colors = {f'color_{i:02}': from_rgb([i*7, i*6, i*4]) for i in range(1, 33)}
        self.roles, _ = assign(self.colors)

    def test_budget_fallbacks_and_preservation(self):
        before = copy.deepcopy(self.colors)
        for budget in (22, 23, 40, 64):
            result = adapt(self.colors, self.roles, 'siyuan', budget)
            self.assertLessEqual(result['named_count'], budget)
            self.assertTrue(set(mapping(result['tokens'])['aliases'].values()) <= set(result['tokens']))
            self.assertEqual(result, adapt(self.colors, self.roles, 'siyuan', budget))
        self.assertEqual(before, self.colors)
        with self.assertRaisesRegex(ValueError, 'mandatory'):
            adapt(self.colors, self.roles, 'siyuan', 21)

    def test_declared_component_contrast_independently(self):
        result = adapt(self.colors, self.roles, 'siyuan', 64)
        self.assertEqual(result['contrast_failures'], 0)
        component_checks = [c for c in result['checks'] if 'selector' in c]
        self.assertGreater(len(component_checks), 70)
        for check in component_checks:
            actual = ratio(result['tokens'][check['foreground']]['hex'], result['tokens'][check['background']]['hex'])
            self.assertGreaterEqual(actual + 1e-9, check['required'], check)

    def test_native_scoping_and_user_layout_preservation(self):
        css = theme_css(adapt(self.colors, self.roles, 'siyuan', 64)['tokens'])
        for rule in css.split('}'):
            if rule.strip():
                self.assertTrue(rule.strip().startswith("html[data-theme-mode='dark']"))
        for forbidden in ('font-family:', '!important', 'table-layout:', 'position:sticky', 'a, h1', '.apt-primary:hover'):
            self.assertNotIn(forbidden, css)
        self.assertIn('.hljs-title.function_', css)
        self.assertIn('tbody tr:nth-child(even)', css)
        self.assertIn('[data-type~="code"]', css)

    def test_status_change_is_target_local(self):
        self.roles['error'] = self.roles['warning']
        siyuan = adapt(self.colors, self.roles, 'siyuan', 64)
        typora = adapt(self.colors, self.roles, 'typora', 40)
        self.assertNotEqual(siyuan['tokens']['error']['hex'], siyuan['tokens']['warning']['hex'])
        self.assertEqual(typora['tokens']['error']['hex'], typora['tokens']['warning']['hex'])
        self.assertEqual(siyuan['tokens']['error']['origin']['source'], self.roles['error'])

    def test_native_package_and_external_specimen(self):
        result = adapt(self.colors, self.roles, 'siyuan', 64)
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / 'siyuan'
            export(result, destination, 'apt-Test', self.colors, 'a'*64)
            with zipfile.ZipFile(destination/result['artifact_paths']['package.zip']) as package:
                self.assertEqual(set(package.namelist()), {'theme.css', 'theme.json', 'README.md', 'preview.png', 'icon.png'})
                self.assertEqual(package.read('theme.css'), (destination/'theme.css').read_bytes())
            tokens = json.loads((destination/result['artifact_paths']['tokens.json']).read_text(encoding='utf-8'))
            self.assertEqual(tokens['siyuan']['schema'], 'aptlantis.siyuan-mapping.v1')
            specimen = (destination/result['artifact_paths']['examples.html']).read_text(encoding='utf-8')
            self.assertIn('Authored browser specimen', specimen)
            self.assertIn('id="unrelated-button"', specimen)
