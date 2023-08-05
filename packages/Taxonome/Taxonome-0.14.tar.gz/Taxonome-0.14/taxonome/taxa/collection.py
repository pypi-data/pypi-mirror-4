from collections import Counter
from copy import copy
import re

from .base import Name, Taxon
from taxonome.config import config
SP_FUZZY_THRESHOLD = float(config['main']['name-fuzzy-threshold'])
from taxonome.tracker import noop_tracker, prepare_tracker, add_tracker, CacheTracker
from taxonome.taxa.name_selector import TerminalNameSelector, TryAnotherName, AmbiguousMatchesError
from taxonome.utils.qgram import QGramIndex
select_name = TerminalNameSelector()

def _filter_non_auth(possnames, name):
    """Filter out name pairs with 'non X' authority conflicts. Used in .select()
    below."""
    return [(n,an) for n,an in possnames if not n.authority.non_match(name.authority)]

class TaxaResource:
    """A base class for classes holding indexed collections of taxa.
    
    Not designed to be instantiated."""
    _nameselector = select_name
    
    def resolve_name(self, name):
        """Needs to be overridden by subclass. Should return a list of 2-tuples,
        (matching_name, accepted_name), matching the name given. The name given
        may be a string or a Name object."""
        raise NotImplementedError
    
    def get_by_accepted_name(self, name):
        """Needs to be overridden by subclass. Called with a Name object known
        to be an accepted name in this resource. Should return the corresponding
        taxon."""
        raise NotImplementedError
    
    def wildcard_resolve_name(self, name_pattern):
        """May be defined by subclasses to allow wildcard matching of names using
        the common * wildcard, and any extra pattern features webservices etc.
        may support. Returns 2-tuples like resolve_name. name_pattern should be
        a string."""
        raise NotImplementedError
    
    def resolve(self, key, wildcard=False):
        """Return a set of taxa matching a name. The name can be an unqualified
        name as a string, a qualified (with authority) Name object, or a Taxon
        object (which is treated as a shorthand for passing its .name property).
        
        If wildcard is True, attempt to match names to a string using the *
        wildcard. This may raise NotImplementedError if the data source
        doesn't support it.
        """
        nameresolver = self.wildcard_resolve_name if wildcard \
                            else self.resolve_name
        return {self.get_by_accepted_name(an) for n, an in nameresolver(key)}
    
    def select(self, name, strict_authority=False, upgrade_subsp="nominal",
                    fuzzy=True, prefer_accepted='noauth', nameselector=None,
                                                        tracker=noop_tracker):
        """Select a taxon by name. If there is more than one match, an
        interactive prompt will ask the user to choose.
        
        Parameters:
            name : Name or str
              The name (qualified or unqualified) to look for
            strict_authority : bool
              If True, names will be disregarded if their authority does not match
              that given (with a qualified name). If False, the authority will be
              used to distinguish homonyms, but will be overlooked if none of the
              names found have matching authority.
            upgrade_subsp : str
              If 'none', subspecies and varieties will only be matched to identical
              names. Otherwise, subspecies and varieties may be matched to their
              parent species if no exact match is found. 'nominal' will cause only
              nominal subspecies/varieties to be upgraded (e.g. *Vicia faba* var. *faba*
              --> *Vicia faba*), while 'all' allows any subspecies/variety to upgrade.
            fuzzy : bool
              If True, fuzzy matching will be used with the specified name where
              possible.
            prefer_accepted : str
              'all' will resolve ambiguities by choosing the accepted name where
              possible. 'noauth' does this only where the given name doesn't have an
              authority. 'none' will always ask the user.
            nameselector : NameSelector instance
              Defines how to choose between alternative matches. See
              :class:`taxonome.taxa.name_selector.NameSelector`. The default
              name selector is the _nameselector attribute on this collection.
            tracker :
              A tracker object - see details in :mod:`taxonome.tracker`.
        
        Returns:
            A taxon object if a match is found in this dataset. Raises KeyError
            if no match is found.
        """
        nameselector = nameselector or self._nameselector
        possnames = self.resolve_name(name)
        
        # Overlook authority?
        if not possnames and not strict_authority and hasattr(name, "plain"):
            tracker.name_event(name, "authority overlooked")
            possnames = _filter_non_auth(self.resolve_name(name.plain), name)
        
        # Upgrade minor taxa?
        if not possnames and isinstance(name, Name) and \
                name.subnames and (upgrade_subsp=="all"\
                or (upgrade_subsp=="nominal" and name.is_nominal_subsp)):
            pn = name.parent
            tracker.name_transform(name, pn, "upgraded subspecies")
            possnames = self.resolve_name(pn)
            if (not possnames) and (not strict_authority):
                possnames = _filter_non_auth(self.resolve_name(pn.plain), pn)
        
        # Fuzzy name matching?
        if not possnames and fuzzy:
            try:
                possnames = self.fuzzy_resolve_name(name, tracker=tracker)
            except (AttributeError, NotImplementedError, KeyError):
                pass
            else:
                if not possnames and not strict_authority and hasattr(name, "plain"):
                    possnames = _filter_non_auth(self.fuzzy_resolve_name(name.plain), name)
        
        # Pick accepted name by default?
        if prefer_accepted=='all' or (prefer_accepted=='noauth' and \
                                (isinstance(name, str) or not name.authority)):
            acc_count = 0
            for n, an in possnames:
                if n==an:
                    acc_count += 1
                    an1 = an
            if acc_count == 1:
                tracker.name_transform(name, an1, "preferring accepted name")
                return self.get_by_accepted_name(an1)
        
        try:
            n, an = nameselector(possnames, name, tracker=tracker)
            return self.get_by_accepted_name(an)
        except TryAnotherName as e:
            return self.select(e.newname, strict_authority=strict_authority,
                                upgrade_subsp=upgrade_subsp, fuzzy=fuzzy,
                                tracker=tracker)

