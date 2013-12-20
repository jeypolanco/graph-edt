try:
    import wx
    from wx.lib.floatcanvas import FloatCanvas as FC
except ImportError:
    print "Install wx-python2.8"
import cPickle
import os

""" puzzle.py is a graph editor."""

class MainFrame(wx.Frame):
    """Frame class that presets menu with graph options."""

    def __init__(self, parent=None, id=-1,
                 pos=wx.DefaultPosition,
                 title="Graph Editor"):
        wx.Frame.__init__(self, parent, id, title, pos)
        # Add the Canvas
        self.filename = ""
        self.grid = None
        canvas = FC.FloatCanvas(self, size = (500,500), ProjectionFun = None,
                                Debug = 0, BackgroundColor = "Purple")
        self.canvas = canvas
        self.canvas.Bind(wx.EVT_SIZE, self.OnSize)
        self.CreateStatusBar()
        self.createMenuBar()
        self.wildcard = "Graph files (*.graph)|*.graph|All files (*.*)|*.*"

    def menuData(self):
        return ("&File",
                ("&New", "Create a new graph", self.OnNew),
                ("&Open", "Open a saved graph", self.OnOpen),
                ("&Save", "Save a graph", self.OnSave),
                ("&Record", "Record moves", self.OnRecord),
                ("&Quit", "Quit", self.OnCloseWindow))

    def createMenuBar(self):
        menuBar = wx.MenuBar()
        eachMenuData = self.menuData()
        menuLabel = eachMenuData[0]
        menuItems = eachMenuData[1:]
        menuBar.Append(self.createMenu(menuItems), menuLabel)
        self.SetMenuBar(menuBar)

    def createMenu(self, menuData):
        menu = wx.Menu()
        for eachLabel, eachStatus, eachHandler in menuData:
            menuItem = menu.Append(-1, eachLabel, eachStatus)
            self.Bind(wx.EVT_MENU, eachHandler, menuItem)
        return menu

    def OnRecord(self, event):
        pass

    def OnSize(self, event):
        """
        re-zooms the canvas to fit the window

        """
        self.canvas.ZoomToBB()
        event.Skip()

    def OnNew(self, event):
        if self.grid == None:
            self.prompt()
            event.Skip()
        else:
            self.grid.clearAll()
            self.grid = None
            self.filename = None
            self.prompt()
            event.Skip()

    def OnCloseWindow(self, event):
        self.Destroy()

    def saveFile(self):
        if self.filename:
            data = self.grid.getGraph()
            file_buf = open(self.filename, 'w')
            cPickle.dump(data, file_buf)
            file_buf.close()

    def readFile(self):
        if self.filename:
            try:
                file_buf = open(self.filename, 'r')
                data = cPickle.load(file_buf)
                file_buf.close()
                if self.grid == None:
                    self.grid = Grid(self.canvas, graph = data)
                else:
                    self.grid.clearAll()
                    self.grid = None
                    self.grid = Grid(self.canvas, graph = data)
            except cPickle.UnpicklingError:
                wx.MessageBox("%s is not a graph file." % self.filename,
                              "oops!", style=wx.OK|wx.ICON_EXCLAMATION)

    def OnOpen(self, event):
        dlg = wx.FileDialog(self, "Open sketch file...", os.getcwd(),
                           style=wx.OPEN, wildcard=self.wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetPath()
            self.readFile()
        dlg.Destroy()

    def OnSave(self, event):
        if self.grid != None:
            if not self.filename:
                self.OnSaveAs(event)
            else:
                self.saveFile()
        else:
            wx.MessageBox("A graph has not been loaded.",
                          "oops!", style=wx.OK|wx.ICON_EXCLAMATION)


    def OnSaveAs(self, event):
        dlg = wx.FileDialog(self, "Save graph as...", os.getcwd(),
                           style=wx.SAVE | wx.OVERWRITE_PROMPT,
                           wildcard = self.wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            if not os.path.splitext(filename)[1]:
                filename = filename + '.graph'
            self.filename = filename
            self.saveFile()
        dlg.Destroy()

    def prompt(self):
        wx.StaticText(self.canvas, -1, 
                      "Enter dimension of square graph that is < 20.", (100,10))
        self.txt = wx.TextCtrl(self.canvas, -1, "", (100,30))
        self.txt.SetFocus()
        self.txt.Bind(wx.EVT_KEY_DOWN, self.OnTextCtrl, self.txt)

    def hide(self):
        for child in self.canvas.GetChildren():
            child.Hide()

    def OnTextCtrl(self, event):
        keycode = event.GetKeyCode()
        dimen = self.txt.GetValue()
        if keycode == wx.WXK_RETURN:
            if dimen.isdigit():
                graph_dimen = int(dimen)
                if graph_dimen <= 20:
                    self.hide()
                    self.grid = Grid(self.canvas, int(dimen))
                else:
                    wx.StaticText(self.canvas, -1, "Entry > 20.  Try Again!",
                                  (100,70))
            else:
                wx.StaticText(self.canvas, -1, "Entry wasn't a digit, Retry!",
                              (100,70))
                self.prompt()
        event.Skip()

class Grid(object):
    def __init__(self, canvas, dimen=None, graph=None):
        self.canvas = canvas
        if graph == None:
            self.graph = Graph(dimen)
            self.old_graph = False
        else:
            self.graph = graph
            self.old_graph = True
        self.grid_edges = {}
        self.circ_dict = {}
        self.drawGraph()

    def drawGraph(self):
        dimen = self.graph.get_graph_dimen()
        self.drawCircles(dimen)
        self.drawLines(dimen)
        if self.old_graph:
            self.showEdges(dimen)
        self.canvas.ZoomToBB()

    def drawCircles(self, dimen):
        dia = 8
        offset = 10
        for i in range(dimen):
            for j in range(dimen):
                circ = self.canvas.AddCircle((i*offset, j*offset), dia,
                                             FillColor="White")
                circ.grid_pos= (i, j)
                self.circ_dict[(i, j)] = circ
                circ.Bind(FC.EVT_FC_LEFT_DOWN, self.CircleHitLeft)

    def drawLines(self, dimen):
        for i in range(dimen):
            for j in range(dimen):
                adj_vert = self.graph.get_adj((i, j))
                for vert in adj_vert:
                    # simplyify check if xy is sufficient in giving the position
                    pos_1 = (self.circ_dict[vert].XY[0], 
                             self.circ_dict[vert].XY[1])
                    pos_2 = (self.circ_dict[(i, j)].XY[0], 
                             self.circ_dict[(i, j)].XY[1])
                    line = self.canvas.AddLine([(pos_1), (pos_2)],
                                               LineColor="Red")
                    self.grid_edges[vert, (i, j)] = line
                    self.grid_edges[(i, j), vert] = line
                    line.Hide()

    def showEdges(self, dimen):
        for i in range(dimen):
            for j in range(dimen):
                adj_vert = self.graph.get_adj((i, j))
                for vert in adj_vert:
                    # Code for adding graph edges to canvas from a loaded
                    # graph object
                    edge = ((i, j), vert)
                    if self.graph.is_edge(edge):
                        self.grid_edges[(i, j), vert].PutInForeground()
                        self.grid_edges[(i, j), vert].Show()
        
    def CircleHitLeft(self, circ):
        """After clicking circle, if edge between adjcent vertices is visible, hide
           it. Else, show it.

        """
        for adj in self.graph.get_adj(circ.grid_pos):
            edge = (adj, circ.grid_pos)
            if self.grid_edges[edge].Visible and self.graph.is_edge(edge):
                self.graph.del_edge(edge)
                self.grid_edges[edge].Hide()
                
            else:
                self.graph.add_edge(edge)
                self.grid_edges[edge].PutInForeground()
                self.grid_edges[edge].Show()

        self.canvas.Draw(True)

    def getGraph(self):

        return self.graph

    def clearAll(self):
        
        self.canvas.ClearAll()
        self.canvas.Draw(True)
        
    def recordMove(self):
        pass

class Graph(object):
    def __init__(self, dimen):
        """Create a vert-vertex graph with no edges """
        self.num_vert = dimen ** 2
        self.dimen = dimen
        self.num_edges = 0
        self.edge_set = set()

    def get_graph_dimen(self):
        """Return number of vertices """
        return self.dimen

    def add_edge(self, edge):
        """Add edge a-b to this graph """
        vert_a = edge[0]
        vert_b = edge[1]
        if self.is_vert(vert_a) and self.is_vert(vert_b):
            if self.are_adj(vert_a, vert_b):
                if self.is_edge(edge):
                    return None
                else:
                    self.edge_set.add(edge)
                    self.num_edges += 1

    def is_edge(self, edge):
        """Return true if edge is a valid vertice in the graph

        """
        edge_inv = (edge[1], edge[0])
        if edge in self.edge_set or edge_inv in self.edge_set:
            return True
        else:
            return False

    def is_vert(self, vert):
        """Return true if vert is a valid vertice in the graph

        """
        if vert[0] in range(0, self.dimen):
            if vert[1] in range(0, self.dimen):
                return True
            else:
                return False
    def get_edges(self):
        """Return the edges dict

        """
        return self.edge_set
    
    def get_num_edges(self):
        """Return number of unique edges 

        """
        return self.num_edges

    def are_adj(self, vert_a, vert_b):
        """Return true if vert_a and vert_b are adjacent and therefore possible to
        connect

        """
        adj_vert_set = self.get_adj(vert_a)
        if vert_b in adj_vert_set:
            return True
        else:
            return False

    def get_adj(self, vert):

        """Vertices adjacent to vert """
        adj_vert_set = set()
        for x in range(-1, 2):
            for y in range(-1, 2):
                adj_vert = (vert[0] + x, vert[1] + y)
                if self.is_vert(adj_vert):
                    if adj_vert != vert:
                        adj_vert_set.add(adj_vert)
        return adj_vert_set

    def del_edge(self, edge):
        """Delete edge to this graph """
        edge_inv = (edge[1], edge[0])
        vert_a = edge[0]
        vert_b = edge[1]
        if self.is_vert(vert_a) and self.is_vert(vert_b):
            if self.are_adj(vert_a, vert_b):
                if self.is_edge(edge):
                    try:
                        self.edge_set.remove(edge)
                    except KeyError:
                        self.edge_set.remove(edge_inv)
                    self.num_edges -= 1
                else:
                    return None

class Recorder(object): 
    """Record circles clicked in order to produce graph solution
    """
    def __init__(self):
        self.moves_lst = []
        self.num_moves = 0

    def record(self, circ_grid_pos):
        self.moves_lst.append(circ_grid_pos)
        self.num_moves += 1
        
    def getRecord(self):
        return self.moves_lst
        
    def getMoves(self):
        return num_moves
    
def main():
    
    app = wx.App()
    frame = MainFrame(None)
    frame.Show(True)
    app.MainLoop()
    
if __name__ == '__main__':
    main()
