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

from   siqolib.logger         import SiqoLogger
from   siqolib.message        import SiqoMessage, askInt, askReal
from   siqo_imatrix           import InfoMatrix

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_VER            = '2.0'
_WIN            = '1300x740'
_DPI            = 100

_FIG_W          = 0.8    # Figure width
_FIG_H          = 1.0    # Figure height

_COMBO_WIDTH    = 12
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
    def __init__(self, name, container, dat:InfoMatrix, **kwargs):
        "Call constructor of InfoMarixGui and initialise it for respective data"

        self.logger = SiqoLogger(name, level='DEBUG')
        self.logger.debug(f'{name}.init:')

        self.name    = name                # Name of this chart
        self.dat     = dat                 # InfoMatrix base data
        self.sub2D   = {}                  # Subset of InfoMatrix data defined as frozen axes with desired values e.g. {'x':4, 't':17}

        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------
        self.w       = 1600                # Width of the chart in px
        self.h       =  600                # Height of the chart in px

        self.type     = '2D'               # Actual type of the chart
        self.iPoints  = []                 # List of InfoPoints to show
        self.actPoint = None               # Actual working InfoPoint

        self.keyS     = 'None'             # key for methods for value to show
        self.keyV     = 'None'             # key for value to show
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
        # Vytvorenie hlavného menu a priradenie do container (okno)
        #----------------------------------------------------------------------
        mainMenu = tk.Menu(container)
        container.config(menu=mainMenu)

        # Pridanie File menu
        fileMenu = tk.Menu(mainMenu, tearoff=0)
        mainMenu.add_cascade(label="File", menu=fileMenu)
        fileMenu.add_command(label="Open", command=self.onOpen)
        fileMenu.add_command(label="Save", command=self.onSave)
        fileMenu.add_separator()

        # Pridanie Data menu
        dataMenu = tk.Menu(mainMenu, tearoff=0)
        mainMenu.add_cascade(label="Data", menu=dataMenu)
        dataMenu.add_command(label="New data", command=self.onNew)

        # Pridanie Help menu
        helpMenu = tk.Menu(mainMenu, tearoff=0)
        mainMenu.add_cascade(label="Info", menu=helpMenu)
        helpMenu.add_command(label="Matrix info", command=self.onInfo)

        #----------------------------------------------------------------------
        # Create head buttons bar
        #----------------------------------------------------------------------
        frmBtn = ttk.Frame(self)
        frmBtn.pack(fill=tk.X, expand=True, side=tk.TOP, anchor=tk.N)

        frmBtn.columnconfigure(0, weight=0)
        frmBtn.columnconfigure(1, weight=3)
        frmBtn.columnconfigure(2, weight=3)
        frmBtn.columnconfigure(3, weight=3)
        frmBtn.columnconfigure(4, weight=2)
        frmBtn.columnconfigure(5, weight=0)

        frmBtn.rowconfigure(0, weight=1)
        frmBtn.rowconfigure(1, weight=1)

        #----------------------------------------------------------------------
        # List of axis
        #----------------------------------------------------------------------
        axesLst = list(self.dat.getAxes().values())
        axesLst.insert(0, 'None') # Insert 'None' as first item

        #----------------------------------------------------------------------
        # X axis dimension selector
        #----------------------------------------------------------------------
        self.strX   = tk.StringVar(value='None') # Name of the X-axis dimesion from ipType.axis, 'None' means nothing to show in this axis

        lblX = ttk.Label(frmBtn, text="Dim for X axis:")
        lblX.grid(column=1, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbX = ttk.Combobox(frmBtn, textvariable=self.strX, width=_COMBO_WIDTH)
        self.cbX['values'] = axesLst
        self.cbX['state' ] = 'readonly'
        self.cbX.bind('<<ComboboxSelected>>', self.dataChanged)
        self.cbX.grid(column=1, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.varLogX = tk.BooleanVar(value=False)
        self.cbLogX = ttk.Checkbutton(frmBtn, text='LogX', variable=self.varLogX, command=self.show)
        self.cbLogX.grid(column=1, row=1, pady=_PADY)

        #----------------------------------------------------------------------
        # Y axis dimension selector
        #----------------------------------------------------------------------
        self.strY   = tk.StringVar(value='None') # Name of the Y-axis dimesion from ipType.axis, 'None' means nothing to show in this axis

        lblY = ttk.Label(frmBtn, text="Dim for Y axis:")
        lblY.grid(column=2, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbY = ttk.Combobox(frmBtn, textvariable=self.strY, width=_COMBO_WIDTH)
        self.cbY['values'] = axesLst
        self.cbY['state' ] = 'readonly'
        self.cbY.bind('<<ComboboxSelected>>', self.dataChanged)
        self.cbY.grid(column=2, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.varLogY = tk.BooleanVar(value=False)
        self.cbLogY = ttk.Checkbutton(frmBtn, text='LogY', variable=self.varLogY, command=self.show)
        self.cbLogY.grid(column=2, row=1, pady=_PADY)

        #----------------------------------------------------------------------
        # Value to show selector
        #----------------------------------------------------------------------
        self.strVP = tk.StringVar() # Name of the method for value to show in the chart
        self.strVX = tk.StringVar() # Name of the value to show in the chart

        lblVal = ttk.Label(frmBtn, text="Value to show:")
        lblVal.grid(column=3, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbVP = ttk.Combobox(frmBtn, textvariable=self.strVP, width=int(_COMBO_WIDTH))
        self.cbVP['values'] = list(self.dat.mapShowMethods().keys())
        self.cbVP['state' ] = 'readonly'
        self.cbVP.current(0)
        self.cbVP.bind('<<ComboboxSelected>>', self.dataChanged)
        self.cbVP.grid(column=3, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbVX = ttk.Combobox(frmBtn, textvariable=self.strVX, width=_COMBO_WIDTH)
        self.cbVX['values'] = list(self.dat.getVals().values())
        self.cbVX['state' ] = 'readonly'
        self.cbVX.current(0)
        self.cbVX.bind('<<ComboboxSelected>>', self.dataChanged)
        self.cbVX.grid(column=3, row=1, padx=_PADX, pady=_PADY)

        #----------------------------------------------------------------------
        # Method to apply selector
        #----------------------------------------------------------------------
        self.strM = tk.StringVar() # Name of the method to apply to the data

        lblMet = ttk.Label(frmBtn, text="Set values:")
        lblMet.grid(column=4, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbM = ttk.Combobox(frmBtn, textvariable=self.strM, width=int(2*_COMBO_WIDTH))
        self.cbM['values'] = list(self.dat.mapSetMethods().keys())
        self.cbM['state' ] = 'readonly'
        self.cbM.current(0)
        self.cbM.bind('<<ComboboxSelected>>', self.method)
        self.cbM.grid(column=4, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)

        #----------------------------------------------------------------------
        # Create a figure with the navigator bar and bind it to mouse events
        #----------------------------------------------------------------------
        self.figure = plt.figure(figsize=(self.w*_FIG_W/100, self.h*_FIG_H/100), dpi=_DPI)
        self.canvas = FigureCanvasTkAgg(self.figure, self)

        self.canvas.callbacks.connect('button_press_event', self.onClick)

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



    #--------------------------------------------------------------------------
    def dims(self):
        "Returns number of not-None dimensions in the chart"

        toRet = 0

        if self.keyX: toRet += 1
        if self.keyY: toRet += 1

        self.logger.info(f'{self.name}.dims: Chart has {toRet} dimensions')
        return toRet

    #--------------------------------------------------------------------------
    def dataChanged(self, event=None, force=False):
        "Prepares npData to show"

        #----------------------------------------------------------------------
        # Read actual settings
        #----------------------------------------------------------------------
        aKeyS = self.strVP.get()
        aKeyV = self.dat.valKeyByName( self.strVX.get())  # Key for Name of the value to show in the chart, 'None' means nothing to show

        aKeyX = self.dat.axeKeyByName( self.strX.get() )  # Key for Name of the X-axis dimension from ipType.axis, 'None' means nothing to show in this axis
        aKeyY = self.dat.axeKeyByName( self.strY.get() )  # Key for Name of the Y-axis dimension from ipType.axis, 'None' means nothing to show in this axis

        self.logger.debug(f'{self.name}.dataChanged: method={aKeyS}->{self.keyS}, value={self.keyV}->{aKeyV}, X-axis={self.keyX}->{aKeyX}, Y-axis={self.keyY}->{aKeyY}')
        changed = False

        if force: changed=True

        #----------------------------------------------------------------------
        # Changes in any key required data refresh
        #----------------------------------------------------------------------
        if  (self.keyS!=aKeyS) or (self.keyV!=aKeyV) or (self.keyX!=aKeyX) or (self.keyY!=aKeyY) or force:

            changed = True

            #------------------------------------------------------------------
            # Vytvorim predpis pre aktualny subset
            #------------------------------------------------------------------
            self.keyS = aKeyS
            self.keyV = aKeyV
            self.keyX = aKeyX
            self.keyY = aKeyY

            #------------------------------------------------------------------
            # Ziskam list InfoPoints (whole object) patriacich subsetu
            #------------------------------------------------------------------
            self.iPoints = self.dat.actSubmatrix(actSub=self.sub2D)

        #----------------------------------------------------------------------
        # Ak nenastala zmena, vyskocim
        #----------------------------------------------------------------------
        if not changed: self.logger.info(f'{self.name}.dataChanged: Settings have not changed, no need for show')
        else          : self.show()



    #==========================================================================
    # Show the chart
    #--------------------------------------------------------------------------
    def show(self, event=None):
        """Vykresli chart na zaklade aktualneho listu self.cIP
        """
        self.logger.info(f"{self.name}.show: axisX='{self.keyX}', axisY='{self.keyY}', value='{self.keyV}', method='{self.keyS}'")

        #----------------------------------------------------------------------
        # Check list of InfoPoints to show
        #----------------------------------------------------------------------
        if len(self.iPoints) == 0:
            self.logger.info(f'{self.name}.show: No InfoPoints, nothig to show')
            return

        #----------------------------------------------------------------------
        # Check value to show
        #----------------------------------------------------------------------
        if not self.keyV:
            self.logger.info(f'{self.name}.show: No value selected, nothig to show')
            return

        #----------------------------------------------------------------------
        # Check axis to show
        #----------------------------------------------------------------------
        if not self.keyX and not self.keyY:
            self.logger.info(f'{self.name}.show: No axis selected, nothig to show')
            return

        #----------------------------------------------------------------------
        # Prepare the data for the chart
        #----------------------------------------------------------------------
        listC = []
        listX = []
        listY = []
        listU = []
        listV = []

        #----------------------------------------------------------------------
        # Prejdem vsetky vybrane body na zobrazenie
        #----------------------------------------------------------------------
        showFtion = self.dat.mapShowMethods()[self.keyS]

        self.logger.debug(f'{self.name}.show: Iterating iPoints for showFtion={showFtion} with keyV={self.keyV}')
        for point in self.iPoints:

            valueToShow = showFtion(point, self.keyV)
            listC.append(valueToShow)

            if self.keyX: listX.append(point.pos(self.keyX))
            if self.keyY: listY.append(point.pos(self.keyY))

        #----------------------------------------------------------------------
        # Skonvertujem do npArrays
        #----------------------------------------------------------------------
        self.npC = np.array(listC)
        self.npX = np.array(listX)
        self.npY = np.array(listY)


        #----------------------------------------------------------------------
        # Kontrola npArrays
        #----------------------------------------------------------------------
        if self.npC.size==0:
            self.logger.info(f'{self.name}.show: No values to show')

            return

        if self.keyX and self.npX.size==0:
            self.logger.info(f'{self.name}.show: Axe X is selected but has no data to show')

            return

        if self.keyY and self.npY.size==0:
            self.logger.info(f'{self.name}.show: Axe Y is selected but has no data to show')

            return


        #----------------------------------------------------------------------
        # Prepare the chart
        #----------------------------------------------------------------------
        self.figure.clear()
        self.chart = self.figure.add_subplot()

#        self.chart.set_title(val, fontsize=14)
        self.chart.grid(False)
        self.chart.set_facecolor('white')

        #----------------------------------------------------------------------
        # Nazvy osi podla aktualneho vyberu
        #----------------------------------------------------------------------
        if self.keyX: self.chart.set_xlabel(self.dat.axeNameByKey(self.keyX))
        if self.keyY: self.chart.set_ylabel(self.dat.axeNameByKey(self.keyY))

        #----------------------------------------------------------------------
        # Log axis X, Y
        #----------------------------------------------------------------------
        if 'selected' in self.cbLogX.state(): self.chart.set_xscale('log')
        if 'selected' in self.cbLogY.state(): self.chart.set_yscale('log')

        #----------------------------------------------------------------------
        # Show the chart
        #----------------------------------------------------------------------
        if self.dims() == 1:
            #------------------------------------------------------------------
            # Chart 1D
            #------------------------------------------------------------------
            if self.keyX: axis = self.npX
            else        : axis = self.npY

#            chrtObj = self.chart.scatter( x=self.C, y=self.Y, linewidths=1 ) #, edgecolors='gray')
            chrtObj = self.chart.plot( self.npC, axis ) #, edgecolors='gray')

        elif self.dims() == 2:
            #------------------------------------------------------------------
            # Chart 2D
            #------------------------------------------------------------------
            chrtObj = self.chart.scatter( x=self.npX, y=self.npY, c=self.npC, marker="s", cmap='RdYlBu_r')
#            chrtObj = self.chart.scatter( x=self.X, y=self.Y, c=self.C, marker="s", lw=0, s=(72./self.figure.dpi)**2, cmap='RdYlBu_r')
            self.figure.colorbar(chrtObj, ax=self.chart)

        else:
            self.logger.error(f'{self.name}.show: Chart with {self.dims()} dimensions is not supported')


        #----------------------------------------------------------------------
        # Vykreslenie noveho grafu
        #----------------------------------------------------------------------
        self.figure.tight_layout()
        self.update()
        self.canvas.draw()

        #----------------------------------------------------------------------


    #--------------------------------------------------------------------------
    def onClick(self, event):
        "Print information about mouse-given position"

        self.logger.debug(f'{self.name}.onClick:')

        if event.inaxes is not None:

            #------------------------------------------------------------------
            # Get the button and coordinates
            #------------------------------------------------------------------
            btn = event.button
            x   = round(float(event.xdata), 3)
            y   = round(float(event.ydata), 3)
            self.logger.info(f'{self.name}.onClick: {btn} button clicked at [{y}, {x}] in axes {event.inaxes.get_title()}')

            #------------------------------------------------------------------
            # Get the actual point by coordinates
            #------------------------------------------------------------------
            coord = {self.keyX: x, self.keyY: y}
            self.actPoint = self.dat.pointByCoord(coord)

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

                self.logger.info(f'{self.name}.onClick: right click for {self.actPoint}')

                try    : self.pointMenu.tk_popup(event.x, event.y)
                finally: self.pointMenu.grab_release()

            #------------------------------------------------------------------

        else:
            self.actPoint = None
            print('Clicked ouside axes bounds but inside plot window')



    #==========================================================================
    # File menu
    #--------------------------------------------------------------------------
    def onOpen(self, event=None):

        return

    #--------------------------------------------------------------------------
    def onSave(self, event=None):

        return

    #==========================================================================
    # Data menu
    #--------------------------------------------------------------------------
    def onNew(self, event=None):

        self.logger.debug(f'{self.name}.onNew:')

        #----------------------------------------------------------------------
        # Zistenie poctov bodov v jednotlivych osiach
        #----------------------------------------------------------------------
        cnts = {}

        for axe, oCnt in self.dat._cnts.items():

            cnt = askInt(container=self, title='Zadaj počet bodov v osi', prompt=axe, initialvalue=oCnt, min=1, max=1000)

            if cnt is None:
                self.logger.debug(f'{self.name}.onNew: cancelled by user')
                return

            cnts[axe] = cnt

        #----------------------------------------------------------------------
        # Zistenie pociatkov a dlzok jednotlivych osi
        #----------------------------------------------------------------------
        origs = {}
        rect  = {}

        for axe, oOrig in self.dat._origs.items():

            orig = askReal(container=self, title='Zadaj počiatok v osi', prompt=axe, initialvalue=oOrig)

            if orig is None:
                self.logger.debug(f'{self.name}.onNew: cancelled by user')
                return

            origs[axe] = orig

            len = askReal(container=self, title='Zadaj dĺžku osi', prompt=axe)

            if len is None:
                self.logger.debug(f'{self.name}.onNew: cancelled by user')
                return

            rect[axe] = len




        #----------------------------------------------------------------------
        self.dat.gener(cnts=cnts, origs=origs, rect=rect)
        self.dataChanged(force=True)

        return


    #==========================================================================
    # Help menu
    #--------------------------------------------------------------------------
    def onInfo(self, event=None):
        "Show information about the InfoMatrix data"

        self.logger.debug(f'{self.name}.onInfo:')


        text = self.dat.info()['msg']
        text = text.split('\n')

        msgWin = SiqoMessage(name=self.dat.name, text=text, wpix=800)

        self.logger.debug(f'{self.name}.onInfo: Show info about {self.dat.name}')

    #==========================================================================
    # Method to apply
    #--------------------------------------------------------------------------
    def method(self, event=None):
        "Apply data in active cut"

        metKey = self.strM.get()
        if metKey == 'None': return

        self.logger.debug(f'{self.name}.method: Value {self.keyV} will be set by {metKey} with subset = {self.sub2D}')

        #----------------------------------------------------------------------
        # Zistenie detailov metody
        #----------------------------------------------------------------------
        metDef = self.dat.mapSetMethods()[metKey]
        params = metDef['par']
        newPar = {}

        for par, entry in params.items():

            newEntry = askReal(container=self, title=f"Parameter of {metKey}", prompt=par, initialvalue=entry)

            if newEntry is None:
                self.logger.info(f"{self.name}.method: {metKey} cancelled by user")
                return

            newPar[par] = newEntry

        #----------------------------------------------------------------------
        # Vykonanie metody
        #----------------------------------------------------------------------
        self.logger.info(f"{self.name}.method: {metKey}(key='{self.keyV}', par={newPar})")
        self.dat.pointSetFunction(keyFtion=metKey, key=self.keyV, par=newPar)

        self.dataChanged(force=True)

        #----------------------------------------------------------------------


    #--------------------------------------------------------------------------
    def reset(self):
        "Reset all data into default values"

        self.iPoints  = []                 # List of InfoPoints to show
        self.actPoint = None               # Actual working InfoPoint

        self.keyV     = 'None'             # key for value to show
        self.keyX     = 'None'             # Default key for Axis X to show
        self.keyY     = 'None'             # Default key for Axis Y to show

        self.npX      = np.array([])       # np array for coordinate X
        self.npY      = np.array([])       # np array for coordinate Y
        self.npC      = np.array([])       # np array for value color
        self.npU      = np.array([])       # np array for quiver re value
        self.npV      = np.array([])       # np array for quiver im value

        self.logger.info(f'{self.name}.reset: done')

    #--------------------------------------------------------------------------
    def clear(self):
        "Clears all data but structure is preserved"

        self.logger.debug(f'{self.name}.clear:')

        #----------------------------------------------------------------------
        # Clear InfoMatrix base data
        #----------------------------------------------------------------------
        self.dat.clear()

        #----------------------------------------------------------------------
        # Reset GUI
        #----------------------------------------------------------------------
        self.reset()



    #--------------------------------------------------------------------------
    def setData(self, dat:InfoMatrix):
        "Reset matrix and set new data"

        self.clear()
        self.dat = dat
        self.logger.info(f'{self.name}.setData: New data name = {self.dat.name}')

    #--------------------------------------------------------------------------
    def setPoint(self, c):

        self.logger.info(f'{self.name}.setPoint: {self.actPoint} = {c}')

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

        self.logger.info( f"{self.name}.getObjScatter" )

#        return lib.squareData(baseObj=self.obj, vec=self.obj.prtLst)
#        return lib.spiralData(baseObj=self.obj, vec=self.obj.prtLst)




#==============================================================================
#   Inicializacia kniznice
#------------------------------------------------------------------------------
print(f'SIQO InfoMarixGui library ver {_VER}')

if __name__ == '__main__':

    from   siqo_imatrix           import InfoMatrix

    #--------------------------------------------------------------------------
    # Test of the InfoMarixGui class
    #--------------------------------------------------------------------------
    win = tk.Tk()
    win.configure(bg='silver', highlightthickness=2, highlightcolor='green')
    win.title('Test of InfoModelGui class')
    #win.maxsize(width=1200, height=800)
    win.minsize(width=600, height=300)
    win.config(highlightbackground = "green", highlightcolor= "green")

    #tk.Grid.columnconfigure(win, 1, weight=1)
    #tk.Grid.rowconfigure   (win, 2, weight=1)

    #--------------------------------------------------------------------------
    # Zaciatok testu
    #--------------------------------------------------------------------------
    matrix = InfoMatrix('Test field', 'ipTest')
    matrix.logger.setLevel('INFO')
    matrix.logger.info('Test of InfoMarixGui class')

    matrix.setAxe('x', 'Epoch')
    matrix.setAxe('y', 'L-dist')
    matrix.setAxe('z', 'Os Z')

    matrix.setVal('m', 'hmotnosť')
    matrix.setVal('v', 'rýchlosť')

    matrix.gener(cnts={'x':10, 'y':40, 'z':2}, origs={'x':0, 'y':0, 'z':0}, rects={'x':5, 'y':5, 'z':2}, defs={'m':1, 'v':2})
    print(matrix)

    matrixGui = InfoMarixGui(name='Test of InfoModelGui class', container=win, dat=matrix)
    matrixGui.pack(fill=tk.BOTH, expand=True, side=tk.TOP, anchor=tk.N)

    matrixGui.sub2D = {'z':1}
    matrixGui.logger.setLevel('DEBUG')

    win.mainloop()

    matrixGui.logger.info('Stop of InfoMarixGui test')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------