"""Cython setup for compiling partpy."""

from distutils.extension import Extension

EXTENSIONS = [
    Extension('partpy.sourcestring', ['partpy/sourcestring.py']),
    Extension('partpy.fpattern', ['partpy/fpattern.py'])
    ]
