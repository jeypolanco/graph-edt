import unittest
import graph-edt
import wx

# Figure out the new feature you want.  Possibly document it, and then write a
# test for it.  

# Write some skeleton code for the feature, so that your program runs without
# any syntax errors or the like, but so that your test fails.  See your test
# fail before you try to make it succeed.

# Write dummy code for your skeleton, just to appease the test.

# Now you rewrite (or refactor) the code so that it actually does what it's
# supposed to, all while making sure that your test keeps succeeding.

class TestGrid(unittest.TestCase):
    def setUp(self):
        self.dimen = 4
        self.graph = graph-edt.Graph(self.dimen)


    def test_DrawLine(self):
        pass

class TestGraph(unittest.TestCase):
    def setUp(self):
        self.dimen = 4
        self.graph = graph-edt.Graph(self.dimen)

    def test_get_num_vertices(self):
        # return number of vertices
        self.num_vert = 16
        self.assertEqual(self.num_vert, self.graph.get_graph_dimen()**2)

    def test_add_edges(self):
        # add edge a-b to this graph
        vert_a = (0, 0)
        vert_b = (0, 1)
        num_edges = 1
        self.graph.add_edge((vert_a, vert_b))
        self.assertEqual(num_edges, self.graph.get_num_edges())

    def test_get_edges(self):
        # return number of edges
        vert_a = (0, 0)
        vert_b = (0, 1)
        num_edges = 1
        self.graph.add_edge((vert_a, vert_b))
        self.assertEqual(num_edges, self.graph.get_num_edges())
        
    def test_get_adj(self):
        # vertices adjacent to vert
        vert_a = (0, 0)
        vert_b = (0, 1)
        vert_c = (1, 0)
        vert_d = (1, 1)
        self.graph.add_edge((vert_a, vert_b))
        self.graph.add_edge((vert_a, vert_c))
        self.graph.add_edge((vert_a, vert_d))
        adj_vert = set([(0, 1), (1, 0), (1, 1)])
        self.assertEqual(adj_vert, self.graph.get_adj(vert_a))

    def test_del_edge(self):
        # delete edge a-b to this graph
        vert_a = (0, 0)
        vert_b = (0, 1)
        vert_c = (1, 0)
        vert_d = (1, 1)
        self.graph.add_edge((vert_a, vert_b))
        self.graph.add_edge((vert_a, vert_c))
        self.graph.add_edge((vert_a, vert_d))
        num_edges = 2
        self.graph.del_edge((vert_a, vert_b))
        self.assertEqual(num_edges, self.graph.get_num_edges())

if __name__ == '__main__':
    unittest.main()
