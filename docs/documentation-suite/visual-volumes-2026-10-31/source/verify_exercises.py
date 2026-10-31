"""Run bounded equivalents of recipes in a fresh workspace-local temporary tree."""
import sys,subprocess,json,os,tomllib,base64
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image
from prepare import ROOT,DEST,sha,dump
def main():
    python=ROOT/'.venv/Scripts/python.exe';attempt=next((a.split('=',1)[1] for a in sys.argv if a.startswith('--attempt=')),'default');work=ROOT/('.build/visual-volumes-exercises-2026-10-31-'+attempt)
    if work.exists():raise FileExistsError('Exercise directory exists; preserve prior evidence')
    work.mkdir(parents=True);tmp=work/'temp';tmp.mkdir();env=dict(os.environ,TEMP=str(tmp),TMP=str(tmp),PYTHONDONTWRITEBYTECODE='1')
    records=[dict(label='Environment',python=str(python),magick_path=__import__('shutil').which('magick'),temp=str(tmp),note='Process-local PATH selects the already-installed HDRI variant; system configuration is unchanged.')]
    def run(label,args,expected=0):
        p=subprocess.run([str(python),*map(str,args)],cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace')
        records.append(dict(label=label,command=[str(python),*map(str,args)],cwd=str(ROOT),exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr,expected_exit=expected))
        dump(DEST/'validation/commands.json',records)
        if p.returncode!=expected:raise RuntimeError(label+'\n'+p.stderr)
        return p
    imports=[('rpm-BlackGold','powerpoint'),('apt-Factor','windows_terminal,powerpoint'),('dnf-Caddy','website'),('apt-Swift','windows_terminal')]
    for name,targets in imports:
        out=work/name
        run(name+' fresh palette import',['-m','apt_theme.cli','import',ROOT/'output'/name/'palette.toml','--output',out,'--targets',targets,'--json'])
        old=tomllib.loads((ROOT/'output'/name/'palette.toml').read_text(encoding='utf-8-sig'))['palette']['canonical'];new=tomllib.loads((out/'palette.toml').read_text(encoding='utf-8-sig'))['palette']['canonical']
        assert {k:c['rgb']for k,c in old.items()}=={k:c['rgb']for k,c in new.items()};records[-1]['canonical_ids_rgb_preserved']=True
    crystal=next((ROOT/'output/apt-Crystal/source').iterdir())
    run('Crystal fresh extraction',['-m','apt_theme.cli','generate',crystal,'--output',work/'crystal-generation','--targets','windows_terminal','--json'])
    run('Cloudflare one-run Atlas snapshot',['-m','apt_theme.cli','atlas',ROOT/'output','--include','dnf-Cloudflare','--output',work/'cloudflare-atlas','--json'])
    source=next((ROOT/'output/dnf-Flathub/source').iterdir());before=sha(source)
    run('Flathub SVG raster embedding',['scripts/Convert-to-SVG.py','--input',source,'--output',work/'flathub-embed.svg'])
    svg=ET.parse(work/'flathub-embed.svg').getroot();image=next(x for x in svg if x.tag.endswith('}image'));assert base64.b64decode(image.get('href').split(',',1)[1])==source.read_bytes()
    records[-1]['embedded_source_bytes_preserved']=True
    run('Flathub ICO frame conversion',['scripts/Convert-to-ICO.py','--input',source,'--output',work/'flathub.ico','--sizes','16,32,48,64,128,256','--fit','contain'])
    with Image.open(work/'flathub.ico') as im:assert im.ico.sizes()=={(n,n)for n in [16,32,48,64,128,256]}
    records[-1]['frames_verified']=[16,32,48,64,128,256];assert sha(source)==before
    plan=work/'finish-preview.toml';plan.write_text('schema = "aptlantis.finish-plan.v1"\n[[assets]]\nid = "dnf-flathub-logo"\ninput = '+json.dumps(source.as_posix())+'\nrole = "logo"\nmode = "embed"\ntheme_name = "dnf-Flathub"\n')
    run('Explicit finishing read-only preview',['-m','apt_theme.cli','finish',plan,'--output',work/'finish-unwritten','--json']);assert not (work/'finish-unwritten').exists()
    records[-1]['no_output_written']=True
    (tmp/'protected.txt').write_text('Non-pipeline directory must remain untouched.')
    run('Unsafe non-pipeline output refused even with overwrite',['-m','apt_theme.cli','import',ROOT/'output/apt-Swift/palette.toml','--output',tmp,'--targets','windows_terminal','--overwrite','--json'],1)
    records.extend([dict(label='Clojure loopback rendering',status='executed separately',receipt='specimen-browser.json'),dict(label='Displayed guide destination paths',status='source-checked; exact illustrative paths not executed',note='Equivalent recipes above use fresh bounded exercise destinations.'),dict(label='Native edit/save/reopen; downstream integration; activation; installation; publication; real trace fidelity',status='not performed')]);dump(DEST/'validation/commands.json',records)
    tests=subprocess.run([str(python),'-m','unittest','tests.test_pipeline','tests.test_logo_tools','-v'],cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace')
    (DEST/'validation/focused-tests.log').write_text(tests.stdout+tests.stderr,encoding='utf-8');dump(DEST/'validation/focused-tests.json',dict(command=[str(python),'-m','unittest','tests.test_pipeline','tests.test_logo_tools','-v'],exit_code=tests.returncode,temp=str(tmp)))
    if tests.returncode:raise RuntimeError('Focused tests failed; inspect retained log')
    print('Recipe equivalents, preservation, ICO frames, embed payload, finishing preview, and focused suites passed')
if __name__=='__main__':main()
