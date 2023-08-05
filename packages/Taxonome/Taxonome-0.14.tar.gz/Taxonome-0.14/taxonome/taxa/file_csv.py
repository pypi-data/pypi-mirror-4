import csv
import os.path
import warnings
from taxonome import TaxonSet, Name, Taxon
from taxonome.tracker import prepare_tracker
from .base import UncertainSpeciesError

def _make_name(d, rawname, authfield):
    if authfield is True:
        return Name.from_string(rawname)
    
    if rawname.strip().endswith((" sp.", " spp.")):
        raise UncertainSpeciesError(rawname)
    if authfield:
        return Name(rawname, d.pop(authfield))
    else:
        return Name(rawname)


def iter_taxa(filehandle, namefield="Name", authfield="Author", progress=None,
                                                tracker=None, *args, **kwargs):
    """Load taxa iteratively from a CSV file. It expects fields for name and author
    to be present, describing the taxa to use. Other fields will be stored as a
    dictionary in each taxon's .info property.
    
    If authfield is set to True, it will attempt to parse names in the namefield
    to names and authorities. If authfield is None, no authfield will be used.
    
    progress is an object used by the GUI to track progress. It is called
    periodically with the number of bytes read.
    
    Any other arguments are passed to the csv.DictReader object--see Python's
    documentation.
    """
    tracker = prepare_tracker(tracker)
    csvin = csv.DictReader(filehandle, *args, **kwargs)
    i = 0
    for line in csvin:
        rawname = line.pop(namefield)    # Raise KeyError if the field isn't there
        try:
            newtaxon = Taxon(_make_name(line, rawname, authfield))
        except Exception as e:
            warnings.warn("Failed to read taxon - error was: %s" % e)
            tracker.unreadable_name(rawname, e)
            tracker.reset()
            continue
        newtaxon.info = line
        yield newtaxon
        
        i += 1
        if progress and (i % 20 == 0):
            progress(filehandle.buffer.tell())

def load_taxa(filehandle, namefield="Name", authfield="Author", *args, **kwargs):
    """Load a TaxonSet from a CSV file. It expects fields for name and author
    to be present, describing the taxa to use. Other fields will be stored as a
    dictionary in each taxon's .info property.
    
    Any other arguments are passed to the csv.DictReader object--see Python's
    documentation.
    """
    taxa = TaxonSet()
    for tax in iter_taxa(filehandle, namefield, authfield, *args, **kwargs):
        taxa.add(tax)
    return taxa

def save_taxa(filehandle, taxonset, namefield="Name", authfield="Author", info_fields = [],
                write_distribution=False, *args, **kwargs):
    """Writes a TaxonSet to a CSV file. Accepted name and author will be
    recorded, along with any fields specified from .info.
    
    If info_fields is True, all fields will be saved. If write_distribution is
    None, distribution will be saved if any data is present. Both of these
    options need a collection of taxa which can be iterated over more than once.
    """
    if info_fields is True:
        info_fields = set()
        for t in taxonset:
            info_fields.update(t.info)
        info_fields = list(info_fields)
    fields = [namefield,authfield] + info_fields
    if (write_distribution is None) and any(t.distribution for t in taxonset):
        fields.append("Distribution")
        write_distribution = True
    csvout = csv.DictWriter(filehandle, fields, extrasaction='ignore', *args, **kwargs)
    csvout.writeheader()
    for ataxon in taxonset:
        towrite = {namefield:ataxon.name.plain, authfield:ataxon.name.authority}
        towrite.update(ataxon.info)
        towrite['Distribution'] = ataxon.distribution
        csvout.writerow(towrite)

def iter_individuals(filehandle, namefield="Name", authfield="Author", progress=None, **kwargs):
    """Read individuals from a CSV file - i.e. the same name may appear on more
    than one row.
    
    Yields pairs of name, info
    """
    csvin = csv.DictReader(filehandle, **kwargs)
    i = 0
    for line in csvin:
        rawname = line.pop(namefield)    # Raise KeyError if the field isn't there
        try:
            name = _make_name(line, rawname, authfield)
        except Exception as e:
            warnings.warn("Failed to read record - error was: %s" % e)
            continue
        yield name, line
        
        # Progress tracking
        i += 1
        if progress and (i % 20 == 0):
            progress(filehandle.buffer.tell())

