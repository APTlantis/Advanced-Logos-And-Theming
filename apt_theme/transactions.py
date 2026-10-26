"""Publish a completed sibling staging directory, restoring the prior run on failure."""
from contextlib import contextmanager
from pathlib import Path
import tempfile


@contextmanager
def staged_directory(output, *, prefix, name='result', overwrite=False):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=prefix, dir=output.parent) as temporary:
        stage = Path(temporary) / name
        yield stage
        if output.exists():
            if not overwrite:
                raise ValueError('Output already exists')
            backup = Path(temporary) / 'previous'
            output.rename(backup)
            try:
                stage.rename(output)
            except BaseException:
                backup.rename(output)
                raise
        else:
            stage.rename(output)
