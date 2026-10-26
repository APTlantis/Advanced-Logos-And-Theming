import copy
import hashlib
import json
import re
import tempfile
import tomllib
import unittest
import zipfile
import io
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

from apt_theme.colors import from_rgb
from apt_theme.identity import PREFIXES, resolve_identity
from apt_theme.output_names import ArtifactNames, SCHEMA
from apt_theme.semantics import assign
from apt_theme.targets import DEFAULTS, adapt, export


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        self.links.extend(value for key, value in attrs if key in ('href', 'src', 'data-source') or (tag == 'object' and key == 'data'))


class OutputNameTests(unittest.TestCase):
    def test_import_identity_roundtrip_without_prefix_or_flag(self):
        from apt_theme.cli import main
        from apt_theme.extraction import palette_toml
        from apt_theme.output_names import artifact_file
        colors = {f'color_{i:02}': from_rgb([i*7, i*6, i*4]) for i in range(1, 33)}
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root/'palette.toml'
            identity = resolve_identity('Ada', 5).record()
            source.write_text(palette_toml(colors, 'Ada', 'a'*64, identity), encoding='utf-8')
            for name, input_file in (('first',source), ('second',root/'first/palette.toml')):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    self.assertEqual(main(['import',str(input_file),'--output',str(root/name),'--targets','windows_terminal']), 0)
                metadata = json.loads((root/name/'run.json').read_text(encoding='utf-8'))
                self.assertEqual(metadata['name'], 'Ada')
                self.assertEqual(metadata['theme_identity']['version'], 5)
                tokens = artifact_file(root/name, 'windows_terminal', 'tokens.json')
                self.assertEqual(tokens.name, 'eopkg-ada-windows-terminal-tokens.json')
                self.assertTrue(tokens.is_file())

    def test_cli_missing_and_conflicting_versions_fail_before_extraction(self):
        from apt_theme.cli import main
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root/'image.png'
            source.write_bytes(b'Identity must be checked before extraction')
            for extra, message in (([], 'Cannot determine'), (['--name','dnf-Ada','--theme-version','1'], 'Conflicting')):
                out, err = io.StringIO(), io.StringIO()
                with patch('apt_theme.pipeline.extract') as extract, redirect_stdout(out), redirect_stderr(err):
                    code = main(['generate',str(source),'--output',str(root/'output'),'--json',*extra])
                self.assertEqual(code, 1)
                extract.assert_not_called()
                self.assertFalse((root/'output').exists())
                self.assertIn(message, json.loads(out.getvalue())['errors'][0]['message'])

    def test_all_versions_targets_inventory_links_and_preservation(self):
        colors = {f'color_{i:02}': from_rgb([i*7, i*6, i*4]) for i in range(1, 33)}
        before = copy.deepcopy(colors)
        roles, _ = assign(colors)
        collected = set()
        with tempfile.TemporaryDirectory() as temp:
            for version, prefix in PREFIXES.items():
                for target, budget in DEFAULTS.items():
                    with self.subTest(version=version, target=target):
                        result = adapt(colors, roles, target, budget)
                        directory = Path(temp)/prefix/target
                        export(result, directory, prefix+'-Ada', colors, 'a'*64)
                        stem = prefix+'-ada-'+target.replace('_', '-')
                        manifest_file = directory/(stem+'-files.json')
                        manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
                        self.assertEqual(manifest['schema'], SCHEMA)
                        self.assertEqual(manifest['theme_identity']['version'], version)
                        self.assertEqual({p.name for p in directory.iterdir() if p.is_file()}, {r['file'] for r in manifest['files']} | {manifest_file.name})
                        for record in manifest['files']:
                            data = (directory/record['file']).read_bytes()
                            self.assertEqual(hashlib.sha256(data).hexdigest(), record['sha256'])
                            if not record['fixed_name_reason']:
                                self.assertTrue(record['file'].startswith(stem))
                                self.assertNotIn(record['file'], collected)
                                collected.add(record['file'])
                            if record['file'].endswith('.html'):
                                parser = Links()
                                parser.feed(data.decode('utf-8'))
                                for link in parser.links:
                                    url = urlsplit(link)
                                    if not url.scheme and not url.netloc and url.path:
                                        self.assertTrue((directory/unquote(url.path)).is_file(), (record['file'], link))
                        palette = tomllib.loads((directory/(stem+'-palette.toml')).read_text(encoding='utf-8'))
                        self.assertEqual(palette['theme']['theme_identity']['prefix'], prefix)
                        if target == 'siyuan':
                            with zipfile.ZipFile(directory/(stem+'.zip')) as bundle:
                                self.assertEqual(set(bundle.namelist()), {'theme.css','theme.json','README.md','icon.png','preview.png'})
                        if target == 'codemirror5':
                            css = (directory/(stem+'.css')).read_text(encoding='utf-8')
                            self.assertIn('.cm-s-'+prefix+'-ada .cm-keyword', css)
                            preview = (directory/(stem+'-examples.html')).read_text(encoding='utf-8')
                            self.assertIn('theme:"'+prefix+'-ada"', preview)
                        if target == 'codemirror6':
                            preview = (directory/(stem+'-examples.html')).read_text(encoding='utf-8')
                            self.assertIn('from "./'+stem+'.mjs"', preview)
        self.assertEqual(before, colors)

    def test_collision_rejected_without_writing(self):
        names = ArtifactNames(resolve_identity('rpm-Ada'), 'svg', 'rpm-Ada')
        names('example.json')
        with self.assertRaisesRegex(ValueError, 'collision'):
            names('example_.json')
        with self.assertRaisesRegex(ValueError, 'top-level'):
            names('../escape.json')

    def test_identity_resolution_and_conflicts(self):
        for version, prefix in PREFIXES.items():
            self.assertEqual(resolve_identity('Aptlantis '+prefix.upper()+' Ada Dark').key, prefix+'-ada-dark')
            self.assertEqual(resolve_identity('Aptlantis-Ada', version).version, version)
        for name in ('', 'Aptlantis', 'apt-', 'dnf-apt-Ada', 'rpm-yum-Ada', 'apt-aptlantis-Ada'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                resolve_identity(name, 1)
        with self.assertRaisesRegex(ValueError, 'Cannot determine'):
            resolve_identity('Ada')
        with self.assertRaisesRegex(ValueError, 'Conflicting'):
            resolve_identity('dnf-Ada', 1)
        for value in (True, 1.0, '1', 6):
            with self.subTest(value=value), self.assertRaises(ValueError):
                resolve_identity('Ada', value)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run = root/'eopkg-Ada'
            (run/'source').mkdir(parents=True)
            source = run/'source'/'image.png'
            self.assertEqual(resolve_identity('Ada', source=source).version, 5)
            (run/'run.json').write_text(json.dumps({'name':'Ada', 'theme_identity':{'version':5,'prefix':'eopkg'}}))
            self.assertEqual(resolve_identity('Ada', source=source).version, 5)
            with self.assertRaisesRegex(ValueError, 'Conflicting'):
                resolve_identity('Ada', 4, source)
            self.assertEqual(resolve_identity('Ada', imported={'theme':{'name':'yum-Ada'}}).version, 4)
            with self.assertRaisesRegex(ValueError, 'Conflicting'):
                resolve_identity('Ada', source=source, imported={'theme':{'name':'rpm-Ada'}})
            # An arbitrary distant ancestor must not label an unversioned input.
            with self.assertRaisesRegex(ValueError, 'Cannot determine'):
                resolve_identity('Ada', source=run/'nested'/'deeper'/'image.png')
