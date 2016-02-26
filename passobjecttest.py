import json
from io import StringIO
import dill


class FileItem:
    def __init__(self, fname):
        self.fname = fname

    def echo(self):
        print(self.fname)

f = FileItem("/foo/bar")
ser = dill.dumps(f)


nf = dill.loads(ser)
nf.echo()

