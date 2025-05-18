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
        self.dat     = dat                 # InfoMatrix to show
        self.myCut   = []                  # Cut of InfoField data for this GUI
        self.w       = 1600                # Width of the chart in px
        self.h       =  900                # Height of the chart in px
        
        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------
        self.type     = '2D'               # Actual type of the chart
        self.IPs      = []                 # List of InfoPoints to show
        self.actPoint = None               # Actual working InfoPoint
        
        self.keyV     = ''                 # key for value to show
        self.keyX     = ''                 # key for Axis X to show
        self.keyY     = ''                 # key for Axis Y to show

        if 'keyV' in kwargs.keys(): self.keyV = kwargs['keyV']
        if 'keyX' in kwargs.keys(): self.keyX = kwargs['keyX']
        if 'keyY' in kwargs.keys(): self.keyY = kwargs['keyY']

        self.X        = None               # np array for coordinate X
        self.Y        = None               # np array for coordinate Y
        self.C        = None               # np array for value color
        self.U        = None               # np array for quiver re value
        self.V        = None               # np array for quiver im value

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

        self.cbV = ttk.Combobox(frmBtn, textvariable=self.strV, width=5)
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

        self.cbX = ttk.Combobox(frmBtn, textvariable=self.strX, width=5)
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

        self.cbY = ttk.Combobox(frmBtn, textvariable=self.strY, width=5)
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

        self.cbM = ttk.Combobox(frmBtn, textvariable=self.strM, width=10)
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
        aKeyV = self.   self.cbV.current()
        aKeyX = self.cbX.current()
        aKeyY = self.cbY.current()
        
        self.journal.I(f'{self.name}.dataChanged: value={self.keyV}->{aKeyV}, X-axis={self.keyX}->{aKeyX}, Y-axis={self.keyY}->{aKeyY}')

        #----------------------------------------------------------------------
        # Check for changes
        #----------------------------------------------------------------------
        changed = False

        # Zmena val, X, Y
        if self.keyV != aKeyV: changed = True
        if self.keyX != aKeyX: changed = True
        if self.keyY != aKeyY: changed = True

        #----------------------------------------------------------------------
        # Ak nenastala zmena v zobrazeni, vyskocim
        #----------------------------------------------------------------------
        if not changed: self.journal.M(f'{self.name}.dataChanged: Settings have not changed, no need for show')
        else          : self.show()
        
        self.journal.O()
        
    #==========================================================================
    # Method to apply
    #--------------------------------------------------------------------------
    def method(self, event=None):
        "Apply data in active cut"
        
        met = self.strM.get()
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

        self.journal.O()
        return

        if 'keyVal' in kwargs.keys(): self.strVal.set(kwargs['val'])
        if 'keyX'   in kwargs.keys(): self.strX.  set(kwargs['axX'])
        if 'keyY'   in kwargs.keys(): self.strY.  set(kwargs['axY'])


        #----------------------------------------------------------------------
        # Ziskam udaje pre zobrazenie podla aktualneho settingu
        #----------------------------------------------------------------------
        nameV = self.strV.get()    # Name value to show on X axis
        nameX = self.strX.get()    # Name of the axe to show on X axis
        nameY = self.strY.get()    # Name of the axe to show on Y axis
        nameM = self.strM.get()    # Name of the axe to show on Y axis







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
print('SIQO InfoMarixGui library ver 1.01')

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

    win.mainloop()

    journal.O()

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------