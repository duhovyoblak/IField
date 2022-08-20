#==============================================================================
# Information field class GUI
#------------------------------------------------------------------------------
#

#------------------------------------------------------------------------------
import sys
sys.path.append('lib')

from   siqo_journal                    import SiqoJournal

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from mpl_toolkits                      import mplot3d

import math
import numpy             as np
import matplotlib.pyplot as plt
import tkinter           as tk

#==============================================================================
# package's constants
#------------------------------------------------------------------------------

_WIN            = '1680x1050'
_DPI            = 100

_FIG_W          = 0.99
_FIG_H          = 1.0

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
class IFieldGui:
    
    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------
    journal = None   # Pointer to global journal

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, obj):
        "Create and show GUI for Information field"

        IFieldGui.journal.I( 'IFieldGui constructor...')
        
        #----------------------------------------------------------------------
        # Internal data
        
        self.obj   = obj
        self.title = self.obj.objId
        
        #----------------------------------------------------------------------
        # Create output window
        win = tk.Tk()
        win.title(self.title)
        win.geometry(_WIN)
        win.resizable(False,False)
        win.update()
        self.w = win.winfo_width()
        self.h = win.winfo_height()
        
        #----------------------------------------------------------------------
        # Create layout

        self.fig = plt.figure(figsize=(self.w*_FIG_W/100, self.h*_FIG_H/100), dpi=_DPI)

        self.canvas = FigureCanvasTkAgg(self.fig, master=win)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().place(x=self.w*0.0, y=self.h*0.0)
        
        self.fig.canvas.callbacks.connect('button_press_event', self.on_click)
        
        #----------------------------------------------------------------------
        # Object scatter
        
        self.axObj = self.fig.add_subplot(1,2,1)
        self.axObj.set_title("{Title}", fontsize=14)
        self.axObj.grid(False)
        self.axObj.set_xlabel( 'X label' )
        self.axObj.set_ylabel( 'Y label')
        
        #----------------------------------------------------------------------
        # aidMatrix scatter
        
        self.axAim = self.fig.add_subplot(1,2,2)
        self.axAim.set_title("{Title}", fontsize=14)
        self.axAim.grid(True)
        self.axAim.set_xlabel( 'X label' )
        self.axAim.set_ylabel( 'Y label')
        
        #----------------------------------------------------------------------
        # Initialisation
        
        self.show()   # Initial drawing
        IFieldGui.journal.O( 'IFieldGui created for Objct {}'.format(self.title))

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
        
        IFieldGui.journal.I( f"{self.title}.getObjScatter" )

        x = []
        y = []
        u = []
        
        lenX = math.sqrt( len(self.obj.prtLst) )
        lenX = round(lenX + 0.5)

        i  = 0
        for obj in self.obj.prtLst:
            
            x.append(i %  lenX)
            y.append(i // lenX)
            u.append(self.obj.charVal( obj.objId ))
            i += 1
        
        X = np.array(x)
        Y = np.array(y)
        U = np.array(u)

        IFieldGui.journal.O( f"{self.title}.getObjScatter: return {i} data points")
        return (X, Y, U)
        
    #--------------------------------------------------------------------------
    def getAimScatter(self):
        "Returns plotable data for AutoIdentityMatrix"
        
        IFieldGui.journal.I( f"{self.title}.getAimScatter" )

        x = []
        y = []
        
        row = 0
        for aidVec in self.obj.aidMat:
            
            col = 0
            for val in aidVec:
                
                if val==1:
                    x.append(col)
                    y.append(row)
                col+=1
            row+=1

        X = np.array(x)
        Y = np.array(y)

        IFieldGui.journal.O( f"{self.title}.getAimScatter: ")
        return (X, Y)
        
    #==========================================================================
    # GUI methods
    #--------------------------------------------------------------------------
    def show(self):
        "Show Information field "
        
        IFieldGui.journal.I( f'IFieldGui{self.title}.show' )
        

        (X, Y, U) = self.getObjScatter()
        sctrObj = self.axObj.scatter( x=X, y=Y, c=U, marker="s", lw=0, s=4, cmap='RdYlBu_r')
#        self.fig.colorbar(sctrObj, ax=self.axObj)
            
        (X, Y) = self.getAimScatter()
        sctrAim = self.axAim.scatter( x=X, y=Y,color='black', marker='o', lw=0, s=(72./self.fig.dpi)**2)
        
        # Vykreslenie noveho grafu
        self.fig.tight_layout()
        self.canvas.draw()
    
        IFieldGui.journal.O( f'IFieldGui {self.title}.show done')
        
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
            
            x = float(event.xdata)
            y = float(event.ydata)

            # Ziskanie nastavenia grafu
            valX = self.values[self.actValX]
            valY = self.values[self.actValY]
            valS = self.values[self.actValS]
            
            x = x                                  / self.meta[valX]['coeff']
            y = y                                  / self.meta[valY]['coeff']
            s = self.getValByGrid(self.sVal, valS) / self.meta[valS]['coeff']
            
            pos = {'x':0, 'y':0, 'z':0, 't':0}
            pos[valX] = x
            pos[valY] = y
            pos[valS] = s
            
            id = self.space3M.getIdFromPos(pos)
            self.space3M.printCell(id)
            
        else:
            print('Clicked ouside axes bounds but inside plot window')
    
    #--------------------------------------------------------------------------

#------------------------------------------------------------------------------
print('Information field class GUI ver 0.30')
#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
