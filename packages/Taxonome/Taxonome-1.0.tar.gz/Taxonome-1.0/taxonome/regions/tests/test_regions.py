import unittest
from .. import regions
from taxonome.utils.testing import check_func

class RegionsTest(unittest.TestCase):
    def testTDWG(self):
        if not regions.world:
            regions.load_tdwg()
        world = regions.world
        assert len(regions.tdwg_levels[1]) == 9
        assert world.is_subregion(regions.tdwg["4"], regions.tdwg["EHM-BH"])
        assert not world.is_subregion(regions.tdwg["3"], regions.names["Bhutan"])
        assert world.is_subregion(regions.ISO["GB"], regions.tdwg["IRE-NI"])
        assert not world.is_subregion(regions.tdwg["26"], regions.names["Netherlands"])
        assert len(list(world.subregions(regions.tdwg["36"]))) == 44
        assert len(world.immediate_subregions(regions.tdwg["36"])) == 9
    
    def test_find_tdwg(self):
        tests = [("Netherlands", {"NET"}),
                 ("Ecuador", {"ECU"}),
                 ("Chongqing", {"CHC"}),   # Level 4 -> 3
                 ("Brazil", {'BZS', 'BZE', 'BZC', 'BZN', 'BZL'}), # Level 2 -> 3
                 ("Turkey", {'TUE', 'TUR'}) # TUE is 'Turkey-in-Europe'
                ]
        check_func(regions.find_tdwg, tests)
        
        with self.assertRaises(KeyError):
            regions.find_tdwg("Mars")
        
        self.assertEqual(regions.find_tdwg("OM",level=2, index=regions.ISO), {"35"})
    
    def test_tdwgise(self):
        """tdwgise should break down larger regions (Brazil), and find parent
        regions (Chongqing)."""
        raw = ["Netherlands","Ecuador", "Brazil", "Chongqing", "Mars", "Turkey"]
        exp = {'CHC', 'BZS', 'ECU', 'BZE', 'BZC', 'BZN', 'NET', 'BZL', 'TUR', 'TUE'}
        tdwged, notfound = regions.tdwgise(raw)
        self.assertEqual(tdwged, exp)
        self.assertEqual(notfound, {"Mars"})
        
if __name__ == "__main__":
    unittest.main()
