"""Tools for working with Q-grams, short sections of a string. For more
information, see this paper:

http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.14.6750

Note that we currently ignore the positions of the Q-grams, and simply compare
the set of Q-grams from each string.
"""
from collections import defaultdict

START="^"
END="$"

def qgrams(s, q=3):
    """Generate a set of Q-grams from a string."""
    s = START*(q-1) + s # + END*(q-1)
    return frozenset(s[i:i+q] for i in range(len(s)-(q-1)))

def compare_strings(s1, s2, q=3):
    """Return the proportion of Q-grams that match between two strings, as a
    float between 0 and 1."""
    q1, q2 = qgrams(s1), qgrams(s2)
    return overlap(q1, q2)
    
def overlap(q1, q2):
    """Return the overlap of two sets, as a proportion of the size of the
    larger set."""
    return len(q1.intersection(q2))/max(len(q1), len(q2))

class QGramIndex:
    """An index to do fuzzy string matching.
    
    Strings are stored by the first idx_chars letters to speed lookups, so it
    will only find matches where these letters are the same. To do full fuzzy
    matching, create the index with idx_chars=0.
    """
    def __init__(self, q=3, idx_chars=3):
        self.q = q
        self.idx_chars = idx_chars
        self.data = defaultdict(set)

    def add(self, s):
        self.data[s[:self.idx_chars]].add((s, qgrams(s, q=self.q)))
    
    def discard(self, s):
        self.data[s[:self.idx_chars]].discard((s, qgrams(s, q=self.q)))
    
    def matches(self, s, threshold=0.85):
        """Find fuzzy matches for the given string. Yields 2-tuples of (string, 
        proportion matched), where proportion matched is above the given
        threshold."""
        target_qgrams = qgrams(s)
        for check_str, check_qgrams in self.data[s[:self.idx_chars]]:
            match_val = overlap(target_qgrams, check_qgrams)
            if match_val > threshold:
                yield check_str, match_val
    
    def best_match(self, s, threshold=0.85):
        """Return a 2-tuple of (string, proportion matched) for the best match
        to the given string. Raises KeyError if no matches are found for that
        threshold."""
        matches = sorted(self.matches(s, threshold=threshold), key=lambda x:x[1])
        if matches:
            return matches[-1]
        raise KeyError("No matches found for {0!r} at threshold {1}".format(s, threshold))
