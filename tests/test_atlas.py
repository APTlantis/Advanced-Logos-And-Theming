import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout,redirect_stderr
from unittest.mock import patch

from apt_theme.atlas import snapshot,build
from apt_theme.cli import main
from apt_theme.colors import from_rgb
from apt_theme.extraction import palette_toml


class AtlasTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.collection=self.root/'collection'
        self.collection.mkdir()
        self.colors={f'color_{i:02}':from_rgb([i*7,i*6,i*4]) for i in range(1,33)}
        self.payload={'target':'test','tokens':{'primary':{**self.colors['color_28'],'origin':{'source':'color_28','derived':False,'purpose':'test primary','requested_oklch':self.colors['color_28']['oklch'],'gamut_mapped':False}}},'contrast_failures':0}
        for name in ('apt-One','apt-Two'):
            run=self.collection/name
            (run/'test').mkdir(parents=True)
            (run/'palette.toml').write_text(palette_toml(self.colors,name,'a'*64),encoding='utf-8')
            (run/'run.json').write_text(json.dumps({'schema':'aptlantis.theme-run.v1','name':name,'variant':'dark','targets':['test']}),encoding='utf-8')
            (run/'semantics.json').write_text(json.dumps({'roles':{'primary':'color_28'}}),encoding='utf-8')
            (run/'test/tokens.json').write_text(json.dumps(self.payload),encoding='utf-8')

    def hashes(self,path):
        return {p.relative_to(path).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in path.rglob('*') if p.is_file()}

    def test_snapshot_identity_lineage_and_source_receipts(self):
        before=self.hashes(self.collection)
        data=snapshot(self.collection)
        self.assertEqual(data['counts'],dict(themes=2,canonical=64,exported_tokens=2,sources=8))
        color=next(c for c in data['canonical'] if c['id']=='apt-One:color_28')
        self.assertEqual(color['rgb'],self.colors['color_28']['rgb'])
        self.assertEqual(color['roles'],['primary'])
        self.assertEqual(data['tokens'][0]['canonical_id'],'apt-One:color_28')
        self.assertEqual(len(color['oklab']),3)
        self.assertEqual(color['stored_oklch']['h'],round(color['oklch'][2],10))
        for record in data['sources']:
            self.assertEqual(record['sha256'],before[record['path']])
        self.assertEqual(before,self.hashes(self.collection))

    def test_deterministic_outputs_and_both_offline_data_forms(self):
        a,b=self.root/'a',self.root/'b'
        build(self.collection,a)
        build(self.collection,b)
        self.assertEqual(self.hashes(a),self.hashes(b))
        data=json.loads((a/'atlas.json').read_text(encoding='utf-8'))
        script=(a/'atlas-data.js').read_text(encoding='utf-8')
        self.assertEqual(data,json.loads(script.removeprefix('window.ATLAS_DATA=').removesuffix(';\n')))
        for name in ('index.html','styles.css','app.js','README.md','.atlas-run.json'):
            self.assertTrue((a/name).is_file())

    def test_rejects_false_lineage_and_inconsistent_rgb(self):
        file=self.collection/'apt-One/test/tokens.json'
        for change in ('source','derived','rgb'):
            with self.subTest(change=change):
                payload=copy.deepcopy(self.payload)
                token=payload['tokens']['primary']
                if change=='source':token['origin']['source']='missing'
                elif change=='derived':token['origin']['derived']=True
                else:token['rgb']=[0,0,0]
                file.write_text(json.dumps(payload),encoding='utf-8')
                with self.assertRaises(ValueError):snapshot(self.collection)

    def test_missing_data_reported_without_inference(self):
        (self.collection/'apt-One/semantics.json').unlink()
        (self.collection/'apt-One/test/tokens.json').unlink()
        data=snapshot(self.collection)
        self.assertEqual({f['kind'] for f in data['findings']},{'missing_semantics','missing_target'})
        self.assertEqual(data['themes'][0]['roles'],{})
        self.assertEqual(data['counts']['exported_tokens'],1)

    def test_output_guards_and_failed_refresh_preserve_existing_snapshot(self):
        out=self.root/'atlas'
        build(self.collection,out)
        before=self.hashes(out)
        with self.assertRaises(ValueError):build(self.collection,out)
        (self.collection/'apt-One/test/tokens.json').write_text('{}',encoding='utf-8')
        with self.assertRaises(ValueError):build(self.collection,out,overwrite=True)
        self.assertEqual(before,self.hashes(out))
        unrelated=self.root/'unrelated'
        unrelated.mkdir()
        (unrelated/'keep.txt').write_text('keep')
        with self.assertRaises(ValueError):build(self.collection,unrelated,overwrite=True)
        self.assertEqual((unrelated/'keep.txt').read_text(),'keep')
        # A source edit during preview copying must not publish stale metadata.
        (self.collection/'apt-One/test/tokens.json').write_text(json.dumps(self.payload),encoding='utf-8')
        preview=self.collection/'apt-One/test/examples.html'
        preview.write_text('<p>Preview</p>',encoding='utf-8')
        original_read=Path.read_bytes
        changed=[]
        def change_during_copy(path):
            content=original_read(path)
            if path.resolve()==preview.resolve() and not changed:
                with (self.collection/'apt-One/palette.toml').open('a',encoding='utf-8') as stream:
                    stream.write('\n# concurrent edit\n')
                changed.append(True)
            return content
        with patch.object(Path,'read_bytes',change_during_copy):
            with self.assertRaisesRegex(ValueError,'data source changed'):
                build(self.collection,out,overwrite=True)
        self.assertEqual(before,self.hashes(out))

        with self.assertRaises(ValueError):build(self.collection,self.collection/'atlas')
        with self.assertRaises(ValueError):snapshot(self.collection,['../*'])

    def test_cli_selection_and_json_envelope(self):
        stdout,stderr=io.StringIO(),io.StringIO()
        with redirect_stdout(stdout),redirect_stderr(stderr):
            result=main(['atlas',str(self.collection),'--include','apt-One','--output',str(self.root/'atlas'),'--json'])
        self.assertEqual(result,0)
        envelope=json.loads(stdout.getvalue())
        self.assertEqual(envelope['status'],'ok')
        self.assertEqual(envelope['data']['canonical'],32)
        self.assertIn('read-only',stderr.getvalue())

    def test_default_collection_includes_both_families_without_merging_identity(self):
        import shutil
        shutil.copytree(self.collection/'apt-One',self.collection/'dnf-One')
        shutil.copytree(self.collection/'apt-One',self.collection/'unrelated-recovery')
        data=snapshot(self.collection)
        self.assertEqual({t['run'] for t in data['themes']},{'apt-One','apt-Two','dnf-One'})
        self.assertEqual(len({c['id'] for c in data['canonical']}),96)
        self.assertEqual({t['family'] for t in data['themes']},{'apt','dnf'})
        self.assertEqual(len(snapshot(self.collection,['apt-*'])['themes']),2)

    def test_offline_examples_are_copied_with_dependencies_and_receipts(self):
        target=self.collection/'apt-One/test'
        (target/'assets').mkdir()
        (target/'examples.html').write_text('<script src="assets/example.js"></script>',encoding='utf-8')
        (target/'assets/example.js').write_text('window.exampleReady=true;',encoding='utf-8')
        before=self.hashes(self.collection)
        out=self.root/'atlas'
        result=build(self.collection,out)
        self.assertEqual(result['offline_examples'],1)
        data=json.loads((out/'atlas.json').read_text())
        self.assertEqual(data['themes'][0]['targets'][0]['example'],'examples/apt-One/test/examples.html')
        receipts=json.loads((out/'examples-manifest.json').read_text())['files']
        self.assertEqual(len(receipts),3)
        for record in receipts:
            self.assertEqual((out/record['file']).read_bytes(),(self.collection/record['source']).read_bytes())
            self.assertEqual(hashlib.sha256((out/record['file']).read_bytes()).hexdigest(),record['sha256'])
        self.assertEqual(before,self.hashes(self.collection))

    def test_inline_data_escapes_markup_and_neutral_hue_is_flagged(self):
        run=self.collection/'apt-One'
        metadata=json.loads((run/'run.json').read_text())
        metadata['name']='</script><img src=x onerror=alert(1)>'
        (run/'run.json').write_text(json.dumps(metadata),encoding='utf-8')
        build(self.collection,self.root/'atlas')
        script=(self.root/'atlas/atlas-data.js').read_text(encoding='utf-8')
        self.assertNotIn('</script>',script)
        self.assertIn('\\u003c/script',script)
        colors=json.loads((self.root/'atlas/atlas.json').read_text())['canonical']
        for color in colors:
            self.assertEqual(color['hue_defined'],color['oklch'][1]>=.02)

if __name__=='__main__':
    unittest.main()
