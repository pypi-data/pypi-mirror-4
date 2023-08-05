# -*- coding: utf-8 -*-
"""This module fetches information from the World Register of Marine Species
webservice.

http://www.marinespecies.org/

Technical note: tested using the Python 3 patches for suds available at
https://bitbucket.org/bernh/suds-python-3-patches/wiki/Home
"""
from suds.client import Client

from taxonome import Name, Taxon
from taxonome.taxa.collection import TaxaResource, TaxonSet

WSDL_URL = "http://www.marinespecies.org/aphia.php?p=soap&wsdl=1"

def _make_taxon(record):
    tax = Taxon(record.valid_name, record.valid_authority)
    tax.name.aphia_id = record.valid_AphiaID
    
    if record.status == "accepted":
        tax.lsid = record.lsid
        tax.url = record.url
    else:
        syn = Name(record.scientficname, record.authority)
        tax.othernames.add(syn)
    
    return tax

class WoRMSTaxaResource(TaxaResource):
    def __init__(self):
        super().__init__()
        self.service = Client(WSDL_URL)
        self.cache_by_id = {}
        
    def get_by_accepted_name(self, name):
        try:
            tax = self.cache_by_id[name.aphia_id]
        except (AttributeError, KeyError):
            records = self.service.service.getAphiaRecords(name.plain)
            tax = _make_taxon(records[0])
        
        for synrecord in self.service.service.getAphiaSynonymsByID(tax.name.aphia_id):
            syn = Name(synrecord.scientificname, synrecord.authority)
            tax.othernames.add(syn)
        
        self.cache_by_id[tax.name.aphia_id] = tax
        return tax
    
    def resolve_name(self, key):
        if isinstance(key, Name):
            return [(n, an) for n, an in self.resolve_name(key.plain) \
                                            if n.authority==key.authority]
        
        names = []
        for record in self.service.service.getAphiaRecords(key):
            n = Name(record.scientificname, record.authority)
            n.aphia_id = record.AphiaID
            an = Name(record.valid_name, record.valid_authority)
            an.aphia_id = record.AphiaID
            names.append((n, an))
        return names

_instance = None
def _get_instance():
    global _instance
    if not _instance:
        _instance = WoRMSTaxaResource()
    return _instance

def select(*args, **kwargs):
    return _get_instance().select(*args, **kwargs)

def resolve_name(*args, **kwargs):
    return _get_instance().resolve_name(*args, **kwargs)
