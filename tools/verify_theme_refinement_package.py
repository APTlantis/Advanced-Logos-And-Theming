"""Compare an isolated installed-wheel import with the source fixture, offline."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('installed', type=Path)
parser.add_argument('fixture', type=Path)
parser.add_argument('output', type=Path)
parser.add_argument('receipt', type=Path)
args = parser.parse_args()
sys.path.insert(0, str(args.installed.resolve()))
import apt_theme
assert Path(apt_theme.__file__).resolve().is_relative_to(args.installed.resolve())


def offline_audit(event, args):
    if event in ('socket.__new__', 'socket.connect', 'socket.bind', 'socket.getaddrinfo', 'subprocess.Popen'):
        raise AssertionError('Generation attempted network or child-process access: ' + event)


sys.addaudithook(offline_audit)
from apt_theme.cli import main
code = main(['import', str(args.fixture/'fixture.toml'), '--name', 'apt-Stabilization',
             '--output', str(args.output), '--strict', '--json'])
assert code == 0


def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


expected, actual = hashes(args.fixture/'import'), hashes(args.output)
changes = [key for key in expected.keys() | actual.keys() if expected.get(key) != actual.get(key)]
assert not changes, changes
receipt = {'module': str(Path(apt_theme.__file__).resolve()), 'all_target_files_identical': len(actual),
           'changed_files': changes, 'network_blocked': True, 'child_processes_blocked': True,
           'native_application_acceptance': 'pending'}
args.receipt.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
print(json.dumps(receipt))
