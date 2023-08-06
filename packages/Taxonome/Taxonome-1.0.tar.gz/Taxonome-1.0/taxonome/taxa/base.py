#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from .author import Authority
from taxonome.utils.htmlrepr import htmlise

NoneType = type(None)

class UncertainSpeciesError(ValueError):
    pass

# Used by Name.from_string()
oddauthbits = {"sensu","anon.","auct."}
extranamebits = {"ssp.", "subsp.", "var.", "forma", "f."}
unknownnamebits = {"spp.", "sp."}
from .author import auth_noncapitalised
auth_noncapitalised_prefix = ("d'",)
def _isauthbit(txt):
    if txt == 'X':   # Hybrid species marker
        return False
    return txt[0].isupper() or txt.startswith("(") or txt.startswith("&")\
        or txt in oddauthbits or txt in auth_noncapitalised \
        or txt.startswith(auth_noncapitalised_prefix)

minor_ranks = {'subsp.': 'subspecies', 'var.': 'variety', 'f.': 'form'}

name_re = re.compile(r"""(?P<hybr_g>[×xX]\s+)?
(?P<g>[\w\-]+)
(\s+
 (?P<hybr_sp>×\s+?|[xX]\s+)?
 (?P<sp>[\w\-]+)
 (\s+(?P<subsp>[\w\-]+))?
)?""", re.VERBOSE)

subtax_re = re.compile(r"""\b(?P<rank>s(ub)?sp|var|f|forma)\.?\s+(?P<name>[\w\-]+)""")

