"""Refresh only the CSS for chart galleries linked by the current output index."""
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from apt_theme.visual_targets import chart_gallery_css, export_visual

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = ROOT / 'output'
    backup = ROOT / 'migration/chart-gallery-backups/2026-10-09'
    evidence = []
    links = re.findall(r'href="([^"?#]+/data_visualization/examples.html)"',
                       (output / 'index.html').read_text(encoding='utf-8'))
    for link in dict.fromkeys(links):
        directory = (output / link).resolve().parent
        if not directory.is_relative_to(output.resolve()):
            raise ValueError('Gallery escapes output root')
        css = directory / 'examples.css'
        original = backup / directory.parent.name / 'examples.css'
        before = {str(p.relative_to(directory)): digest(p)
                  for p in directory.rglob('*') if p.is_file() and p != css}
        original.parent.mkdir(parents=True, exist_ok=True)
        if not original.exists():
            original.write_bytes(css.read_bytes())
        css.write_text(chart_gallery_css(), encoding='utf-8')
        after = {str(p.relative_to(directory)): digest(p)
                 for p in directory.rglob('*') if p.is_file() and p != css}
        assert before == after, 'Non-CSS chart assets changed'
        evidence.append({'gallery': link, 'backup': str(original.relative_to(ROOT)),
                         'original_css_sha256': digest(original), 'css_sha256': digest(css),
                         'unchanged_assets': before})
    pilot = ROOT / 'pilot/chart-neutral-gallery-2026-10-09/data_visualization'
    if not pilot.exists():
        pilot.mkdir(parents=True)
        result = json.loads((output / links[0]).parent.joinpath('tokens.json').read_text())
        export_visual(result, pilot, 'Neutral chart gallery')
    record = {'date': '2026-10-09', 'scope': 'Gallery CSS only; chart artwork and theme tokens unchanged',
              'galleries': evidence, 'native_application_acceptance': 'not evaluated',
              'recovery': 'Restore each backup examples.css to its recorded gallery directory.'}
    (ROOT / 'migration/chart-neutral-gallery-2026-10-09.json').write_text(
        json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(f'Updated {len(evidence)} linked chart galleries; all non-CSS assets unchanged.')


if __name__ == '__main__':
    main()
