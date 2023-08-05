"""Setup script for formast."""

from setuptools import setup
from distutils.core import Extension
import codecs
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

long_description = codecs.open("README.rst", "rb", "utf8").read()

sources = ['formastPYTHON_wrap.cxx']
libraries = ['formast']
extra_compile_args = []
define_macros = []

### platform specific configuration ###

if sys.platform == "win32":
    extra_compile_args += ['/EHsc']
    define_macros += [('FORMAST_STATIC', None)]

### extension module ###

ext_formast = Extension(
    'formast._formast',
    sources=sources,
    libraries=libraries,
    extra_compile_args=extra_compile_args,
    define_macros=define_macros,
    )

### setup configuration ###

setup(
    name='formast',
    version='0.1.0a0',
    author='Amorilia',
    author_email='amorilia@users.sourceforge.net',
    packages=['formast'],
    ext_modules=[ext_formast],
    download_url=r'https://github.com/amorilia/formast/downloads',
    platforms=['any'],
    zip_safe=False,
    description=long_description.split('\n')[0],
    long_description=long_description,
    classifiers=[_f for _f in classifiers.split('\n') if _f],
    license='BSD',
    keywords='file format, abstract syntax tree',
    url=r'https://github.com/amorilia/formast',
    )
