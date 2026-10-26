"""Capture/compare deterministic generation and import fixtures (never existing runs)."""
import argparse
import contextlib
import hashlib
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image
from apt_theme.cli import main
from apt_theme.colors import from_rgb
from apt_theme.extraction import palette_toml


def capture(root):
    root.mkdir(parents=True, exist_ok=False)
    values = []
    for i in range(16):
        values.extend(([10 + i * 15, 7 + i * 11, 2 + i * 4],
                       [3 + i * 5, 8 + i * 14, 12 + i * 15]))
    colors = {f'color_{i:02}': from_rgb(rgb) for i, rgb in enumerate(values, 1)}
    palette = root / 'fixture.toml'
    palette.write_text(palette_toml(colors, 'apt-Stabilization', 'fixture'), encoding='utf-8')
    image = Image.new('RGB', (256, 128))
    image.putdata([tuple(values[(x // 32) + 8 * (y // 32)]) for y in range(128) for x in range(256)])
    image.save(root / 'fixture.png')
    records = {}
    for command, source in (('import', palette), ('generate', root / 'fixture.png')):
        with contextlib.redirect_stdout(io.StringIO()):
            code = main([command, str(source), '--name', 'apt-Stabilization', '--output', str(root / command)])
        if code:
            raise RuntimeError(f'{command} failed: {code}')
        records[command] = {p.relative_to(root / command).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted((root / command).rglob('*')) if p.is_file()}
    (root / 'hashes.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
    return records


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='new fixture directory')
    parser.add_argument('--compare', type=Path, help='previous hashes.json')
    args = parser.parse_args()
    current = capture(args.output)
    if args.compare:
        previous = json.loads(args.compare.read_text(encoding='utf-8'))
        changes = {cmd: sorted(key for key in set(previous[cmd]) | set(current[cmd])
                               if previous[cmd].get(key) != current[cmd].get(key)) for cmd in current}
        print(json.dumps(changes, indent=2))
        raise SystemExit(1 if any(changes.values()) else 0)
    print(json.dumps({cmd: len(files) for cmd, files in current.items()}))
