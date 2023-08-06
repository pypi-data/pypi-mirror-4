base_url = "http://tnrs.iplantc.org/tnrsm-svc/matchNames?"

import io
from itertools import chain
import json
from urllib.parse import urlencode

from taxonome import Name, Taxon
from taxonome.taxa.collection import build_matched_taxonset, combine_dicts
from taxonome.tracker import noop_tracker, prepare_tracker
from .utils import urlopen

def call_api(names, retrieve="best"):
    names = ",".join(names)
    query = urlencode(dict(names=names, retrieve=retrieve))
    return json.load(io.TextIOWrapper(urlopen(base_url + query), 'utf-8'))

def _make_name(result_dict):
    if not result_dict['acceptedName']:
        return None
    return Name(result_dict['acceptedName'], result_dict['authorAttributed'])

def _make_taxon(result_dict):
    n = _make_name(result_dict)
    if n is None:
        return None
    t = Taxon(n)
    t.info['family'] = result_dict['family']
    return t

def chunklist(l, chunksize=100):
    start=0
    while start < len(l):
        chunkend = min(start+chunksize, len(l))
        # Work around an apparent bug in TNRS: if a name has '&' in it (for
        # authorities), TNRS stops processing at that point.
        for i in range(start, chunkend):
            if '&' in l[i]:
                yield l[start:i+1]
                start = i+1
        if start < chunkend:
            yield l[start:chunkend]
        start = chunkend

def match_names(names, include_unmatched=False):
    strnames = [str(n) for n in names]
    result_chunks = (call_api(chunk)['items'] for chunk in chunklist(strnames))
    matched = (_make_taxon(d) for d in chain(*result_chunks)) 
    if include_unmatched:
        return zip(names, matched)
    else:
        return ((n,m) for n,m in zip(names, matched) if m is not None)

def streaming_match_taxa(taxa, taxa2=None, tracker=None):
    """Match taxa to the names in TNRS.
    
    If taxa is a single-use iterable (like an iterator over a file), taxa2 must
    be specified as a second equivalent iterable, which will be used up first.
    With a collection like a TaxonSet, taxa can be used twice.
    """
    tracker = prepare_tracker(tracker)
    if taxa2 is None:
        taxa2 = taxa
    
    names = list({t.name for t in taxa2})
    namematches = dict(match_names(names))
    del names, taxa2
    
    for taxon in taxa:
        tracker.reset()
        tracker.start_taxon(taxon)
        try:
            t2 = namematches[taxon.name]
        except KeyError:
            tracker.name_event(taxon.name, "no match")
            continue
        else:
            tracker.name_transform(taxon.name, t2.name, "matched")
            yield taxon, t2

def run_match_taxa(taxa, taxa2=None, **kwargs):
    for taxonpair in streaming_match_taxa(taxa, taxa2, **kwargs):
        pass
    
def match_taxa(taxa, taxa2=None, merge_info=combine_dicts, **kwargs):
    matching = streaming_match_taxa(taxa, taxa2, **kwargs)
    return build_matched_taxonset(matching, merge_info=merge_info)

def select(name, strict_authority=False, upgrade_subsp="nominal",
                    fuzzy=True, prefer_accepted='noauth', nameselector=None,
                                                        tracker=noop_tracker):
    if not isinstance(name, str):
        name = str(name)
    
    d = call_api([name])['items'][0]
    taxon = _make_taxon(d)
    if taxon is None:
        raise KeyError("No match found", name)
    return taxon
