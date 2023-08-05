import gzip
import os
import errno
import codecs
from contextlib import nested

__version__ = '0.1.2'

GZ_SUFF = '.gz'
BUFSIZE = 1048576

builtin_open = open

def gzip_fname(filename):
    with nested(open(filename), 
            smart_open(filename + GZ_SUFF, 'w')) as (inf, outf):
        while True:
            data = inf.read(BUFSIZE)
            if not data:
                break
            outf.write(data)
    os.unlink(filename)

def open(filename, mode='r', encoding=None, exts=None):
    """A replacement for `open` (well, `codecs.open` really) which 
    checks the file for a '.gz' suffix and opens it as a gzip file if found.
    You can also have it check for uncompressed and compressed versions by 
    supplying an argument for `exts`, which should be a list of suffixes to try
    in order of priority"""
    if exts is None:
        if filename.endswith(GZ_SUFF):
            newfile = ContextGzipFile(filename, mode=mode)
        else:
            newfile = builtin_open(filename, mode)
        if encoding:
            newfile = codecs.EncodedFile(newfile, encoding)
        return newfile
    else:
        all_exts = exts
        if '' not in all_exts:
            all_exts = [''] + all_exts # priority to uncompressed by default
        for e in all_exts:
            new_fname = filename + e
            try:
                return smart_open(new_fname, mode, encoding=encoding) 
            except IOError, e:
                if e.errno != errno.ENOENT:
                    raise
        raise IOError(errno.ENOENT, "Couldn't find any of {%s}" % ', '.join(filename + e for e in all_exts))
    
class ContextGzipFile(gzip.GzipFile):
    """ adds a context manager to gzipfile since this isn't in python2.6
    """
    def __enter__(self):
        if self.fileobj is None:
            raise ValueError("I/O operation on closed GzipFile object")
        return self

    def __exit__(self, *args):
        self.close()
