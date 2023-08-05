import builtins
import tempfile
import unittest
from os import remove

import taxonome
from taxonome.taxa import file_csv, name_selector
from taxonome.taxa.base import UncertainSpeciesError
from taxonome.taxa.author import Authority
import taxonome.taxa.collection

Name = taxonome.Name

class AutoInput:
    """Context manager to override the input() call. Will automatically
    return the given response."""
    def __init__(self, response=''):
        self.response = response
    
    def __enter__(self):
        self.saved_input = builtins.input
        def autoinput(prompt):
            return self.response
        builtins.input = autoinput
    
    def __exit__(self, exc_type, exc_value, traceback):
        builtins.input = self.saved_input

class HyacinthBeanTest(unittest.TestCase):
    def setUp(self):
        self.bean = taxonome.Taxon("Lablab purpureus", "(L.) Sweet")
        self.bean.othernames.add(Name("Dolichos lablab","L."))
        self.bean.othernames.add(Name("Lablab niger", "Medikus"))
        self.bean.othernames.add(Name("Vigna aristata", "Piper"))
        self.ts = taxonome.TaxonSet()
        self.ts.add(self.bean)
    
    def testSynonymy(self):
        assert self.bean.hasname("Dolichos lablab")
        assert self.bean.hasname(Name("Lablab niger", "Medikus"))
    
    def testShortauth(self):
        assert self.bean.name == Name("Lablab purpureus", "Sweet.")
        assert self.bean.name == Name("Lablab purpureus", "Sweet ex. Madeup")
        
    def testTSSynonymy(self):
        assert Name("Vigna aristata","Piper.") in self.ts
        assert self.ts["Lablab niger"]
    
    def testAccnameLookup(self):
        self.assertEqual(self.ts.get_by_accepted_name(Name("Lablab purpureus",
                                "(L.) Sweet")), self.bean)
        with self.assertRaises(KeyError):
            self.ts.get_by_accepted_name(Name("Dolichos lablab","L."))
    
    def test_non_auth_lookup(self):
        t1 = self.ts.select(Name("Dolichos lablab", "L."))
        self.assertIs(t1, self.bean)
        with self.assertRaises(KeyError):
            self.ts.select(Name("Dolichos lablab", "non L."))
        with self.assertRaises(KeyError):
            self.ts.select(Name("Dolichos lablab", "sensu non L."))
        with self.assertRaises(KeyError):
            self.ts.select(Name("Dolichos lablab", "auct. non L."))
        
        # Test selecting the other way round.
        ts2 = taxonome.TaxonSet()
        ts2.add(taxonome.Taxon("Dolichos lablab", "non L."))
        with self.assertRaises(KeyError):
            ts2.select(Name("Dolichos lablab", "L."))
        
        # This should succeed.
        ts2.select(Name("Dolichos lablab", "Vahl"), strict_authority=False)

class PoaTest(unittest.TestCase):
    def setUp(self):
        self.t1 = taxonome.Taxon("Poa annua", "L.")
        self.t2 = taxonome.Taxon("Poa infirma", "H. B. & K.")
        self.t2.othernames.add(Name("Poa annua", "Cham. & Schlecht."))
        self.ts = taxonome.TaxonSet()
        self.ts.add(self.t1)
        self.ts.add(self.t2)
        self.ts._nameselector = name_selector.TerminalNameSelector(previous_choices={})
    
    def testPreferAccName(self):
        # No authority: should pick accepted name without asking for input.
        with AutoInput("N"):
            t1 = self.ts.select("Poa annua")
        self.assertEqual(t1, self.t1)
        
        # With authority: should ask the user by default.
        with AutoInput("0"), self.assertRaisesRegex(KeyError, "0"):
            self.ts.select(Name("Poa annua", "Madeup"))
        
        # With authority: When requested, prefer the accepted name:
        with AutoInput("N"):
            t1a = self.ts.select(Name("Poa annua", "Madeup"), prefer_accepted='all')
        self.assertEqual(t1a, self.t1)
        
class LiquoriceTestBase(unittest.TestCase):
    def setUp(self):
        self.ts = taxonome.TaxonSet()
        self.liquorice = taxonome.Taxon("Glycyrrhiza glabra", "L.")
        self.liquorice.othernames.add(Name("Glycyrrhiza glandulifera", "Waldst. and Kit."))
        self.ts.add(self.liquorice)
        ch_liquorice = taxonome.Taxon("Glycyrrhiza uralensis", "Fisch.")
        ch_liquorice.othernames.add(Name("Glycyrrhiza glandulifera", "Ledeb."))
        self.ts.add(ch_liquorice)