class Name(object):
    """Store a species name, optionally qualified with an authority.
    
    When comparing two names, the authority of each will be simplified
    to try to overcome differences in format and punctuation. For example::
    
      a = Name("Lablab purpureus", "(L.) Sweet")
      b = Name("Lablab purpureus","Sweet.")
      c = Name("Lablab purpureus", "Sweet. ex. MadeUp.")
      a == b
      a == c
      b == c    # All True
    """
    hybrid = False   # Default
    _parent = None
    sp = None
    
    def __init__(self, name, authority="", rank=None):
        self.authority = Authority(authority)
        
        if isinstance(name, str):
            namematch = name_re.match(name)
            if namematch is None:
                raise ValueError("Could not parse name", name)
            g, self.sp, subsp = namematch.group("g", "sp", "subsp")
            self.g = g.capitalize()
            rankguess = 'species' if self.sp else 'genus'
            
            if self.sp in {'sp', 'spp'}:
                raise UncertainSpeciesError("Invalid sp. or spp. name", name)
        
            hybr_g, hybr_sp = namematch.group("hybr_g", "hybr_sp")
            if hybr_sp:
                self.hybrid = "species"
            elif hybr_g:
                self.hybrid = "genus"
            
            subnames = []
            if subsp and not subtax_re.search(name):
                # Animal style name with subspecies: Gorilla gorilla gorilla
                rankguess = "subspecies"
                subnames.append(("subsp.", subsp))
            for subtax_match in subtax_re.finditer(name):
                # Plant style name with subspecies: Alloteropsis semialata subsp. semialata
                r, n = subtax_match.group("rank", "name")
                r += '.'
                if r == 'ssp.': r = 'subsp.'
                if r == 'forma.': r = 'f.'
                rankguess = minor_ranks[r]
                subnames.append((r, n))
            self.subnames = tuple(subnames)
            
            if self.subnames and not self.sp:
                raise UncertainSpeciesError('Subspecies with species', name)
        else:
            # We were given name parts:
            if len(name) == 1:  # genus
                self.g = name[0]
                rankguess = 'genus'
                self.subnames = ()
            else:
                self.g, self.sp = name[:2]
                rankguess = 'species'
                self.subnames = tuple(tuple(p) for p in name[2:])
                if self.subnames:
                    rankguess = minor_ranks[self.subnames[-1][0]]
        
        self.rank = rank or rankguess
    
    @property
    def plain(self):
        """The unqualified name as a string."""
        parts = [self.g, self.sp] if self.sp else [self.g]
        for sn in self.subnames:
            parts.extend(sn)
        return " ".join(parts)
    
    @property
    def _nameparts(self):
        parts = (self.g, self.sp) if self.sp else (self.g,)
        return parts + self.subnames
    
    @property
    def parent(self):
        """The name one rank up, i.e. species -> genus."""
        if not self._parent:
            self._parent = self._make_parent()
        return self._parent
    
    def _make_parent(self):
        if not self.sp:
            return None     # Can't give a parent for a genus.
        return Name(self._nameparts[:-1])
    
    def __str__(self):
        if self.authority:
            return self.plain + " " + str(self.authority)
        return self.plain
        
    def __repr__(self):
        return "taxonome.Name(\"{0}\", \"{1}\")".format(self.plain, str(self.authority))
    
    _html_template = "<i>{}</i> {}"
    
    def html(self):
        return self._html_template.format(self.plain, str(self.authority))
                
    def __eq__(self, other):
        return (self._nameparts == other._nameparts) \
                and (self.authority == other.authority)
                
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        # ^ is bitwise XOR
        return hash(self._nameparts) ^ hash(self.authority)
    
    @property
    def is_nominal_subsp(self):
        """True if this is a subspecies or variety, and is the nominal form of
        the species, e.g. Vigna unguiculata subsp. unguiculata.
        """
        return self.subnames and (self.subnames[-1][1] == self.sp)
        
    def match(self, other):
        """Compare the name with another qualified name as a Name object, or an
        unqualified name as a string."""
        if isinstance(other, str):
            return self.match_unqualified(other)
        return self == other
        
    def match_unqualified(self, other):
        """Compares the unqualified name with another Name object or a string. E.g.
        
        a = Name("Lablab purpureus", "(L.) Sweet")
        a.match_unqualified("Lablab purpureus")    # True
        """
        if not hasattr(other, "_nameparts"):
            other = Name(other)
        return self._nameparts == other._nameparts
        
    def match_qualified(self, other):
        """Compares the name, including authority, with another Name object or a
        string. If a string is given, it must match the string form of the name
        exactly. With two Name objects, the usual fuzzy logic applies. E.g.
        
        a = Name("Lablab purpureus", "(L.) Sweet")
        a.match_unqualified("Lablab purpureus (L.) Sweet")    # True
        """
        if not hasattr(other, "_nameparts"):
            other = Name(other)
        return self == other
    
    def to_dict(self):
        """Produce a simple dict from this name, suitable for serialising it
        as JSON."""
        d = dict(nameparts=self._nameparts, authority=str(self.authority),)
        if self.hybrid:
            d['hybrid'] = self.hybrid
        return d
    
    @classmethod
    def from_dict(cls, d):
        """Load a Name from a dictionary."""
        nameparts = d['nameparts']
        name = cls(nameparts, d['authority'])
        if 'hybrid' in d:
            name.hybrid = d['hybrid']
        return name
    
    @classmethod
    def from_string(cls, s):
        """Attempts to parse a biological name and authority from a raw string
        of the name, with no other hints to separate them.
        
        An UncertainSpeciesError will be raised if the name is like 'Festuca sp.'
        or 'Festuca spp.'
        """
        namebits = []
        authbits = s.split()
        authbits.reverse()
        namebits.append(authbits.pop())
        
        # Hybrid genera - first word is X/x/×
        if namebits[0] in {'X','x','×'}:
            namebits.append(authbits.pop())
        
        #lowercase first letter --> name
        while authbits and not _isauthbit(authbits[-1]):
            namebits.append(authbits.pop())
        
        # Handles cases where a species is named with its authority, but the name
        # continues into a subspecies or variety.
        parent_authbits = []
        added_subname = False
        while extranamebits.intersection(authbits):
            parent_authbits = []
            while authbits and ((authbits[-1] not in extranamebits) or authbits[-1] =='f.'):
                if authbits[-1] == 'f.' and len(authbits) > 1 and (not _isauthbit(authbits[-2]))\
                                    and authbits[-2] not in extranamebits:
                    break
                parent_authbits.append(authbits.pop())
            
            # f. can be either filius (part of an authority) or forma (part
            # of the name). If the next part is like 'subsp.', put f. in the
            # authority.
            #~ if authbits[-1] == 'f.' and len(authbits) > 1 and \
                    #~ (authbits[-2] in extranamebits):
                #~ parent_authbits.append(authbits.pop())
            
            while authbits and not _isauthbit(authbits[-1]):
                added_subname = True
                namebits.append(authbits.pop())
        
        # Ugh. Sometimes the section above runs erroneously, and the authority
        # gets moved to parent_authbits. Put it back in place.
        if parent_authbits and (not authbits) and (not added_subname):
            authbits = list(reversed(parent_authbits))
            parent_authbits = []
        
        if authbits and authbits[-1].startswith("&"):
            raise UncertainSpeciesError("Name not recognised", s)
        if unknownnamebits.intersection(namebits):
            raise UncertainSpeciesError("Invalid sp. or spp. name", s)
        
        name = cls(" ".join(namebits), " ".join(reversed(authbits)))
        if name.parent and parent_authbits:
            name._parent.authority = Authority(" ".join(parent_authbits))
        return name
    

