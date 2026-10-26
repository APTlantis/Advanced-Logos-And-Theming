"""Finishing contract: explicit selection, preserved sources, accurate vectors and SESM."""
import base64
import io
import json
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from apt_theme import finishing
from apt_theme.cli import main
from apt_theme.colors import from_rgb
from apt_theme.extraction import palette_toml
from apt_theme.output_names import artifact_file, manifest_records, SCHEMA as ARTIFACT_SCHEMA
from apt_theme.target_palette import toml_document
from apt_theme.transactions import staged_directory

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent / 'SESM-Metadata-Embedder'
STANDARD = Path('D:/.city_hall/SESM')


class FinishingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix='finish fixtures ')
        cls.fixture = Path(cls.temporary.name)
        colors = {f'color_{i:02}': from_rgb([i * 7, i * 6, i * 4]) for i in range(1, 33)}
        palette = cls.fixture / 'fixture.toml'
        palette.write_text(palette_toml(colors, 'dnf-Fixture', 'fixture'), encoding='utf-8')
        cls.fixture_run = cls.fixture / 'dnf-Fixture'
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            code = main(['import', str(palette), '--output', str(cls.fixture_run), '--targets', 'windows_terminal'])
        if code:
            raise RuntimeError('Finishing test fixture generation failed')

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='finish selected ')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.image = self.root / 'art.png'
        Image.new('RGBA', (80, 40), (170, 112, 36, 120)).save(self.image)
        self.output = self.root / 'finished'
        self.plan = self.root / 'selection.toml'

    def selection(self, assets):
        self.plan.write_text(toml_document({'schema': finishing.SCHEMA, 'assets': assets}), encoding='utf-8')

    def call(self, write=False, extra=()):
        out, err = io.StringIO(), io.StringIO()
        argv = ['finish', str(self.plan), '--output', str(self.output), '--json',
                '--sesm-project', str(PROJECT), '--sesm-standard', str(STANDARD), *extra]
        with redirect_stdout(out), redirect_stderr(err):
            code = main(argv + (['--write'] if write else []))
        return code, json.loads(out.getvalue()), err.getvalue()

    def basic(self, **changes):
        return {'id': 'art', 'input': str(self.image), 'role': 'decorative', **changes}

    def test_explicit_preview_preparation_and_fresh_destination(self):
        self.selection([self.basic()])
        before = finishing.digest(self.image)
        items, sources = finishing.prepare(self.plan, self.output)
        self.assertEqual(items[0]['mode'], 'embed')
        self.assertEqual(items[0]['metadata']['asset']['role'], 'decorative')
        self.assertEqual(sources[str(self.image.resolve())], before)
        self.assertFalse(self.output.exists())
        self.assertEqual(finishing.digest(self.image), before)

    def test_invalid_selection_collisions_and_overlap(self):
        invalid = [[], [self.basic(), self.basic()],
                   [self.basic(), self.basic(id='other', output='ART.svg')],
                   [self.basic(output='../escape.svg')], [self.basic(output='CON.svg')],
                   [self.basic(mode='invent')], [self.basic(mode='palette')],
                   [self.basic(input=str(self.root))], [self.basic(unexpected=True)]]
        for assets in invalid:
            with self.subTest(assets=assets):
                self.selection(assets)
                with self.assertRaises((ValueError, OSError)):
                    finishing.prepare(self.plan, self.output)
        self.selection([{'id': 'palette', 'run': str(self.fixture_run), 'mode': 'palette', 'role': 'theme-board'}])
        with self.assertRaises(ValueError):
            finishing.prepare(self.plan, self.fixture_run / 'finished')

    def test_palette_requires_matching_pixels_and_structure(self):
        self.selection([self.basic(mode='palette', palette=str(self.fixture_run / 'palette.toml'))])
        with self.assertRaisesRegex(ValueError, 'dimensions'):
            finishing.prepare(self.plan, self.output)
        bad = self.root / 'wrong.png'
        Image.new('RGB', (1024, 656), 'red').save(bad)
        self.selection([self.basic(input=str(bad), mode='palette', palette=str(self.fixture_run / 'palette.toml'))])
        with self.assertRaisesRegex(ValueError, 'fill'):
            finishing.prepare(self.plan, self.output)

    def test_native_palette_preserves_order_fills_labels_and_bounds(self):
        self.selection([{'id': 'palette', 'run': str(self.fixture_run), 'mode': 'palette', 'role': 'theme-board'}])
        items, _ = finishing.prepare(self.plan, self.output)
        item = items[0]
        svg = ET.fromstring(finishing.palette_svg(item))
        rectangles = [e for e in svg if e.get('data-color-id')]
        self.assertEqual([(e.get('data-color-id'), e.get('fill')) for e in rectangles],
                         [(k, c['hex']) for k, c in item['rows']])
        self.assertFalse(any(e.tag.endswith('image') for e in svg))
        for e in svg:
            if e.tag.endswith('text'):
                self.assertLessEqual(float(e.get('x')) + float(e.get('textLength')), float(svg.get('width')))
                self.assertLessEqual(float(e.get('y')), float(svg.get('height')))

    def test_manifest_hash_mismatch_rejects_before_writing(self):
        run = self.root / 'dnf-Copy'
        shutil.copytree(self.fixture_run, run)
        source = finishing.artifact_file(run, 'windows_terminal', 'swatch.png')
        source.write_bytes(self.image.read_bytes())
        self.selection([{'id': 'target', 'run': str(run), 'target': 'windows_terminal', 'mode': 'palette', 'role': 'theme-board'}])
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            finishing.prepare(self.plan, self.output)
        self.assertFalse(self.output.exists())

    @unittest.skipUnless((PROJECT / 'scripts/Embed-SESM.py').exists() and (STANDARD / 'svg_asset.schema.json').exists(), 'Canonical SESM integration requires the sibling tools and standard')
    def test_four_representative_outputs_real_embedding_and_validation(self):
        self.selection([self.basic(id='logo', role='logo'),
                        {'id': 'canonical', 'run': str(self.fixture_run), 'mode': 'palette', 'role': 'theme-board'},
                        {'id': 'target', 'run': str(self.fixture_run), 'target': 'windows_terminal', 'mode': 'palette', 'role': 'theme-board'},
                        self.basic(id='misc')])
        source_hashes = {str(p): finishing.digest(p) for p in self.fixture_run.rglob('*') if p.is_file()}
        code, preview, err = self.call()
        self.assertEqual(code, 0, err)
        self.assertEqual(len(preview['data']['assets']), 4)
        self.assertFalse(self.output.exists())
        code, response, err = self.call(True)
        self.assertEqual(code, 0, err)
        receipt = json.loads((self.output / 'finish-receipt.json').read_text(encoding='utf-8'))
        self.assertEqual(response['data'], receipt)
        self.assertTrue(receipt['written'])
        for item in receipt['assets']:
            self.assertEqual(item['sha256'], finishing.digest(self.output / item['file']))
            self.assertEqual(item['validation']['profile'], 'sesm-safe')
            self.assertEqual(item['schema_validation'], 'passed')
            svg = ET.parse(self.output / item['file']).getroot()
            metadata = json.loads(next(e.text for e in svg if e.get('id') == 'sesm'))
            self.assertEqual(metadata['asset']['role'], 'theme-board' if item['id'] in ('canonical', 'target') else 'logo' if item['id'] == 'logo' else 'decorative')
            if item['id'] in ('logo', 'misc'):
                image = next(e for e in svg if e.tag.endswith('image'))
                self.assertEqual(base64.b64decode(image.get('href').split(',', 1)[1]), self.image.read_bytes())
            else:
                self.assertEqual(metadata['theme']['id'], 'dnf-fixture')
        self.assertEqual(source_hashes, {str(p): finishing.digest(p) for p in self.fixture_run.rglob('*') if p.is_file()})

    def test_missing_tools_and_invalid_metadata_report_json_errors(self):
        self.selection([self.basic()])
        code, result, err = self.call(extra=['--sesm-project', str(self.root / 'absent')])
        self.assertEqual(code, 1)
        self.assertEqual(result['status'], 'error')
        self.assertTrue(err.startswith('Error:'))
        self.assertFalse(self.output.exists())
        if (STANDARD / 'svg_asset.schema.json').exists():
            self.selection([self.basic(role='not-a-role')])
            code, result, err = self.call()
            self.assertEqual(code, 1)
            self.assertFalse(self.output.exists())

    def test_missing_tracer_never_falls_back(self):
        self.selection([self.basic(mode='trace')])
        with patch.object(finishing, 'invoke', return_value='[]'):
            code, result, err = self.call(True, ['--vtracer', str(self.root / 'missing.exe')])
        self.assertEqual(code, 1)
        self.assertEqual(result['status'], 'error')
        self.assertFalse(self.output.exists())

    def test_trace_finishing_contract_with_stub_and_real_raster_preparation(self):
        self.selection([self.basic(mode='trace', role='logo')])
        original = finishing.svg_converter.run
        def tracer(command):
            if command[0] == 'test-vtracer':
                if '--version' in command:
                    return 'vtracer 1.0.0-alpha.4 (test stub)'
                target = Path(command[command.index('--output') + 1])
                target.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="80" height="40" viewBox="0 0 80 40"><path fill="#AA7024" d="M0 0 L80 0 L80 40 Z"/></svg>', encoding='utf-8')
                return ''
            return original(command)
        with patch.object(finishing.svg_converter, 'run', side_effect=tracer):
            code, result, err = self.call(True, ['--vtracer', 'test-vtracer'])
        self.assertEqual(code, 0, err)
        svg = ET.parse(self.output / 'art.svg').getroot()
        self.assertTrue(any(e.tag.endswith('path') for e in svg))
        self.assertFalse(any(e.tag.endswith('image') for e in svg))
        self.assertEqual(result['data']['assets'][0]['settings']['mode'], 'trace')

    def test_historical_generic_artifact_lookup_and_bounded_version_inference(self):
        run = self.root / 'dnf-legacy'
        shutil.copytree(self.fixture_run, run)
        metadata = json.loads((run / 'run.json').read_text(encoding='utf-8'))
        manifest = json.loads((run / metadata['artifact_manifests']['windows_terminal']).read_text(encoding='utf-8'))
        for record in manifest['files']:
            (run / 'windows_terminal' / record['file']).rename(run / 'windows_terminal' / record['logical_name'])
        metadata.pop('artifact_manifests')
        metadata.pop('theme_identity')
        metadata['name'] = 'Aptlantis-Fixture'
        (run / 'run.json').write_text(json.dumps(metadata), encoding='utf-8')
        self.selection([{'id': 'legacy', 'run': str(run), 'target': 'windows_terminal', 'role': 'theme-board'}])
        items, _ = finishing.prepare(self.plan, self.output)
        self.assertEqual(items[0]['source'].name, 'swatch.png')
        self.assertEqual(items[0]['metadata']['theme']['id'], 'dnf-fixture')

    def test_warning_is_not_reported_as_safe_and_sources_are_rechecked(self):
        self.selection([self.basic()])
        original = finishing.invoke
        def warning(command, **kwargs):
            result = original(command, **kwargs)
            if '--safe-profile' in command:
                validation = json.loads(result)
                validation.update(status='warning', profile='sesm-unverified', warnings=[{'code': 'review', 'message': 'Review needed', 'path': ''}])
                return json.dumps(validation)
            return result
        with patch.object(finishing, 'invoke', side_effect=warning):
            code, result, err = self.call(True)
        self.assertEqual(code, 0, err)
        self.assertEqual(result['status'], 'warning')
        self.assertEqual(result['data']['assets'][0]['validation']['profile'], 'sesm-unverified')
        second = self.root / 'second'
        self.output = second
        def change_source(command, **kwargs):
            result = original(command, **kwargs)
            if '--safe-profile' in command:
                self.image.write_bytes(b'changed concurrently')
            return result
        with patch.object(finishing, 'invoke', side_effect=change_source):
            code, result, err = self.call(True)
        self.assertEqual(code, 1)
        self.assertIn('changed during finishing', err)
        self.assertFalse(second.exists())

    def test_invalid_svg_rolls_back_and_existing_destination_is_untouched(self):
        self.selection([self.basic()])
        with patch.object(finishing.svg_converter, 'embed_svg', return_value=b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'):
            code, result, err = self.call(True)
        self.assertEqual(code, 1)
        self.assertFalse(self.output.exists())
        self.output.mkdir()
        marker = self.output / 'preserve'
        marker.write_bytes(b'original')
        code, result, err = self.call(True)
        self.assertEqual(code, 1)
        self.assertEqual(marker.read_bytes(), b'original')


class TransactionTests(unittest.TestCase):
    def test_artifact_inventory_rejects_traversal_duplicates_and_stale_hashes(self):
        valid = {'schema': ARTIFACT_SCHEMA, 'target': 'example',
                 'files': [{'file': 'image.png', 'logical_name': 'swatch.png', 'sha256': 'wrong'}]}
        for filename in ('../escape.png', 'folder/image.png', 'folder\\image.png', ''):
            invalid = {**valid, 'files': [{**valid['files'][0], 'file': filename}]}
            with self.assertRaises(ValueError):
                manifest_records(invalid, 'example')
        with self.assertRaises(ValueError):
            manifest_records({**valid, 'files': valid['files'] * 2}, 'example')
        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            (run / 'example').mkdir()
            (run / 'example/image.png').write_bytes(b'changed')
            (run / 'example/files.json').write_text(json.dumps(valid), encoding='utf-8')
            (run / 'run.json').write_text(json.dumps({'artifact_manifests': {'example': 'example/files.json'}}), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                artifact_file(run, 'example', 'swatch.png', verify=True)

    def test_failed_commit_restores_existing_run(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'output'
            output.mkdir()
            (output / 'keep').write_bytes(b'original')
            rename = Path.rename
            def fail(stage, destination):
                if stage.name == 'result':
                    raise OSError('simulated commit failure')
                return rename(stage, destination)
            with patch.object(Path, 'rename', fail), self.assertRaises(OSError):
                with staged_directory(output, prefix='test-', overwrite=True) as stage:
                    stage.mkdir()
                    (stage / 'new').write_bytes(b'new')
            self.assertEqual((output / 'keep').read_bytes(), b'original')
            self.assertFalse((output / 'new').exists())

    def test_fresh_transaction_does_not_overwrite_new_destination(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'output'
            with self.assertRaises(ValueError):
                with staged_directory(output, prefix='test-') as stage:
                    stage.mkdir()
                    output.mkdir()
                    (output / 'keep').write_bytes(b'other writer')
            self.assertEqual((output / 'keep').read_bytes(), b'other writer')


if __name__ == '__main__':
    unittest.main()