class TaxonSet(TaxaResource):
    """This allows storing a collection of taxa, along with synonymy
    and easy lookup by name (whether or not that is qualified with
    an authority.
    
    Looking up synonyms that have been added returns the taxon, but
    looping through it will ignore synonyms.
    
    Usage example::
    
      mygenus = TaxonSet()
      mygenus.add(Taxon("Lablab purpureus","(L.) Sweet"))
      mygenus.add_synonym(Name("Dolichos lablab", "L."),\\
                        Name("Lablab purpureus","(L.) Sweet") )
      mygenus.add_synonym(Name("Vigna aristata", "Piper"),\\
                        Name("Lablab purpureus","(L.) Sweet") )
                        
      # Unqualified name:
      "Lablab purpureus" in mygenus       # -> True
      "Dolichos lablab" in mygenus        # -> True
      "Lablab vulgaris" in mygenus        # -> False
      "Dolichos lablab L." in mygenus     # -> False (Don't add authority)
      mygenus.resolve("Lablab purpureus") # -> List of possible Taxon() objects
      mygenus.resolve("Dolichos lablab")  #    (will usually only have one item)
      mygenus["Lablab purpureus"]         # -> A Taxon() object, so long as there
                                          #    is exactly one match.
    
      # Qualified name:
      Name("Lablab purpureus","(L.) Sweet") in mygenus # -> True
      Name("Lablab purpureus","Sweet") in mygenus      # -> True
      mygenus[Name("Dolichos lablab","L.")]  # Returns a Taxon() object
      mygenus[Taxon("Dolichos lablab","L.")] # Same - Only uses the taxon's
                                             # accepted name
    """
    type_err_msg = "Don't know how to look for type {0}"
    def __init__(self):
        self.names = {}
        self.taxa = {}
        self.qgram_index = QGramIndex()
        
    def add(self, taxon):
        """Add a taxon. This will be indexed by its name, and any synonyms
        attached to the taxon object.
        
        Adding a taxon with the same name as an existing taxon will replace it.
        An accepted name will replace the same qualified name as a synonym for
        another taxon, although the synonym will still be in the .othernames
        property of the relevant taxon.
        """
        if not taxon.name in self:
            self._add_qname(taxon.name)
        elif self.select(taxon.name).name != taxon.name:
            self._del_qname(taxon.name)
            self._add_qname(taxon.name)
        #if taxon.name in self:
            #if self[taxon.name].name == taxon.name:
                #raise KeyError("Taxon already added")
            #else:
                #self._del_qname(taxon.name)
        self.taxa[repr(taxon.name)] = taxon
        #self._add_qname(taxon.name)
        for synonym in taxon.othernames:
            if not synonym in self:
                self._add_qname(synonym, taxon.name)
        
    def _add_qname(self, qname, acceptedname=None):
        """Add a qualified name to the index. To add a synonym, specify an
        acceptedname to which it maps. The acceptedname should refer to a taxon
        which is in the set.
        """
        if not acceptedname:
            acceptedname = qname
        if not qname.plain in self.names:
            self.names[qname.plain] = []
            self.qgram_index.add(qname.plain)
        self.names[qname.plain].append((qname, acceptedname))
        
    def _del_qname(self, qname):
        """Remove a qualified name from the index. Taxa with no remaining
        names in the index will still take up space, but cannot easily be
        accessed, so you should ensure that at least one name remains for each.
        
        Returns the accepted name to which it mapped.
        """
        if not qname.plain in self.names:
            raise KeyError
        for namematch in self.names[qname.plain]:
            if namematch[0] == qname:
                self.names[qname.plain].remove(namematch)
                if not self.names[qname.plain]:
                    del self.names[qname.plain]
                    self.qgram_index.discard(qname.plain)
                return namematch[1]
        raise KeyError(qname)
    
    def __contains__(self, taxon):
        if isinstance(taxon, str):
            return taxon in self.names
        elif isinstance(taxon, Name):   # Qualified name
            if taxon.plain in self.names:
                return any([taxon == n for n,t in self.names[taxon.plain] ])
        elif isinstance(taxon, Taxon):
            return self.__contains__(taxon.name) # Redo using name
        else:
            raise TypeError(self.type_err_msg.format(type(taxon)))
    
    def resolve_name(self, key):
        """Return a list of 2-tuples, (name, accepted_name), matching the given
        name. The name can be an unqualified name as a string or a qualified
        (with authority) Name object.
        """
        if isinstance(key, Name):  # Qualified name
            return [(n, an) for n, an in self.names.get(key.plain, []) if key == n]
        # Unqualified name as string
        return self.names.get(key, [])
    
    def fuzzy_resolve_name(self, key, tracker=noop_tracker):
        """Return a list of 2-tuples as for :meth:`resolve_name`, but including
        fuzzy matches to the specified name.
        """
        rawkey = key.plain if isinstance(key, Name) else key
        allnames = []
        similarname, score = self.qgram_index.best_match(rawkey, SP_FUZZY_THRESHOLD)
        allnames.extend(self.names[similarname])
        tracker.name_transform(key, similarname, "fuzzy match", score=score)
        if isinstance(key, Name):
            return [(n, an) for n, an in allnames if n.authority==key.authority]
        return allnames
    
    def wildcard_resolve_name(self, name_pattern):
        """Return a list of 2-tuples as for :meth:`resolve_name`, but matching
        a wildcard pattern in the Unix shell style. See the docs for the fnmatch
        module for more details."""
        import fnmatch
        pattern_re = re.compile(fnmatch.translate(name_pattern))
        allnames = []
        for plainname in self.names:
            if pattern_re.match(plainname):
                allnames.extend(self.names[plainname])
        return allnames
    
    def get_by_accepted_name(self, key):
        """Return the taxon identified by an accepted name."""
        return self.taxa[repr(key)]
    
    def __getitem__(self, key):
        """The simplest retrieval option. Will return a single match, or raise
        an error if there is more than one match."""
        matches = self.resolve(key)
        if len(matches) == 1:
            return matches.pop()
        elif len(matches) < 1:
            raise KeyError("No matching taxa found for '%s'" % key)
        else:
            raise KeyError("Multiple matches found for '%s'" % key)
    
    def __setitem__(self, key, value):
        if key in self:
            key = self[key].name
            self.taxa[repr(key)] = value
        else:
            self.add(value)
            if key != value.name:
                self._add_qname(key, value.name)

    def __delitem__(self, key):
        if isinstance(key, str):
            if len(self.names[key]) > 1:
                raise KeyError("More than one match for name")
            name = self.names[key][0]
            del self.taxa[repr(name[1])]
            del self.names[key]
        elif isinstance(key, Name):
            # Qualified name
            accname = self._del_qname(key)
            if accname != key:
                self._del_qname(accname)
            for synonym in self.taxa[repr(accname)].othernames:
                try:
                    synonym_maps_to = self._del_qname(synonym)
                    if synonym_maps_to != accname:
                        # Oops, we removed a name that had been overwritten. Put it back.
                        self._add_qname(synonym, synonym_maps_to)
                except KeyError:
                    pass
            del self.taxa[repr(accname)]

        elif isinstance(key, Taxon):
            self.__delitem__(key.name)
        else:
            raise TypeError(self.type_err_msg.format(type(key)) )
        
    def __iter__(self):
        return iter(self.taxa.values())
            
    def __len__(self):
        return len(self.taxa)
    
    def __repr__(self):
        return "<{0}: {1} taxa with {2} names>".format(self.__class__.__name__,\
                        len(self.taxa), len(self.names))

