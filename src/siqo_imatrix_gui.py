#==============================================================================
# Info tkChart library
#------------------------------------------------------------------------------
import tkinter                as tk
from   tkinter                import (ttk, font, PanedWindow)
from   tkinter.messagebox     import showinfo, askokcancel, askyesno

from   matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
#from   mpl_toolkits                      import mplot3d

import numpy                    as np
import matplotlib.pyplot        as plt

from   siqolib.logger           import SiqoLogger
from   siqolib.message          import SiqoMessage, askInt, askReal
from   siqo_imatrix             import InfoMatrix
from   siqo_ipoint_gui          import InfoPointGui
from   siqo_imatrix_data_gui    import InfoMatrixDataGui
from   siqo_imatrix_display_gui import InfoMatrixDisplayGui

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_VER            = '2.0'
_WIN            = '1300x740'
_DPI            = 100

_FIG_W          = 0.8    # Figure width
_FIG_H          = 1.0    # Figure height

_COMBO_WIDTH    = 27
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

        self.name     = name                # Name of this chart
        self.dat      = dat                 # InfoMatrix base data
        self.sub2D    = {}                  # Subset of InfoMatrix data defined as frozen axes with desired values e.g. {'x':4, 't':17}
        self.display  = {}                  # Display options

        self.resetDisplay()                 # Display options

        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------
        self.w        = 1600                # Width of the chart in px
        self.h        =  600                # Height of the chart in px

        self.actPoint = None                # Actual working InfoPoint


        #if 'keyV' in kwargs.keys(): self.display['valName'] = kwargs['keyV']
        #if 'keyX' in kwargs.keys(): self.display['keyX'] = kwargs['keyX']
        #if 'keyY' in kwargs.keys(): self.display['keyY'] = kwargs['keyY']


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
        dataMenu.add_command(label="Point Schema",       command=self.onPointSchema)
        dataMenu.add_command(label="Matrix properties",  command=self.onMatrixProp )
        dataMenu.add_command(label="Display properties", command=self.onDisplay    )
        dataMenu.add_command(label="Set data",           command=self.onSetData    )

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
        self.updateDisplayBar()

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
    def resetDisplay(self):
        "Reset display options to default values based on matrix data"

        axeKeys  = list(self.dat.getAxes().keys())
        axeNames = list(self.dat.getAxes().values())

        self.display  = {'type'       : '2D'                                 # Actual type of the chart
                        ,'needShow'   : False                                # Flag to show the chart, True means data changed and need to be shown
                        ,'axeKeys'    : axeKeys                              # List of axes keys
                        ,'axeNames'   : axeNames                             # List of axes names
                        ,'keyX'       : axeKeys[0] if len(axeKeys)>0 else '' # key for Axis X to show
                        ,'keyY'       : axeKeys[1] if len(axeKeys)>1 else '' # key for Axis Y to show
                        ,'keyZ'       : axeKeys[2] if len(axeKeys)>2 else '' # key for Axis Z to show
                        ,'showMethod' : ''                                   # key for methods for value to show
                        ,'valName'    : ''                                   # Value name to show
                        ,'valKey'     : ''                                   # Value key to show
                        }

        self.display['axeKeys' ].append('None')
        self.display['axeNames'].append('None')

        self.logger.info(f'{self.name}.resetDisplay: Display options reset to {self.display}')

    #--------------------------------------------------------------------------
    def showDisplayBar(self):
        "Show diplay options bar"

        self.frmDispBar.columnconfigure(0, weight=1)
        self.frmDispBar.columnconfigure(1, weight=1)
        self.frmDispBar.columnconfigure(2, weight=1)
        self.frmDispBar.columnconfigure(3, weight=1)

        self.frmDispBar.rowconfigure(0, weight=1)
        self.frmDispBar.rowconfigure(1, weight=1)

        #----------------------------------------------------------------------
        # X axis dimension
        #----------------------------------------------------------------------
        self.varLogX = tk.BooleanVar(value=False)
        cbLog = ttk.Checkbutton(self.frmDispBar, text='Log    X:', variable=self.varLogX, command=self.show)
        cbLog.grid(column=0, row=0, sticky=tk.E, pady=_PADY)

        self.lblX = ttk.Label(self.frmDispBar, text="None")
        self.lblX.grid(column=1, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        #----------------------------------------------------------------------
        # Y axis dimension
        #----------------------------------------------------------------------
        self.varLogY = tk.BooleanVar(value=False)
        cbLog = ttk.Checkbutton(self.frmDispBar, text='Log    Y:', variable=self.varLogY, command=self.show)
        cbLog.grid(column=0, row=1, sticky=tk.E, pady=_PADY)

        self.lblY = ttk.Label(self.frmDispBar, text="None")
        self.lblY.grid(column=1, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)

        #----------------------------------------------------------------------
        # Value to show selector
        #----------------------------------------------------------------------
        self.varValMet  = tk.StringVar(value='Float value') # Name of the method for value to show in the chart
        self.varValName = tk.StringVar()                    # Name of the value to show in the chart

        lblVal = ttk.Label(self.frmDispBar, text="Value to show:")
        lblVal.grid(column=2, row=0, sticky=tk.E, padx=_PADX, pady=_PADY)

        self.cbValMet = ttk.Combobox(self.frmDispBar, textvariable=self.varValMet, width=int(_COMBO_WIDTH))
        self.cbValMet['values'] = list(self.dat.mapShowMethods().keys())
        self.cbValMet['state' ] = 'readonly'
        self.cbValMet.bind('<<ComboboxSelected>>', self.viewChanged)
        self.cbValMet.grid(column=3, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        lblVal = ttk.Label(self.frmDispBar, text="of")
        lblVal.grid(column=4, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.cbValName = ttk.Combobox(self.frmDispBar, textvariable=self.varValName, width=_COMBO_WIDTH)
        self.cbValName['values'] = list(self.dat.getVals().values())
        self.cbValName['state' ] = 'readonly'
        self.cbValName.bind('<<ComboboxSelected>>', self.viewChanged)
        self.cbValName.grid(column=5, row=0, sticky=tk.E, padx=_PADX, pady=_PADY)

        #----------------------------------------------------------------------
        # Method to apply selector
        #----------------------------------------------------------------------
        self.varSetMet = tk.StringVar() # Name of the method to apply to the data

        lblMet = ttk.Label(self.frmDispBar, text="Set values:")
        lblMet.grid(column=2, row=1, sticky=tk.E, padx=_PADX, pady=_PADY)

        self.cbSetMet = ttk.Combobox(self.frmDispBar, textvariable=self.varSetMet, width=int(_COMBO_WIDTH))
        self.cbSetMet['values'] = list(self.dat.mapSetMethods().keys())
        self.cbSetMet['state' ] = 'readonly'
        self.cbSetMet.bind('<<ComboboxSelected>>', self.setMethod)
        self.cbSetMet.grid(column=3, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)

    #--------------------------------------------------------------------------
    def updateDisplayBar(self):

        self.lblX['text'] = self.dat.axeNameByKey(self.display['keyX']) if self.display['keyX'] != 'None' else 'None'
        self.lblY['text'] = self.dat.axeNameByKey(self.display['keyY']) if self.display['keyY'] != 'None' else 'None'


    #--------------------------------------------------------------------------
    def dims(self):
        "Returns number of not-None dimensions in the chart"

        toRet = 0

        if self.display['keyX']: toRet += 1
        if self.display['keyY']: toRet += 1

        self.logger.debug(f'{self.name}.dims: Chart has {toRet} dimensions')
        return toRet

    #--------------------------------------------------------------------------
    def viewChanged(self, event=None, force=False):
        "Prepares npData to show according to axes and value to show"

        #----------------------------------------------------------------------
        # Check for Changes in show options
        #----------------------------------------------------------------------
        if self.display['showMethod'] != self.varValMet:
            self.display['showMethod'] = self.varValMet.get()
            self.display['needShow']   = True

        if self.display['valName'] != self.varValName:
            self.display['valName'] = self.varValName.get()
            self.display['needShow']  = True

        self.display['valKey'] = self.dat.valKeyByName(self.display['valName'])
        if not self.display['valKey']:
            self.logger.warning(f"{self.name}.viewChanged: Value '{self.display['valName']}' not in values {list(self.dat.getVals().values())}, setting to 'None'")
            return

        #----------------------------------------------------------------------
        self.logger.info(f"{self.name}.viewChanged: Show {self.display['showMethod']}({self.display['valName']}[{self.display['valKey']}]) in X:{self.display['keyX']}, Y:{self.display['keyY']}")

        #----------------------------------------------------------------------
        # Changes in any key required data refresh
        #----------------------------------------------------------------------
        if self.display['needShow'] or force:

            self.display['needShow'] = True

            #------------------------------------------------------------------
            # Ziskam list InfoPoints (whole object) patriacich subsetu
            #------------------------------------------------------------------
            self.dat.actSubmatrix(actSubIdxs=self.sub2D)

        #----------------------------------------------------------------------
        # Ak nenastala zmena, vyskocim
        #----------------------------------------------------------------------
        self.logger.info(f'{self.name}.viewChanged: needShow = {self.display['needShow']}')
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
        self.logger.info(f"{self.name}.show: axisX='{self.display['keyX']}', axisY='{self.display['keyY']}', value='{self.display['valKey']}', method='{self.display['showMethod']}'")

        #----------------------------------------------------------------------
        # Ak nenastala zmena, vyskocim
        #----------------------------------------------------------------------
        if not self.display['needShow']:
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
        if not self.display['valKey']:
            self.logger.warning(f'{self.name}.show: No value selected, nothig to show')
            return

        #----------------------------------------------------------------------
        # Check axis to show
        #----------------------------------------------------------------------
        if not self.display['keyX'] and not self.display['keyY']:
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
        showFtion = self.dat.mapShowMethods()[self.display['showMethod']]

        self.logger.debug(f'{self.name}.show: Iterating {len(self.dat.actList)} iPoints for showFtion={self.display['showMethod']} with keyV={self.display['valKey']}')
        for i, point in enumerate(self.dat.actList):

            valueToShow = showFtion(point, self.display['valKey'])

            if valueToShow:

                listC.append(valueToShow)
                if self.display['keyX']: listX.append(point.pos(self.display['keyX']))
                if self.display['keyY']: listY.append(point.pos(self.display['keyY']))

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

        if self.display['keyX'] and npX.size==0:
            self.logger.info(f'{self.name}.show: Axe X is selected but has no data to show')
            return

        if self.display['keyY'] and npY.size==0:
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
        if self.display['keyX']: chart.set_xlabel(self.dat.axeNameByKey(self.display['keyX']))
        if self.display['keyY']: chart.set_ylabel(self.dat.axeNameByKey(self.display['keyY']))

        #----------------------------------------------------------------------
        # Log axis X, Y
        #----------------------------------------------------------------------
        if self.varLogX.get(): chart.set_xscale('log')
        if self.varLogX.get(): chart.set_yscale('log')

        #----------------------------------------------------------------------
        # Show the chart
        #----------------------------------------------------------------------
        if self.dims() == 1:
            #------------------------------------------------------------------
            # Chart 1D
            #------------------------------------------------------------------
            if self.display['keyX']: axis = npX
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

        self.logger.info(f'{self.name}.onClick:')

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
            coord = {self.display['keyX']: x, self.display['keyY']: y}
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

                val     = self.actPoint.val(self.display['valName'])
                valName = self.actPoint.valName(self.display['valName'])

                self.logger.info(f'{self.name}.onClick: right click for {self.display['valName']}[{valName}] = {val} {type(val)}')

                #--------------------------------------------------------------
                # User input based on value type
                #--------------------------------------------------------------
                if type(val) in [int, float]:

                   inp = askReal(container=self, title=f'Zadaj hodnotu pre {valName}', prompt=self.display['valName'], initialvalue=val)

                   if inp is None:
                       self.logger.audit(f'{self.name}.onClick: User input cancelled by user')
                       return

                   self.actPoint.set(vals={self.display['valName']:inp})
                   self.logger.audit(f'{self.name}.onClick: Set {self.display['valName']} = {inp} for {self.actPoint}')

                #--------------------------------------------------------------
                # Data was changed, so show the chart
                #--------------------------------------------------------------
                self.logger.warning(f'{self.name}.onClick: Data changed, need to show the chart')
                self.display['needShow'] = True
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
    def onPointSchema(self, event=None):

        self.logger.info(f'{self.name}.onPointSchema:')

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
                    self.logger.warning(f'{self.name}.onPointSchema: Axes changed from {origSchema} to {self.dat.getSchema()}, reset data')

                else:
                    self.dat.setSchema(origSchema)
                    self.logger.warning(f'{self.name}.onPointSchema: Axes changed from {origSchema} to {self.dat.getSchema()}, but user cancelled changes, schema restored')
                    return

        #----------------------------------------------------------------------
        self.logger.debug(f'{self.name}.onPointSchema: InfoPointGui window closed')

    #--------------------------------------------------------------------------
    def onMatrixProp(self, event=None):

        self.logger.info(f'{self.name}.onMatrixProp:')

        gui = InfoMatrixDataGui(name=f'Matrix {self.dat.name}', container=self, matrix=self.dat)
        gui.grab_set()
        self.wait_window(gui)

        #----------------------------------------------------------------------
        # Vyhodnotenie zmien v scheme
        #----------------------------------------------------------------------
        self.updateDisplayBar()

        #----------------------------------------------------------------------
        self.logger.debug(f'{self.name}.onMatrixProp: Matrix properties set')

    #--------------------------------------------------------------------------
    def onDisplay(self, event=None):

        self.logger.info(f'{self.name}.onDisplay:')

        gui = InfoMatrixDisplayGui(name=f'Display options', container=self, display=self.display)
        gui.grab_set()
        self.wait_window(gui)

        #----------------------------------------------------------------------
        # Ak sa zmenili osy, zresetujem sub2D
        #----------------------------------------------------------------------
        if (self.display['keyX'] != gui.display['keyX']) or (self.display['keyY'] != gui.display['keyY']):

                self.logger.info(f"{self.name}.viewChanged: X:{self.display['keyX']}->{gui.display['keyX']} Y:{self.display['keyY']}->{gui.display['keyY']}, resetting sub2D")
                self.display = gui.display.copy()

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











        #----------------------------------------------------------------------
        self.updateDisplayBar()
        self.show()

    #--------------------------------------------------------------------------
    def onSetData(self, event=None):

        metKey = self.varSetMet.get()
        if not metKey:
            self.logger.warning(f'{self.name}.method: No method selected, nothing to do')
            return

        if not self.display['valKey']:
            self.logger.warning(f'{self.name}.method: No value selected, nothing to set to')
            return

        #----------------------------------------------------------------------
        self.logger.info(f'{self.name}.method: Value {self.display['valName']}({self.display['valKey']}) will be set by {metKey} with subset = {self.sub2D}')

        #----------------------------------------------------------------------
        # Ziskanie hodnot parametrov metody od usera
        #----------------------------------------------------------------------
        metDef = self.dat.mapSetMethods()[metKey]
        params = metDef['par']
        usrPar = {}

        for par, entry in params.items():

            newEntry = askReal(container=self, title=f"Parameter of {metKey}", prompt=par, initialvalue=entry)

            if newEntry is None:
                self.logger.info(f"{self.name}.method: {metKey} cancelled by user")
                return

            usrPar[par] = newEntry

        #----------------------------------------------------------------------
        # Vykonanie metody
        #----------------------------------------------------------------------

        self.logger.info(f"{self.name}.method: {metKey}(key={self.display['valKey']}), par={usrPar})")
        self.dat.setData(methodKey=metKey, valueKey=self.display['valKey'], params=usrPar)

        self.viewChanged(force=True)

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
    def setMethod(self, event=None):
        "Apply data in active cut"

        #----------------------------------------------------------------------


    #--------------------------------------------------------------------------
    def reset(self):
        "Reset all data into default values"

        self.actPoint = None               # Actual working InfoPoint

        self.display['valName']     = 'None'             # key for value to show
        self.display['keyX']     = 'None'             # Default key for Axis X to show
        self.display['keyY']     = 'None'             # Default key for Axis Y to show

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