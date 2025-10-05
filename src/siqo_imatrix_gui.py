#==============================================================================
# Info tkChart library
#------------------------------------------------------------------------------
import tkinter                as tk
from   tkinter                import (ttk, font, PanedWindow)
from   tkinter.messagebox     import showinfo, askokcancel, askyesno

from   matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
#from   mpl_toolkits                      import mplot3d

import numpy                  as np
import matplotlib.pyplot      as plt

from   siqolib.logger         import SiqoLogger
from   siqolib.message        import SiqoMessage, askInt, askReal
from   siqo_imatrix           import InfoMatrix
from   siqo_ipoint_gui        import InfoPointGui
from   siqo_imatrix_data_gui  import InfoMatrixDataGui

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
        self.logger.audit(f'{name}.init:')

        self.name     = name               # Name of this chart
        self.dat      = dat                # InfoMatrix base data
        self.sub2D    = {}                 # Subset of InfoMatrix data defined as frozen axes with desired values e.g. {'x':4, 't':17}
        self.needShow = False              # Flag to show the chart, True means data changed and need to be shown

        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------
        self.w        = 1600               # Width of the chart in px
        self.h        =  600               # Height of the chart in px

        self.type     = '2D'               # Actual type of the chart
        self.actPoint = None               # Actual working InfoPoint

        self.keyS     = 'None'             # key for methods for value to show
        self.keyV     = 'None'             # key for value to show
        self.keyX     = 'None'             # Default key for Axis X to show
        self.keyY     = 'None'             # Default key for Axis Y to show

        if 'keyV' in kwargs.keys(): self.keyV = kwargs['keyV']
        if 'keyX' in kwargs.keys(): self.keyX = kwargs['keyX']
        if 'keyY' in kwargs.keys(): self.keyY = kwargs['keyY']

        self.axesLst  = list()             # List of axes names for combo boxes

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
        mainMenu.add_cascade(label="Point/Data", menu=dataMenu)
        dataMenu.add_command(label="Point Schema",      command=self.onSchema)
        dataMenu.add_command(label="Matrix properties", command=self.onProp  )
        dataMenu.add_command(label="New data",          command=self.onNew   )

        # Pridanie Help menu
        helpMenu = tk.Menu(mainMenu, tearoff=0)
        mainMenu.add_cascade(label="Info", menu=helpMenu)
        helpMenu.add_command(label="Matrix info short", command=lambda: self.onInfo(mode='short'))
        helpMenu.add_command(label="Matrix info full",  command=lambda: self.onInfo(mode='full' ))

        #----------------------------------------------------------------------
        # Create and show display bar
        #----------------------------------------------------------------------
        self.frmDispBar = ttk.Frame(self)
        self.frmDispBar.pack(fill=tk.X, expand=True, side=tk.TOP, anchor=tk.N)
        self.showDisplayBar()

        #----------------------------------------------------------------------
        # Create a figure with the navigator bar and bind it to mouse events
        #----------------------------------------------------------------------
        self.figure = plt.figure(figsize=(self.w*_FIG_W/100, self.h*_FIG_H/100), dpi=_DPI)

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.callbacks.connect('button_press_event', self.onClick)
        NavigationToolbar2Tk(self.canvas, self)

        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        #----------------------------------------------------------------------
        # Initialisation
        #----------------------------------------------------------------------
        self.logger.audit(f'{name}.init: Done')

    #--------------------------------------------------------------------------
    def updateDisplayBar(self):

        self.axesLst = list(self.dat.getAxes().values())
        self.axesLst.insert(0, 'None')        # Insert 'None' as first item

        self.cbX['values'] = self.axesLst
        self.cbX.current(0)

        self.cbY['values'] = self.axesLst
        self.cbY.current(0)

        self.cbM['values'] = list(self.dat.mapSetMethods().keys())
        self.cbM.current(0)

        self.cbVP['values'] = list(self.dat.mapShowMethods().keys())
        self.cbVP.current(0)

        self.cbVX['values'] = list(self.dat.getVals().values())
        self.cbVX.current(0)

    #--------------------------------------------------------------------------
    def showDisplayBar(self):
        "Show diplay options bar"

        self.frmDispBar.columnconfigure(0, weight=3)
        self.frmDispBar.columnconfigure(1, weight=3)
        self.frmDispBar.columnconfigure(2, weight=4)
        self.frmDispBar.columnconfigure(3, weight=3)
        self.frmDispBar.columnconfigure(4, weight=3)
        self.frmDispBar.columnconfigure(5, weight=3)

        self.frmDispBar.rowconfigure(0, weight=1)
        self.frmDispBar.rowconfigure(1, weight=1)

        #----------------------------------------------------------------------
        # X axis dimension selector
        #----------------------------------------------------------------------
        colX = 0
        self.strX   = tk.StringVar(value='None') # Name of the X-axis dimesion from ipType.axis, 'None' means nothing to show in this axis

        lblX = ttk.Label(self.frmDispBar, text="Dim for X axis:")
        lblX.grid(column=colX, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbX = ttk.Combobox(self.frmDispBar, textvariable=self.strX, width=_COMBO_WIDTH)
        self.cbX['values'] = self.axesLst
        self.cbX['state' ] = 'readonly'
        self.cbX.bind('<<ComboboxSelected>>', self.viewChanged)
        self.cbX.grid(column=colX, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.varLogX = tk.BooleanVar(value=False)
        self.cbLogX = ttk.Checkbutton(self.frmDispBar, text='LogX', variable=self.varLogX, command=self.show)
        self.cbLogX.grid(column=colX, row=1, sticky=tk.E, pady=_PADY)

        #----------------------------------------------------------------------
        # Y axis dimension selector
        #----------------------------------------------------------------------
        colY = 1
        self.strY   = tk.StringVar(value='None') # Name of the Y-axis dimesion from ipType.axis, 'None' means nothing to show in this axis

        lblY = ttk.Label(self.frmDispBar, text="Dim for Y axis:")
        lblY.grid(column=colY, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbY = ttk.Combobox(self.frmDispBar, textvariable=self.strY, width=_COMBO_WIDTH)
        self.cbY['values'] = self.axesLst
        self.cbY['state' ] = 'readonly'
        self.cbY.bind('<<ComboboxSelected>>', self.viewChanged)
        self.cbY.grid(column=colY, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.varLogY = tk.BooleanVar(value=False)
        self.cbLogY = ttk.Checkbutton(self.frmDispBar, text='LogY', variable=self.varLogY, command=self.show)
        self.cbLogY.grid(column=colY, row=1, sticky=tk.E, pady=_PADY)

        #----------------------------------------------------------------------
        # Value to show selector
        #----------------------------------------------------------------------
        colS = 2
        self.strVP = tk.StringVar() # Name of the method for value to show in the chart
        self.strVX = tk.StringVar() # Name of the value to show in the chart

        lblVal = ttk.Label(self.frmDispBar, text="Value to show:")
        lblVal.grid(column=colS, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbVP = ttk.Combobox(self.frmDispBar, textvariable=self.strVP, width=int(_COMBO_WIDTH))
        self.cbVP['values'] = list(self.dat.mapShowMethods().keys())
        self.cbVP['state' ] = 'readonly'
        self.cbVP.bind('<<ComboboxSelected>>', self.viewChanged)
        self.cbVP.grid(column=colS, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbVX = ttk.Combobox(self.frmDispBar, textvariable=self.strVX, width=_COMBO_WIDTH)
        self.cbVX['values'] = list(self.dat.getVals().values())
        self.cbVX['state' ] = 'readonly'
        self.cbVX.bind('<<ComboboxSelected>>', self.viewChanged)
        self.cbVX.grid(column=colS, row=1, sticky=tk.E, padx=_PADX, pady=_PADY)

        #----------------------------------------------------------------------
        # Method to apply selector
        #----------------------------------------------------------------------
        colM = 3
        self.strM = tk.StringVar() # Name of the method to apply to the data

        lblMet = ttk.Label(self.frmDispBar, text="Set values:")
        lblMet.grid(column=colM, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbM = ttk.Combobox(self.frmDispBar, textvariable=self.strM, width=int(2*_COMBO_WIDTH))
        self.cbM['values'] = list(self.dat.mapSetMethods().keys())
        self.cbM['state' ] = 'readonly'
        self.cbM.bind('<<ComboboxSelected>>', self.method)
        self.cbM.grid(column=colM, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)

        #----------------------------------------------------------------------
        # Frozen axis indexes
        #----------------------------------------------------------------------
        colFA = 4
        self.strFA = tk.StringVar() # Frozen axis indexes, e.g. 'x:4, t:17'

        lblFax = ttk.Label(self.frmDispBar, text="Frozen axis:")
        lblFax.grid(column=colFA, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        valFax = ttk.Label(self.frmDispBar, textvariable=self.strFA)
        valFax.grid(column=colFA, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)

        #----------------------------------------------------------------------
        # Update display bar with actual data
        #----------------------------------------------------------------------
        self.updateDisplayBar()


    #--------------------------------------------------------------------------
    def dims(self):
        "Returns number of not-None dimensions in the chart"

        toRet = 0

        if self.keyX: toRet += 1
        if self.keyY: toRet += 1

        self.logger.debug(f'{self.name}.dims: Chart has {toRet} dimensions')
        return toRet

    #--------------------------------------------------------------------------
    def viewChanged(self, event=None, force=False):
        "Prepares npData to show"

        #----------------------------------------------------------------------
        # Read actual settings
        #----------------------------------------------------------------------
        aKeyS = self.strVP.get()
        aKeyV = self.dat.valKeyByName( self.strVX.get())  # Key for Name of the value to show in the chart, 'None' means nothing to show
        aKeyX = self.dat.axeKeyByName( self.strX.get() )  # Key for Name of the X-axis dimension from ipType.axis, 'None' means nothing to show in this axis
        aKeyY = self.dat.axeKeyByName( self.strY.get() )  # Key for Name of the Y-axis dimension from ipType.axis, 'None' means nothing to show in this axis

        self.logger.info(f'{self.name}.viewChanged: method={aKeyS}->{self.keyS}, value={self.keyV}->{aKeyV}, X-axis={self.keyX}->{aKeyX}, Y-axis={self.keyY}->{aKeyY}')
        self.needShow = False

        #----------------------------------------------------------------------
        # Changes in any key required data refresh
        #----------------------------------------------------------------------
        if (self.keyS!=aKeyS) or (self.keyV!=aKeyV) or (self.keyX!=aKeyX) or (self.keyY!=aKeyY) or force:

            self.logger.info(f'{self.name}.viewChanged: {self.keyS}->{aKeyS}, {self.keyV}->{aKeyV}, {self.keyX}->{aKeyX}, {self.keyY}->{aKeyY} - need to show the chart')
            self.needShow = True

            #------------------------------------------------------------------
            # Ak sa zmenili osy, zresetujem sub2D
            #------------------------------------------------------------------
            if (self.keyX != aKeyX) or (self.keyY != aKeyY):

                self.logger.info(f'{self.name}.viewChanged: X or Y axis changed, resetting sub2D')
                self.sub2D = {}

                #--------------------------------------------------------------
                # Nastavim zmrazene indexy pre osi, ktore sa nezobrazia
                #--------------------------------------------------------------
                for axe, axeName in self.dat.getAxes().items():

                    # Preskocim zobrazene osi
                    if axe==aKeyX or axe==aKeyY: continue

                    #----------------------------------------------------------
                    # Zamrazim index pre danu os
                    #----------------------------------------------------------
                    inp = askInt(container=self, title=f'Zadaj zmrazenú hodnotu pre {axeName}', prompt=axe, initialvalue=0, min=0, max=self.dat._cnts[axe]-1)

                    if inp is None:
                       self.logger.audit(f'{self.name}.viewChanged: User input for axe {axeName} cancelled by user')
                       continue

                    self.setSub2D({axe: inp})

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
            self.dat.actSubmatrix(actSubIdxs=self.sub2D)

        #----------------------------------------------------------------------
        # Ak nenastala zmena, vyskocim
        #----------------------------------------------------------------------
        self.logger.info(f'{self.name}.viewChanged: needShow = {self.needShow}')
        self.show()

    #--------------------------------------------------------------------------
    def setSub2D(self, axeFreezeIdxs: dict):
        "Add frozen axes for the chart, e.g. {'x':4, 't':17}"

        self.logger.info(f'{self.name}.setSub2D: Set sub2D = {axeFreezeIdxs}')

        #----------------------------------------------------------------------
        # Prejdem vsetky zmrazene osi
        #----------------------------------------------------------------------
        for axe, idx in axeFreezeIdxs.items():

            if axe not in self.dat.getAxes():
                self.logger.warning(f'{self.name}.setSub2D: Axis {axe} not in axes {self.dat.getAxes()}, skipping')

            else:
                self.sub2D[axe] = idx
                self.logger.audit(f'{self.name}.setSub2D: Axe {axe} was frozen to index {idx}')

        #----------------------------------------------------------------------
        # Update the string variable for frozen axes
        #----------------------------------------------------------------------
        if len(self.sub2D) > 0: self.strFA.set(', '.join([f'{axe}:{idx}' for axe, idx in self.sub2D.items()]))
        else                  : self.strFA.set('None')

    #==========================================================================
    # Show the chart
    #--------------------------------------------------------------------------
    def show(self, event=None):
        """Vykresli chart na zaklade aktualneho listu actList
        """
        self.logger.info(f"{self.name}.show: axisX='{self.keyX}', axisY='{self.keyY}', value='{self.keyV}', method='{self.keyS}'")

        #----------------------------------------------------------------------
        # Ak nenastala zmena, vyskocim
        #----------------------------------------------------------------------
        if not self.needShow:
            self.logger.info(f'{self.name}.show: Data have not changed, no need for show')
            return

        #----------------------------------------------------------------------
        # Check list of InfoPoints to show
        #----------------------------------------------------------------------
        if len(self.dat.actList) == 0:
            self.logger.warning(f'{self.name}.show: No InfoPoints, nothig to show')
            return

        #----------------------------------------------------------------------
        # Check value to show
        #----------------------------------------------------------------------
        if not self.keyV:
            self.logger.warning(f'{self.name}.show: No value selected, nothig to show')
            return

        #----------------------------------------------------------------------
        # Check axis to show
        #----------------------------------------------------------------------
        if not self.keyX and not self.keyY:
            self.logger.warning(f'{self.name}.show: No axis selected, nothig to show')
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

        self.logger.debug(f'{self.name}.show: Iterating {len(self.dat.actList)} iPoints for showFtion={self.keyS} with keyV={self.keyV}')
        for i, point in enumerate(self.dat.actList):

            valueToShow = showFtion(point, self.keyV)
            listC.append(valueToShow)

            if self.keyX: listX.append(point.pos(self.keyX))
            if self.keyY: listY.append(point.pos(self.keyY))

        #----------------------------------------------------------------------
        # Skonvertujem do npArrays
        #----------------------------------------------------------------------
        npC = np.array(listC)
        npX = np.array(listX)
        npY = np.array(listY)

        #----------------------------------------------------------------------
        # Kontrola npArrays
        #----------------------------------------------------------------------
        if npC.size==0:
            self.logger.info(f'{self.name}.show: No values to show')
            return

        if self.keyX and npX.size==0:
            self.logger.info(f'{self.name}.show: Axe X is selected but has no data to show')
            return

        if self.keyY and npY.size==0:
            self.logger.info(f'{self.name}.show: Axe Y is selected but has no data to show')
            return

        #----------------------------------------------------------------------
        # Prepare the chart
        #----------------------------------------------------------------------
        self.figure.clear()
        chart = self.figure.add_subplot()

#        self.chart.set_title(val, fontsize=14)
        chart.grid(False)
        chart.set_facecolor('white')

        #----------------------------------------------------------------------
        # Nazvy osi podla aktualneho vyberu
        #----------------------------------------------------------------------
        if self.keyX: chart.set_xlabel(self.dat.axeNameByKey(self.keyX))
        if self.keyY: chart.set_ylabel(self.dat.axeNameByKey(self.keyY))

        #----------------------------------------------------------------------
        # Log axis X, Y
        #----------------------------------------------------------------------
        if 'selected' in self.cbLogX.state(): chart.set_xscale('log')
        if 'selected' in self.cbLogY.state(): chart.set_yscale('log')

        #----------------------------------------------------------------------
        # Show the chart
        #----------------------------------------------------------------------
        if self.dims() == 1:
            #------------------------------------------------------------------
            # Chart 1D
            #------------------------------------------------------------------
            if self.keyX: axis = npX
            else        : axis = npY

            self.logger.debug(f'{self.name}.show: Chart 1D')
            chrtObj = chart.plot( npC, axis ) #, linewidths=1, edgecolors='gray')

        elif self.dims() == 2:
            #------------------------------------------------------------------
            # Chart 2D
            #------------------------------------------------------------------
            self.logger.debug(f'{self.name}.show: Chart 2D')

            chrtObj = chart.scatter( x=npX, y=npY, c=npC, marker="s", cmap='RdYlBu_r') # , lw=0, s=(72./self.figure.dpi)**2
            self.figure.colorbar(chrtObj, ax=chart)

        else:
            self.logger.error(f'{self.name}.show: Chart with {self.dims()} dimensions is not supported')

        #----------------------------------------------------------------------
        # Vykreslenie noveho grafu
        #----------------------------------------------------------------------
        self.figure.tight_layout()
        self.update()
        self.canvas.draw()

        #----------------------------------------------------------------------
        self.logger.info(f'{self.name}.show: Chart with {self.dims()} dimensions is shown')

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
            self.logger.debug(f'{self.name}.onClick: Actual point = {self.actPoint}@{id(self.actPoint)}')

            #------------------------------------------------------------------
            # Left button
            #------------------------------------------------------------------
            if btn == 1: #MouseButton.LEFT:

               self.logger.info(f'{self.name}.onClick: left click for {self.actPoint}')

               tit = f'Nearest point to [{round(y,2)}, {round(x,2)}]'
               mes = str(self.actPoint)
               showinfo(title=tit, message=mes)

            #------------------------------------------------------------------
            # Right button - edit value menu
            #------------------------------------------------------------------
            elif btn == 3: #MouseButton.RIGHT:

                val     = self.actPoint.val(self.keyV)
                valName = self.actPoint.valName(self.keyV)

                self.logger.info(f'{self.name}.onClick: right click for {self.keyV}[{valName}] = {val} {type(val)}')

                #--------------------------------------------------------------
                # User input based on value type
                #--------------------------------------------------------------
                if type(val) in [int, float]:

                   inp = askReal(container=self, title=f'Zadaj hodnotu pre {valName}', prompt=self.keyV, initialvalue=val)

                   if inp is None:
                       self.logger.audit(f'{self.name}.onClick: User input cancelled by user')
                       return

                   self.actPoint.set(vals={self.keyV:inp})
                   self.logger.audit(f'{self.name}.onClick: Set {self.keyV} = {inp} for {self.actPoint}')

                #--------------------------------------------------------------
                # Data was changed, so show the chart
                #--------------------------------------------------------------
                self.logger.warning(f'{self.name}.onClick: Data changed, need to show the chart')
                self.needShow = True
                self.show()

            #------------------------------------------------------------------
        else:
            self.actPoint = None
            self.logger.warning(f'{self.name}.onClick: Clicked ouside axes bounds but inside plot window')

        #----------------------------------------------------------------------
        self.logger.debug(f'{self.name}.onClick: Done')

    #==========================================================================
    # File menu
    #--------------------------------------------------------------------------
    def onOpen(self, event=None):

        return

    #--------------------------------------------------------------------------
    def onSave(self, event=None):

        return

    #==========================================================================
    # Point/Data menu
    #--------------------------------------------------------------------------
    def onSchema(self, event=None):

        self.logger.debug(f'{self.name}.onSchema:')

        origSchema = self.dat.getSchema()

        gui = InfoPointGui(name=f'Schema {self.dat.ipType}', container=self, ipType=self.dat.ipType)
        gui.grab_set()
        self.wait_window(gui)

        #----------------------------------------------------------------------
        # Vyhodnotenie zmien v scheme
        #----------------------------------------------------------------------
        test = self.dat.equalSchema(origSchema)

        if test['exists']:

            if not test['equalAxes']:

                #--------------------------------------------------------------
                # Zmena osí
                #--------------------------------------------------------------
                if askyesno(title='Axes changed', message='Axes was changed. Apply changes and reset  data?'):

                    self.dat.setIpType(self.dat.ipType, force=True)
                    self.dat.init()
                    self.updateDisplayBar()
                    self.logger.warning(f'{self.name}.onSchema: Axes changed from {origSchema} to {self.dat.getSchema()}, reset data')

                else:
                    self.dat.setSchema(origSchema)
                    self.logger.warning(f'{self.name}.onSchema: Axes changed from {origSchema} to {self.dat.getSchema()}, but user cancelled changes, schema restored')
                    return

        #----------------------------------------------------------------------
        self.logger.debug(f'{self.name}.onSchema: InfoPointGui window closed')

    #--------------------------------------------------------------------------
    def onProp(self, event=None):

        self.logger.debug(f'{self.name}.onProp:')

        gui = InfoMatrixDataGui(name=f'Matrix {self.dat.name}', container=self, matrix=self.dat)
        gui.grab_set()
        self.wait_window(gui)

        #----------------------------------------------------------------------
        # Vyhodnotenie zmien v scheme
        #----------------------------------------------------------------------
        self.updateDisplayBar()

        #----------------------------------------------------------------------
        self.logger.debug(f'{self.name}.onProp: Matrix properties set')

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
        rects = {}

        for axe, oOrig in self.dat._origs.items():

            orig = askReal(container=self, title='Zadaj počiatok v osi', prompt=axe, initialvalue=oOrig)

            if orig is None:
                self.logger.debug(f'{self.name}.onNew: cancelled by user')
                return

            origs[axe] = orig

            len = askReal(container=self, title='Zadaj dĺžku osi', prompt=axe, initialvalue=cnts[axe])

            if len is None:
                self.logger.debug(f'{self.name}.onNew: cancelled by user')
                return

            rects[axe] = len

        #----------------------------------------------------------------------
        self.dat.gener(cnts=cnts, origs=origs, rects=rects)
        self.viewChanged(force=True)

        return

    #==========================================================================
    # Info menu
    #--------------------------------------------------------------------------
    def onInfo(self, event=None, mode='short'):
        "Show information about the InfoMatrix data"

        self.logger.debug(f'{self.name}.onInfo:')

        if   mode=='short': text = self.dat.info(short=True)['msg']
        elif mode=='full' : text = self.dat.info(full=True)['msg']
        else: text = [f'Unknown mode {mode}']

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

        self.viewChanged(force=True)

        #----------------------------------------------------------------------


    #--------------------------------------------------------------------------
    def reset(self):
        "Reset all data into default values"

        self.actPoint = None               # Actual working InfoPoint

        self.keyV     = 'None'             # key for value to show
        self.keyX     = 'None'             # Default key for Axis X to show
        self.keyY     = 'None'             # Default key for Axis Y to show

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
        self.viewChanged()

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
    matrix = InfoMatrix('Test field')
    matrix.logger.setLevel('INFO')
    matrix.logger.frameDepth = 2
    print(f'logger.frameDepth = {matrix.logger.frameDepth}')

    matrix.logger.info('Test of InfoMarixGui class')
    matrix.setIpType('ipTest')
    print(matrix.info(full=True)['msg'])


    matrixGui = InfoMarixGui(name='Test of InfoModelGui class', container=win, dat=matrix)
    matrixGui.pack(fill=tk.BOTH, expand=True, side=tk.TOP, anchor=tk.N)

    matrixGui.sub2D = {'z':1}
#    matrixGui.logger.setLevel('DEBUG')

    win.mainloop()

    matrixGui.logger.info('Stop of InfoMarixGui test')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------