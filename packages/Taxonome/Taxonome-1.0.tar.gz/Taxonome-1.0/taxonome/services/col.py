#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module gets information from the Catalogue of Life Annual Checklist
(currently the 2010 version). Browse the checklist at:
http://www.catalogueoflife.org/annual-checklist/2010/

Information about the RESTful web service is at:
http://webservice.catalogueoflife.org/annual-checklist/2010/search/all
"""

import os.path
from urllib.parse import urlencode
from xml.etree import ElementTree

from taxonome import Taxon, Name, TaxonSet
from taxonome.config import config
from taxonome.taxa.collection import TaxaResource
from taxonome.taxa.taxonshelf import TaxonShelf
from .utils import urlopen

BASE_URL = "http://www.catalogueoflife.org/annual-checklist/2010/webservice?"

CACHE_FILE = os.path.join(os.path.expanduser(config['cache']['location']), 'CoL_cache')

cache = TaxonShelf(CACHE_FILE)

def _make_taxon(xmldesc, name=None):
    "Make a Taxon object from a suitable XML tree."
    if not name:
        name = _make_name(xmldesc)
    newtaxon = Taxon(name)
    newtaxon.url = xmldesc.find("url").text
    newtaxon.id = xmldesc.find("id").text
    for synonym in xmldesc.findall("synonyms/synonym"):
        synname = _make_name(synonym)
        newtaxon.othernames.add(synname)
    xdistrib = xmldesc.find("distribution")
    distribution = xdistrib.text if (xdistrib is not None) else None
    if distribution:
        newtaxon.distribution = set(distribution.split("; "))
    cache.add(newtaxon)
    return newtaxon

def _make_name(xmldesc):
    "Make a Name object from a suitable XML tree."
    barename = xmldesc.find("name").text
    xauth = xmldesc.find("author")
    auth = xauth.text if (xauth is not None) else ""
    name = Name(barename, auth)
    return name

def _get_xml(name):
    "Get the XML for a given name."
    query = urlencode({'name':name, 'response':'full'})
    return ElementTree.parse(urlopen(BASE_URL+query))

def _get_name_results(name):
    "Find the (name, accepted) name pairs for a given unqualified name."
    results = []
    for result in _get_xml(name).findall("result"):
        status = result.find("name_status").text
        if status == "accepted name":
            accname = _make_name(result)
            results.append((accname, accname))
        
        elif status == "synonym":
            synname = _make_name(result)
            accxml = result.find("accepted_name")
            accname = _make_name(accxml)
            results.append((synname, accname))
            
            # We call this so the taxon gets added to the cache
            _make_taxon(accxml)
        
        else:
            msg = "Unrecognised name status: {0}".format(status)
            raise NotImplementedError(msg) 
            
    return results

def fetch(search):
    """Fetch taxa matching a search term, e.g. "Restionacae". Returns a TaxonSet.
    
    Note that Catalogue of Life only looks one level down, so searching for a
    family will return a collection of genera. There will be minimal information
    about each.
    """
    ts = TaxonSet()
    for xtax in _get_xml(search).findall("result/child_taxa/taxon"):
        ts.add(_make_taxon(xtax))
    return ts

class CoLTaxaResource(TaxaResource):
    def resolve_name(self, key):
        if key in cache:
            return cache.resolve_name(key)
        if isinstance(key, Name):
            return [(n, an) for n, an in _get_name_results(key.plain) \
                                            if n.authority==key.authority]
        return _get_name_results(key)
    
    def get_by_accepted_name(self, name):
        if name in cache:
            return cache.get_by_accepted_name(name)
        tax = _make_taxon(_get_xml(name.plain).find('result'))
        if not name.match_qualified(tax.name):
            raise KeyError("Name did not match with authority.")
        return tax
    
_instance = CoLTaxaResource()

resolve_name = _instance.resolve_name
select = _instance.select
    
