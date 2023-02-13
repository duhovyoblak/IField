#==============================================================================
# Information field class GUI
#------------------------------------------------------------------------------
#

#------------------------------------------------------------------------------
import sys
sys.path.append('..\siqo_lib')

from   siqo_tkchart        import SiqoChart

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from mpl_toolkits                      import mplot3d

import math
import numpy             as np
import matplotlib.pyplot as plt

import tkinter           as tk
from   tkinter           import ttk

import inf_lib           as lib

#==============================================================================
# package's constants
#------------------------------------------------------------------------------

_WIN            = '1400x800'
_MAX_ROWS       = 250
_MAX_COLS       = 500


_SC_RED         = 1.4

_BTN_AXE_W      = 0.81
_BTN_AXE_H      = 0.03

_BTN_VAL_W      = 0.81
_BTN_VAL_H      = 0.10

_BTN_DIS_W      = 0.1
_BTN_DIS_H      = 0.025

#==============================================================================
# class IFieldGui
#------------------------------------------------------------------------------
class IFieldGui():
    
    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------
    journal = None   # Pointer to global journal

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, journal, name, dat):
        "Create and show GUI for Information field"

        self.journal = journal
        self.journal.I( 'IFieldGui constructor...')
        
        #----------------------------------------------------------------------
        # Internal data
        #----------------------------------------------------------------------
        self.name   = name
        
        #----------------------------------------------------------------------
        # Initialise main window
        #----------------------------------------------------------------------
        self.win = tk.Tk()

        self.win.title(self.name)
        self.win.geometry(_WIN)
        self.win.resizable(True,True)
#        self.win.update()

        self.style = ttk.Style(self.win)
        self.style.theme_use('classic')
        
        #----------------------------------------------------------------------
        # Staus bar
        #----------------------------------------------------------------------


        #----------------------------------------------------------------------
        # Right over bar
        #----------------------------------------------------------------------
        frm_over = ttk.Frame(self.win) #, width=100
        frm_over.pack(fill=tk.Y, expand=True, side=tk.RIGHT, anchor=tk.E)

        self.btn_refr = ttk.Button(frm_over, text='Refresh', command=self.refresh)
        self.btn_refr.pack(ipadx=20, ipady=20, fill=tk.X, expand=True)

        #----------------------------------------------------------------------
        # Panned window with charts
        #----------------------------------------------------------------------
        pnw = ttk.PanedWindow(self.win, orient=tk.HORIZONTAL)

        # Left Chart
        
        
        self.left = SiqoChart(self.journal, 'Left IField visualisation', container=self.win)
        self.left.setData(dat)
        self.left.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        pnw.add(self.left)

        # Right chart
        self.right = SiqoChart(self.journal, 'Right IField visualisation', container=self.win)
        self.right.setData(dat)
        self.right.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
        pnw.add(self.right)

        # place the panedwindow on the root window
        pnw.pack(fill=tk.BOTH, expand=True)
       






        

        
        self.show()   # Initial drawing
        self.journal.O( 'IFieldGui created for Object {}'.format(self.name))

        self.win.mainloop()       # Start listening for events

    #--------------------------------------------------------------------------
    def refresh(self):
        
        self.show()


    #--------------------------------------------------------------------------
    def setData(self, dat):
        "Clears data and set new data"
        
        self.left.setData(dat)
        self.right.setData(dat)
        
        
        
    #==========================================================================
    # GUI methods
    #--------------------------------------------------------------------------
    def show(self):
        "Show Information field "
        
        self.journal.I( f'IFieldGui{self.name}.show' )
        
        self.left.show()
        self.right.show()

    
        self.journal.O( f'IFieldGui {self.name}.show done')
        
    #--------------------------------------------------------------------------
    def onButAxe(self):
        "Resolve radio buttons selection for active Axe of figure"
        
        self.actAxe = self.butAxeMap.get() # get integer value for selected button
        self.show()
    
    #--------------------------------------------------------------------------
    def onButValX(self):
        "Resolve radio buttons selection for active X Value in plot"
        
        self.actValX = self.butValMapX.get() # get integer value for selected button
        self.show()
    
    #--------------------------------------------------------------------------
    def onButValY(self):
        "Resolve radio buttons selection for active Y Value in plot"
        
        self.actValY = self.butValMapY.get() # get integer value for selected button
        self.show()
    
    #--------------------------------------------------------------------------
    def onButValU(self):
        "Resolve radio buttons selection for active U Value in plot"
        
        self.actValU = self.butValMapU.get() # get integer value for selected button
        self.show()
    
    #--------------------------------------------------------------------------
    def onButValV(self):
        "Resolve radio buttons selection for active V Value in plot"
        
        self.actValV = self.butValMapV.get() # get integer value for selected button
        self.show()
    
    #--------------------------------------------------------------------------
    def onSlider(self, new_val):
        "Resolve change of Slider"

        self.sVal = self.sldS.get()
        self.show()
    
    #--------------------------------------------------------------------------
    def on_click(self, event):
        "Print information about mouse-given position"
        
        if event.inaxes is not None:
            
            ax = event.inaxes.get_title()
            x = float(event.xdata)
            y = float(event.ydata)
            
            print(f'x={x},  y={y}, ax={ax}')

            
        else:
            print('Clicked ouside axes bounds but inside plot window')
    
    #--------------------------------------------------------------------------

#------------------------------------------------------------------------------
print('Information field class GUI ver 0.30')
#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