class LiquoriceTest(LiquoriceTestBase):
    def testHomonym(self):
        assert self.ts[Name("Glycyrrhiza glabra", "L.")].hasname(Name("Glycyrrhiza glandulifera", "Waldst. & Kit."))
        homonyms = self.ts.resolve_name("Glycyrrhiza glandulifera")
        assert len(homonyms) == 2
        assert homonyms[0][0].match_unqualified(homonyms[1][0])
        assert not homonyms[0][1].match_unqualified(homonyms[1][1])
        with AutoInput("1"):
            self.assertIn(self.ts.select("Glycyrrhiza glandulifera"), self.ts)
    
    def testFuzzyLookup(self):
        fuzzy_match = self.ts.select("Glycyrhiza glabra")
        self.assertEqual(self.liquorice, fuzzy_match)
        with self.assertRaises(KeyError):
            self.ts.select("Glycyrrhiza echinata")
        
    def testUpgradeSubsp(self):
        n1 = Name("Glycyrrhiza glabra subsp. glabra")
        n2 = Name("Glycyrrhiza glabra var. glabra")
        n3 = Name("Glycyrrhiza glabra subsp. spammens")
        with self.assertRaises(KeyError):
            self.ts.select(n1, upgrade_subsp="none")
        match1 = self.ts.select(n1, upgrade_subsp="nominal")
        self.assertEqual(match1, self.liquorice)
        match2 = self.ts.select(n2, upgrade_subsp="nominal")
        self.assertEqual(match2, self.liquorice)
        with self.assertRaises(KeyError):
            self.ts.select(n3, upgrade_subsp="nominal")
        match3 = self.ts.select(n3, upgrade_subsp="all")
        self.assertEqual(match3, self.liquorice)
        
    def testDeletionByString(self):
        with self.assertRaises(KeyError):
            del self.ts["Glycyrrhiza glandulifera"]
        del self.ts["Glycyrrhiza glabra"]
        assert taxonome.Name("Glycyrrhiza glabra", "L.") not in self.ts
        assert len(self.ts.resolve("Glycyrrhiza uralensis")) == 1
        
    def testDeletionByQName(self):
        name = taxonome.Name("Glycyrrhiza glandulifera", "Ledeb.")
        del self.ts[name]
        assert name not in self.ts
        assert "Glycyrrhiza uralensis" not in self.ts

