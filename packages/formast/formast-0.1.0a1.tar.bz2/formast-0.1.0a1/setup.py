"""Setup script for formast."""

# set this to True if you want to link against system libs and
# includes; this requires that you have the C++ boost and formast
# dynamic libraries installed at default system locations (i.e.
# /usr/lib and /usr/include on linux) or that you pass appropriate
# --include-dirs and --library-dirs options to python setup.py
# build_ext
USE_SYSTEM_LIBS = False

from setuptools import setup
from distutils.core import Extension
import codecs
from glob import glob
import re
import sys

### general options ###

classifiers = """\
Development Status :: 3 - Alpha
License :: OSI Approved :: BSD License
Intended Audience :: Developers
Topic :: Software Development :: Code Generators
Topic :: Software Development :: Compilers
Topic :: Software Development :: Interpreters
Topic :: Text Processing :: Markup :: XML
Programming Language :: C++
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.0
Programming Language :: Python :: 3.1
Programming Language :: Python :: 3.2
Programming Language :: Python :: 3.3
Operating System :: OS Independent"""
#Topic :: Formats and Protocols :: Data Formats

readme_lines = codecs.open("README.rst", "rb", "utf8").read().split('\n')

### global settings for library and extension module ###

extra_compile_args = []
define_macros = []
include_dirs = []
if not USE_SYSTEM_LIBS:
    include_dirs += ['include']
libraries = []
sources = ['formastPYTHON_wrap.cxx']

### platform specific configuration ###

if sys.platform == 'win32':
    extra_compile_args += ['/EHsc']

### library ###

if not USE_SYSTEM_LIBS:
    # implementation note: don't use build_clib, it's broken on windows
    define_macros += [('FORMAST_STATIC', None)]
    sources += glob('lib/*.cpp')
else:
    libraries += ['formast']

### extension module ###

ext_formast = Extension(
    'formast._formast',
    sources=sources,
    libraries=libraries,
    extra_compile_args=extra_compile_args,
    define_macros=define_macros,
    include_dirs=include_dirs,
    )

### setup configuration ###

setup(
    name='formast',
    version='0.1.0a1',
    author='Amorilia',
    author_email='amorilia@users.sourceforge.net',
    packages=['formast'],
    ext_modules=[ext_formast],
    download_url=r'http://pypi.python.org/pypi/formast/',
    platforms=['any'],
    zip_safe=False,
    description=readme_lines[0],
    long_description="\n".join(readme_lines[2:]),
    classifiers=[_f for _f in classifiers.split('\n') if _f],
    license='BSD',
    keywords='file format, abstract syntax tree',
    url=r'https://github.com/amorilia/formast',
    )
