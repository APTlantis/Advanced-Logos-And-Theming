"""Verify an isolated wheel install, byte-stable generation/import and real SESM finishing."""
import argparse
from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import runpy
import socket
import sys
from unittest.mock import patch
import zipfile


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--installed', type=Path, required=True)
    parser.add_argument('--wheel', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='fresh verification directory')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    installed = args.installed.resolve(strict=True)
    output = args.output.resolve()
    if output.exists():
        raise ValueError('Verification output must be fresh')
    sys.path.insert(0, str(installed))
    import apt_theme
    from apt_theme.cli import main
    assert Path(apt_theme.__file__).is_relative_to(installed)
    with zipfile.ZipFile(args.wheel) as archive:
        resources = [name for name in archive.namelist() if name.startswith('apt_theme/')]
        for name in resources:
            assert archive.read(name) == (root / name).read_bytes(), name
    capture = runpy.run_path(str(root / 'tools/check_stabilization.py'))['capture']
    with patch.object(socket.socket, 'connect', side_effect=AssertionError('network forbidden')), \
         patch.object(socket, 'create_connection', side_effect=AssertionError('network forbidden')), \
         redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        current = capture(output / 'fixtures')
        assert current == json.loads(args.baseline.read_text(encoding='utf-8'))
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(['finish', str(root / 'docs/examples/finish-selected.toml'), '--output', str(output / 'finished'),
                         '--write', '--json', '--sesm-project', str(root.parent / 'SESM-Metadata-Embedder')])
        assert code == 0, stderr.getvalue()
        finishing = json.loads(stdout.getvalue())
        assert finishing['status'] == 'ok'
        assert len(finishing['data']['assets']) == 4
    modules = {name: str(Path(module.__file__).relative_to(installed)) for name, module in sys.modules.items()
               if name == 'apt_theme' or name.startswith('apt_theme.')}
    record = {'passed': True, 'network_blocked_in_generator_process': True,
              'external_sesm_processes': 'local scripts; no network operations implemented',
              'resources_compared': len(resources), 'modules': modules,
              'fixture_files': {command: len(files) for command, files in current.items()},
              'changed_fixture_hashes': 0,
              'finished_assets': [{'file': a['file'], 'profile': a['validation']['profile']} for a in finishing['data']['assets']]}
    (output / 'package-validation.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record))
