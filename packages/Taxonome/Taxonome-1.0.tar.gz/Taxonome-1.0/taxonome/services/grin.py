# coding: utf-8
"""
Module for scraping data from the USDA GRIN database.

Note that GRIN (and this module) works with a separate set of IDs from the PI
PI numbers used for accessions. These are on the end of URLs for pages. E.g.
the URL for accession PI 219824 is:
http://www.ars-grin.gov/cgi-bin/npgs/acc/display.pl?1178105
Hence the ID to use for the accession is 1178105.
"""

SEARCHb = "http://www.ars-grin.gov/cgi-bin/npgs/acc/search.pl?"
TAX_ACCb = "http://www.ars-grin.gov/cgi-bin/npgs/html/tax_acc.pl"
OBSb = "http://www.ars-grin.gov/cgi-bin/npgs/acc/obs.pl?"
ACCb = "http://www.ars-grin.gov/cgi-bin/npgs/acc/display.pl?"
TAX_SEARCH_URL = "http://www.ars-grin.gov/cgi-bin/npgs/html/tax_search.pl"
TAXON_URL = "http://www.ars-grin.gov/cgi-bin/npgs/html/taxon.pl?"
import re
from collections import defaultdict
from urllib.parse import urlencode
import warnings
from bs4 import BeautifulSoup

from taxonome import Name, Taxon, TaxonSet
from taxonome.taxa.base import UncertainSpeciesError
from taxonome.taxa.collection import TaxaResource
from .utils import urlopen

locnre = re.compile(r'Collected in: (.+?)<')
improvementre = re.compile(r'Improvement status: (.+?)\.')

improve_status = {'100':"Wild",
    '110':"Wild: Natural",
    '120':"Semi-natural/wild",
    '200':"Weedy",
    '300':"Landrace",
    '400':"Breeding/research material",
    '410':"Breeder's line",
    '411':"Synthetic population",
    '412':"Hybrid (breeding/research material)",
    '413':"Founder stock/base population",
    '414':"Inbred line (parent of hybrid cultivar)",
    '415':"Segregating population (breeding/research material)",
    '420':"Mutant/genetic stock",
    '500':"Advanced/improved cultivar",
    '999':"(Other)"}
improve_status_code = dict((v, k) for k, v in improve_status.items())

def _parse_name_item(tag):
    if isinstance(tag.contents[-1], str):
        auth = tag.contents[-1].strip()
        nameparts = tag.contents[:-1]
    else:
        auth = ""
        nameparts = tag.contents 
    rawname = "".join(a.text if hasattr(a, 'text') else a 
                    for a in nameparts).replace("&#215;", "×")
    if rawname.endswith((" spp.", " sp."," hybr.")):
        raise UncertainSpeciesError
    return Name(rawname, auth)

def _parse_synonym(tag):
    accname = _parse_name_item(tag.b)
    contents = tag.contents[:-2]
    auth = contents[-1].rstrip("(=").strip()
    rawname = "".join(a.text if hasattr(a, 'text') else a 
                    for a in contents[:-1]).replace("&#215;", "×")
    synname = Name(rawname, auth)
    return synname, accname

def _search(query, progress=None):
    """Do a simple species search on GRIN. Takes the search parameter, e.g.
    'Vicia', and returns a list of Taxon objects.
    """
    query = urlencode({"search":query}).encode('utf-8')
    page = BeautifulSoup(urlopen(TAX_SEARCH_URL, query))
    # Pages for single taxa have h2, a list of results has h1
    if page.h2:
        acctax = _read_sp_page(page)
        accname = acctax.name
        accname.grin_id = acctax.id
        return [(None, accname)]
    
    results = []
    lis = page.ol.findAll("li")
    if progress:
        progress.max(len(lis))
    i = 0
    for li in lis:
        ID = li.a['href'].split("?")[-1]
        if li.a.contents[0].name != "b":
            try:
                namepair = _parse_synonym(li.a)
            except Exception as e:
                warnings.warn("Error parsing name: %s" % e)
                continue
            namepair[1].grin_id = ID
            results.append(namepair)
            continue
        try:
            accname = _parse_name_item(li.a.b)
        except Exception as e:
            warnings.warn("Error parsing name: %s" % e)
            continue
        accname.grin_id = ID
        results.append((None,accname))
        
        i += 1
        if progress and (i % 50 == 0):
            progress(i)

    return results

def get_by_PI(PIcode):
    """Returns basic details of an accession, by searching for its PI number or 
    equivalent code"""
    PIcode = PIcode.lstrip("PI ")
    acc_url = SEARCHb + urlencode({'accid':"PI "+PIcode})
    return _read_acc_page(acc_url)
    
def get_acc(ID):
    """Returns basic details of an accession, given its numeric ID"""
    return _read_acc_page(ACCb + ID)
    
