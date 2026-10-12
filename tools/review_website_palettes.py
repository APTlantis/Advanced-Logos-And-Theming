"""Generate fresh local website specimens from existing canonical palettes."""
import hashlib
import html
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from apt_theme.cli import main as pipeline
from apt_theme.extraction import load_palette

ROOT = Path(__file__).resolve().parents[1]


def hashes(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob('*') if p.is_file()}


def main():
    destination = ROOT / 'pilot/website-review-2026-10-09-v2'
    destination.mkdir(parents=True, exist_ok=True)
    records = []
    for folder in ('dnf-D', 'dnf-CoffeeScript', 'dnf-Assembly'):
        source = ROOT / 'output' / folder
        before = hashes(source)
        name = json.loads((source / 'run.json').read_text())['name']
        output = destination / folder
        arguments = ['import', str(source / 'palette.toml'), '--output', str(output),
                     '--name', name, '--targets', 'website', '--strict']
        if '--refresh' in sys.argv:
            arguments.append('--overwrite')
        code = pipeline(arguments)
        if code not in (0, 2):
            raise RuntimeError(f'{folder}: generation failed; existing output is never overwritten')
        old, _ = load_palette(source / 'palette.toml')
        new, _ = load_palette(output / 'palette.toml')
        assert {k: c['rgb'] for k, c in old.items()} == {k: c['rgb'] for k, c in new.items()}
        assert hashes(source) == before
        tokens = json.loads((output / 'website/tokens.json').read_text())
        semantics = json.loads((output / 'semantics.json').read_text())
        status_hues = [finding for finding in semantics['findings']
                       if finding.get('role') in ('success', 'warning', 'error', 'info')]
        records.append({'folder': folder, 'name': name, 'exit_code': code,
                        'named_tokens': tokens['named_count'], 'unique_colors': tokens['unique_count'],
                        'contrast_failures': tokens['contrast_failures'], 'status_hue_findings': status_hues,
                        'semantic_findings': semantics['findings'], 'aliases': tokens['aliases'],
                        'canonical_32_preserved': True, 'existing_output_unchanged': True,
                        'existing_output_hashes': before, 'visual_suitability': 'operator review pending'})
    cards = ''.join('<article><h2>'+html.escape(r['name'])+'</h2><img src="'+r['folder']+'/palette.png" alt="Canonical 32 palette"><p>'+str(r['named_tokens'])+' named tokens · '+str(r['unique_colors'])+' unique colors · '+str(r['contrast_failures'])+' contrast failures</p><p>Conventional status-hue gaps: '+(', '.join(f['role'] for f in r['status_hue_findings']) or 'none')+'.</p><p><a href="'+r['folder']+'/website/landing.html">Landing page</a> · <a href="'+r['folder']+'/website/components.html">Components</a> · <a href="'+r['folder']+'/review.html">Palette and findings</a></p></article>' for r in records)
    (destination / 'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Website palette comparison</title><style>body{background:#181a1d;color:#eceef0;font:16px/1.6 system-ui;max-width:1200px;margin:auto;padding:32px}a{color:#dce1e6}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:24px}article{background:#22252a;border:1px solid #60656d;border-radius:12px;padding:24px}img{width:100%}</style><h1>Website palette comparison</h1><p>D, CoffeeScript and Assembly: the same website contract, unchanged source palettes, fresh local runs.</p><p>Passing contrast does not settle visual suitability. Compare surface character, accent identity, readable content and status-color collisions. Keep labels when conventional hues are missing. There is no automatic keep/discard decision.</p><div class="grid">'+cards+'</div></html>', encoding='utf-8')
    record = {'date': '2026-10-09', 'target': 'website', 'budget': 112,
              'scope': 'Fresh local imports of three existing canonical palettes; no public asset changes',
              'reviews': records, 'production_integration': 'not performed', 'publication': 'not performed'}
    record['pilot'] = str(destination.relative_to(ROOT))
    record_path = ROOT / 'migration/website-target-acceptance-2026-10-09.json'
    if record_path.exists():
        original = record_path.with_suffix('.initial.json')
        if not original.exists():
            original.write_bytes(record_path.read_bytes())
    record_path.write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
    print(json.dumps([{k: r[k] for k in ('name','named_tokens','unique_colors','contrast_failures')} for r in records], indent=2))


if __name__ == '__main__':
    main()
