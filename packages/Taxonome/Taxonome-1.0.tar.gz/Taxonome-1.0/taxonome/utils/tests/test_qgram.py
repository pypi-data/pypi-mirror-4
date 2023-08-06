from unittest import TestCase
from taxonome.utils import qgram, testing

# Shorthand
S, E = qgram.START, qgram.END
tests = [("abcdef", {S*2+"a", S+"ab", "abc", "bcd", "cde", "def"})]

tests4 = [("abcdef", {S*3+"a", S*2+"ab", S+"abc", "abcd", "bcde", "cdef"})
         ]
q4grams = lambda s: qgram.qgrams(s, q=4)

def test_qgram():
    testing.check_func(q4grams, tests4)
    testing.check_func(qgram.qgrams, tests)

# Check we have Python 3 style divsion:
assert 1/2 == 0.5

match_tests = [("Trisetum preslei", "Trisetum preslii", 14/16)]

def test_compare_strings():
    testing.check_func(qgram.compare_strings, match_tests)

class TestQGramIndex(TestCase):
    def test_lookup(self):
        qindex = qgram.QGramIndex()
        qindex.add("Hilaria swalleni")
        res, score = qindex.best_match("Hilaria swallenii") # N.B. Double i
        self.assertEqual(res, "Hilaria swalleni")
        self.assertGreater(score, 0.85)
