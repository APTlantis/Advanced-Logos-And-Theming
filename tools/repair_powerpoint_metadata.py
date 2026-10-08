"""Write a corrected copy of a pipeline PPTX; never overwrite the input."""
import argparse
import os
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from apt_theme.powerpoint import normalize_core_properties, validate_core_properties


def repair(source, destination):
    source, destination = Path(source).resolve(strict=True), Path(destination).resolve()
    if source == destination or destination.exists():
        raise ValueError('Choose a new output file; input and existing files are never overwritten')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source) as original:
        corrected = normalize_core_properties(original.read('docProps/core.xml'))
        validate_core_properties(corrected)
        with tempfile.NamedTemporaryFile(dir=destination.parent, suffix='.pptx', delete=False) as temp:
            temporary = Path(temp.name)
        try:
            with zipfile.ZipFile(temporary, 'w') as output:
                for info in original.infolist():
                    output.writestr(info, corrected if info.filename == 'docProps/core.xml' else original.read(info.filename))
            # Hard-link creation refuses an output created concurrently.
            os.link(temporary, destination)
        finally:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        repair(args.input, args.output)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1
    print(f'Corrected metadata: {args.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
