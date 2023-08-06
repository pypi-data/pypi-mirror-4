import os

_ROOT = os.path.abspath(os.path.dirname(__file__))

def schema_path(path):
    return os.path.join(_ROOT, 'schema', path)
