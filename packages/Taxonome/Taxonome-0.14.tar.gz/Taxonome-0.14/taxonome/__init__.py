# -*- coding: utf-8 -*-
from .taxa import Taxon, Name, TaxonSet
from . import config, taxa, regions

__all__ = ['config', 'taxa', 'regions', 'wikipedia', 'col']

__version__ = "0.14"

#caches = [wikipedia.cache]
#def clean_caches():
#    for cache in caches:
#        cache.clean_outdated()

#if config.getboolean('cache', 'clean-on-load'):
#    clean_caches()
