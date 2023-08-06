import unittest
import io
import warnings

from taxonome.taxa import file_csv
from taxonome import Name

csvdata = '''"Name","Author","Lives in"
"Solanum lycopersicum","L.","Peru"
"Lablab purpureus","(L.) Sweet.","Africa"'''

csvdata2 = '''"Name","Lives in"
"Solanum lycopersicum L.","Peru"
"Lablab purpureus (L.) Sweet.","Africa"'''

csvdata_noauth = '''"Name","Lives in"
"Solanum lycopersicum","Peru"
"Lablab purpureus","Africa"'''

csv_sp_data1 = io.StringIO('''"Name","Author"
"Solanum sp.",""
"Solanum spp.",""
"Solanum tuberosum","L."''')

csv_sp_data2 = io.StringIO('''"Name","Foo"
"Solanum sp.",""
"Solanum spp.",""
"Solanum tuberosum L.","Bar"''')

csv_sp_data3 = io.StringIO('''"Name","Foo"
"Solanum sp.",""
"Solanum spp.",""
"Solanum tuberosum","Bar"''')

class CsvTest(unittest.TestCase):
    def setUp(self):
        self.csvfile = io.StringIO(csvdata)
        self.ts = file_csv.load_taxa(self.csvfile)
        self.csvfile2 = io.StringIO(csvdata2)
        self.csvfile_noauth = io.StringIO(csvdata_noauth)
        
    def testRead(self):
        self.assertEqual(len(self.ts), 2)
        assert "Solanum lycopersicum" in self.ts
        assert Name("Lablab purpureus","Sweet") in self.ts
        self.assertEqual(self.ts["Lablab purpureus"].info["Lives in"], "Africa")
    
    def test_read_combined_name_auth(self):
        ts = file_csv.load_taxa(self.csvfile2, authfield=True)
        self.assertEqual(len(ts), 2)
        self.assertIn("Solanum lycopersicum", ts)
        self.assertIn(Name("Lablab purpureus","Sweet"), ts)
        self.assertEqual(ts["Solanum lycopersicum"].info["Lives in"], "Peru")
    
    def test_read_noauth(self):
        ts = file_csv.load_taxa(self.csvfile_noauth, authfield=None)
        self.assertEqual(len(ts), 2)
        self.assertIn("Solanum lycopersicum", ts)
        self.assertEqual(ts["Solanum lycopersicum"].info["Lives in"], "Peru")
    
    def testWrite(self):
        new_csvfile = io.StringIO()
        file_csv.save_taxa(new_csvfile, self.ts, info_fields=True)
        new_csvfile.seek(0)
        newts = file_csv.load_taxa(new_csvfile)
        self.assertEqual(len(newts), 2)
        self.assertEqual(newts["Lablab purpureus"].info["Lives in"], "Africa")
    
    def test_read_sp(self):
        "Check that 'sp.' and 'spp.' species are excluded when reading CSV."
        def check_ts(ts):
            self.assertEqual(len(ts), 1)
            self.assertIn("Solanum tuberosum", ts)
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            check_ts(file_csv.load_taxa(csv_sp_data1))
            check_ts(file_csv.load_taxa(csv_sp_data2, authfield=True))
            check_ts(file_csv.load_taxa(csv_sp_data3, authfield=None))

csv_syn_data = '''"Name","Author","Synonym name","Synonym author","Lives in"
"Solanum lycopersicum","L.","Lycopersicon lycopersicum","Foo.","Ignored"
"Solanum lycopersicum","L.","Solanum lycopersicum","L.","Peru"
"Lablab purpureus","(L.) Sweet.","Lablab purpureus","(L.) Sweet.","Africa"
"Lablab purpureus","(L.) Sweet.","Dolichos lablab","L.","Africa"
"Lablab purpureus","(L.) Sweet.","Vigna aristata","Piper","Ignored"
'''

class CSVSynonymyTests(unittest.TestCase):
    def setUp(self):
        self.csvfile = io.StringIO(csv_syn_data)
        self.ts = file_csv.load_synonyms(self.csvfile, synnamefield="Synonym name",
                                    synauthfield="Synonym author", accnamefield="Name",
                                    accauthfield="Author", get_info=True)
    
    def test_read(self):
        self.assertEqual(len(self.ts), 2)
        self.assertEqual(self.ts["Lablab purpureus"].othernames,
                {Name("Dolichos lablab","L."), Name("Vigna aristata", "Piper")})
        self.assertEqual(self.ts["Lablab purpureus"].info["Lives in"], "Africa")
        self.assertEqual(self.ts["Solanum lycopersicum"].info["Lives in"], "Peru")
        print(*self.ts.names)
        self.assertIn("Dolichos lablab", self.ts)
        self.assertIn("Lycopersicon lycopersicum", self.ts)
    
    def test_write(self):
        csvfile2 = io.StringIO()
        file_csv.save_synonyms(csvfile2, self.ts)
        csvfile2.seek(0)
        ts2 = file_csv.load_synonyms(csvfile2)
        self.assertEqual(len(ts2), 2)
        self.assertEqual(ts2["Lablab purpureus"].othernames,
                {Name("Dolichos lablab","L."), Name("Vigna aristata", "Piper")})
        print(*ts2.names)
        self.assertIn("Dolichos lablab", ts2)
        self.assertIn("Lycopersicon lycopersicum", ts2)

csv_individual_data = '''"Nom","Authority","Accession number","Seed mass"
"Vigna radiata","(L.) R. Wilczek","PI 291365",5.92
"Vigna radiata","(L.) R. Wilczek","PI 378024",5.27
"Vigna unguiculata","(L.) Walp.","Grif 13969",9.46
"Vigna unguiculata","(L.) Walp.","PI 349852 ",8.98
'''

class CSVIndividualsTest(unittest.TestCase):
    def setUp(self):
        self.csvfile = io.StringIO(csv_individual_data)
        self.ts = file_csv.load_individuals(self.csvfile, namefield="Nom", authfield="Authority")
    
    def check_ts(self, ts):
        self.assertEqual(len(ts), 2)
        Vr = ts["Vigna radiata"]
        self.assertEqual([ind["Accession number"] for ind in Vr.individuals], ["PI 291365", "PI 378024"])
        Vu = ts["Vigna unguiculata"]
        self.assertEqual([ind["Seed mass"] for ind in Vu.individuals], ["9.46", "8.98"])
    
    def test_read(self):
        self.check_ts(self.ts)
    
    def test_html(self):
        "Check that taxon.html() mentions individuals."
        for tax in self.ts:
            self.assertIn("individual records", tax.html())
    
    def test_write(self):
        csvfile2 = io.StringIO()
        file_csv.save_individuals(csvfile2, self.ts)
        csvfile2.seek(0)
        ts2 = file_csv.load_individuals(csvfile2)
        self.check_ts(ts2)
        
