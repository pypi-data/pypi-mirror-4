from marlib import __version__ as MARLIB_VERSION
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

long_desc = """
MARLib - Music Signal Processing and Analysis Library
  Under development by the Music and Audio Research Lab (MARL) at NYU
  http://marl.smusic.nyu.edu

=====

Provides
    1. Abstracted audio file reading & writing (internal buffering)
    2. Integration with SoX for various CODEC support

Under Development
    1. Basic time-frequency transforms
    2. Integration with SoX for various CODEC support

How to use the documentation
----------------------------
Documentation is available inline as docstrings provided within the code. In
time, it is our intention to host a Sphynx-like online reference to facilitate
ease of use.


Examples provided assume that each module has been imported as its first
characters in uppercase::

  >>> import marlib.audiofile as AF
  >>> import marlib.timefreq as TF
      ...

...where code snippets are indicated by three greater-than signs.

Use the built-in ``help`` function to view a function's docstring::

  >>> help(TF.mel)

Available subpackages
---------------------
audiofile
timefreq
signal
utils


Dependencies
-----------------------------------
This package builds upon freely available Python libraries at various
stages of maturity:

- NumPy: Numerical Computing in Python
- SciPy: Scientific Computing in Python

Additionally, this library takes advantage of SoX, a command
line utility for non-wave file support and audio file conversion.
If you do not currently have SoX, it can be obtained here:

    http://sox.sourceforge.net

SoX functionality is currently supported under Unix-like OS's only,
(sorry, Windows). However, extending this library should be straightforward
if necessary. Note that SoX is required only for file conversions and
non-wave file formats, so - while strongly encouraged - SoX is not
truly mandatory.
"""


download_url = "http://pypi.python.org/packages/source/m/marlib/"\
               "marlib-0.3.tar.gz"

setup(name='marlib',
      version=MARLIB_VERSION,
      description='Music Signal Processing and Analysis Library',
      author='Eric Humphrey',
      author_email='ejhumphrey@nyu.edu',
      url='https://bitbucket.org/ejh333/marlib',
      download_url=download_url,
      license='LGPL',
      packages=find_packages(),
      install_requires=['numpy'],
      py_modules=['marlib'],
      long_description=long_desc
)
