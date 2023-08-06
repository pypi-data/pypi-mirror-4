#! /usr/bin/env python

"""\
A simple wrapper on the main classes of the HepMC event simulation
representation, making it possible to create, read and manipulate HepMC events
from Python code.
"""

from distutils.core import setup, Extension

## Extension definition
import os
ext = Extension('_hepmcwrap',
                ['./hepmc/hepmcwrap_wrap.cc'],
                define_macros = [("SWIG_TYPE_TABLE", "hepmccompat")],
                include_dirs=['/home/andy/heplocal/include'],
                library_dirs=['/home/andy/heplocal/lib'],
                libraries=['HepMC'])

## Setup definition
setup(name = 'pyhepmc',
      version = '0.4.0',
      ext_package = "hepmc",
      ext_modules = [ext],
      py_modules = [ 'hepmc.__init__', 'hepmc.hepmcwrap'],
      author = ['Andy Buckley'],
      author_email = 'andy@insectnation.org',
      url = 'http://projects.hepforge.org/pyhepmc/',
      description = 'A Python interface to the HepMC high-energy physics event record API',
      long_description = __doc__,
      keywords = 'generator montecarlo simulation data hep physics particle',
      license = 'GPL')
