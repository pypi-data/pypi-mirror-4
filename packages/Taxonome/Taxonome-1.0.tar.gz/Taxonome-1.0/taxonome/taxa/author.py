import re

from taxonome.config import config
FUZZY_COMPARISON_THRESHOLD = float(config['main']['author-fuzzy-threshold'])
from taxonome.utils import qgram

try:    # unidecode removes accents from letters to simplify comparison
    from unidecode import unidecode
except ImportError: # If we don't have unidecode, do nothing.
    def unidecode(input): return input
    
altspellings = {"Tsevelev":"Tzevelev"}

# f. seems to stand for filius, i.e. son. We currently ignore it.
surname_end_twiddles  = {"f."}
auth_noncapitalised = {"de", "du", "von", "van"}

class Author(object):
    initials = ()
    def __init__(self, author_str):
        *bits, surname = author_str.replace(".",". ").split()
        surname = surname.strip()
        # Special case for Linnaeus
        if surname == 'Linnaeus' and not bits:
            self.surname = 'L.'
            return

        if surname in surname_end_twiddles and bits:        # 'Forst. f.'
            *bits, surname = bits

        if bits and (bits[-1] in auth_noncapitalised):      # 'de Rigeur'
            *bits, prefix = bits
            surname = prefix + " " + surname

        self.initials = tuple(i[0].upper() for i in bits)
        self.surname = altspellings.get(surname, surname)
        
    def fuzzy_cmp(self, other):
        """Attempts a fuzzy logic comparison with another author name. The value
        returned is closer to 1 if they are the same, and closer to zero if they
        are different."""
        pdiff = 0.99
        sn1 = unidecode(self.surname)
        sn2 = unidecode(other.surname)
        if sn1.strip(".") == sn2.strip("."): # Exact match (give or take punctuation)
            pdiff *= 0.05
        elif min(len(sn1.strip(".")), len(sn2.strip("."))) > 1:
            # Try matching an abbreviation against a full name.
            if "." in sn1 and sn2.startswith(sn1.partition(".")[0]):
                pdiff *= 0.1
            if "." in sn2 and sn1.startswith(sn2.partition(".")[0]):
                pdiff *= 0.1
        if pdiff==0.99 and sn1.startswith(sn2[0]):
            # Fuzzy string matching with Q-grams if they start with the same
            # letter.
            score = qgram.compare_strings(sn1.strip("."), sn2.strip("."))
            pdiff *= 1 - (0.9 * score)
        # Bonus points for matching initials
        otherinitials = {unidecode(i) for i in other.initials}
        for i in self.initials:
            if unidecode(i) in otherinitials:
                pdiff *= 0.8
                
        return 1- pdiff
        
    def matches(self, other):
        return self.fuzzy_cmp(other) > FUZZY_COMPARISON_THRESHOLD

    def __eq__(self, other):
        return (self.initials == other.initials) and (self.surname == other.surname)
        
    def __ne__(self, other):
        return not(self.__eq__(other))
        
    def __repr__(self):
        return repr(self.initials) + " " + repr(self.surname)
        
    def __str__(self):
        if self.initials:
            part = " ".join(i+"." for i in self.initials)
            return part + " " + self.surname
        return self.surname
        
    def __hash__(self):
        return hash(self.initials) ^ hash(self.surname) ^ -311416313
        
    def __bool__(self):
        return bool(self.surname)
    
    def to_dict(self):
        return dict(initials=self.initials, surname=self.surname)

def _authors(s):
    return tuple(Author(n.strip()) for n in s.split("&") if n.strip() != "")

def _fuzzy_compare_groups(g1, g2, permatch_weight=1):
    if not(g1) or not(g2):
        return 1
    pdiff = 1.0
    for a1 in g1:
        pdiff *= 1- (permatch_weight * max(a1.fuzzy_cmp(a2) for a2 in g2))
    return pdiff

def _extract(pattern, auth_str, get_group=0):
    match = pattern.search(auth_str)
    if match:
        return match.group(get_group).strip(), pattern.sub("", auth_str)
    return "", auth_str
    
non_auth_re = re.compile(r"\bnon (.+)$")
prefix_re = re.compile(r"^(sensu)? ?(auct\.?)?")
suffix_re = re.compile(r"(, )?(p\.p\.)$")
basauth_re = re.compile(r"^\((.*)\)")
exauth_re = re.compile(r"\bex\.? (.*)")
year_re = re.compile(r",? +(\d{4})")

