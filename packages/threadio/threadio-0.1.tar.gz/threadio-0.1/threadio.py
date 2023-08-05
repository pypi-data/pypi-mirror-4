r"""ThreadIO, is good for capture stdout at multi-thread environment.

[HIDE]
I don't know what is restruct text.
>>> from __future__ import print_function
>>> import io, sys
>>> TextIO = sys.version_info[0] <= 2 and io.BytesIO or io.StringIO
>>> oldstdout = sys.stdout

[/HIDE]
>>> # standard capture
>>> from threadio import print_to_file
>>> with print_to_file(TextIO()) as fp:
...     print("hello world")
...
>>> fp.getvalue()
'hello world\n'

>>> # standard capture (but not stdout, stderr)
>>> from threadio import ThreadIO
>>> fp = ThreadIO(TextIO())
>>> with fp.capture(TextIO()) as fp2:
...     print("hello world", file=fp)
...     with fp.capture(TextIO()) as fp3:
...         print("hello world3", file=fp)
...         # not captured fp3, stored fp2
...         print("fail captured", file=fp2)
...
>>> fp.getvalue()
''
>>> fp2.getvalue()
'hello world\nfail captured\n'
>>> fp3.getvalue()
'hello world3\n'

>>> # thread example
>>> from threading import Thread
>>> from threadio import print_to_file
>>> th = Thread(target=print, args=("hello world!",))
>>> with print_to_file(TextIO()) as fp:
...     th.start()
...     th.join()
...     print("HAYO!")
... 
hello world!
>>> fp.getvalue() # not capture other thread's print
'HAYO!\n'

[HIDE]
>>> sys.stdout = oldstdout

[/HIDE]
>>> # note. print_to_xxx function change everything. 
>>> a = sys.stdout
>>> with print_to_file(TextIO()): pass
>>> b = sys.stdout
>>> a is b
False

"""
from __future__ import print_function
__author__ = "EcmaXp ( module-threadio@ecmaxp.pe.kr )"

import sys
import io
import threading
from contextlib import contextmanager

__all__ = ["ThreadIO", "print_to_file", "print_to_list"]

CAPTURE_STDNAME = "stderr", "stdout"

class ThreadIO():
    def __init__(self, fileio):
        self.default_io = fileio
        self.local_io = threading.local()

    def __getattr__(self, name):
        return getattr(self.current_io, name)

    def get_current_io(self):
        try:
            return self.local_io.ios[-1]
        except (AttributeError, IndexError):
            return self.default_io

    def set_current_io(self, fileio):
        try:
            ios = self.local_io.ios
        except AttributeError:
            ios = self.local_io.ios = []

        ios.append(fileio)

    def remove_current_io(self):
        self.local_io.ios.pop()

    current_io = property(get_current_io)

    @contextmanager
    def capture(self, io):
        self.set_current_io(io)
        try:
            yield io
        finally:
            self.remove_current_io()

class ListWriteIO(io.TextIOBase):
    def __init__(self):
        self.data = []

    def write(self, data):
        if self.closed:
            raise ValueError("write to closed file")
        elif not isinstance(data, str):
            raise TypeError("can't write str to text stream")
        else:
            self.data.append(data)

    def writable(self):
        return True

    def getlist(self):
        return self.data

    def close(self):
        super().close()
        self.data = None

@contextmanager
def print_to_file(fileobj, name="stdout"):
    if name not in CAPTURE_STDNAME:
        raise ValueError("name must %s or %s" % CAPTURE_STDNAME)

    if isinstance(getattr(sys, name), ThreadIO):
        stdout = getattr(sys, name)
    else:
        stdout = ThreadIO(getattr(sys, name))
        setattr(sys, name, stdout)

    stdout.set_current_io(fileobj)

    try:
        yield fileobj # inner block
    finally:
        stdout.remove_current_io()

@contextmanager
def print_to_list(out):
    if not isinstance(out, list):
        raise TypeError("first argment must be list")

    fileobj = ListWriteIO()

    with print_to_file(fileobj):
        yield out

    out.extend(fileobj.getlist())

def main():
    import __main__
    import sys
    sys.modules["threadio"] = __main__

    import doctest
    doctest.testmod()

if __name__ == "__main__":
    main()
