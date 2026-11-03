"""Prepare a fresh, offline three-theme pilot; existing runs stay read-only."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from apt_theme.cli import main
from apt_theme.extraction import load_palette
from apt_theme.output_names import artifact_file
from apt_theme.siyuan import specimen

THEMES = ('apt-Codex', 'apt-BlueSlate', 'rpm-BlackGold')


def prepare(destination):
    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    records, sections = [], []
    for theme in THEMES:
        source = Path('output') / theme
        original = json.loads((source/'run.json').read_text(encoding='utf-8'))
        roles = json.loads((source/'semantics.json').read_text(encoding='utf-8'))['roles']
        config = destination / (theme + '.toml')
        config.write_text('[overrides]\n' + ''.join(f'{key} = "{value}"\n' for key, value in roles.items()), encoding='utf-8')
        before = artifact_file(source, 'siyuan', 'theme.css', verify=True)
        (destination/(theme+'-before.html')).write_text(specimen(before.read_text(encoding='utf-8'), theme+' · Before'), encoding='utf-8')
        result = main(['import', str(source/'palette.toml'), '--name', original['name'],
                       '--output', str(destination/theme), '--targets', 'siyuan,kmindz',
                       '--config', str(config), '--strict', '--json'])
        if result:
            raise RuntimeError(f'{theme} failed strict generation: {result}')
        old, _ = load_palette(source/'palette.toml')
        new, _ = load_palette(destination/theme/'palette.toml')
        assert {k:v['rgb'] for k,v in old.items()} == {k:v['rgb'] for k,v in new.items()}
        after = artifact_file(destination/theme, 'siyuan', 'examples.html', verify=True)
        kmind = artifact_file(destination/theme, 'kmindz', 'KMINDS.json', verify=True)
        package = artifact_file(destination/theme, 'siyuan', 'package.zip', verify=True)
        sections.append(f'<section><h2>{html.escape(theme)}</h2><p><a href="{theme}/siyuan/{package.name}">SiYuan package</a> · <a href="{theme}/kmindz/{kmind.name}" download>KMind package</a> · <a href="{theme}/review.html">Validation and palettes</a></p><div class="pair"><div><h3>Before</h3><iframe title="{theme} before" src="{theme}-before.html"></iframe></div><div><h3>After</h3><iframe title="{theme} after" src="{theme}/siyuan/{after.name}"></iframe></div></div></section>')
        tokens = json.loads(artifact_file(destination/theme, 'siyuan', 'tokens.json').read_text(encoding='utf-8'))
        records.append({'theme':theme, 'source_run':str(source.resolve()), 'canonical_colors_unchanged':32,
                        'source_palette_sha256':hashlib.sha256((source/'palette.toml').read_bytes()).hexdigest(),
                        'named_tokens':tokens['named_count'], 'contrast_checks':len(tokens['checks']),
                        'contrast_failures':tokens['contrast_failures'],
                        'status_collision':tokens['siyuan']['status_collision'],
                        'native_application_acceptance':'pending'})
    (destination/'index.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Theme refinement pilot</title><style>body{margin:24px;font:16px system-ui;background:#101820;color:#e6edf3}a{color:#8dccff}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}iframe{width:100%;height:1250px;border:1px solid #53606d}section{margin-bottom:40px}@media(max-width:1000px){.pair{grid-template-columns:1fr}}</style><h1>KMind and SiYuan refinement pilot</h1><p>Three preserved identities, unchanged canonical palettes. Authored offline browser specimens; native import/apply/rendering remains pending. The light KMind slot mirrors dark styling for compatibility.</p>'+''.join(sections), encoding='utf-8')
    (destination/'pilot.json').write_text(json.dumps(records, indent=2)+'\n', encoding='utf-8')
    return records


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    print(json.dumps(prepare(parser.parse_args().destination), indent=2))
