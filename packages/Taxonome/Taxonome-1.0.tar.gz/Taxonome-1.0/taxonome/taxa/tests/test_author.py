import unittest

from taxonome.taxa.author import Author, Authority

class AuthorityTests(unittest.TestCase):
    def test_simple_authority(self):
        a = Authority("L.")
        self.assertEqual(a.main[0], Author("L."))
        assert a.ex == a.basauth == a.non == ()

    def test_complex_authority(self):
        a = Authority("(Smith) Gray & Presl. ex. L. Stev.")
        self.assertEqual(a.basauth[0], Author("Smith"))
        self.assertEqual(a.main, (Author("Gray"), Author("Presl.")))
        self.assertEqual(a.ex[0], Author("L. Stev."))
        self.assertEqual(str(a), "(Smith) Gray & Presl. ex L. Stev.")
        
        self.assertGreater(a.fuzzy_cmp(Authority("Gray and Presley")), 0.5)
        
        self.assertGreater(a.fuzzy_cmp(Authority("L. Stevens")), 0.5)

    def test_authority_non(self):
        a = Authority("Bert non Miq.")
        self.assertEqual(a.main[0], Author("Bert"))
        self.assertEqual(a.non, (Author("Miq."),))
        self.assertEqual(str(a), "Bert non Miq.")
        
        b = Authority("Miq.")
        assert a.non_match(b)
        assert b.non_match(a)
        self.assertLess(a.fuzzy_cmp(b), 0.2)
    
    def test_authority_extras(self):
        a = Authority("sensu A.Gray")
        self.assertEqual(a.prefix, "sensu")
        self.assertEqual(a.main[0], Author("A. Gray"))
        
        a = Authority("sensu auct., non Benth")
        self.assertEqual(a.prefix, "sensu auct.")
        self.assertEqual(a.non[0], Author("Benth"))
        
        a = Authority("sensu Meeuwen, p.p., non B.L.Burtt")
        self.assertEqual(a.prefix, "sensu")
        self.assertEqual(a.suffix, "p.p.")
        self.assertEqual(a.main[0], Author("Meeuwen"))
        self.assertEqual(a.non[0], Author("B.L. Burtt"))
        
        a = Authority("sensu auct., p.p.")
        self.assertEqual(a.prefix, "sensu auct.")
        self.assertEqual(a.suffix, "p.p.")
    
    def test_with_year(self):
        # Zoological style
        a = Authority("Linnaeus, 1758")
        self.assertEqual(a.main[0], Author("Linnaeus"))
        self.assertEqual(a.year, "1758")
        self.assertEqual(str(a), "L., 1758")
        
        # Without the comma
        a = Authority("Linnaeus 1758")
        self.assertEqual(a.main[0], Author("Linnaeus"))
        self.assertEqual(a.year, "1758")
        self.assertEqual(str(a), "L., 1758")
        
        # In brackets; indicates a basionym
        a = Authority("(Scopoli, 1769)")
        self.assertEqual(a.basauth[0], Author("Scopoli"))
        self.assertEqual(a.basyear, "1769")
        self.assertEqual(str(a), "(Scopoli, 1769)")
        
        # Something like this was causing a failure
        a = Authority("(Bloggs) 1952")
        str(a)

class AuthorTests(unittest.TestCase):
    def test_surname_f(self):
        a = Author("Forst. f.")
        self.assertEqual(a.to_dict()["surname"], "Forst.")
    
    def test_specialcase_Linnaeus(self):
        self.assertEqual(Author("L."), Author("Linnaeus"))
    
    def test_noncapitalised_part(self):
        a = Author("de Rigeur")
        self.assertEqual(a.surname, "de Rigeur")
