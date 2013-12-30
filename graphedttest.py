import unittest
import graphedt
import wx

class TestGrid(unittest.TestCase):
    """ Test gui code
    """
    def setUp(self):
        self.dimen = 4
        self.graph = graphedt.Graph(self.dimen)

    def test_DrawLine(self):
        pass

class TestGraph(unittest.TestCase):
    def setUp(self):
        self.dimen = 4
        self.graph = graphedt.Graph(self.dimen)

    def test_getNumVertices(self):
        # return number of vertices
        self.num_vert = 16
        self.assertEqual(self.num_vert, self.graph.getGraphDimen()**2)

    def test_addEdges(self):
        # add edge a-b to this graph
        vert_a = (0, 0)
        vert_b = (0, 1)
        num_edges = 1
        self.graph.addEdge((vert_a, vert_b))
        self.assertEqual(num_edges, self.graph.getNumEdges())

    def test_getEdges(self):
        # return number of edges
        vert_a = (0, 0)
        vert_b = (0, 1)
        num_edges = 1
        self.graph.addEdge((vert_a, vert_b))
        self.assertEqual(num_edges, self.graph.getNumEdges())
        
    def test_getAdj(self):
        # vertices adjacent to vert
        vert_a = (0, 0)
        vert_b = (0, 1)
        vert_c = (1, 0)
        vert_d = (1, 1)
        self.graph.addEdge((vert_a, vert_b))
        self.graph.addEdge((vert_a, vert_c))
        self.graph.addEdge((vert_a, vert_d))
        adj_vert = set([(0, 1), (1, 0), (1, 1)])
        self.assertEqual(adj_vert, self.graph.getAdj(vert_a))

    def test_delEdge(self):
        # delete edge a-b to this graph
        vert_a = (0, 0)
        vert_b = (0, 1)
        vert_c = (1, 0)
        vert_d = (1, 1)
        self.graph.addEdge((vert_a, vert_b))
        self.graph.addEdge((vert_a, vert_c))
        self.graph.addEdge((vert_a, vert_d))
        num_edges = 2
        self.graph.delEdge((vert_a, vert_b))
        self.assertEqual(num_edges, self.graph.getNumEdges())

if __name__ == '__main__':
    unittest.main()
