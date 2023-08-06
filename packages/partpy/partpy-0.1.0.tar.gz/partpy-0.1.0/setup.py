#!/usr/bin/python
import re
import os
import sys
import platform
from distutils.core import setup, Command
cy = True
try:
    from Cython.Distutils import build_ext
    import partcy
except ImportError:
    cy = False

__version__ = '0.1.0'
__author__ = 'Nekroze'
__email__ = 'nekroze@eturnilnetwork.com'
SOURCE = 'partpy'
TESTDIR = 'test'
PROJECTNAME = 'partpy'
PROJECTSITE = 'http://github.com/Nekroze/partpy'
PROJECTDESC = 'Parser Tools in Python, a collection of tools for hand writing lexers and parsers.'
PROJECTLICENSE = 'MIT'
PLATFORMS = ['*nix', 'Windows']

EXTENSIONS = []
if cy:
    EXTENSIONS.extend(partcy.EXTENSIONS)


PYTHON = 'python'
if platform.system() != 'Windows' and sys.version_info[0] == 3:
    PYTHON = 'python3'


class CleanUp(Command):
    """Cleanup all python/cython temporary or build files."""
    description = "Cleanup all python/cython temporary or build files."
    user_options = []

    def initialize_options(self):
        """pass."""
        pass

    def finalize_options(self):
        """pass."""
        pass

    def run(self):
        """Run CleanUp."""
        import fnmatch
        import shutil
        import glob
        matches = []
        matches.extend(glob.glob('./*.pyc'))
        matches.extend(glob.glob('./*.pyd'))
        matches.extend(glob.glob('./*.pyo'))
        matches.extend(glob.glob('./*.so'))
        dirs = []
        dirs.extend(glob.glob('./__pycache__'))
        for root, dirnames, filenames in os.walk(SOURCE):
          for filename in fnmatch.filter(filenames, '*.pyc'):
              matches.append(os.path.join(root, filename))
          for filename in fnmatch.filter(filenames, '*.pyd'):
              matches.append(os.path.join(root, filename))
          for filename in fnmatch.filter(filenames, '*.pyo'):
              matches.append(os.path.join(root, filename))
          for filename in fnmatch.filter(filenames, '*.so'):
              matches.append(os.path.join(root, filename))
          for dirname in fnmatch.filter(dirnames, '__pycache__'):
              dirs.append(os.path.join(root, dirname))

        for match in matches:
            os.remove(match)
        for dir in dirs:
            shutil.rmtree(dir)

class Test(Command):
    """Run test suite."""
    description = "Run test suite"
    user_options = []

    def initialize_options(self):
        """pass."""
        pass

    def finalize_options(self):
        """pass."""
        pass

    def run(self):
        """Run unittests."""
        if os.system(PYTHON + ' -m unittest discover ' + TESTDIR + ' "test_*.py"'):
            sys.exit(1)


class Style(Command):
    """Check style with pylint."""
    description = "Run pylint on source code."
    user_options = []

    def initialize_options(self):
        """pass."""
        pass

    def finalize_options(self):
        """pass."""
        pass

    def run(self):
        """Run pylint."""
        if not os.system('pylint --rcfile=.pylintrc ' + SOURCE + ' examples'):
            print("Pylint reports no inconsistencies.")
        else:
            sys.exit(1)


class Prep(Command):
    """Prepare code by running style check and test suite and freezing."""
    description = "Run test suite"
    user_options = []

    def initialize_options(self):
        """pass."""
        pass

    def finalize_options(self):
        """pass."""
        pass

    def run(self):
        if os.system(PYTHON + ' setup.py test'):
            sys.exit(1)
        if os.system(PYTHON + ' setup.py style'):
            sys.exit(1)


class GitCommit(Command):
    """Git add and commit with message."""
    description = "Git commit."
    user_options = [('message=', 'm', 'Git commit message.')]

    def initialize_options(self):
        """Set message to None by default."""
        self.message = None

    def finalize_options(self):
        """pass."""
        pass

    def run(self):
        """Run git add and commit with message if provided."""
        if os.system('git add .'):
            sys.exit(1)
        if self.message is not None:
            os.system('git commit -a -m "' + self.message + '"')
        else:
            os.system('git commit -a')


class PyPiUpload(Command):
    """Update this project at the current version to pypi."""
    description = "Update pypi."
    user_options = []

    def initialize_options(self):
        """pass."""
        pass

    def finalize_options(self):
        """pass."""
        pass

    def run(self):
        """build an sdist and then upload."""
        if os.system(PYTHON + ' setup.py sdist upload'):
            sys.exit(1)
        print('PyPi Upload successful.')


vRe = re.compile(r'__version__\s*=\s*(\S+)', re.M)
data = open('setup.py').read()

kwds = {}
kwds['version'] = eval(vRe.search(data).group(1))
kwds['description'] = PROJECTDESC
kwds['long_description'] = open('README.rst').read()
kwds['license'] = PROJECTLICENSE
cmdclass={
        'style': Style,
        'test': Test,
        'prep': Prep,
        'commit': GitCommit,
        'pypiup': PyPiUpload,
        'cleanup': CleanUp}
if cy:
    cmdclass['build_ext'] = build_ext

setup(
    cmdclass = cmdclass,

    name=PROJECTNAME,
    author=__author__,
    author_email=__email__,
    url=PROJECTSITE,
    platforms=PLATFORMS,
    packages=[SOURCE],
    ext_modules = EXTENSIONS,
    requires = ['cython'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Compilers',
        'Topic :: Text Processing :: General'
    ],
    **kwds
)
