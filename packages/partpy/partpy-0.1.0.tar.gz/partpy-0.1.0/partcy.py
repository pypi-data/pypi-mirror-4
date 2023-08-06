"""Cython setup for compiling partpy."""

from distutils.extension import Extension

EXTENSIONS = [
    Extension('partpy.sourcestring', ['partpy/sourcestring.py']),
    Extension('partpy.matcher', ['partpy/matcher.py']),
    Extension('partpy.fpattern', ['partpy/fpattern.py']),
    Extension('partpy.spattern', ['partpy/spattern.py'])
    ]