def _read_acc_page(acc_url):
    acc_page = BeautifulSoup(urlopen(acc_url))
    detail_para = acc_page('p')[0]
    detail_para_s = str(detail_para)
    details = {}
    locn_match = locnre.search(detail_para_s)
    if locn_match:
        details['locn'] = locn_match.group(1)
    details['improvement'] = improvementre.search(detail_para_s).group(1)
    if acc_url.startswith(ACCb):
        details['id'] = acc_url.partition("?")[-1]
    else:
        a = detail_para.findAll("h2")[-1].a
        if a:
            details['id'] = a['href'].partition("?")[-1]			
    return details
    
def get_accs_of_species(sp_id, withUnavailable=True):
    """Given the numeric ID of a species, returns the list of accessions held
    of that species. For each accession, a tuple is returned:
    (numeric id, PI number or equivalent, Accession name)"""
    if withUnavailable:
        listpage = urlopen(TAX_ACCb,"taxno=%s&rownum=0&sort=numb&unavail=off" % sp_id)
    else:
        listpage = urlopen(TAX_ACCb,"taxno=%s&rownum=0&sort=numb" % sp_id)
    listsoup = BeautifulSoup(listpage)
    accs = []
    if not listsoup.ol:
        return []
    for li in listsoup.ol.findAll("li"):
        PInum = li.a.text
        accname = li.text.replace(PInum,"")
        accid = li.a['href'].rpartition("?")[2]
        accs.append((accid, PInum, accname))
    return accs

def _get_distribution(soup):
    try:
        gofrom = soup.find(text="Distributional range").parent.parent
    except AttributeError:    # heading wasn't found
        return {}
    distrib = {}
    while True:
        part = gofrom.findNextSibling("b")
        if not part or part.text not in ("Native:", "Naturalized:", "Cultivated:"):
            break
        countries = set()
        ul = part.findNextSibling("ul")
        for li in ul.findAll("li"):
            # This link is in bold, so it appears in the results if left.
            nse_link = li.find("a", title="Link to NatureServe Explorer")
            if nse_link is not None:
                nse_link.extract()
            countries.update(b.text for b in li.findAll("b")[1:]) # 1st is the continent name
        distrib[part.text.strip(':')] = countries 
        gofrom = ul
    return distrib
    
def _get_species_info(sp_id):
    """Return a dictionary of information for the species with the given
    numeric ID."""
    sp_page = urlopen(TAXON_URL + sp_id)
    soup = BeautifulSoup(sp_page)
    
    info = {'distribution': _get_distribution(soup)}
    
    return info
    
    
def get_obs(ID):
    """Given the numeric ID of an accession, returns a dictionary of the observations made on it."""
    page = BeautifulSoup(urlopen(OBSb + ID))
    obs = defaultdict(list)
    for obtr in page.findAll("tr"):
        if obtr.contents[0].name == "th":
            continue
        obname = obtr.contents[0].a.text
        obs[obname].append((obtr.contents[1].a.text,obtr.contents[1].a['href']))
    return dict(obs)

def _read_sp_page(soup):
    """Read a species page for the name. Returns a GrinTaxon object.
    """
    rank = "sp"
    accname = []
    accauthor = ""
    for chunk in soup.h2.contents[2:]:
        try:
            accname.append(chunk.text)
        except AttributeError:
            chunk = chunk.strip()
            if not chunk:
                continue
            if chunk in ("var.","subsp."):
                accname.append(chunk)
                rank = chunk
            else:
                accauthor = chunk
    accname = " ".join(accname)
    tax = GrinTaxon(accname, accauthor)
    selflink = soup.find("a",title="Jump to images")['href'].partition("#")[0]
    tax.id = selflink.partition("?")[2]
    
    return tax

def fetch(search, progress=None):
    """Fetch taxa matching a search term, e.g. "Restionaceae". Returns a TaxonSet.
    
    The taxa will only have synonymy data, so we only need to make one HTTP
    request.
    """
    by_id = {}
    for synname, accname in _search(search):
        ID = accname.grin_id
        if ID in by_id:
            acctax = by_id[ID]
        else:
            acctax = by_id[ID] = GrinTaxon(accname)
            acctax.id = ID
        
        if synname:
            acctax.othernames.add(synname)
    
    ts = TaxonSet()
    for tax in by_id.values():
        ts.add(tax)
    return ts

class GrinTaxon(Taxon):
    id = ""
    @property
    def url(self):
        return TAXON_URL + self.id
    
    def get_info(self):
        return _get_species_info(self.id)

class GrinTaxaResource(TaxaResource):
    def resolve_name(self, key):
        plainkey = key.plain if hasattr(key, "plain") else key
        names = []
        for synname, accname in _search(plainkey):
            if synname is None:
                names.append((accname, accname))
            elif synname.match(key):
                names.append((synname, accname))
        return names
    
    # GRIN search accepts wildcards
    wildcard_resolve_name = resolve_name
    
    def get_by_accepted_name(self, name):
        t = GrinTaxon(name)
        t.id = name.grin_id
        return t

_instance = GrinTaxaResource()

resolve_name = _instance.resolve_name
select = _instance.select
