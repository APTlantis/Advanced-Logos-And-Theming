import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from apt_theme.browser_themes import TARGETS, verify_vendor
from apt_theme.colors import from_rgb
from apt_theme.semantics import assign
from apt_theme.targets import DEFAULTS, adapt, export

class BrowserThemeTests(unittest.TestCase):
    def setUp(self):
        self.colors={f'color_{i:02}':from_rgb([i*7,i*6,i*4]) for i in range(1,33)}
        self.roles,_=assign(self.colors)

    def test_defaults_budgets_and_deterministic_exports(self):
        before=copy.deepcopy(self.colors)
        self.assertEqual(len(DEFAULTS),15)
        with tempfile.TemporaryDirectory() as temp:
            for target in TARGETS:
                self.assertEqual(DEFAULTS[target],40)
                hashes=[]
                for run in ('a','b'):
                    result=adapt(self.colors,self.roles,target,40)
                    self.assertEqual(result['named_count'],39)
                    tokens=copy.deepcopy(result['tokens'])
                    dest=Path(temp)/run/target
                    export(result,dest,'Test Dark',self.colors,'a'*64)
                    self.assertEqual(tokens,result['tokens'])
                    self.assertTrue((dest/'examples.html').exists())
                    self.assertTrue((dest/result['palette_artifacts']['palette']).exists())
                    hashes.append({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.rglob('*') if p.is_file()})
                self.assertEqual(*hashes)
                for key in ('cursor','search_text','matching_bracket','inserted','deleted'):
                    self.assertIn(key,result['tokens'])
                self.assertTrue(any(c['background']=='selection' and c['foreground']=='keyword' for c in result['checks']))
                with self.assertRaises(ValueError):
                    adapt(self.colors,self.roles,target,38)
        self.assertEqual(before,self.colors)

    def test_scoping_native_interfaces_and_coverage(self):
        with tempfile.TemporaryDirectory() as temp:
            for target in TARGETS:
                result=adapt(self.colors,self.roles,target,40)
                dest=Path(temp)/target
                export(result,dest,'Test Dark',self.colors,'a'*64)
                if target=='markdown':
                    css=(dest/'tokens.css').read_text()+(dest/'markdown.css').read_text()+(dest/'syntax-prism.css').read_text()
                    self.assertNotIn(':root',css)
                    self.assertNotIn('#write',css)
                    self.assertIn('.markdown-body .token.keyword',css)
                    self.assertNotIn('text-align:',css)
                    coverage=json.loads((dest/'coverage.json').read_text())
                    self.assertIn('footnotes',coverage['conditional'])
                    self.assertIn('Mermaid',coverage['deferred'])
                    preview=(dest/'examples.html').read_text()
                    self.assertIn('DOMPurify.sanitize',preview)
                    self.assertIn('marked.parse',preview)
                    self.assertNotIn('<script>window.unsafeMarkdownExecuted',preview)
                elif target=='codemirror5':
                    css=(dest/'apt-test-dark.css').read_text()
                    self.assertIn('.cm-s-apt-test-dark .cm-keyword',css)
                    self.assertNotIn(':root',css)
                    self.assertIn('.cm-s-apt-test-dark .CodeMirror-hints',css)
                else:
                    module=(dest/'theme.mjs').read_text()
                    for text in ('export const theme=', 'export const highlightStyle=', 'export const extension=', 'dark:true','syntaxHighlighting(highlightStyle)'):
                        self.assertIn(text,module)
                    self.assertNotIn('document.',module)

    def test_selected_targets_and_review_artifact_links(self):
        from apt_theme.cli import main
        from apt_theme.extraction import palette_toml
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            source=root/'palette.toml'
            source.write_text(palette_toml(self.colors,'Test Dark','a'*64),encoding='utf-8')
            output=root/'run'
            self.assertEqual(main(['import',str(source),'--output',str(output),'--targets',','.join(TARGETS)]),0)
            summary=json.loads((output/'run.json').read_text())
            self.assertEqual(summary['targets'],list(TARGETS))
            review=(output/'markdown-editors.html').read_text()
            for artifact in ('markdown/tokens.css','markdown/coverage.json','codemirror5/apt-palette.css','codemirror6/theme.mjs'):
                self.assertIn(artifact,review)
            self.assertIn('markdown-editors.html',(output/'review.html').read_text())
            self.assertEqual(main(['import',str(source),'--output',str(output),'--targets','markdown']),1)

    def test_vendor_integrity_and_fail_closed(self):
        manifest=verify_vendor()
        self.assertTrue(any(p['name']=='dompurify' for p in manifest['packages']))
        self.assertTrue(any(p['name']=='@codemirror/view' for p in manifest['packages']))
        with patch('apt_theme.browser_themes.hashlib.sha256') as sha:
            sha.return_value.hexdigest.return_value='invalid'
            with self.assertRaisesRegex(ValueError,'hash mismatch'):
                verify_vendor()

if __name__=='__main__':
    unittest.main()
