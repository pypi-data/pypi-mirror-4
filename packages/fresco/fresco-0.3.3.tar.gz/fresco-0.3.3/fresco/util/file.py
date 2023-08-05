from contextlib import contextmanager
from os import rename, makedirs
from os.path import dirname, isdir
from tempfile import NamedTemporaryFile


@contextmanager
def atomic_writer(path, mode=0644):
    """
    Write to path in an atomic operation. Auto creates any directories leading
    up to ``path``
    """
    d = dirname(path)
    makedir(d)
    tmpfile = NamedTemporaryFile(delete=False, dir=d)
    yield tmpfile
    tmpfile.close()
    rename(tmpfile.name, path)


def makedir(path):
    """
    Create a directory at ``path``.
    Unlike ``os.makedirs`` don't raise an error if ``path`` already exists.
    """
    try:
        makedirs(path)
    except OSError:
        # Path already exists or cannot be created
        if not isdir(path):
            raise
