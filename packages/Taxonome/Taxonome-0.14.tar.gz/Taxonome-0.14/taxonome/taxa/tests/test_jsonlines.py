import io

from .test_taxa import LiquoriceTestBase
from taxonome.taxa import file_jsonlines

class JsonlinesTest(LiquoriceTestBase):
    def test_roundtrip(self):
        f = io.StringIO()
        file_jsonlines.save_taxa(f, self.ts)
        f.seek(0)
        newts = file_jsonlines.load_taxa(f)
        
        self.assertEqual(len(newts), 2)
        self.assertIn("Glycyrrhiza glabra", newts)
        self.assertIn(self.liquorice.name, newts)
        homonyms = newts.resolve_name("Glycyrrhiza glandulifera")
        self.assertEqual(len(homonyms), 2)
