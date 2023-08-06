"""Cython setup for compiling partpy."""

from distutils.extension import Extension

EXTENSIONS = [
    Extension('partpy.sourcestring', ['partpy/sourcestring.py']),
    Extension('partpy.fpattern', ['partpy/fpattern.py'])
    ]

CY_OPTS = {"boundscheck": False, "wraparround": False, 'embedsignature': True,
    'infer_types': True}

for e in EXTENSIONS:
    e.pyrex_directives = CY_OPTS
