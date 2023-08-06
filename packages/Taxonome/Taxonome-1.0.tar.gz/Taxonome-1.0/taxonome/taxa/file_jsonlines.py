#! /usr/bin/env python
# -*- coding: utf8 -*-
"""
This modules is for loading and saving taxa in the JSON lines format. This is a
modification of JSON where a series of JSON items are stored line by lines,
allowing them to be decoded individually, without having to hold the entire
object in memory.
"""
import json

from taxonome import Taxon, TaxonSet

def iter_taxa(filehandle, progress=None):
    """Loads taxa from a JSON lines file, iterating over them, without
    keeping the entire set in memory."""
    i = 0
    for line in filehandle:
        d = json.loads(line)
        yield Taxon.from_dict(d)
        
        i += 1
        if progress and (i % 50 == 0):
            progress(filehandle.buffer.tell())

def load_taxa(filehandle, progress=None):
    """Load a TaxonSet from a JSON lines file."""
    ts = TaxonSet()
    for taxon in iter_taxa(filehandle, progress=progress):
        ts.add(taxon)
    return ts
    
def save_taxon(filehandle, taxon):
    """Saves a single taxon to the given file. Can be called repeatedly to save
    successive taxa."""
    s = json.dumps(taxon.to_dict(), indent=None)
    filehandle.write(s + "\n")

def save_taxa(filehandle, taxasource):
    """Saves a TaxonSet (or any iterable source of taxa) to the given handle, in
    JSON lines format."""
    for taxon in taxasource:
        save_taxon(filehandle, taxon)
