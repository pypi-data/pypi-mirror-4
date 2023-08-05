import contextlib
import tempfile
import shutil


@contextlib.contextmanager
def temporary_directory():
    """Create temporary directory, than remove it."""
    path = tempfile.mkdtemp()
    try:
        yield path
    finally:
        shutil.rmtree(path)
