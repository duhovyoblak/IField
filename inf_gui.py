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
class IFieldGui(tk.Tk):
    
    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------
    journal = None   # Pointer to global journal

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, journal, name):
        "Create and show GUI for Information field"

        self.journal = journal
        self.journal.I( 'IFieldGui constructor...')
        
        #----------------------------------------------------------------------
        # Internal data
        
        self.name   = name
#        self.obj   = obj
#        self.name = self.obj.objId
        
        #----------------------------------------------------------------------
        # Initialise original tkInter.Tk
        #----------------------------------------------------------------------
        super().__init__()

#        win = tk.Tk()
        self.title(self.name)
        self.geometry(_WIN)
        self.resizable(False,False)
        self.update()
        
#        self.w = win.winfo_width()
#        self.h = win.winfo_height()
        
        self.chart = SiqoChart(self.journal, 'IField visualisation', container=self)



        self.journal.O( 'IFieldGui created for Object {}'.format(self.name))

        self.mainloop()       # Start listening for events
        return

        #----------------------------------------------------------------------
        # Create layout

        self.fig = plt.figure(figsize=(self.w*_FIG_W/100, self.h*_FIG_H/100), dpi=_DPI)

        self.canvas = FigureCanvasTkAgg(self.fig, master=win)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().place(x=self.w*0.0, y=self.h*0.0)
        
        self.fig.canvas.callbacks.connect('button_press_event', self.on_click)
        
        #----------------------------------------------------------------------
        # Object scatter
        
        self.axObj = self.fig.add_subplot(2,2,1)
        self.axObj.set_title("Encoded values by rank", fontsize=14)
        self.axObj.grid(False)
        self.axObj.set_facecolor('black')
#        self.axObj.set_xlabel( 'X label' )
#        self.axObj.set_ylabel( 'Y label')
        
        #----------------------------------------------------------------------
        # aidMatrix scatter
        
        self.axAim = self.fig.add_subplot(2,2,2)
        self.axAim.set_title("Length of virt vs. delta by count", fontsize=14)
        self.axAim.grid(False)
        self.axAim.set_facecolor('black')
        self.axAim.set_xlabel( 'Delta' )
        self.axAim.set_ylabel( 'Length of virtual patrticle')
        
        #----------------------------------------------------------------------
        # aidVector plot
        
        self.axAiv = self.fig.add_subplot(2,2,3)
        self.axAiv.set_title("Aggregated autoidentity", fontsize=14)
        self.axAiv.grid(True)
        self.axAiv.set_xlabel( 'Delta' )
        self.axAiv.set_ylabel( 'Ratio of Identities')
        
        #----------------------------------------------------------------------
        # eimMatrix scatter
        
        self.axEim = self.fig.add_subplot(2,2,4)
        self.axEim.set_title("asv", fontsize=14)
        self.axEim.grid(False)
        self.axEim.set_facecolor('black')
        self.axEim.set_xlabel( 'Delta' )
        self.axEim.set_ylabel( 'trticle')
        
        #----------------------------------------------------------------------
        # Initialisation
        
        self.show()   # Initial drawing
        self.journal.O( 'IFieldGui created for Object {}'.format(self.name))

        win.mainloop()       # Start listening for events

    #==========================================================================
    # Tools for figure setting
    #--------------------------------------------------------------------------
    def getDataLabel(self, key):
        "Return data label for given data's key"
        
        return "${}$ [{}{}]".format(key, self.meta[key]['unit'], 
                                         self.meta[key]['dim' ])
    
    #--------------------------------------------------------------------------
    def getValByGrid(self, gv, key):
        "Return rescaled value for given grid's value and data's key"
        
        gl = self.meta['g'+key]['max'] - self.meta['g'+key]['min']
        vl = self.meta[    key]['max'] - self.meta[    key]['min']
        
        return (gv/gl) * vl * self.meta[key]['coeff']
    
    #--------------------------------------------------------------------------
    def getObjScatter(self):
        "Returns plotable data for Object value"
        
        self.journal.M( f"{self.name}.getObjScatter" )

#        return lib.squareData(baseObj=self.obj, vec=self.obj.prtLst)
        return lib.spiralData(baseObj=self.obj, vec=self.obj.prtLst)
        
    #--------------------------------------------------------------------------
    def getAimScatter(self):
        "Returns plotable data for AutoIdentityMatrix"
        
        self.journal.I( f"{self.name}.getAimScatter" )

        x = []
        y = []
        
        rows = min(_MAX_ROWS, len(self.obj.aidMat))
        
        row = 0
        for row in range(rows):
            
            aidVec = self.obj.aidMat[row]
            
            cols = min(_MAX_COLS, len(aidVec))
            for col in range(cols):
                
                if aidVec[col]==1:
                    y.append(col)
                    x.append(row)
                col+=1
            row+=1

        X = np.array(x)
        Y = np.array(y)

        self.journal.O( f"{self.name}.getAimScatter: ")
        return (X, Y)
        
    #==========================================================================
    # GUI methods
    #--------------------------------------------------------------------------
    def show(self):
        "Show Information field "
        
        self.journal.I( f'IFieldGui{self.name}.show' )
        

        (X, Y, U) = self.getObjScatter()
        sctrObj = self.axObj.scatter( x=X, y=Y, c=U, marker="s", lw=0, s=(72./self.fig.dpi)**2, cmap='RdYlBu_r')
        self.fig.colorbar(sctrObj, ax=self.axObj)
            
        (X, Y) = self.getAimScatter()
        sctrAim = self.axAim.scatter( x=X, y=Y,color='white', marker='o', lw=0, s=(72./self.fig.dpi)**2)
        
#        (X, Y) = self.getAimScatter()
        sctrAiv = self.axAiv.plot( np.array(self.obj.aidVec))

        (X, Y) = self.getAimScatter()
        sctrEim = self.axEim.scatter( x=X, y=Y, color='blue', marker='o', lw=0, s=(72./self.fig.dpi)**2)

        # Vykreslenie noveho grafu
        self.fig.tight_layout()
        self.canvas.draw()
    
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