class Taxon(object):
    url = None
    def __init__(self, name, authority=""):
        if isinstance(name, Name):
            self.name = name
        else:
            self.name = Name(name, authority)
        self.othernames = set()
        self.individuals = []
        self.info = {} #Store other information here
        self.distribution = set() # e.g. For TDWG codes
        
    def __repr__(self):
        return "<Taxon: "+str(self.name)+">"
    
    _html_template = ("<h3>{name}</h3>\n"
                      "{info}\n{individuals}\n{distrib}\n{synonyms}")
    
    def html(self):
        distrib, synonyms, individuals = "", "", ""
        if self.distribution:
            distrib = "<h4>Distribution</h4>{}".format(htmlise(self.distribution))
        if self.othernames:
            synonyms = "<h4>Synonyms</h4>\n{}".format(htmlise([n.html() for n in self.othernames]))
        if self.individuals:
            individuals = "{} individual records".format(len(self.individuals))
        return self._html_template.format(name=self.name.html(), info=htmlise(self.info),
                            distrib=distrib, individuals=individuals, synonyms=synonyms)
        
    def hasname(self, name):
        """Tests if the given name is among the names of this taxon. This
        expects either something like a Name object (with a name attribute) or
        an unqualified name as a string."""
        if isinstance(name, Name):
            if name == self.name:
                return True
            if any(name == othername for othername in self.othernames):
                return True
                
        else:   # Assume the object to compare is like a plain string
            if name == self.name.plain:
                return True
            if any(name == othername.plain for othername in self.othernames):
                return True
                
        return False
    
    def to_dict(self):
        """Produce a simple dict of this taxon's information, suitable for
        serialising as JSON."""
        info = {}
        for k, v in self.info.items():
            if not isinstance(v, (str, int, float, NoneType, bool, dict, list)):
                try:
                    v = str(v)
                except Exception:
                    continue
            info[k] = v
        othernames = [n.to_dict() for n in self.othernames]
        d = dict(name=self.name.to_dict())
        if info:              d['info'] = info
        if othernames:        d['othernames'] = othernames
        if self.url:          d['url'] = self.url
        if self.distribution: d['distribution'] = list(self.distribution)
        if self.individuals:  d['individuals'] = list(self.individuals)
        return d
    
    @classmethod
    def from_dict(cls, d):
        name = Name.from_dict(d['name'])
        t = cls(name, d.get('url'))
        t.info = d.get('info', {})
        t.distribution = set(d.get('distribution', []))
        t.othernames = set(Name.from_dict(n) for n in d.get('othernames', []))
        t.individuals = d.get('individuals', [])
        return t
