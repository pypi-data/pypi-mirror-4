from distutils.core import setup
from os.path import join as pjoin

version = "0.14"

packages = ['taxonome',
            'taxonome.regions',
            'taxonome.regions.tests',
            'taxonome.external',
            'taxonome.services',
            'taxonome.taxa',
            'taxonome.taxa.tests',
            'taxonome.tests',
            'taxonome.utils',
            'taxonome.utils.tests',
            'taxonome.gui',
            'taxonome.gui.ui',
            ]
classifiers = ["Development Status :: 4 - Beta",
               "Intended Audience :: Science/Research",
               "License :: OSI Approved :: MIT License",
               "Programming Language :: Python :: 3",
               "Topic :: Scientific/Engineering"
               ]
scripts = [pjoin("scripts", "taxonome"),
          ]

long_description = \
"""Taxonome is a set of tools for working with information on biological taxa.

In particular, it handles scientific names, and can match the names found in a
dataset to a given synonymy, taking into account spelling differences, synonyms
and homonyms.

It also includes functions to standardise species distribution information to the
regions defined by the `Taxonomic Diversity Working Group (TDWG)
<http://www.kew.org/science-research-data/kew-in-depth/gis/resources-and-publications/data/tdwg/index.htm>`_.

Taxonome includes a GUI interface for working with collections of taxa. This
requires `PyQt4 <http://pypi.python.org/pypi/PyQt>`_.
"""

setup(name="Taxonome",
      version=version,
      description="Tools for working with information on species or other taxa.",
      long_description=long_description,
      author="Thomas Kluyver",
      author_email="takowl@gmail.com",
      url="http://taxonome.bitbucket.org/",
      packages=packages,
      classifiers=classifiers,
      scripts=scripts,
      )