def combine_dicts(d1, d2):
    """Default function for combining info dicts. It gives the union of two
    dicts, while preserving multiple values with matching keys. If the
    corresponding values are both dicts, they are likewise combined; otherwise
    values are placed in a list."""
    res = copy(d1)
    for k, v in d2.items():
        if k not in res:
            res[k] = v
        elif isinstance(res[k], dict) and isinstance(v, dict):
            res[k] = combine_dicts(res[k], v)
        elif isinstance(res[k], set) and isinstance(v, set):
            res[k].update(v)
        elif isinstance(res[k], list):
            if isinstance(v, list):
                if v != res[k]:
                    res[k].extend(v)
            else:
                res[k].append(v)
        else:
            res[k] = [res[k], v]
    return res

def build_matched_taxonset(streaming_match_taxa, merge_info=combine_dicts):
    results = TaxonSet()
    
    for taxon, t2 in streaming_match_taxa:
        try:
            restaxon = results.select(t2.name)
        except KeyError:
            taxon = copy(taxon)
            taxon.name = t2.name
            taxon.othernames = set()
            results.add(taxon)
        else:
            restaxon.info = merge_info(restaxon.info, taxon.info)
            restaxon.distribution.update(taxon.distribution)
            restaxon.individuals.extend(taxon.individuals)
    
    return results

