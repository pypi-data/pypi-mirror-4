from ..digraph import DiGraph
import unittest

class SimpleTestCase(unittest.TestCase):
    def setUp(self):
        self.g = DiGraph()
        
    def test_add_node(self):
        self.g.nodes.add(1)
        self.g.nodes.add("spam")
        self.assertIn(1, self.g.nodes)
        self.assertNotIn(2, self.g.nodes)
        self.assertIn("spam", self.g.nodes)
        self.assertNotIn("eggs", self.g.nodes)
        
    def test_add_edge(self):
        self.g.nodes.add(1)
        self.g.nodes.add(2)
        self.g.edges.add(1, 2)
        self.g.edges.add(3, 4)
        self.assertIn(3, self.g.nodes)
        self.assertIn(4, self.g.nodes)
        self.g.edges.add(1, 3)
        
        self.assertIn((1,3), self.g.edges)
        self.assertIn((3, 4), self.g.edges)
        self.assertNotIn((3, 1), self.g.edges)
        self.assertNotIn((1, 4), self.g.edges)


class BuildTestCase(unittest.TestCase):
    def test_build_nodes(self):
        g = DiGraph.build([], range(6))
        self.assertEqual(len(g.nodes), 6)
        self.assertEqual(len(g.edges), 0)
        
    def test_build_edges(self):
        edges = zip(range(5), range(1, 6))
        g = DiGraph.build(edges)
        self.assertEqual(len(g.nodes), 6)
        self.assertEqual(len(g.edges), 5)
        self.assertIn((1,2), g.edges)
        self.assertNotIn((1,3), g.edges)
        self.assertNotIn((2,1), g.edges)
        
    def test_build_mixed(self):
        edges = zip(range(5), range(1, 6))
        g = DiGraph.build(edges, range(3, 8))
        self.assertEqual(len(g.nodes), 8)
        self.assertEqual(len(g.edges), 5)

class LinksTestCase(unittest.TestCase):
    def setUp(self):
        edges = zip(range(5), range(1, 6))
        self.g = DiGraph.build(edges)
        self.g.edges.add(2, 5)
    
    def test_incoming(self):
        self.assertEqual(len(self.g.incoming(0)), 0)
        self.assertEqual(len(self.g.incoming(3)), 1)
        in3 = set(self.g.incoming(3))
        self.assertEqual(in3, {2})
        
    def test_outgoing(self):
        self.assertEqual(len(self.g.outgoing(5)), 0)
        self.assertEqual(len(self.g.outgoing(3)), 1)
        out3 = set(self.g.outgoing(3))
        self.assertEqual(out3, {4})
        
    def test_successors(self):
        succ1 = list(self.g.successors(1))
        self.assertEqual(len(succ1), 4)
        self.assertEqual(set(succ1), {2,3,4,5})
        
        self.assertTrue(self.g.is_successor(2, 5))
        self.assertTrue(self.g.is_successor(3, 5))
        self.assertFalse(self.g.is_successor(5, 3))
        self.assertFalse(self.g.is_successor(5, 7))   # There is no 7
        self.assertTrue(self.g.is_successor(1, 2))
        self.assertFalse(self.g.is_successor(2, 2))
        
    def test_infinite_loop(self):
        "Make a cycle, and check that it doesn't hang. May need to be killed."
        self.g.edges.add(5, 3)
        succ2 = set(self.g.successors(2))
        self.assertEqual(succ2, {3,4,5})
        for x in succ2:
            self.assertTrue(self.g.is_successor(2, x))
            self.assertFalse(self.g.is_successor(x, 2))
            
            self.assertTrue(self.g.is_successor(3, x))
            self.assertTrue(self.g.is_successor(x, 3))
            
if __name__ == "__main__":
    unittest.main()
