""" argopen is open() for argparse """

import sys
import argparse


def argopen(filename, mode='r', bufsize=None):
    """open() which handles dash '-' as stdin/stdout, and fixes binary mode on Windows"""
    if filename == '-':
        if 'r' in mode:
            f = sys.stdin
        elif 'w' in mode:
            f = sys.stdout
        else:
            raise ValueError(mode)
        if 'b' in mode and sys.platform == 'win32':
            import os
            import msvcrt
            msvcrt.setmode(f.fileno(), os.O_BINARY)
        return f
    else:
        if bufsize is None:
            return open(filename, mode)
        else:
            return open(filename, mode, bufsize)


class FileType(argparse.FileType):
    """A drop-in replacement for argparse.FileType"""

    def __call__(self, string):
        return argopen(string, self._mode, self._bufsize)
