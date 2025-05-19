#==============================================================================
# Info tkChart library
#------------------------------------------------------------------------------
import tkinter                as tk
from   tkinter                import (ttk, font, PanedWindow)
from   tkinter.messagebox     import showinfo

from   matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
#from   mpl_toolkits                      import mplot3d

import numpy                  as np
import matplotlib.pyplot      as plt

from   siqo_imatrix           import InfoMatrix

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_VER            = '2.0'
_WIN            = '1300x740'
_DPI            = 100

_FIG_W          = 0.8    # Figure width
_FIG_H          = 1.0    # Figure height

_COMBO_WIDTH    = 10
_PADX           =  5
_PADY           =  5

#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# Class InfoMarixGui
#------------------------------------------------------------------------------
class InfoMarixGui(ttk.Frame):
    
    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, journal, name, container, dat:InfoMatrix, **kwargs):
        "Call constructor of InfoMarixGui and initialise it for respective data"

        journal.I(f'{name}.init:')

        self.journal = journal             # Global journal
        self.name    = name                # Name of this chart
        self.dat     = dat                 # InfoMatrix base data
        self.sub2D   = {}                  # Subset of InfoMatrix data defined as frozen axes with desired values e.g. {'x':4, 't':17}
        
        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------
        self.w       = 1600                # Width of the chart in px
        self.h       =  900                # Height of the chart in px

        self.type     = '2D'               # Actual type of the chart
        self.iPoints  = []                 # List of InfoPoints to show
        self.actPoint = None               # Actual working InfoPoint
        
        self.keyV     =  None              # key for value to show
        self.keyX     = 'None'             # Default key for Axis X to show
        self.keyY     = 'None'             # Default key for Axis Y to show

        if 'keyV' in kwargs.keys(): self.keyV = kwargs['keyV']
        if 'keyX' in kwargs.keys(): self.keyX = kwargs['keyX']
        if 'keyY' in kwargs.keys(): self.keyY = kwargs['keyY']

        self.npX      = np.array([])       # np array for coordinate X
        self.npY      = np.array([])       # np array for coordinate Y
        self.npC      = np.array([])       # np array for value color
        self.npU      = np.array([])       # np array for quiver re value
        self.npV      = np.array([])       # np array for quiver im value

        #----------------------------------------------------------------------
        # Initialise original tkInter.Tk
        #----------------------------------------------------------------------
        super().__init__(container)

        #----------------------------------------------------------------------
        # Create head buttons bar
        #----------------------------------------------------------------------
        frmBtn = ttk.Frame(self)
        frmBtn.pack(fill=tk.X, expand=True, side=tk.TOP, anchor=tk.N)
 
        frmBtn.columnconfigure(0, weight=1)
        frmBtn.columnconfigure(1, weight=1)
        frmBtn.columnconfigure(2, weight=1)
        frmBtn.columnconfigure(3, weight=1)
        frmBtn.columnconfigure(4, weight=1)
        
        frmBtn.rowconfigure(0, weight=1)
        frmBtn.rowconfigure(1, weight=1)
        
        #----------------------------------------------------------------------
        # Value to show selector
        #----------------------------------------------------------------------
        self.strV = tk.StringVar(value='None') # Name of the value to show in the chart

        lblVal = ttk.Label(frmBtn, text="Value to show:")
        lblVal.grid(column=0, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbV = ttk.Combobox(frmBtn, textvariable=self.strV, width=_COMBO_WIDTH)
        self.cbV['values'] = list(self.dat.getVals().values())
        self.cbV['state' ] = 'readonly'
        self.cbV.bind('<<ComboboxSelected>>', self.dataChanged)
        self.cbV.grid(column=0, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)
        
        #----------------------------------------------------------------------
        # X axis dimension selector
        #----------------------------------------------------------------------
        self.strX   = tk.StringVar(value='None') # Name of the X-axis dimesion from ipType.axis, 'None' means nothing to show in this axis

        lblX = ttk.Label(frmBtn, text="Dim for X axis:")
        lblX.grid(column=1, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbX = ttk.Combobox(frmBtn, textvariable=self.strX, width=_COMBO_WIDTH)
        self.cbX['values'] = list(self.dat.getAxes().values())
        self.cbX['state' ] = 'readonly'
        self.cbX.bind('<<ComboboxSelected>>', self.dataChanged)
        self.cbX.grid(column=1, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)
        
        self.cbLogX = ttk.Checkbutton(frmBtn, text='LogX', command=self.show)
        self.cbLogX.grid(column=1, row=1, pady=_PADY)
        
        #----------------------------------------------------------------------
        # Y axis dimension selector
        #----------------------------------------------------------------------
        self.strY   = tk.StringVar(value='None') # Name of the Y-axis dimesion from ipType.axis, 'None' means nothing to show in this axis

        lblY = ttk.Label(frmBtn, text="Dim for Y axis:")
        lblY.grid(column=2, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbY = ttk.Combobox(frmBtn, textvariable=self.strY, width=_COMBO_WIDTH)
        self.cbY['values'] = list(self.dat.getAxes().values())
        self.cbY['state' ] = 'readonly'
        self.cbY.bind('<<ComboboxSelected>>', self.dataChanged)
        self.cbY.grid(column=2, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)
        
        self.cbLogY = ttk.Checkbutton(frmBtn, text='LogY', command=self.show)
        self.cbLogY.grid(column=2, row=1, pady=_PADY)

        #----------------------------------------------------------------------
        # Method to apply selector
        #----------------------------------------------------------------------
        self.strM = tk.StringVar(value='None') # Name of the method to apply to the data

        lblMet = ttk.Label(frmBtn, text="Apply:")
        lblMet.grid(column=3, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbM = ttk.Combobox(frmBtn, textvariable=self.strM, width=_COMBO_WIDTH)
        self.cbM['values'] = ['None', 'Clear Data', 'Random Bit 10%', 'Random Phase']
        self.cbM['state' ] = 'readonly'
        self.cbM.bind('<<ComboboxSelected>>', self.method)
        self.cbM.grid(column=3, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)

        #----------------------------------------------------------------------
        # Create a figure with the navigator bar and bind it to mouse events
        #----------------------------------------------------------------------
        self.figure = plt.figure(figsize=(self.w*_FIG_W/100, self.h*_FIG_H/100), dpi=_DPI)
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        
        self.canvas.callbacks.connect('button_press_event', self.on_click)
        
        NavigationToolbar2Tk(self.canvas, self)
        
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        #----------------------------------------------------------------------
        # Vytvorim Menu pre click on Point
        #----------------------------------------------------------------------
        self.pointMenu = tk.Menu(self, tearoff = 0)
        self.pointMenu.add_command(label ="Set to ( 0,0)", command=lambda c=complex( 0,0): self.setPoint(c))
        self.pointMenu.add_command(label ="Set to ( 1,0)", command=lambda c=complex( 1,0): self.setPoint(c))
        self.pointMenu.add_command(label ="Set to (-1,0)", command=lambda c=complex(-1,0): self.setPoint(c))
        self.pointMenu.add_command(label ="Set to (0, 1)", command=lambda c=complex(0, 1): self.setPoint(c))
        self.pointMenu.add_command(label ="Set to (0,-1)", command=lambda c=complex(0,-1): self.setPoint(c))
        
        #----------------------------------------------------------------------
        # Initialisation
        #----------------------------------------------------------------------
        self.dataChanged()

        self.journal.O()

    #--------------------------------------------------------------------------
    def is2D(self):
        "Returns True if this chart is 2D otherwise returns False"

        if self.keyX!='None' and self.keyY!='None': return True
        else                                      : return False
        
    #--------------------------------------------------------------------------
    def dataChanged(self, event=None, force=False):
        "Prepares npData to show"
        
        #----------------------------------------------------------------------
        # Read actual settings
        #----------------------------------------------------------------------
        aKeyV = self.dat.getValKey(self.cbV.current())
        aKeyX = self.dat.getAxeKey(self.cbX.current())
        aKeyY = self.dat.getAxeKey(self.cbY.current())
        
        self.journal.I(f'{self.name}.dataChanged: value={self.keyV}->{aKeyV}, X-axis={self.keyX}->{aKeyX}, Y-axis={self.keyY}->{aKeyY}')
        changed = False

        #----------------------------------------------------------------------
        # Changes in any key required data refresh
        #----------------------------------------------------------------------
        if (self.keyV!=aKeyV) or (self.keyX!=aKeyX) or (self.keyY!=aKeyY) or force: 
            
            changed = True

            #------------------------------------------------------------------
            # Vytvorim predpis pre aktualny subset
            #------------------------------------------------------------------
            self.keyV = aKeyV
            self.keyX = aKeyX
            self.keyY = aKeyY

            #------------------------------------------------------------------
            # Ziskam list InfoPoints (whole object) patriacich subsetu
            #------------------------------------------------------------------
            self.iPoints = self.dat.actMatrix(sub2D=self.sub2D, struct='list')

        #----------------------------------------------------------------------
        # Ak nenastala zmena, vyskocim
        #----------------------------------------------------------------------
        if not changed: self.journal.M(f'{self.name}.dataChanged: Settings have not changed, no need for show')
        else          : self.show()
        
        self.journal.O()
        
    #==========================================================================
    # Show the chart
    #--------------------------------------------------------------------------
    def show(self, event=None):
        """Vykresli chart na zaklade aktualneho listu self.cIP
        """
        self.journal.I(f'{self.name}.show:')

        #----------------------------------------------------------------------
        # Check list of InfoPoints to show
        #----------------------------------------------------------------------
        if len(self.iPoints) == 0:
            self.journal.M(f'{self.name}.show: No InfoPoints, nothig to show', True)
            self.journal.O()
            return

        #----------------------------------------------------------------------
        # Check axis to show
        #----------------------------------------------------------------------
        if self.keyX=='None' and self.keyY=='None':
            self.journal.M(f'{self.name}.show: No axis selected, nothig to show', True)
            self.journal.O()
            return
        
        #----------------------------------------------------------------------
        # Prepare the data for the chart
        #----------------------------------------------------------------------




        if self.npC.size==0:
            self.journal.M(f'{self.name}.show: No values to show', True)
            self.journal.O()
            return

        if  self.is2D() and (self.npX.size==0 or self.npY.size==0):
            self.journal.M(f'{self.name}.show: No axes to show', True)
            self.journal.O()
            return



        #----------------------------------------------------------------------
        # Prepare the chart
        #----------------------------------------------------------------------
        self.figure.clear() 
        self.chart = self.figure.add_subplot()

#        self.chart.set_title(val, fontsize=14)
        self.chart.grid(False)
        self.chart.set_facecolor('white')
        self.chart.set_xlabel(self.keyX)
        self.chart.set_ylabel(self.keyY)
        
        #----------------------------------------------------------------------
        # Log axis X, Y
        #----------------------------------------------------------------------
        if 'selected' in self.cbLogX.state(): self.chart.set_xscale('log')
        if 'selected' in self.cbLogY.state(): self.chart.set_yscale('log')
        
        #----------------------------------------------------------------------
        # Show the chart
        #----------------------------------------------------------------------
        if self.is2D():
            #------------------------------------------------------------------
            # Chart 2D
            #------------------------------------------------------------------
            chrtObj = self.chart.scatter( x=self.X, y=self.Y, c=self.C, marker="s", cmap='RdYlBu_r')
#            chrtObj = self.chart.scatter( x=self.X, y=self.Y, c=self.C, marker="s", lw=0, s=(72./self.figure.dpi)**2, cmap='RdYlBu_r')
            self.figure.colorbar(chrtObj, ax=self.chart)

        else:
            #------------------------------------------------------------------
            # Chart 1D
            #------------------------------------------------------------------
            if self.keyX=='None': axis = self.X
            else                : axis = self.Y

#            chrtObj = self.chart.scatter( x=self.C, y=self.Y, linewidths=1 ) #, edgecolors='gray')
            chrtObj = self.chart.plot( self.C, axis ) #, edgecolors='gray')
        
        #----------------------------------------------------------------------
        # Vykreslenie noveho grafu
        #----------------------------------------------------------------------
        self.figure.tight_layout()
        self.update()
        self.canvas.draw()
        
        #----------------------------------------------------------------------
        self.journal.O()
        
    #--------------------------------------------------------------------------
    def on_click(self, event):
        "Print information about mouse-given position"
        
        self.journal.I(f'{self.name}.on_click:')

        if event.inaxes is not None:
            
#            ax  = event.inaxes.get_title()
            btn = event.button
            #           btn = event.num
            x = round(float(event.xdata), 3)
            y = round(float(event.ydata), 3)
            
            if self.is2D(): coord = [y, x]
            else          : coord = [y   ]
            
            self.actPoint = self.dat.getPointByPos(coord)
            
            #------------------------------------------------------------------
            # Left button
            #------------------------------------------------------------------
            if btn == 1 and False: #MouseButton.LEFT:
               tit = f'Nearest point to [{round(y,2)}, {round(x,2)}]'
               mes = str(self.actPoint)
               showinfo(title=tit, message=mes)
            
            #------------------------------------------------------------------
            # Right button - edit value menu
            #------------------------------------------------------------------
            elif btn == 3: #MouseButton.RIGHT:
                
                self.journal.M(f'{self.name}.on_click: right click for {self.actPoint}')
                
                try    : self.pointMenu.tk_popup(event.x, event.y)
                finally: self.pointMenu.grab_release()
            
            #------------------------------------------------------------------
            
        else:
            self.actPoint = None
            print('Clicked ouside axes bounds but inside plot window')
        
        self.journal.O()

    #==========================================================================
    # Method to apply
    #--------------------------------------------------------------------------
    def method(self, event=None):
        "Apply data in active cut"
        
        met = self.strM.get()
        self.journal.I(f'{self.name}.method: {met} with subset = {self.sub2D}')


        if met != 'None':self.dataChanged()
        self.journal.O()

    #--------------------------------------------------------------------------
    def reset(self):
        "Reset all data into default values"

        self.iPoints  = []                 # List of InfoPoints to show
        self.actPoint = None               # Actual working InfoPoint
        
        self.keyV     =  None              # key for value to show
        self.keyX     = 'None'             # Default key for Axis X to show
        self.keyY     = 'None'             # Default key for Axis Y to show

        self.npX      = np.array([])       # np array for coordinate X
        self.npY      = np.array([])       # np array for coordinate Y
        self.npC      = np.array([])       # np array for value color
        self.npU      = np.array([])       # np array for quiver re value
        self.npV      = np.array([])       # np array for quiver im value

        self.journal.M(f'{self.name}.reset: done')

    #--------------------------------------------------------------------------
    def clear(self):
        "Clears all data but structure is preserved"
        
        self.journal.I(f'{self.name}.clear:')

        #----------------------------------------------------------------------
        # Clear InfoMatrix base data
        #----------------------------------------------------------------------
        self.dat.clear()

        #----------------------------------------------------------------------
        # Reset GUI
        #----------------------------------------------------------------------
        self.reset()

        self.journal.O()

    #--------------------------------------------------------------------------
    def setData(self, dat:InfoMatrix):
        "Reset matrix and set new data"
        
        self.clear()
        self.dat = dat
        self.journal.M(f'{self.name}.setData: New data name = {self.dat.name}')

    #--------------------------------------------------------------------------
    def setPoint(self, c):
        
        self.journal.M(f'{self.name}.setPoint: {self.actPoint} = {c}')
        
        self.actPoint.setComp(c)
        self.dataChanged()
        
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
#        return lib.spiralData(baseObj=self.obj, vec=self.obj.prtLst)
        
        
        

#==============================================================================
#   Inicializacia kniznice
#------------------------------------------------------------------------------
print(f'SIQO InfoMarixGui library ver {_VER}')

if __name__ == '__main__':

    from   siqolib.journal          import SiqoJournal
    from   siqo_imatrix             import InfoMatrix

    journal = SiqoJournal('InfoMarixGui component test', debug=4)

    #--------------------------------------------------------------------------
    # Test of the InfoMarixGui class
    #--------------------------------------------------------------------------
    journal.I('Test of InfoMarixGui class')

    win = tk.Tk()
    win.configure(bg='silver', highlightthickness=2, highlightcolor='green')
    win.title('Test of InfoModelGui class')
    win.maxsize(width=1200, height=800)
    win.minsize(width=600, height=300)
    win.config(highlightbackground = "green", highlightcolor= "green")

    #tk.Grid.columnconfigure(win, 1, weight=1)
    #tk.Grid.rowconfigure   (win, 2, weight=1)

    #--------------------------------------------------------------------------
    # Zaciatok testu 
    #--------------------------------------------------------------------------
    matrix = InfoMatrix(journal, 'Test field', 'ipTest')
    matrix.gener(cnts={'x':3, 'y':4, 'z':2}, origs={'x':0, 'y':0, 'z':0}, rect={'x':5, 'y':5, 'z':2}, vals={'m':'hmotnosť', 'v':'rýchlosť'}, defs={'m':1, 'v':2})
    print(matrix)

    matrixGui = InfoMarixGui(journal, name='Test of InfoModelGui class', container=win, dat=matrix)
    matrixGui.pack(fill=tk.BOTH, expand=True, side=tk.TOP, anchor=tk.N)

    matrixGui.sub2D = {'z':1}

    win.mainloop()

    journal.O()

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------