"""Capture immutable inputs before authoring. Run once in a fresh collection."""
from pathlib import Path
import hashlib,json,shutil,tomllib
ROOT=Path(__file__).resolve().parents[4]
DEST=Path(__file__).resolve().parents[1]
RUNS=['rpm-BlackGold','apt-Crystal','apt-Factor','dnf-Caddy','dnf-Clojure','dnf-Cloudflare','dnf-Flathub','apt-Swift']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,data): p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def prepare():
    baseline=DEST/'validation/input-inventory.json'
    if baseline.exists(): raise FileExistsError('Preserve existing baseline; choose a fresh collection')
    records=[]; inventory={}
    for name in RUNS:
        run=ROOT/'output'/name;r=json.loads((run/'run.json').read_text())
        inventory.update({p.relative_to(ROOT).as_posix():sha(p) for p in run.rglob('*') if p.is_file()})
        manifests={}
        for target,rel in r['artifact_manifests'].items():
            manifest=run/rel;data=json.loads(manifest.read_text())
            for entry in data['files']:
                file=manifest.parent/entry['file']
                assert file.is_file() and sha(file)==entry['sha256'],file
            manifests[target]=data
        ident=r['theme_identity'];stem=ident['prefix']+'-'+ident['slug']
        directory=DEST/stem;directory.mkdir(parents=True,exist_ok=True)
        for sub in ['figures','previews','pdf-previews']: (directory/sub).mkdir(exist_ok=True)
        selected={}
        # Complete target trees keep CSS, local fonts/scripts and native dependencies together.
        for target in r['targets']:
            shutil.copytree(run/target,directory/'artifacts'/target)
        for rel in ['run.json','palette.toml','semantics.json','selection.json','provenance.json','candidates.json','palette.png']:
            p=run/rel
            if p.exists(): shutil.copy2(p,directory/'figures'/p.name)
        artwork=next((run/'source').iterdir());shutil.copy2(artwork,directory/'figures'/artwork.name)
        for e in manifests['powerpoint']['files']:
            selected[e['role']]=(run/Path(r['artifact_manifests']['powerpoint']).parent/e['file']).relative_to(ROOT).as_posix()
        palette=tomllib.loads((run/'palette.toml').read_text(encoding='utf-8-sig'))['palette']['canonical']
        records.append(dict(run=name,stem=stem,identity=ident,powerpoint=selected,artwork=artwork.relative_to(ROOT).as_posix(),palette=palette))
    dump(baseline,inventory);dump(DEST/'validation/template-inventory.json',records)
    refs=[ROOT/'README.md',ROOT/'profiles.toml',ROOT/'PROJECT-READMAP.toml',ROOT/'Project-README.md',ROOT/'Logos-And-Theming.manifest.toml']
    refs+=list((ROOT/'docs').glob('*.md'))+list((ROOT/'apt_theme').glob('*.py'))
    refs+=[ROOT/'scripts/help.md',ROOT/'docs/examples/finish-selected.toml']
    snapshots={}
    for p in refs:
        rel=p.relative_to(ROOT);out=DEST/'source/snapshot'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out);snapshots[rel.as_posix()]=sha(p)
    dump(DEST/'validation/source-snapshot.json',snapshots)
    print(f'Preserved {len(inventory)} input hashes; checked all target artifact hashes; captured {len(refs)} source files')
if __name__=='__main__':prepare()
