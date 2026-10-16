"""Verify atlas resources and generation from an isolated wheel installation."""
import hashlib
import io
import json
from pathlib import Path
import sys
from contextlib import redirect_stdout,redirect_stderr
from unittest.mock import patch

root=Path(__file__).resolve().parents[1]
verification=root/(sys.argv[1] if len(sys.argv)>1 else '.build/atlas-collection-2026-10-16')
installed=verification/'installed'
sys.path.insert(0,str(installed))
import apt_theme
from apt_theme.cli import main
assert Path(apt_theme.__file__).is_relative_to(installed)
output=verification/'package-atlas'
stdout,stderr=io.StringIO(),io.StringIO()
with patch('socket.socket.connect',side_effect=AssertionError('network forbidden')),patch('socket.create_connection',side_effect=AssertionError('network forbidden')),patch('subprocess.Popen',side_effect=AssertionError('child process forbidden')),redirect_stdout(stdout),redirect_stderr(stderr):
    assert main(['atlas',str(root/'output'),'--output',str(output),'--overwrite','--json'])==0
response=json.loads(stdout.getvalue())
assert response['status']=='ok'
data=json.loads((output/'atlas.json').read_text(encoding='utf-8'))
for record in data['sources']:
    assert hashlib.sha256((root/'output'/record['path']).read_bytes()).hexdigest()==record['sha256']
examples=json.loads((output/'examples-manifest.json').read_text(encoding='utf-8'))['files']
for item in examples:
    assert hashlib.sha256((output/item['file']).read_bytes()).hexdigest()==item['sha256']
    assert hashlib.sha256((root/'output'/item['source']).read_bytes()).hexdigest()==item['sha256']
for name in ('index.html','app.js','styles.css'):
    assert (output/name).read_bytes()==(installed/'apt_theme/atlas_assets'/name).read_bytes()
script=(output/'atlas-data.js').read_text(encoding='utf-8')
assert json.loads(script.removeprefix('window.ATLAS_DATA=').removesuffix(';\n'))==data
record={'passed':True,'module':str(Path(apt_theme.__file__).relative_to(root)),'network_blocked':True,'child_processes_blocked':True,'counts':data['counts'],'packaged_assets':['index.html','app.js','styles.css'],'source_receipts_verified':len(data['sources']),'copied_example_files_verified':len(examples)}
(verification/'package-validation.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record))
