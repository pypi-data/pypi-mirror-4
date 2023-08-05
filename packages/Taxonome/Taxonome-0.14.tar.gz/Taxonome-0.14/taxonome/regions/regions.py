# -*- coding: utf-8 -*-
"""Handle geographic regions, which can be nested within one another.

This automatically loads the TDWG regions, together with indexes of
names and ISO country codes (see tdwg_load.py for details of the data
sources). They are accessible via the module variables ``tdwg``, ``names`` and ``iso``,
as well as specific TDWG levels in ``tdwg_levels[1]`` - ``tdwg_levels[4]``.
The variable ``index`` combines these three sets of names for convenience.

Example usage::

  regions.tdwg["IND"]     # TDWG level 3 region (most of India)
  regions.names["India"]  # The country
  i = regions.ISO["IN"]   # The country (ISO code)
  regions.index["India"]  # .index includes all codes and names
  print(i.children)       # Show immediate subregions

  for subregion in i:     # Gets all subregions, down to the smallest
      print subregion.name

  ## Test if a region is in a larger region:
  "NET" in regions.names["Europe"]  # True: The Netherlands is in Europe
  "NET" in regions.tdwg["14"]       # False (14 is Eastern Europe, TDWG level 2)

  for region in regions.tdwg_levels[1]:
      print(region.name)     # tdwg_levels has a set of the regions at each level

You can also use the add to the hierarchy, or create your own (e.g. for a much
smaller area). See the :class:`Map` class.
"""
import logging
try:
    from unidecode import unidecode
except ImportError:
    def unidecode(input): return input

from taxonome.config import config
from taxonome.utils.digraph import DiGraph
                    
class Map(DiGraph):
    subregions = DiGraph.successors
    is_subregion = DiGraph.is_successor
    
    superregions = DiGraph.predecessors
    immediate_superregions = DiGraph.immediate_predecessors
    
    def add_region(self, region, parent=None):
        self.nodes.add(region)
        if parent:
            self.edges.add(parent, region)
            
    def includes(self, region, targets):
        """Test whether a region in the map includes any of a collection of
        regions, such as an organism's distribution. E.g.
        
        africa = tdwg["2"]
        world.includes(africa, elephant.distribution)
        
        The return value is the set of matching subregions: this can be treated
        as a boolean, since it is empty if there is no overlap.
        """
        subregions = set(self.subregions(region)) | {region}
        return subregions.intersection(targets)
        
    def immediate_subregions(self, region):
        """Return only the immediate child regions of the given region."""
        return set(self.outgoing(region))


class CombinedIndex(list):
    """A sequence of dictionaries: will retrieve an item
    from the first one it is found in.
    """
    def __contains__(self, key):
        return any(key in index for index in self)
    
    def __getitem__(self, key):
        for index in self:
            if key in index:
                return index[key]
        raise KeyError(key)

def _find_tdwg_level(region):
    for n, contents in enumerate(tdwg_levels):
        if region in contents:
            return n

def find_tdwg(name, level=3, index=None):
    """Find the set of TDWG regions at a given level corresponding to a given
    name.
    
    Parameters:
      name : str
        The name or code to search for.
      level : int
        The target TDWG level (1-4). Defaults to 3.
      index :
        The index to use for looking up names/codes. Defaults to names. Others
        available in this module are: tdwg, ISO (two-letter ISO country codes, e.g
        NL) and combinedindex (which checks tdwg, names and ISO).
    
    Returns:
      A set of TDWG codes; either all the regions contained within the specified
      region, or the single region which contains or matches the specified region.
    
    Raises: KeyError if the name/code is not found.
    """
    if not world: load_tdwg()
    
    if index is None:
        index = names
    
    r = index[name]
    rlevel = _find_tdwg_level(r)
    if rlevel == level:
        return {r[1]}
    
    elif rlevel is None:   # Extra regions without a TDWG code.
        out = set()
        for n,t in world.immediate_subregions(r):
            out.update(find_tdwg(t, level=level, index=tdwg))
        if not out:
            for n,t in world.immediate_superregions(r):
                out.update(find_tdwg(t, level=level, index=tdwg))
        return out
    
    elif rlevel < level:  # Larger regions
        return {sr[1] for sr in world.subregions(r) if sr in tdwg_levels[level]}
    
    # Smaller regions
    return {gr[1] for gr in world.superregions(r) if gr in tdwg_levels[level]}
    
def tdwgise(namegroup, level=3, index=None):
    """Transform an iterable of names to a set of TDWG regions at a particular
    level.
    
    Note that, if the input specifies a larger region than the required tdwg
    level, the output will include all subregions of that region. This may lead
    to some inaccuracies - e.g. a species recorded as occurring in 'Africa'
    will appear to occur all over Africa.
    
    Parameters: The same as :func:`find_tdwg`, except that the first parameter
    is an iterable of names.
    
    Returns:
      A pair of sets: the matching TDWG codes at the specified level, and any
      names which could not be matched.
    """
    out, notfound = set(), set()
    for name in namegroup:
        try:
            t = find_tdwg(name, level, index)
        except KeyError:
            notfound.add(name)
        else:
            out.update(t)
    return out, notfound
    
def load_tdwg():
    """Call this function to load the TDWG set of world regions.
    
    If the 'load-tdwg-regions' config value is True, this will be called when
    the module is imported.
    """
    global world, names, tdwg, ISO, combinedindex, tdwg_levels
    from . import tdwg_data
    world = Map()
    names = {}
    tdwg = {}
    ISO = {}
    combinedindex = CombinedIndex([tdwg, names, ISO])
    
    for code, name, isocode, parent, notes in tdwg_data.data:
        newregion = (name, code)
        if parent == "!!WORLD":
            parent = None
        else:
            parent = tdwg[parent]
        world.add_region(newregion, parent)
        
        # Add to indices
        tdwg[code] = newregion
        if name not in names:
            names[name] = newregion
            # Strip off accents for more reliable matching
            names[unidecode(name)] = newregion
        if isocode and isocode not in ISO:
            ISO[isocode] = newregion
        
    for name, parent, children in tdwg_data.extra_countries:
        newregion = (name, None)
        if parent:
            parent = tdwg[parent]
        world.add_region(newregion, parent)
            
        for childcode in children:
            child = tdwg[childcode]
            world.edges.add(newregion, child)
            if parent:   # Cut any direct links from the old parent to children
                world.edges.discard(parent, child)
        names[name] = newregion
        
    for name, origname in tdwg_data.extra_names:
        names[name] = names[origname]
    for name, tcode in tdwg_data.extra_names_tdwg:
        names[name] = tdwg[tcode]
    for code, name in tdwg_data.extra_ISO.items():
        ISO[code] = names[name]
        
    tdwg_levels = [set()]
    for levelcodes in tdwg_data.tdwg_by_level[1:]:
        tdwg_levels.append({tdwg[code] for code in levelcodes})
        
world = None   # Test for this to see if TDWG data is loaded.
if config.getboolean('main', 'load-tdwg-regions'):
    load_tdwg()
