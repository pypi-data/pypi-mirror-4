#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module fetches information from the MBG Tropicos database.

http://www.tropicos.org/
"""
import json
from urllib.parse import urlencode
from urllib.request import urlopen

from taxonome import Name, Taxon
from taxonome.taxa.collection import TaxaResource
from taxonome.config import config

apikey = config['api-keys']['tropicos']

class TropicosError(KeyError): pass
class TropicosNoAPIKey(TropicosError):
    def __str__(self):
        return ("An API key is needed for Tropicos. Please visit "
                "http://services.tropicos.org/help?requestkey\n\n"
                "See the doc page on configuration for where to put the key.")

urlbase = "http://services.tropicos.org/Name/"
common_params = dict(apikey=apikey, format='json')

def _make_name(res):
    name = res["ScientificName"]
    auth = res["ScientificNameWithAuthors"].replace(name, "")
    return Name(name, auth)

def _load(url):
    res = json.loads(urlopen(url).read().decode())
    if "Error" in res[0]:
        raise TropicosError(res[0]["Error"])
    return res

def _search(name, wildcard=False):
    """Search for the specified name with the tropicos API"""
    if not common_params['apikey']:
        raise TropicosNoAPIKey
    params = {'name':name, 'type': 'wildcard' if wildcard else 'exact'}
    params.update(common_params)
    return _load(urlbase + "Search?" + urlencode(params))

def _summary(name_id):
    """Get summary info."""
    if not common_params['apikey']:
        raise TropicosNoAPIKey
    return _load(urlbase + name_id + "?" + urlencode(common_params))

def _call_method(method, name_id):
    """Get info for a given name_id. method is the name of one of the API methods,
    such as Synonyms or HigherTaxa. Details are on the Tropicos website:
    http://services.tropicos.org/help
    """
    if not common_params['apikey']:
        raise TropicosNoAPIKey
    url = urlbase + name_id + "/" + method + "?" + urlencode(common_params)
    return _load(url)

class TropicosTaxon(Taxon):
    id = ""
    @property
    def url(self):
        return "http://www.tropicos.org/Name/" + id

class TropicosTaxaResource(TaxaResource):
    def resolve_name(self, key):
        plainkey = key.plain if hasattr(key, "plain") else key
        names = []
        for res in _search(plainkey):
            name = _make_name(res)
            name.id = str(res["NameId"])
            if name.match(key):
                try:
                    r2 = _call_method("AcceptedNames", name.id)[0]["AcceptedName"]
                    accname = _make_name(r2)
                    accname.id = str(r2["NameId"])
                except TropicosError:
                    accname = name
                names.append((name, accname))
        return names
    
    def get_by_accepted_name(self, name):
        if not hasattr(name, "id"):
            name.id = str(_search(name.name)["NameId"])
        t = TropicosTaxon(name)
        t.id = name.id
        return t

_instance = TropicosTaxaResource()

resolve_name = _instance.resolve_name
select = _instance.select
    
