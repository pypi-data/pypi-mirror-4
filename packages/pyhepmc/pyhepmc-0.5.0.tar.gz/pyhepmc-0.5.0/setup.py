#! /usr/bin/env python

"""\
A simple wrapper on the main classes of the HepMC event simulation
representation, making it possible to create, read and manipulate HepMC events
from Python code.
"""

from distutils.core import setup, Extension
import os, sys

## Specify HepMC install dir
HEPMCINCPATH, HEPMCLIBPATH = None, None
if os.path.join(os.environ.has_key("HEPMCPATH")):
    HEPMCINCPATH = os.path.join(os.environ["HEPMCPATH"], "include")
    HEPMCLIBPATH = os.path.join(os.environ["HEPMCPATH"], "lib")
if os.path.join(os.environ.has_key("HEPMCINCPATH")):
    HEPMCINCPATH = os.environ["HEPMCINCPATH"]
if os.path.join(os.environ.has_key("HEPMCLIBPATH")):
    HEPMCLIBPATH = os.environ["HEPMCLIBPATH"]
if HEPMCLIBPATH is None or HEPMCINCPATH is None:
    print "You must specify the HepMC install path via the HEPMCPATH (or HEPMCINCPATH & HEPMCLIBPATH) env variables"
    print "e.g. HEPMCPATH=$HOME/local ./setup.py --prefix=$HOME/local"
    sys.exit(1)

## Extension definition
ext = Extension('_hepmcwrap', ['hepmc/hepmcwrap.i'],
                swig_opts=['-c++', '-Iinclude', '-I'+HEPMCINCPATH],
                include_dirs = [HEPMCINCPATH], library_dirs = [HEPMCLIBPATH], libraries = ['HepMC'])

## Setup definition
setup(name = 'pyhepmc',
      version = '0.5.0',
      ext_package = "hepmc",
      ext_modules = [ext],
      py_modules = [ 'hepmc.__init__', 'hepmc.hepmcwrap'],
      author = 'Andy Buckley',
      author_email = 'andy@insectnation.org',
      url = 'http://projects.hepforge.org/pyhepmc/',
      description = 'A Python interface to the HepMC high-energy physics event record API',
      long_description = __doc__,
      keywords = 'generator montecarlo simulation data hep physics particle',
      license = 'GPL')