def match_taxa(taxa, target, merge_info=combine_dicts,
               tracker=noop_tracker, **kwargs):
    """Match one set of taxa against another by name.
    
    Parameters:
        taxa : iterable
          The taxa to be matched
        target : TaxonSet
          The taxa whose names we want to match to.
        merge_info : function
          A function which takes two dictionaries as arguments, and returns a
          dictionary. Called with the .info parameters of multiple taxa which are
          mapped to the same name.
        tracker :
          A tracker object (see :mod:`taxonome.tracker`) or tuple of trackers to
          record the name matching process.
        strict_authority, upgrade_subsp, fuzzy, prefer_accepted, nameselector :
          Control the matching procedure; see :meth:`TaxonSet.select` for details.
    
    Returns:
        A TaxonSet, containing copies of the input taxa, with the .name
        attribute replaced with the name of the corresponding taxon from target_ts,
        .othernames cleared, and .info combined with taxa mapping to the same name.
        
        Taxa which fail to match send a 'no match' event to the tracker.
    """
    matching = streaming_match_taxa(taxa, target, tracker=tracker, **kwargs)
    return build_matched_taxonset(matching, merge_info=merge_info)

def streaming_match_taxa(taxa, target, tracker=None, auto_cache=True, **kwargs):
    """Similar to match_taxa, but suitable for handling large amounts of data.
    
    This is a generator, yielding pairs of (input_taxon, matched_taxon). The same
    matched taxon may be yielded more than once.
    
    By default, unless the source is a TaxaResource, a cache of names matched
    will be used to speed the process up. This is useful for matching big
    datasets which may have many repeats of each name. If it causes problems
    (e.g. with memory use), pass auto_cache=False to disable it.
    """
    tracker = prepare_tracker(tracker)
    if isinstance(taxa, TaxaResource) or not auto_cache:
        caching = False
    else:
        caching = True
        cache = CacheTracker()
        tracker = add_tracker(tracker, cache)
    
    for taxon in taxa:
        tracker.start_taxon(taxon)
        
        if caching:
            # Look up name in cache
            try:
                accname = cache.retrieve(taxon.name, tracker)
            except KeyError:
                pass
            else:
                if accname:
                    t2 = target.get_by_accepted_name(accname)
                    yield taxon, t2
                tracker.reset()
                continue
        
        # Look in the target dataset
        try:
            t2 = target.select(taxon.name, tracker=tracker, **kwargs)
        except AmbiguousMatchesError:
            tracker.name_event(taxon.name, "multiple matches")
        except KeyError:
            tracker.name_event(taxon.name, "no match")
        else:
            yield taxon, t2

        tracker.reset()

def run_match_taxa(taxa, target, **kwargs):
    """Run the matching process without collecting the results - suitable
    for use with big datasets.
    """
    for taxonpair in streaming_match_taxa(taxa, target, **kwargs):
        pass
