import copy
import json
import re
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote
import xml.etree.ElementTree as ET
from apt_theme.colors import from_rgb,contrast
from apt_theme.semantics import assign
from apt_theme.targets import DEFAULTS,adapt,export
from apt_theme.kmindz import package

class KmindzTests(unittest.TestCase):
    def setUp(self):
        values=[]
        for i in range(16):
            values += [from_rgb([10+i*15,7+i*11,2+i*4]),from_rgb([3+i*5,8+i*14,12+i*15])]
        self.colors={f'color_{i:02}':c for i,c in enumerate(values,1)}
        self.roles,_=assign(self.colors)
        self.result=adapt(self.colors,self.roles,'kmindz',DEFAULTS['kmindz'])

    def test_contract_and_identity_are_template_based(self):
        p,svg,slots,_=package(self.result,'Aptlantis Cyan Test')
        self.assertEqual(p['kind'],'kmind.theme-package')
        self.assertEqual(p['schemaVersion'],1)
        self.assertEqual(p['id'],'aptlantis-cyan-test-canonical32')
        self.assertEqual(p['theme']['id'],p['id'])
        self.assertEqual(set(p['theme']['variants']),{'dark'})
        v=p['theme']['variants']['dark']
        self.assertEqual(len(v['rules']['nodeRules']),4)
        self.assertEqual(v['edges']['routeType'],'orthogonal-rounded')
        self.assertEqual(v['rules']['nodeRules'][1]['apply']['incomingEdge']['routeType'],'center-quadratic')
        self.assertEqual(len(v['rainbow']['palette']),12)
        self.assertNotIn('BlackGold',json.dumps(p))

    def test_every_exported_color_is_a_mapped_target_token(self):
        p,svg,slots,_=package(self.result,'Test')
        native=set(re.findall(r'#[0-9A-Fa-f]{6}',json.dumps(p['theme'])))
        adapted={c['hex'] for c in self.result['tokens'].values()}
        self.assertTrue(native <= adapted)
        decoded=unquote(p['preview']['thumbnail']['dataUrl'].split(',',1)[1])
        self.assertEqual(decoded,svg)
        root=ET.fromstring(decoded)
        self.assertEqual(root.attrib['width'],'244')
        self.assertTrue(set(re.findall(r'#[0-9A-Fa-f]{6}',svg)) <= adapted)

    def test_canonical_preservation_determinism_and_budget(self):
        before=copy.deepcopy(self.colors)
        self.assertEqual(package(self.result,'Test'),package(self.result,'Test'))
        self.assertEqual(self.colors,before)
        self.assertEqual(self.result['named_count'],32)
        with self.assertRaises(ValueError): adapt(self.colors,self.roles,'kmindz',31)

    def test_exported_node_text_in_normal_and_selected_states(self):
        p,*_=package(self.result,'Test'); v=p['theme']['variants']['dark']
        colors={c['hex']:c for c in self.result['tokens'].values()}
        base=v['tokens']['paint']
        for rule in v['rules']['nodeRules']:
            paint={**base,**rule['apply']['paint']}
            for fill in ['nodeFill','nodeFillSelected']:
                self.assertGreaterEqual(contrast(colors[paint['text']],colors[paint[fill]]),4.5)
        self.assertEqual(self.result['contrast_failures'],0)

    def test_native_files_and_common_palette_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            dest=Path(temp)/'kmindz'
            before=copy.deepcopy(self.colors)
            export(self.result,dest,'Test',self.colors,'a'*64, theme_version=1)
            p=json.loads((dest / self.result["artifact_paths"]["KMINDS.json"]).read_text())
            self.assertEqual(p['theme']['variants']['dark']['tokens']['paint']['bg'],self.result['tokens']['background']['hex'])
            for f in ['preview.svg','format-provenance.json','tokens.json','validation.json','apt-test-kmindz-palette.toml','apt-test-kmindz-swatch.png']:
                self.assertTrue((dest/self.result["artifact_paths"].get(f,f)).is_file(),f)
            self.assertEqual(self.colors,before)
            self.assertEqual(json.loads((dest / self.result["artifact_paths"]["validation.json"]).read_text())['native_visual_acceptance'],'pending')