class NameParseTest(unittest.TestCase):
    def test_parse_name(self):
        n = Name.from_string("Teramnus repens (Taub.)Baker f. ssp. gracilis (Chiov.)Verdc.")
        self.assertEqual(n.plain, "Teramnus repens subsp. gracilis")
        self.assertEqual(str(n.authority), "(Chiov.) Verdc.")
        parent = n.parent
        self.assertEqual(parent.plain, "Teramnus repens")
        # f. (filius, i.e. son) is ignored for now
        self.assertEqual(str(parent.authority), "(Taub.) Baker")
        
        # N.B. var without a .
        n = Name("Vigna radiata var sublobata", "(Roxb.) Verdc.")
        self.assertEqual(n.plain, "Vigna radiata var. sublobata")
        
        # Extra spaces
        n = Name("Vigna    radiata\tvar. \t sublobata")
        self.assertEqual(n.plain, "Vigna radiata var. sublobata")
    
    def test_subspecies(self):
        n = Name("Gorilla gorilla gorilla", "Savage, 1847")
        self.assertEqual(n.rank, "subspecies")
        self.assertEqual(n.parent.plain, "Gorilla gorilla")
        
        n = Name.from_string("Gorilla gorilla gorilla Savage, 1847")
        self.assertEqual(n.rank, "subspecies")
        self.assertEqual(n.parent.plain, "Gorilla gorilla")
        
        n = Name("Alloteropsis semialata subsp. eckloniana", "(Nees) Gibbs-Russ.")
        self.assertEqual(n.rank, "subspecies")
        self.assertEqual(n.parent.plain, "Alloteropsis semialata")
        
        n = Name.from_string("Alloteropsis semialata (R. Br.) Hitchc. subsp. eckloniana (Nees) Gibbs-Russ.")
        self.assertEqual(n.rank, "subspecies")
        self.assertEqual(n.parent.plain, "Alloteropsis semialata")
        self.assertEqual(str(n.parent.authority), "(R. Br.) Hitchc.")
        self.assertEqual(str(n.authority), "(Nees) Gibbs-Russ.")
        
    def test_forma(self):
        n = Name('Muhlenbergia mexicana f. ambigua')
        self.assertEqual(n.rank, 'form')
        self.assertEqual(n.parent.plain, 'Muhlenbergia mexicana')
        
        n = Name.from_string('Muhlenbergia mexicana L. f. ambigua Foo.')
        self.assertEqual(n.rank, 'form')
        self.assertEqual(n.parent.plain, 'Muhlenbergia mexicana')
        self.assertEqual(str(n.authority), "Foo.")
        self.assertEqual(str(n.parent.authority), "L.")
        
        n = Name('Muhlenbergia mexicana forma mexicana')
        self.assertEqual(n.rank, 'form')
        self.assertEqual(n.parent.plain, 'Muhlenbergia mexicana')
        
        n = Name.from_string('Muhlenbergia mexicana L. forma mexicana Bar.')
        self.assertEqual(n.rank, 'form')
        self.assertEqual(n.parent.plain, 'Muhlenbergia mexicana')
        self.assertEqual(str(n.authority), "Bar.")
        self.assertEqual(str(n.parent.authority), "L.")
        
        # With f. for filius
        n = Name.from_string('Crotalaria dolichonyx Baker f. & Martin')
        self.assertEqual(n.rank, 'species')
        self.assertEqual(n.plain, 'Crotalaria dolichonyx')
        self.assertEqual(n.authority, Authority('Baker f. & Martin'))
    
    def test_hybrid(self):
        names = [('X Achnella caduca', 'Achnella caduca', 'genus'),
                 ('x Achnella caduca', 'Achnella caduca', 'genus'),
                 ('× Achnella caduca', 'Achnella caduca', 'genus'),
                 ('Calammophila X baltica', 'Calammophila baltica', 'species'),
                 ('Calammophila x baltica', 'Calammophila baltica', 'species'),
                 ('Calammophila × baltica', 'Calammophila baltica', 'species'),
                ]
        
        for raw, plain, hybrid in names:
            print(raw)
            n = Name(raw)
            self.assertEqual(n.plain, plain)
            self.assertEqual(n.hybrid, hybrid)
            
            n = Name.from_string(raw + " Bloggs")
            self.assertEqual(n.plain, plain)
            self.assertEqual(str(n.authority), "Bloggs")
            self.assertEqual(n.hybrid, hybrid)
        
    def test_genus_name(self):
        n = Name("Alloteropsis", "Presl.")
        self.assertEqual(n.plain, "Alloteropsis")
        self.assertEqual(str(n.authority), "Presl.")
    
    def test_with_year(self):
        n = Name.from_string("Balaena mysticetus Linnaeus, 1758")
        self.assertEqual(n.plain, "Balaena mysticetus")
        self.assertEqual(n.authority.year, "1758")
        
        self.assertEqual(n, Name("Balaena mysticetus", "L."))
    
    def test_invalid_name(self):
        with self.assertRaises(UncertainSpeciesError):
            Name.from_string("Festuca ovina & rubra")
        
        with self.assertRaises(UncertainSpeciesError):
            Name.from_string("Festuca sp.")
        with self.assertRaises(UncertainSpeciesError):
            Name.from_string("Festuca spp.")
        
        with self.assertRaises(UncertainSpeciesError):
            Name("Brachiaria sp")
        with self.assertRaises(UncertainSpeciesError):
            Name("Brachiaria sp.")
        with self.assertRaises(UncertainSpeciesError):
            Name("Brachiaria spp")
        with self.assertRaises(UncertainSpeciesError):
            Name("Brachiaria spp.")
    
    def test_not_capitalised(self):
        n = Name.from_string("cynodon dactylon")
        self.assertEqual(n.plain, "Cynodon dactylon")
        n = Name("echinochloa haploclada", "")
        self.assertEqual(n.plain, "Echinochloa haploclada")
    
    def test_auth_noncapital(self):
        n = Name.from_string("Trifolium pauciflorum d'Urv.")
        self.assertEqual(n.plain, "Trifolium pauciflorum")
        self.assertEqual(str(n.authority), "d'Urv.")
        
        n = Name.from_string("Trifolium pauciflorum de Madeup")
        self.assertEqual(n.plain, "Trifolium pauciflorum")
        self.assertEqual(str(n.authority), "de Madeup")
