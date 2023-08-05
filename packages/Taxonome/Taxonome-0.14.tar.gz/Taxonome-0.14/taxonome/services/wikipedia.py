#!/usr/bin/python3
# -*- coding: utf-8 -*-
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import re
import os.path

from taxonome import config, Taxon, Name, TaxonSet
from taxonome.utils import structxt, fshelf
from taxonome.taxa.base import TaxonShelf

class NoInfoError(Exception):
    pass

USER_AGENT = config['main']['user-agent']

CACHE_FILE = os.path.join(config['cache']['location'], 'wikipedia_cache')
EXPIRY = datetime.timedelta(days=config.getint('cache', 'expiry'))

#cache = fshelf.ForgetfulShelf(CACHE_FILE, expiry=EXPIRY)
titlecache = fshelf.ForgetfulShelf(CACHE_FILE+"_titles", expiry=EXPIRY)
cache = TaxonShelf(CACHE_FILE)

RAW_BASE = "http://en.wikipedia.org/w/index.php?"
PAGE_BASE = "http://en.wikipedia.org/wiki/"
Redirect_RE = re.compile(r'#REDIRECT ?\[\[(.+?)\]\]',re.I) # I=Ignore Case
Smalltext_RE = re.compile(r'<small>(.+?)</small>', re.I)
RANKS = ['trinomial','binomial','genus','familia','ordo','classis','phylum','regnum']

def get_page(title, follow_redirects=True):
    """Gets the raw wikicode of a page, given the title."""
    query = urlencode({'title':title.replace(" ","_"), 'action':'raw'})
    page = urlopen(Request(RAW_BASE + query, headers={'ua':USER_AGENT}))
    content = page.read().decode('utf-8')
    if follow_redirects and content.upper().startswith("#REDIRECT"):
        new_title = Redirect_RE.match(content).group(1)
        titles, page = get_page(new_title)
        return titles + [title], page
    else:
        return [title], content
    
def _get_taxobox(page):
    """Cuts the taxobox out of a page, and translates its parameters
    into a dictionary."""
    for template in structxt.grabchunks(page, '{{','}}'):
        if template.strip().lower().startswith('taxobox'):
            break
    else:
        raise NoInfoError("No taxobox found")
    slots = structxt.splitwithout(template, '|', [('{{','}}'),('[[',']]')])
    params = {}
    for slot in slots[1:]:
        name, dummy, value = slot.partition("=")
        params[name.strip().lower()] = value.strip()
    return params

def get_taxobox(name):
    """Look up a name, and return the parameters in its taxobox as a
    dictionary."""
    title, page = get_page(name)
    return title, _get_taxobox(page)
    
def _munge_synonyms(wikicode):
    synlines = wikicode.split("*")
    if len(synlines) <= 1:
        wikicode = wikicode.replace("<br>","<br/>")
        synlines = wikicode.split("<br/>")
    synonyms = []
    for synline in synlines:
        synline = synline.strip()
        if not synline:
            continue
        if "<small>" in synline: # small tags are often used for authors
            name = _strip_wikicode(synline[:synline.find("<small>")] )
            auth = _strip_wikicode(Smalltext_RE.search(synline).group(1) )
            synonyms.append(Name(name, auth))
            continue
        italicbits = synline.split("''")
        if italicbits[0].strip() != "":
            continue # Name should start italic
        name = " ".join(italicbits[1:-1]) # This allows for var./subsp.
        auth = _strip_wikicode(italicbits[-1])
        synonyms.append(Name(name, auth))
    return synonyms

    
def _strip_wikicode(text):
    # Tidy up links, including piped links
    text = re.sub(r"\[\[(.+?\|)?(.+?)\]\]",r"\2",text)
    while "<ref" in text: # Cut references out.
        refstart = text.find("<ref")
        if "</ref>" in text:
            refend = text.find("</ref>") + len("</ref>")
        else:
            refend = text.find("/>",refstart) + 2
        text = text[:refstart] + text[refend:]
    return text.replace("'''","").replace("''","").strip()

def resolve(qname):
    if qname in cache:
        return cache[qname]
    if isinstance(qname, str) and qname in titlecache:
        return [cache[titlecache[qname]]]
    if hasattr(qname, "name"):
        name = qname.name
    else:
        name = qname
    title, taxobox = get_taxobox(name)
    for rank in RANKS:
        if rank in taxobox:
            accname = _strip_wikicode(taxobox[rank])
            authkey = rank + "_authority"
            if authkey in taxobox:
                auth = _strip_wikicode(taxobox[authkey])
            else:
                auth = ""
            break
    else:   # No taxon name found.
        return None
    wp_taxon = Taxon(accname, auth)
    wp_taxon.url = PAGE_BASE + title[0].replace(" ","_")
    if 'synonyms' in taxobox:
        wp_taxon.othernames = _munge_synonyms(taxobox['synonyms'])
    cache.add(wp_taxon)
    for pagetitle in title:
        if not wp_taxon.hasname(pagetitle):
            titlecache[pagetitle] = wp_taxon.name
    if hasattr(qname, "name"):
        if wp_taxon.hasname(qname):
            return wp_taxon
        return None      # Name found, but qualifier didn't match, so don't return.
    return [wp_taxon]
