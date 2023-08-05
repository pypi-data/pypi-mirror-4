import csv
from io import StringIO
import unittest

from taxonome import Taxon, TaxonSet
from taxonome.taxa import match_taxa
from taxonome import tracker

class TrackerTest(unittest.TestCase):
    def setUp(self):
        self.ts = TaxonSet()
        self.ts.add(Taxon("Amborella trichopoda", "Baill."))
        
        self.taxa = [Taxon("Amborella trichopoda", "Norbert"),
                     Taxon("Amborella trichopode", "Baill."),
                     Taxon("Amborella trichopoda subsp. trichopoda", "Baill."),
                     Taxon("Amborella figmentimagionatium", "Me"),
                    ]
    
    def do_match(self, tracker):
        match_taxa(self.taxa, self.ts, tracker=tracker)
    
    def test_csv_tracker(self):
        sio = StringIO()
        track = tracker.CSVTracker(sio)
        self.do_match(track)
        
        sio.seek(0)
        #print(sio.getvalue()) #DBG
        reader = csv.reader(sio)
        next(reader)
        events = [r[5] for r in reader]
        self.assertEqual(events, ['authority overlooked', 'one match',  # wrong authority
        'authority overlooked', 'fuzzy match', 'name variation', 'one match', # Mis-spelling
        'authority overlooked', 'upgraded subspecies', 'name variation', 'one match', # subspecies
        'authority overlooked', 'no match',   # non-matching taxon
        ])
    
    def test_csv_matches(self):
        sio = StringIO()
        track = tracker.CSVListMatches(sio)
        self.do_match(track)
        
        sio.seek(0)
        print(sio.getvalue()) #DBG
        reader = csv.reader(sio)
        next(reader)
        matched_names = [(r[2],r[3]) for r in reader]
        self.assertEqual(matched_names[:3], [("Amborella trichopoda", "Baill.")]*3)
        self.assertEqual(matched_names[3], ("",""))
