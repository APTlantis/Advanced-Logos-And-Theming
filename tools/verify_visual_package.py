"""Verify wheel resources and generation from an isolated wheel installation.

Usage: python tools/verify_visual_package.py WHEEL INSTALL_DIRECTORY PALETTE OUTPUT [TARGETS]
Install the wheel with pip --no-deps --target INSTALL_DIRECTORY first.
"""
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path


def verify(wheel, installation, palette, output, targets="syntax_highlighting,data_visualization"):
    wheel, installation, palette, output = [Path(p).resolve() for p in (wheel, installation, palette, output)]
    root = Path(__file__).resolve().parents[1]
    records, engine_files = {}, {}
    with zipfile.ZipFile(wheel) as archive:
        for folder in ("vendor/prism", "examples/syntax"):
            for source in sorted((root / "apt_theme" / folder).iterdir()):
                name = f"apt_theme/{folder}/{source.name}"
                assert archive.read(name) == source.read_bytes(), name
                assert (installation / name).read_bytes() == source.read_bytes(), name
                records[name] = hashlib.sha256(source.read_bytes()).hexdigest()
        for source in sorted((root / "apt_theme").glob("*.py")):
            name = f"apt_theme/{source.name}"
            assert archive.read(name) == source.read_bytes(), name
            assert (installation / name).read_bytes() == source.read_bytes(), name
            engine_files[name] = hashlib.sha256(source.read_bytes()).hexdigest()
    script = """
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
import apt_theme
assert Path(apt_theme.__file__).resolve().is_relative_to(Path(sys.argv[1]).resolve())
from apt_theme.syntax_examples import verify_vendor
verify_vendor()
from apt_theme.cli import main
raise SystemExit(main(['import', sys.argv[2], '--output', sys.argv[3], '--name',
    'Wheel quality verification', '--targets', sys.argv[4], '--strict']))
"""
    subprocess.run([sys.executable, "-c", script, str(installation), str(palette), str(output), targets],
                   cwd=installation, check=True)
    result = {"wheel": wheel.name, "wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
              "installed_package_generation": "passed", "resource_count": len(records), "resources": records,
              "engine_files": engine_files, "targets": targets.split(','),
              "python_version": sys.version, "scope": "Isolated local wheel installation; no theme installation or publication."}
    (output / "wheel-verification.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(f"Verified {len(records)} packaged resources and isolated installed-wheel generation.")


if __name__ == "__main__":
    verify(*sys.argv[1:])