def load_individuals(filehandle, namefield="Name", authfield="Author", **kwargs):
    """Load a TaxonSet representing the individuals in the CSV file. Each name
    may appear on several rows.
    """
    taxa = TaxonSet()
    for name, info in iter_individuals(filehandle, namefield, authfield, **kwargs):
        try:
            taxon = taxa[name]
        except KeyError:
            taxon = Taxon(name)
            taxa.add(taxon)
        taxon.individuals.append(info)
    return taxa

def save_individuals(filehandle, taxonset, namefield="Name", authfield="Author", **kwargs):
    """Save records of individuals (e.g. specimens, sightings) from a TaxonSet.
    
    This requires a collection which can be iterated more than once.
    """
    info_fields = set()
    for t in taxonset:
        for ind in t.individuals:
            info_fields.update(ind)
    fields = [namefield, authfield] + list(info_fields)
    
    csvout = csv.DictWriter(filehandle, fields, extrasaction='ignore', **kwargs)
    csvout.writeheader()
    
    for t in taxonset:
        name_fields = {namefield: t.name.plain, authfield:str(t.name.authority)}
        for ind in t.individuals:
            row = dict(ind)
            row.update(name_fields)
            csvout.writerow(row)

def load_synonyms(filehandle, synnamefield="Name", synauthfield="Author",\
                    accnamefield="Accname", accauthfield="Accauthor",\
                    get_info=True, *args, **kwargs):
    """Loads a set of synonyms from a CSV file. Returns a TaxonSet containing
    the taxa.
    
    *field parameters work like load_taxa.
    
    If get_info is True (the default), extra info from the lines with the
    accepted names is attached to the taxa.
    """
    holding = {}
    for synname, accname, info in iter_synonyms(filehandle, synnamefield, synauthfield,
                                accnamefield, accauthfield, *args, **kwargs):
        #print(repr(synname), repr(accname))
        if accname in holding:
            taxon = holding[accname]
        else:
            holding[accname] = taxon = Taxon(accname)
        
        # Add info from the line.
        if accname == synname:
            if get_info:
                taxon.info = info
        else:
            # Add synonym
            taxon.othernames.add(synname)
    
    taxonset = TaxonSet()
    for tax in holding.values():
        taxonset.add(tax)
    return taxonset
    
def iter_synonyms(filehandle, synnamefield="Name", synauthfield="Author",\
                    accnamefield="Accname", accauthfield="Accauthor",\
                    progress=None, *args, **kwargs):
    """Loads a set of synonyms from a CSV file. Yields triples of (synonym,
    accepted name, other fields dict).
    
    *field parameters work like load_taxa.
    """
    csvin = csv.DictReader(filehandle, *args, **kwargs)
    i = 0
    for line in csvin:
        rawaccname = line.pop(accnamefield)
        try:
            accname = _make_name(line, rawaccname, accauthfield)
        except Exception as e:
            warnings.warn("Failed to read accepted name - error was: %r" % e)
            continue
        rawsynname = line.pop(synnamefield)
        try:
            synname = _make_name(line, rawsynname, synauthfield)
        except Exception as e:
            warnings.warn("Failed to read synonym - error was: %r" % e)
            continue
        yield (synname, accname, line)
        
        i += 1
        if progress and (i % 20 == 0):
            progress(filehandle.buffer.tell())

def save_synonyms(filehandle, taxonset, snamefield="Name", sauthfield="Author",\
                    accnamefield="Accname", accauthfield="Accauthor",\
                    include_accepted_names=True, *args, **kwargs):
    """Writes a set of synonyms to a CSV file. (This only uses the synonyms in
    the .othernames property of each Taxon, not the names in the TaxonSet's
    index."""
    fields = [snamefield, sauthfield, accnamefield, accauthfield]
    csvout = csv.writer(filehandle, *args, **kwargs)
    csvout.writerow(fields)
    for taxon in taxonset:
        if include_accepted_names:
            csvout.writerow([taxon.name.plain, taxon.name.authority]*2)
        for synname in taxon.othernames:
            csvout.writerow([synname.plain, synname.authority,\
                        taxon.name.plain, taxon.name.authority])
