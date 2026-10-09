import copy, importlib.util, tempfile, unittest, tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('palette_transformer',ROOT/'palette_transformer.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
class TransformerTests(unittest.TestCase):
    def setUp(self): self.data,self.colors,self.digest,self.notices=m.load(ROOT/'examples/apt-aptlantis-dnf-Blackgold-palette.toml')
    def test_rgb_roundtrip_and_contrast(self):
        for rgb in ([255,0,0],[0,255,0],[0,0,255],[3,11,20],[255,255,255],[0,0,0],[128,64,32]):
            actual,_=m.lch_to_rgb(m.rgb_to_lch(rgb)); self.assertEqual(actual,list(rgb))
        self.assertAlmostEqual(m.contrast(m.color([0,0,0]),m.color([255,255,255])),21)
    def test_all_profile_sizes_roles_and_preservation(self):
        for profile,count in m.PROFILES.items():
            colors,roles,added,remaps=m.transform(self.data,self.colors,count,profile)
            self.assertEqual(len(colors),count)
            for entries in roles.values(): self.assertTrue(all(r in colors for r in entries.values()))
            if count>=32:
                for n,c in self.colors.items(): self.assertEqual(colors[n],c)
            if profile=='terminal':
                for r in self.data['roles']['terminal'].values(): self.assertIn(r,colors)
    def test_gamut_mapping(self):
        rgb,mapped=m.lch_to_rgb([.7,.5,40]); self.assertTrue(mapped); self.assertTrue(all(0<=v<=255 for v in rgb))
    def test_fallbacks_and_bad_references(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'p.toml'; p.write_text('[palette.test]\na={hex="#FF0000"}\nb={rgb=[0,255,0]}\n')
            data,c,_,_=m.load(p); self.assertEqual(c['a']['rgb'],[255,0,0]); self.assertEqual(c['b']['rgb'],[0,255,0])
            p.write_text(p.read_text()+'[roles.text]\nprimary="missing"\n')
            with self.assertRaises(ValueError): m.load(p)
    def test_light_direction(self):
        data=copy.deepcopy(self.data); data['theme']['variant']='light'; data['roles']['base']['app_bg']='text_light_01'
        colors,_,_,_=m.transform(data,self.colors,40,'sublime')
        surfaces=[c for c in colors.values() if c['family']=='surface']; self.assertTrue(surfaces)
        self.assertTrue(all(c['oklch']['l']<self.colors['text_light_01']['oklch']['l'] for c in surfaces))
    def test_deterministic_and_roundtrip_outputs(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/'a'; b=Path(d)/'b'
            for p in (a,b): m.run(ROOT/'examples/apt-aptlantis-dnf-Blackgold-palette.toml',p,'website')
            for name in ('palette.toml','manifest.json','validation.json','swatch.png'): self.assertEqual((a/name).read_bytes(),(b/name).read_bytes())
            decoded=tomllib.loads((a/'palette.toml').read_text()); self.assertEqual(decoded['transformation']['actual_count'],112)
            _,c,_,_=m.load(a/'palette.toml'); self.assertEqual(len(c),112)
    def test_impossible_anchor_budget(self):
        with self.assertRaises(ValueError): m.transform(self.data,self.colors,2,'terminal')
if __name__=='__main__': unittest.main()
