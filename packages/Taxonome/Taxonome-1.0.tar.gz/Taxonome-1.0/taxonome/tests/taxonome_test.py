#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import taxonome
from taxonome.taxa import file_csv
import unittest
from os import remove

Name = taxonome.Name    

class ElephantTest(unittest.TestCase):
    """Tests both taxa and distribution."""
    def setUp(self):
        self.ts = taxonome.TaxonSet()
        a_elephant = taxonome.Taxon("Elephas maximus","L.")
        name_ix = taxonome.regions.names
        a_elephant.distribution = {name_ix[n] for n in \
                                    ["India", "Nepal","Thailand","Bhutan"]}
        self.ts.add(a_elephant)
        
        forest_elephant = taxonome.Taxon(Name("Loxodonta cyclotis","Matchie"))
        forest_elephant.distribution = {name_ix["Congo"]}
        self.ts.add(forest_elephant)
        
    def testTS(self):
        assert len(self.ts) == 2
        assert Name("Elephas maximus","L") in self.ts
        assert self.ts["Elephas maximus"].name == Name("Elephas maximus","L")
        assert "Loxodonta cyclotis" in self.ts
    
    def testDistrib(self):
        a_elephant = self.ts["Elephas maximus"]
        world = taxonome.regions.world
        trop_asia = taxonome.regions.tdwg["4"]     # 4 is Tropical Asia, TDWG L1
        africa = taxonome.regions.tdwg["2"]        # 2 is Africa, TDWG L1
        assert africa == taxonome.regions.names["Africa"]
        assert world.includes(trop_asia, a_elephant.distribution)
        assert not world.includes(africa, a_elephant.distribution)
        
        forest_elephant = self.ts[Name("Loxodonta cyclotis", "Matchie")]
        assert world.includes(africa, forest_elephant.distribution)
        denmark = taxonome.regions.names["Denmark"]
        assert not world.includes(denmark, forest_elephant.distribution)

if __name__ == "__main__":
    unittest.main()
