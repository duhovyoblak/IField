#==============================================================================
# Info tkChart library
#------------------------------------------------------------------------------
import sys
sys.path.append('..\siqo_lib')

import tkinter                as tk
from   tkinter                import (ttk, font, PanedWindow)
from   tkinter.messagebox     import showinfo

from   matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
#from   mpl_toolkits                      import mplot3d

import numpy             as np
import matplotlib.pyplot as plt

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_WIN            = '1300x740'
_DPI            = 100

_FIG_W          = 0.8    # Figure width
_FIG_H          = 1.0    # Figure height

_PADX           = 5
_PADY           = 5

#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# Class InfoChart
#------------------------------------------------------------------------------
class InfoChart(ttk.Frame):
    
    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, journal, name, container, dat, **kwargs):
        "Call constructor of InfoChart and initialise it for respective data"

        journal.I(f'{name}.init:')

        self.journal = journal         # Global journal
        self.name    = name            # Name of this chart
        self.dat     = dat             # ComplexField data
        self.myCut   = []              # Cut of ComplexField data for this GUI
        self.w       = 1600            # width of the chart
        self.h       =  900            # Height of the chart
        
        self.strVal = tk.StringVar()   # Name of the value to show in the chart
        self.strMet = tk.StringVar()   # Name of the method to apply to the data
        self.strX   = tk.StringVar()   # Name of the X-axis dimesion from ['0', '1', '2', etc.]
                                       # '0' means No value to show if this axis
        self.strY   = tk.StringVar()   # Name of the Y-axis dimesion from ['0', '1', '2', etc.]
        
        if 'val' in kwargs.keys(): self.strVal.set(kwargs['val'])
        else                     : self.strVal.set('re')          # Default is real part of points

        if 'axX' in kwargs.keys(): self.strX.set(kwargs['axX'])
        else                     : self.strX.set('0')             # Default is No data to show on X 

        if 'axY' in kwargs.keys(): self.strY.set(kwargs['axY'])
        else                     : self.strY.set('1')             # Default is 1-st dimension

        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------
        self.type     = '2D'           # Actual type of the chart
        self.CPs      = []             # List of values (cP) to show
        self.actPoint = None           # Actual working point (cP)
        
        self.keyX     = ''             # Dimension name for coordinate X
        self.X        = None           # np array for coordinate X
        self.keyY     = ''             # Dimension name for coordinate Y
        self.Y        = None           # np array for coordinate Y
        self.C        = None           # np array for value color
        self.U        = None           # np array for quiver re value
        self.V        = None           # np array for quiver im value

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
        lblVal = ttk.Label(frmBtn, text="Value to show:")
        lblVal.grid(column=0, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbVal = ttk.Combobox(frmBtn, textvariable=self.strVal, width=5)
        self.cbVal['values'] = ['re', 'im', 'phase', 'abs', 'sqr']
        self.cbVal['state' ] = 'readonly'
        self.cbVal.bind('<<ComboboxSelected>>', self.show)
        self.cbVal.grid(column=0, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)
        
        #----------------------------------------------------------------------
        # X axis dimension selector
        #----------------------------------------------------------------------
        lblX = ttk.Label(frmBtn, text="Dim for X axis:")
        lblX.grid(column=1, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbX = ttk.Combobox(frmBtn, textvariable=self.strX, width=5)
        self.cbX['values'] = ['0', '1', '2', '3']
        self.cbX['state' ] = 'readonly'
        self.cbX.bind('<<ComboboxSelected>>', self.dataChanged)
        self.cbX.grid(column=1, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)
        
        self.cbLogX = ttk.Checkbutton(frmBtn, text='LogX', command=self.show)
        self.cbLogX.grid(column=1, row=1, pady=_PADY)
        
        #----------------------------------------------------------------------
        # Y axis dimension selector
        #----------------------------------------------------------------------
        lblY = ttk.Label(frmBtn, text="Dim for Y axis:")
        lblY.grid(column=2, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbY = ttk.Combobox(frmBtn, textvariable=self.strY, width=5)
        self.cbY['values'] = ['1', '2', '3']
        self.cbY['state' ] = 'readonly'
        self.cbY.bind('<<ComboboxSelected>>', self.dataChanged)
        self.cbY.grid(column=2, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)
        
        self.cbLogY = ttk.Checkbutton(frmBtn, text='LogY', command=self.show)
        self.cbLogY.grid(column=2, row=1, pady=_PADY)

        #----------------------------------------------------------------------
        # Method to apply selector
        #----------------------------------------------------------------------
        lblMet = ttk.Label(frmBtn, text="Apply:")
        lblMet.grid(column=3, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbMet = ttk.Combobox(frmBtn, textvariable=self.strMet, width=10)
        self.cbMet['values'] = ['None', 'Clear Data', 'Random Bit 10%', 'Random Phase']
        self.cbMet['state' ] = 'readonly'
        self.cbMet.bind('<<ComboboxSelected>>', self.method)
        self.cbMet.grid(column=3, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)

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
    def is1D(self):
        "Returns True if this chart is 1D otherwise returns False"

        # Only axis X can be void
        axX = int(self.strX.get())
        
        if axX==0: return True
        else     : return False
        
    #--------------------------------------------------------------------------
    def dataChanged(self, event=None):
        "Prepares cut of the dat and assignes self.CPs to show"
        
        #----------------------------------------------------------------------
        # Read actual settings
        #----------------------------------------------------------------------
        axX = int(self.strX.get())    # Dimension number to show on X axis
        axY = int(self.strY.get())    # Dimension number to show on Y axis
        
        self.journal.I(f'{self.name}.dataChanged: axX={axX}, axY={axY}')

        #----------------------------------------------------------------------
        # Set actual filter according to user settings
        #----------------------------------------------------------------------
        if self.is1D(): self.myCut = self.dat.cutDim(1)
        else          : self.myCut = self.dat.cutDim(2)
        
        self.journal.M(f'{self.name}.dataChanged: cut={self.myCut}')

        #----------------------------------------------------------------------
        # Get dat = [ {'key':'x1',  'val':np_array},     dim X1
        #             {'key':'x2',  'val':np_array},     dim X2
        #                .
        #                .
        #             {'key':'val', 'val':[cP]    }      values
        #           ]
        #----------------------------------------------------------------------
        dat = self.dat.getData(cut=self.myCut)

        #----------------------------------------------------------------------
        # Assign coordinate arrays for Y axis
        #----------------------------------------------------------------------
        self.keyY = dat[axY-1]['key']
        self.Y    = dat[axY-1]['arr']
        self.journal.M(f'{self.name}.dataChanged: keyY={self.keyY}')
        
        #----------------------------------------------------------------------
        # Assign coordinate arrays for X axis
        #----------------------------------------------------------------------
        if self.is1D():
            self.keyX = 'No dimension'
            self.X    = np.zeros(len(self.Y))
            
        else:
            self.keyX = dat[axX-1]['key']
            self.X    = dat[axX-1]['arr']

        self.journal.M(f'{self.name}.dataChanged: keyX={self.keyX}')
        
        #----------------------------------------------------------------------
        # Remember values (list of cP) for this dataset
        # It is the last item in the dat list
        #----------------------------------------------------------------------
        self.CPs = dat[-1]['arr']
        
        self.journal.O()
        self.show()
        
    #==========================================================================
    # Method to apply
    #--------------------------------------------------------------------------
    def method(self, event=None):
        "Apply data in active cut"
        
        met = self.strMet.get()
        self.journal.I(f'{self.name}.method: {met} with cut = {self.myCut}')

        self.dat.cutSet(self.myCut)

        if   met == 'Clear Data'    : self.clear()
        elif met == 'Random Bit 10%': self.rndBit(0.1)
        elif met == 'Random Phase'  : self.rndPhase()

        if met != 'None':self.dataChanged()
        self.journal.O()

    #--------------------------------------------------------------------------
    def clear(self):
        "Clears data in active cut"
        
        self.journal.I(f'{self.name}.clear: with cut = {self.myCut}')

        for node in self.dat:
            node['cP'].clear()
            
        self.journal.O()

    #--------------------------------------------------------------------------
    def rndBit(self, prob):
        ""
        
        self.journal.I(f'{self.name}.rndBit: with cut = {self.myCut} and prob = {prob}')

        for node in self.dat:
            node['cP'].rndBit(prob)
            
        self.journal.O()

    #--------------------------------------------------------------------------
    def rndPhase(self):
        ""
        
        self.journal.I(f'{self.name}.rndPhase: with cut = {self.myCut}')

        for node in self.dat:
            node['cP'].rndPhase()
            
        self.journal.O()

    #--------------------------------------------------------------------------
    def setData(self, dat):
        "Clears data and set new data"
        
        self.dat = dat
        
    #--------------------------------------------------------------------------
    def setPoint(self, c):
        
        self.journal.M(f'{self.name}.setPoint: {self.actPoint} = {c}')
        
        self.actPoint.setComp(c)
        self.dataChanged()
        
    #==========================================================================
    # Show the chart
    #--------------------------------------------------------------------------
    def show(self, event=None):

        self.journal.I(f'{self.name}.show:')
        
        #----------------------------------------------------------------------
        # Assign value array to show as a color array
        #----------------------------------------------------------------------
        val = self.strVal.get()
        arrC = []
        
        # Value is in the last position in the list
        for cP in self.CPs:
            
            if   val == 're'    : arrC.append( cP.real()   )
            elif val == 'im'    : arrC.append( cP.imag()   )
            elif val == 'abs'   : arrC.append( cP.abs()    )
            elif val == 'phase' : arrC.append( cP.phase()  )
            elif val == 'sqr'   : arrC.append( cP.sqrAbs() )
            
        self.C = np.array(arrC)
        
        #----------------------------------------------------------------------
        # Prepare the chart
        #----------------------------------------------------------------------
        self.figure.clear() 
        self.chart = self.figure.add_subplot()

        self.chart.set_title(val, fontsize=14)
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
        if self.is1D():
        
#            chrtObj = self.chart.scatter( x=self.C, y=self.Y, linewidths=1 ) #, edgecolors='gray')
            chrtObj = self.chart.plot( self.C, self.Y ) #, edgecolors='gray')
        
        else:
            chrtObj = self.chart.scatter( x=self.X, y=self.Y, c=self.C, marker="s", cmap='RdYlBu_r')
#            chrtObj = self.chart.scatter( x=self.X, y=self.Y, c=self.C, marker="s", lw=0, s=(72./self.figure.dpi)**2, cmap='RdYlBu_r')
            self.figure.colorbar(chrtObj, ax=self.chart)
            
        # Vykreslenie noveho grafu
        self.figure.tight_layout()
        self.update()
        self.canvas.draw()
        
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
            
            if self.is1D(): coord = [y   ]
            else          : coord = [y, x]
            
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
print('SIQO InfoChart library ver 1.01')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------