from contextlib import contextmanager

@contextmanager
def atomic_writer(path, mode=0644):
    """
    Write to path in an atomic operation. Auto creates any directories leading up to ``path``
    """
    dirname = os.path.dirname(path)
    makedir(dirname)
    tmpfile = NamedTemporaryFile(delete=False, dir=os.path.dirname(path))
    yield tmpfile
    tmpfile.close()
    os.rename(tmpfile.name, path)

def makedir(path):
    """
    Create a directory at ``path``. Unlike ``os.makedirs`` don't raise an error if ``path`` already exists.
    """
    try:
        os.makedirs(path)
    except OSError, e:
        # Path already exists or cannot be created
        if not os.path.isdir(path):
            raise