class Authority(object):
    basauth = ex = non = ()
    year = basyear = ""
    prefix = suffix = ""
    def __init__(self, auth_str):
        auth_str = auth_str.replace(" and "," & ").replace(" et al."," & al.").\
                    replace(" E. al.", " & al.")
        
        self.prefix, auth_str = _extract(prefix_re, auth_str)
        self.suffix, auth_str = _extract(suffix_re, auth_str, get_group=2)
        
        # "Person non Someoneelse"
        non_auth, auth_str = _extract(non_auth_re, auth_str, get_group=1)
        if non_auth:
            self.non = _authors(non_auth)
        auth_str = auth_str.strip(", ").replace(","," &")
        
        # p.p. suffix can be before or after "non Someoneelse".
        if not self.suffix:
            self.suffix, auth_str = _extract(suffix_re, auth_str, get_group=2)
        
        # "(Someone) Newauthority"
        basauth_str, auth_str = _extract(basauth_re, auth_str, get_group=1)
        if basauth_str:
            self.basyear, basauth_str = _extract(year_re, basauth_str, get_group=1)
            self.basauth = _authors(basauth_str.partition(" ex ")[0])
        
        # "Person, 1753"
        self.year, auth_str = _extract(year_re, auth_str, get_group=1)
        
        # "Person ex. Someoneelse"
        ex_str, auth_str =  _extract(exauth_re, auth_str, get_group=1)
        if ex_str:
            self.ex = _authors(ex_str)
            
        if auth_str.strip():
            self.main = _authors(auth_str)
            self._short = self._make_shortform() # For hash()
        else:
            self.main = ()
            self._short = ()
    
    def has_author(self, author):
        if any(a.matches(author) for a in self.non):
            return False
        if any(a.matches(author) for a in self.main + self.ex + self.basauth):
            return True
        return False
    
    def __iter__(self):
        return iter(self.main + self.ex + self.basauth)
    
    def non_match(self, other):
        """Returns True if any 'non X' authors match identified authors in the
        other taxon (either way round)."""
        if any(other.has_author(author) for author in self.non):
            return True
        if any(self.has_author(author) for author in other.non):
            return True
        return False
    
    def fuzzy_cmp(self, other):
        """Compares self with another Authority object, returning a number
        between 0 and 1 indicating the likelihood they match."""
        # Exact match:
        if self.main == other.main and self.ex == other.ex and self.basauth == other.basauth:
            return 1
        
        if self.non_match(other):
            return 0.01
        
        pdiff = 0.99
        pdiff *= _fuzzy_compare_groups(self.main, other.main, 0.9)
        if pdiff > 0.5: # Not matching yet
            if other.ex:
                pdiff *= _fuzzy_compare_groups(self.main, other.ex, 0.85)
            if self.ex:
                pdiff *= _fuzzy_compare_groups(self.ex, other.main, 0.85)
            return 1- pdiff
            
        if not(self.basauth) and not(other.basauth):
            pdiff *= 0.8
        elif self.basauth and other.basauth:
            pdiff *= _fuzzy_compare_groups(self.basauth, other.basauth, 0.5)
                
        if not(self.ex) and not(other.ex):
            pdiff *= 0.8
        elif self.ex and other.ex:
            pdiff *= _fuzzy_compare_groups(self.ex, other.ex, 0.5)
                
        return 1- pdiff
        
    def __eq__(self, other):
        return self.fuzzy_cmp(other) > FUZZY_COMPARISON_THRESHOLD
                
    def __ne__(self, other):
        return not(self.__eq__(other))
        
    def _make_shortform(self):   # Simplify authority.
        return tuple(unidecode(n.surname[:2].strip(".").lower()) for n in self.main)
        
    def __hash__(self):
        return hash(self.__class__) ^ hash(self._short)
                
#    def __hash__(self):
#        h = 1723863662
#        for a in self.main:
#            h ^= hash(a) ^ 359251845
#        if self.basauth:
#            for a in self.basauth:
#                h ^= hash(a) ^ -423436257
#        if self.ex:
#            for a in self.ex:
#                h ^= hash(a) ^ -289918925
#        return h
        
    def __repr__(self):
        return repr({"basauth":self.basauth, "main":self.main, "ex":self.ex,
                        "non": self.non})
        
    def __str__(self):
        basauth = mainauth = exauth = nonauth = None
        if self.basauth:
            basauth = "("+ " & ".join(str(a) for a in self.basauth)
            if self.basyear:
                basauth += ", " + self.basyear
            basauth += ")"
        if self.ex:
            exauth = "ex " + " & ".join(str(a) for a in self.ex)
        if self.non:
            nonauth = "non " + " & ".join(str(a) for a in self.non)
        if self.main:
            mainauth = " & ".join(str(a) for a in self.main)
        if self.year and mainauth:
            mainauth += ","
        bits = [self.prefix, basauth, mainauth, exauth, nonauth, self.year, self.suffix]
        return " ".join(b for b in bits if b)
        
    def __bool__(self):
        return bool(self.main or self.ex or self.basauth or self.non or \
                        self.prefix or self.suffix)
        
        
