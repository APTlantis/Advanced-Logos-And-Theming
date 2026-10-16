"""Verify wheel-only resource loading and generation with network/process calls blocked."""
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

root=Path(__file__).resolve().parents[1]
installed=root/'.build/browser-themes-2026-10-16/installed'
sys.path.insert(0,str(installed))
import apt_theme
from apt_theme.browser_themes import verify_vendor
from apt_theme.cli import main
from apt_theme.extraction import load_palette
assert Path(apt_theme.__file__).is_relative_to(installed)
manifest=verify_vendor()
run=root/'.build/browser-themes-2026-10-16/package-run'
checks=[]
for theme,source,name,targets in [('black-gold','apt-BlackGold','Black-Gold',None),('ada','apt-Ada','Ada','markdown,codemirror5,codemirror6')]:
    palette=root/'output'/source/'palette.toml'
    dest=run/theme
    argv=['import',str(palette),'--name',name,'--output',str(dest),'--overwrite']
    if targets:argv+=['--targets',targets]
    with patch('socket.socket.connect',side_effect=AssertionError('network forbidden')),patch('socket.create_connection',side_effect=AssertionError('network forbidden')),patch('subprocess.Popen',side_effect=AssertionError('child process forbidden')):
        assert main(argv)==0
    before,_=load_palette(palette)
    after,_=load_palette(dest/'palette.toml')
    assert {k:(v['hex'],v['rgb']) for k,v in before.items()}=={k:(v['hex'],v['rgb']) for k,v in after.items()}
    for target in ('markdown','codemirror5','codemirror6'):
        resource=dest/target/'vendor/browser-themes'
        for item in manifest['files']:
            assert hashlib.sha256((resource/item['file']).read_bytes()).hexdigest()==item['sha256']
    summary=json.loads((dest/'run.json').read_text())
    checks.append({'theme':theme,'targets':summary['targets'],'contrast_failures':summary['contrast_failures'],'canonical_preserved':True})
record={'passed':True,'module':str(Path(apt_theme.__file__).relative_to(root)),'network_blocked':True,'child_processes_blocked':True,'checks':checks,'vendor_files':len(manifest['files'])}
(root/'.build/browser-themes-2026-10-16/package-validation.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
