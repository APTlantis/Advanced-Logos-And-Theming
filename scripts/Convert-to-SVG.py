"""Compatibility entry point for raster wrapping and explicit VTracer tracing."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from apt_theme.svg_converter import *

if __name__ == '__main__':
    raise SystemExit(main())
