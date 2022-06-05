"""
Core class of the suite. Combines the "real" simulation with the editor.
This way some "useless" methods are added to some objects that are not 
needed for the editor or simulation, but the development of both does
not go in different directions.

========================================================================
                           by Claudius Mueller                          
version 1.0 (01-26-13)                                                       
========================================================================
"""

# Importing "official" modules
from PyQt4 import QtCore

# Importing "self-made" modules
from gui import gui_manager
from data import data_manager
from data import gridmap
from data import pathfinder

# test
import time

class CoreManager:
    """Core class of the program."""
    def __init__(self, app, qt_app):
        self.app = app
        self.qt_app = qt_app
        
        t1 = time.clock()
        self.gridmap = self.create_gridmap(200, 200)
        t2 = time.clock()
        print("gridmap:", t2-t1)
        
        t1 = time.clock()
        self.pathfinder = self.create_pathfinder()
        t2 = time.clock()
        print("pathfinder:", t2-t1)
        
        t1 = time.clock()
        self.data = data_manager.DataManager(self, self.gridmap, 
                                             self.pathfinder)
        t2 = time.clock()
        print("data:", t2-t1)
        
        t1 = time.clock()
        self.gui = gui_manager.GuiManager(app, self.data, self)
        t2 = time.clock()
        print("gui:", t2-t1)
        
        self.data.gui = self.gui
        
        app.setCentralWidget(self.gui.mapview)
        app.showMaximized()
        
        # managing the simulation game loop
        self.sim = False        # simulation is running or not
        self.timer = None
        self.paused = False
        self.speed = 30         # in msec
        
    def create_gridmap(self, ncols, nrows):
        """Create the gridmap."""
        return gridmap.GridMap(ncols, nrows)
        
    def create_pathfinder(self):
        """Create the pathfinder."""
        return pathfinder.PathFinder(self.gridmap.successors, 
                                     self.gridmap.move_cost, 
                                     self.gridmap.heuristic_to_goal)
        
    def simulation(self, state):
        """Start or stop simulation."""

        # if simulation not active - start it
        if state == True:
            self.sim = True
            
            # central simulation timer
            if not self.timer:
                self.timer = QtCore.QTimer(self.app)
                self.timer.timeout.connect(self.new_tick)
            self.timer.start(self.speed)
            
            # gui updates
            self.gui.setup_sim_gui()
            
        # if simulation active - deactivate it
        if state == False:
            self.sim = False
            
            # stop central simulation timer
            self.timer.stop()
            
            # gui updates
            self.gui.setup_editor_gui()

    def new_tick(self):
        self.data.advance_tick()
        self.gui.update_time()
        for actor in self.data.actors.values():
            actor.advance_tick()
            self.gui.infodock.update(actor)
        
    def pause(self):
        """Pause the game."""
        if self.paused == False:
            self.paused = True
            self.timer.stop()
        else:
            self.paused = False
            self.timer.start(self.speed)
        self.gui.update_speedlbl()
            
    def accelerate(self):
        """Speed up game by 2x."""
        self.speed = self.speed / 2
        self.timer.setInterval(self.speed)
        self.gui.update_speedlbl()
        
    def decelerate(self):
        """Slow down game by 2x."""
        self.speed = self.speed * 2
        self.timer.setInterval(self.speed)
        self.gui.update_speedlbl()
        
    def quit(self):
        """Quit game and exit."""
        self.app.close()
