#! /usr/bin/env python

"""\
mcview uses the Python wrapper for HepMC to load and view HepMC events as
3D final-state representations in (log-)momentum space, and to dump the graph
structure to PDF and graphviz formats.
"""

## Test for visual package (not in PyPI)
try:
    import visual
except:
    import sys
    sys.stderr.write("mcview requires the 'visual' Python package from vpython\n")
    sys.stderr.write("This package can't be automatically downloaded: please get it"
                     "manually or via system packages (e.g. 'python-visual' on Ubuntu)")
    sys.exit(1)


## Setup definition
from distutils.core import setup
setup(name = 'mcview',
      version = "0.4.1",
      #include_package_data = True,
      install_requires = ['pyhepmc', 'pydot'],
      scripts = ['mcview'],
      author = ['Andy Buckley'],
      author_email = 'andy@insectnation.org',
      description = 'A 3D / graph event viewer for high-energy physics event simulations',
      long_description = __doc__,
      keywords = 'generator montecarlo simulation data hep physics particle',
      license = 'GPL',
      classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering :: Physics'])
