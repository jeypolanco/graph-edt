try:
    import wx
    from wx.lib.floatcanvas import FloatCanvas as FC
except ImportError:
    print "Install wx-python2.8"
import shelve
import os
import sys

""" puzzle.py is a graph editor."""

class MainFrame(wx.Frame):
    """Frame class that presets menu with graph options."""

    def __init__(self, parent=None, id=-1,
                 pos=wx.DefaultPosition,
                 title="Graph Editor"):
        wx.Frame.__init__(self, parent, id, title, pos)
        self.filename = ""

        self.initpos = 300
        self.splitter_win = wx.SplitterWindow(self)
        
        # Create panels
        self.hist_frame = HistList(self.splitter_win)
        self.grid_frame = Grid(self.splitter_win)

        self.grid_frame.Bind(wx.EVT_SIZE, self.OnSize)

        status_bar = self.CreateStatusBar()
        self.splitter_win.parent = status_bar 
        self.createMenuBar()

        self.wildcard = "Graph files (*.graph)|*.graph|All files (*.*)|*.*"
        self.splitter_win.Initialize(self.grid_frame)

    def menuData(self):
        return ("&File",
                ("&New", "Create a new graph", self.OnNew),
                ("&Open", "Open a saved graph", self.OnOpen),
                ("&Save", "Save a graph", self.OnSave),
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

    def OnSize(self, event):
        """
        re-zooms the canvas to fit the window

        """
        self.grid_frame.ZoomToBB()
        event.Skip()

    def OnNew(self, event):
        """ Event called when the new label in the file menu is clicked.
        """
        if self.grid_frame.hasGraph():
            self.splitter_win.Unsplit(self.hist_frame)
            
            self.loadNewFrames()
            self.filename = None

            self.prompt()
            event.Skip()

        else:
            self.prompt()
            event.Skip()

    def loadNewFrames(self, graph=None, hist=None):
        """ Creates and loads new history and grid frames.
        """
        # Destroy current frames
        self.grid_frame.Destroy()
        self.hist_frame.Destroy()

        # Create new frames
        self.hist_frame = HistList(self.splitter_win, hist)
        self.grid_frame = Grid(self.splitter_win, graph, self.hist_frame)
        self.grid_frame.Bind(wx.EVT_SIZE, self.OnSize)
            
        # Initialize panel and make it fit frame
        self.splitter_win.Initialize(self.grid_frame)
        self.splitter_win.SizeWindows()

        if graph == None and hist == None:
            pass
        else:
            self.splitter_win.SplitVertically(self.grid_frame,
                                              self.hist_frame, self.initpos)
            
            
    def OnCloseWindow(self, event):
        self.Destroy()

    def saveFile(self):
        if self.filename:
            file_buf = shelve.open(self.filename)
            file_buf['graph'] = self.grid_frame.getGraph()
            file_buf['hist'] = self.hist_frame.getHist()
            file_buf.close()

    def readFile(self):
        if os.path.isfile(self.filename):
            file_buf = shelve.open(self.filename, 'r')
            graph = file_buf['graph']
            hist = file_buf['hist']
            file_buf.close()
            self.loadNewFrames(graph, hist)
        else:
            wx.MessageBox("%s is not a file." % self.filename,
                              "oops!", style=wx.OK|wx.ICON_EXCLAMATION)

    def OnOpen(self, event):
        dlg = wx.FileDialog(self, "Open sketch file...", os.getcwd(),
                           style=wx.OPEN, wildcard=self.wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetPath()
        if self.filename:
            self.readFile()
        dlg.Destroy()

    def OnSave(self, event):
        if self.grid_frame.hasGraph():
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
        """ Prompts user for the size of the graph.
        """
        wx.StaticText(self.grid_frame, -1, 
                      "Enter dimension of square graph that is < 20.", (100,10))
        self.txt = wx.TextCtrl(self.grid_frame, -1, "", (100,30))
        self.txt.SetFocus()
        self.txt.Bind(wx.EVT_KEY_DOWN, self.OnTextCtrl, self.txt)

    def hide(self):
        """ Hides widgets related to the prompt window.
        """
        for child in self.grid_frame.GetChildren():
            child.Hide()

    def OnTextCtrl(self, event):
        """ Event called when user is finished entering the size of graph.
        """
        keycode = event.GetKeyCode()
        dimen = self.txt.GetValue()
        if keycode == wx.WXK_RETURN:
            if dimen.isdigit():
                graph_dimen = int(dimen)
                if graph_dimen <= 20:
                    self.hide()
                    self.grid_frame.setHistFrame(self.hist_frame)
                    self.grid_frame.setGraphDim(graph_dimen)
                    self.grid_frame.drawGraph()

                    self.splitter_win.SplitVertically(self.grid_frame, self.hist_frame,
                                                      self.initpos)
                else:
                    wx.StaticText(self.grid_frame, -1, "Entry > 20.  Try Again!",
                                  (100,70))
            else:
                wx.StaticText(self.grid_frame, -1, "Entry wasn't a digit, Retry!",
                              (100,70))
                self.prompt()
        event.Skip()

class HistList(wx.ListCtrl):
    """Class shows the number of moves (ie clicks) the user makes in the course
    manipulating the graph.

    """
    def __init__(self, parent, move_hist=None):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        if move_hist == None:
            self.move_hist = Recorder()
            self.num = 0

        else:
            self.move_hist = move_hist
            self.num = self.move_hist.getMoves()

        self.itemDataMap = {}
        # add columns
        for col, data in enumerate(self.columnData()):
            self.InsertColumn(col, data)

        # add rows
        if move_hist == None:
            pass
        else:
            for item in enumerate(self.rowData()):
                index = self.InsertStringItem(0, str(item[0]))
                for row, data in enumerate(item[1:]):
                    self.SetStringItem(index, 1, str(data)) 
        self.Hide()

    def columnData(self):

        return ("Move #", "Circle clicked")

    def rowData(self):
        """This function is used for saving the data structure that histlist is based
        on

        """

        return self.move_hist.getHist()
    
    def update(self, circ_grid_pos):
        """ Updates both the history frame and it's representative data structure
        """
        
        self.move_hist.record(circ_grid_pos)
        index = self.InsertStringItem(0, str(self.num))
        self.SetStringItem(index, 1, str(circ_grid_pos))

        self.num += 1

    def getHist(self):
        """ Returns the data structure that stores the history
        """

        return self.move_hist

class Grid(FC.FloatCanvas):
    """  Frame responsible for drawing the graph.
    """
    def __init__(self, parent, graph=None, hist_frame = None):
        FC.FloatCanvas.__init__(self, parent, BackgroundColor = "Purple")
        self.parent = parent
        self.hist_frame = hist_frame
        self.graph = graph
        self.grid_edges = {}
        self.circ_dict = {}
        if self.graph == None:
            self.dimen = 0
        else:
            self.dimen = self.graph.getGraphDimen()
            self.drawGraph()

    def drawGraph(self):
        self.drawCircles(self.dimen)
        self.drawLines(self.dimen)
        self.showEdges(self.dimen)
        self.ZoomToBB()

    def drawCircles(self, dimen):
        dia = 8
        offset = 10
        for i in range(dimen):
            for j in range(dimen):
                circ = self.AddCircle((i*offset, j*offset), dia,
                                             FillColor="White")
                circ.grid_pos= (i, j)
                self.circ_dict[(i, j)] = circ
                circ.Bind(FC.EVT_FC_LEFT_DOWN, self.CircleHitLeft)
                circ.Bind(FC.EVT_FC_ENTER_OBJECT, self.OnEnterCircle)
                circ.Bind(FC.EVT_FC_LEAVE_OBJECT, self.OnLeaveCircle)

    def drawLines(self, dimen):
        for i in range(dimen):
            for j in range(dimen):
                adj_vert = self.graph.getAdj((i, j))
                for vert in adj_vert:
                    # simplyify check if xy is sufficient in giving the position
                    pos_1 = (self.circ_dict[vert].XY[0], 
                             self.circ_dict[vert].XY[1])
                    pos_2 = (self.circ_dict[(i, j)].XY[0], 
                             self.circ_dict[(i, j)].XY[1])
                    line = self.AddLine([(pos_1), (pos_2)],
                                               LineColor="Red")
                    self.grid_edges[vert, (i, j)] = line
                    self.grid_edges[(i, j), vert] = line
                    line.Hide()

    def showEdges(self, dimen):
        for i in range(dimen):
            for j in range(dimen):
                adj_vert = self.graph.getAdj((i, j))
                for vert in adj_vert:
                    # Code for adding graph edges to canvas from a loaded
                    # graph object
                    edge = ((i, j), vert)
                    if self.graph.isEdge(edge):
                        self.grid_edges[(i, j), vert].PutInForeground()
                        self.grid_edges[(i, j), vert].Show()
        
    def CircleHitLeft(self, circ):
        """After clicking circle, if edge between adjcent vertices is visible, hide
           it. Else, show it.

        """
        for adj in self.graph.getAdj(circ.grid_pos):
            edge = (adj, circ.grid_pos)
            if self.grid_edges[edge].Visible and self.graph.isEdge(edge):
                self.graph.delEdge(edge)
                self.grid_edges[edge].Hide()
            else:
                self.graph.addEdge(edge)
                self.grid_edges[edge].PutInForeground()
                self.grid_edges[edge].Show()

        self.updateHist(circ.grid_pos)

        self.Draw(True)
        
    def OnEnterCircle(self, circ):
        """ Event that shows the position of the circle in the status bar
        """
        self.parent.parent.SetStatusText("(%s, %s)"  % circ.grid_pos)

    def OnLeaveCircle(self, circ):
        """Event removes the position of the circle that we've just left in the status
        bar

        """

        self.parent.parent.SetStatusText("")

    def updateHist(self, circ_grid_pos):
        """ Updates the history frame whenever a circle is clicked
        """

        self.hist_frame.update(circ_grid_pos)

    def setGraphDim(self, graph_dimen):

        self.dimen = graph_dimen
        self.graph = Graph(self.dimen)

    def getGraph(self):

        return self.graph

    def setGraph(self, graph):
    
        self.graph = graph

    def setHistFrame(self, hist_frame):

        self.hist_frame = hist_frame

    def hasGraph(self):

        if not self.graph == None:
            return True
        else:
            return False
        
class Graph(object):
    def __init__(self, dimen):
        """Create a vert-vertex graph with no edges """
        self.num_vert = dimen ** 2
        self.dimen = dimen
        self.num_edges = 0
        self.edge_set = set()

    def getNumEdges(self):
        """ Return number of edges (for testing purposes).
        """
        return self.num_edges

    def getGraphDimen(self):
        """Return number of vertices """
        return self.dimen

    def addEdge(self, edge):
        """Add edge a-b to this graph """
        vert_a = edge[0]
        vert_b = edge[1]
        if self.isVert(vert_a) and self.isVert(vert_b):
            if self.areAdj(vert_a, vert_b):
                if self.isEdge(edge):
                    return None
                else:
                    self.edge_set.add(edge)
                    self.num_edges += 1

    def isEdge(self, edge):
        """Return true if edge is a valid vertice in the graph

        """
        edge_inv = (edge[1], edge[0])
        if edge in self.edge_set or edge_inv in self.edge_set:
            return True
        else:
            return False

    def isVert(self, vert):
        """Return true if vert is a valid vertice in the graph

        """
        if vert[0] in range(0, self.dimen):
            if vert[1] in range(0, self.dimen):
                return True
            else:
                return False
    
    def areAdj(self, vert_a, vert_b):
        """Return true if vert_a and vert_b are adjacent and therefore possible to
        connect

        """
        adj_vert_set = self.getAdj(vert_a)
        if vert_b in adj_vert_set:
            return True
        else:
            return False

    def getAdj(self, vert):

        """Vertices adjacent to vert """
        adj_vert_set = set()
        for x in range(-1, 2):
            for y in range(-1, 2):
                adj_vert = (vert[0] + x, vert[1] + y)
                if self.isVert(adj_vert):
                    if adj_vert != vert:
                        adj_vert_set.add(adj_vert)
        return adj_vert_set

    def delEdge(self, edge):
        """Delete edge to this graph """
        edge_inv = (edge[1], edge[0])
        vert_a = edge[0]
        vert_b = edge[1]
        if self.isVert(vert_a) and self.isVert(vert_b):
            if self.areAdj(vert_a, vert_b):
                if self.isEdge(edge):
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
        self.moves_hist = []
        self.num_moves = 0

    def record(self, circ_grid_pos):
        self.moves_hist.append(circ_grid_pos)
        self.num_moves += 1
        
    def getHist(self):
        return self.moves_hist
        
    def getMoves(self):
        return self.num_moves
    
def main():
    
    app = wx.App()
    frame = MainFrame(None)
    frame.Show(True)
    app.MainLoop()
    
if __name__ == '__main__':
    main()
