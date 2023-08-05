from pyparsing import (Word, alphas, alphas8bit, Optional, Regex, Combine, 
               MatchFirst, ZeroOrMore, delimitedList, Literal, FollowedBy,
               Group, ParseResults, ParseException)
latinchars = alphas + alphas8bit
upper = "".join(c for c in latinchars if c.isupper())
lower = "".join(c for c in latinchars if c.islower())

# Species name components
genus = Regex("[A-Z][\w\-]*").setResultsName("genus")
sp_epithet = Word(latinchars + "-").setResultsName("sp")
species = genus + sp_epithet
subtax_rank = MatchFirst([Literal(s) for s in ("ssp", "subsp", "var", "f", "forma")]).setResultsName("subtax_rank")
subtax_rank_abbr = Combine(subtax_rank + Optional("."))
subtax_epithet = Word(latinchars + "-").setResultsName("subtax")
subtax = Group(subtax_rank_abbr + subtax_epithet)

# Author components
authsep = MatchFirst([Literal(s) for s in (",","&","and")]).suppress()
initial_letter = Word(upper, max=1).setResultsName("initial")
initials = ZeroOrMore(Combine(initial_letter + ".") + FollowedBy(Word(upper, latinchars)))
surname = Combine(Word(upper, latinchars) + Optional(".")).setResultsName("surname")
filius = Optional("f." + FollowedBy(authsep | subtax_rank)).setResultsName("filius")
author = Group(initials + surname + filius)

authorgroup = author + ZeroOrMore(authsep + author)

# Authority components
pp = Optional(Optional(",") + "p.p.")
nonauth = Optional("non" + authorgroup.setResultsName("nonauth"))
basauth = Optional("("+authorgroup.setResultsName("basauth")+")")
exauth = Optional("ex." + authorgroup.setResultsName("exauth"))
year = Optional(Optional(",") + Regex(r"\d{4}").setResultsName("year"))
mainauth = authorgroup.setResultsName("mainauth")
authority = Group(basauth + mainauth + exauth + nonauth).setResultsName("authority")

name_with_authority = species + Optional(Optional(authority) + subtax) + authority
name_without_authority = species + ZeroOrMore(subtax)

def parse_name(s, with_authority=True):
    if with_authority:
        try:
            res = name_with_authority.parseString(s)
        except ParseException:
            raise ValueError(s)
        yield res.genus, None
        if res[2].getName() == 'authority':
            yield res.sp, res[2]
            res = res[3:]
        else:
            yield res.sp, None
            res = res[2:]
        while res:
            subtax, auth, *res = res
            yield subtax, auth
    
    else: # No authority
        res = name_without_authority.parseString(s)
        for part in res:
            yield part, None

# Stashed here - this was attached to taxonome.taxa.base.Name

@classmethod
def from_string_new(cls, s):
    (genus,_), (sp, auth), *subpairs = parse_name(s)
    auths = [auth]
    subnames = []
    for namepart, auth in subpairs:
        #if namepart == 'ssp.': namepart = 'subsp.'
        subnames.append(namepart)
        auths.append(auth)
    name = cls([genus, sp] + subnames,"")# auths[-1])
    if subnames and len(auths) > 1 and auths[-2]:
        name.parent.authority = auths[-2]
    return name
    
