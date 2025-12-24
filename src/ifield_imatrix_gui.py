#==============================================================================
# Info tkChart library
#------------------------------------------------------------------------------
import tkinter                  as tk
from   tkinter                  import ttk

from   siqolib.message          import SiqoMessage
from   siqo_imatrix_gui         import InfoMatrixGui
from   ifield_imatrix           import InfoFieldMatrix

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_VER            = '1.1'

_PADX           =  5
_PADY           =  5

#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# Class IFieldMatrixGui
#------------------------------------------------------------------------------
class IFieldMatrixGui(InfoMatrixGui):

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, container, dat:InfoFieldMatrix):
        "Call constructor of IFieldMatrixGui and initialise it for respective data"

        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------
        self.varL2E   = tk.IntVar   (value=dat.l2e  ) # Pocet posunu epochy na jeden krok na osi Lambda = 1 / rychlost informacie
        self.varPhs   = tk.IntVar   (value=dat.phs  ) # Pocet fazovych stavov pre komplexne hodnoty
        self.varL2P   = tk.IntVar   (value=dat.l2p  ) # Pocet pootoceni fazy na jeden krok na osi Lambda =

        self.varSType = tk.StringVar(value=dat.sType) # Typ stavu
        self.varSAgg  = tk.StringVar(value=dat.sAgg ) # Spôsob agregácie stavov do jednej hodnoty
        self.varRule  = tk.StringVar(value=dat.rule ) # Pravidlo agregacie stavov susednych bodov
        self.varMaxL  = tk.IntVar   (value=dat.maxL ) # Maximalny pocet krokov na osi Lambda pri ziskani zoznamu stavov susednych bodov

        #----------------------------------------------------------------------
        # Initialise InfoMatrixGui
        #----------------------------------------------------------------------
        super().__init__(container=container, dat=dat)

        #----------------------------------------------------------------------
        # Inicializacia
        #----------------------------------------------------------------------
        self.cbValName.set('State')
        self.viewChanged()

        #----------------------------------------------------------------------
        self.logger.audit(f'{self.name}.init: Done')

    #--------------------------------------------------------------------------
    def showChildFrame(self, container):
        """Show frame in parent container InfoMatrixGui dedicated to child classes.
           This method is called in InfoMatrixGui.show()"""

        #----------------------------------------------------------------------
        # Pocet posunu epochy na jeden krok na osi Lambda = 1 / rychlost informacie
        #----------------------------------------------------------------------
        lbl = ttk.Label(container, text="L2E (epoch per lambda):")
        lbl.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)

        spinBox = ttk.Spinbox(container, from_=0, to=100, textvariable=self.varL2E, width=10, command=self.updateChildFrame)
        spinBox['state'] = 'normal'
        spinBox.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)

        #----------------------------------------------------------------------
        # Pocet fazovych stavov pre komplexne hodnoty
        #----------------------------------------------------------------------
        lbl = ttk.Label(container, text="Number of phases:")
        lbl.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)

        spinBox = ttk.Spinbox(container, from_=1, to=360, textvariable=self.varPhs, width=10, command=self.updateChildFrame)
        spinBox['state'] = 'normal'
        spinBox.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)

        #----------------------------------------------------------------------
        # Pocet pootoceni fazy na jeden krok na osi Lambda =
        #----------------------------------------------------------------------
        lbl = ttk.Label(container, text="L2P (delta phase per lambda):")
        lbl.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)

        spinBox = ttk.Spinbox(container, from_=0, to=100, textvariable=self.varL2P, width=10, command=self.updateChildFrame)
        spinBox['state'] = 'normal'
        spinBox.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)

        # Add space between spinBox and the next label
        ttk.Label(container, text="").pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, pady=_PADY)

        #----------------------------------------------------------------------
        # Vyber typu stavu
        #----------------------------------------------------------------------
        lbl = ttk.Label(container, text="State type:")
        lbl.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)

        comboBox = ttk.Combobox(container, textvariable=self.varSType, state='readonly')
        comboBox['values'] = self.dat.sTypes
        comboBox.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)
        comboBox.bind('<<ComboboxSelected>>', lambda event: self.updateChildFrame())

        #----------------------------------------------------------------------
        # Spôsob agregácie stavov do jednej hodnoty
        #----------------------------------------------------------------------
        lbl = ttk.Label(container, text="Aggregation method:")
        lbl.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)
        comboBox = ttk.Combobox(container, textvariable=self.varSAgg, state='readonly')
        comboBox['values'] = self.dat.sAggs
        comboBox.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)
        comboBox.bind('<<ComboboxSelected>>', lambda event: self.updateChildFrame())

        #----------------------------------------------------------------------
        # Pravidlo agregacie stavov susednych bodov
        #----------------------------------------------------------------------
        lbl = ttk.Label(container, text="Neighbors' rule:")
        lbl.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)
        comboBox = ttk.Combobox(container, textvariable=self.varRule, state='readonly')
        comboBox['values'] = self.dat.rules
        comboBox.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)
        comboBox.bind('<<ComboboxSelected>>', lambda event: self.updateChildFrame())

        #----------------------------------------------------------------------
        # Maximalny pocet krokov na osi Lambda pri ziskani zoznamu stavov susednych bodov
        #----------------------------------------------------------------------
        lbl = ttk.Label(container, text="Neighbors' to consider")
        lbl.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)

        spinBox = ttk.Spinbox(container, from_=0, to=1000, textvariable=self.varMaxL, width=10, command=self.updateChildFrame)
        spinBox['state'] = 'normal'
        spinBox.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)

    #--------------------------------------------------------------------------
    def updateChildFrame(self):
        """Update frame in parent container InfoMatrixGui dedicated to child classes.
           This method is called in InfoMatrixGui.viewChanged()"""

        if self.dat.l2e != self.varL2E.get():
            self.logger.warning(f'{self.name}.updateChildFrame: L2E changed {self.dat.l2e} -> {self.varL2E.get()}')
            self.dat.l2e = self.varL2E.get()

        if self.dat.phs != self.varPhs.get():
            self.logger.warning(f'{self.name}.updateChildFrame: Number of phases changed {self.dat.phs} -> {self.varPhs.get()}')
            self.dat.phs = self.varPhs.get()

        if self.dat.l2p != self.varL2P.get():
            self.logger.warning(f'{self.name}.updateChildFrame: L2P changed {self.dat.l2p} -> {self.varL2P.get()}')
            self.dat.l2p = self.varL2P.get()

        if self.dat.sType != self.varSType.get():
            self.logger.warning(f'{self.name}.updateChildFrame: State type changed {self.dat.sType} -> {self.varSType.get()}')
            self.dat.sType = self.varSType.get()

        if self.dat.sAgg != self.varSAgg.get():
            self.logger.warning(f'{self.name}.updateChildFrame: Aggregation method changed {self.dat.sAgg} -> {self.varSAgg.get()}')
            self.dat.sAgg = self.varSAgg.get()

        if self.dat.rule != self.varRule.get():
            self.logger.warning(f'{self.name}.updateChildFrame: Neighbors\' rule changed {self.dat.rule} -> {self.varRule.get()}')
            self.dat.rule = self.varRule.get()

        if self.dat.maxL != self.varMaxL.get():
            self.logger.warning(f'{self.name}.updateChildFrame: Maximal number of neighbors changed {self.dat.maxL} -> {self.varMaxL.get()}')
            self.dat.maxL = self.varMaxL.get()

        self.logger.debug(f'{self.name}.updateChildFrame: Done')

    #--------------------------------------------------------------------------
    def onClickLeft(self, x, y):
        "Print information about mouse-given position"

        self.logger.info(f'{self.name}.onClick: left click for {self.actPoint}')

        valueKey=self.display['valKey']
        actState = self.actPoint.val(valueKey)

        text = [f'Information about nearest point to [{round(y,2)}, {round(x,2)}] for value "{valueKey}"']
        text.append('')

        idxs = self.dat.lastPosIdxs()
        text.append(f"{str(self.actPoint)} at {idxs}")
        text.append('')

        leftStates, rightStates = self.dat.getNeighStates(valueKey=valueKey, l=idxs[0], e=idxs[1])
        text.append(f'Left states  : {leftStates}')
        text.append(f'Right states : {rightStates}')
        text.append('')

        leftState = self.dat.aggStates(leftStates )
        rightState= self.dat.aggStates(rightStates)
        text.append(f'Aggregated left  state : {leftState}')
        text.append(f'Aggregated right state : {rightState}')
        text.append('')

        newState = self.dat.aggNeighbors(leftState, actState, rightState)
        text.append(f'New state after applying neighbors\' rule : {newState}')


        msgWin = SiqoMessage(name=self.dat.name, text=text, wpix=800)

    #--------------------------------------------------------------------------


#==============================================================================
#   Inicializacia kniznice
#------------------------------------------------------------------------------
print(f'SIQO IFieldMatrixGui library ver {_VER}')

if __name__ == '__main__':

    from   siqolib.logger           import SiqoLogger
    from   ifield_imatrix           import InfoFieldMatrix

    logger = SiqoLogger(name='InfoFieldMatrix test')
    logger.setLevel('DEBUG')

    #--------------------------------------------------------------------------
    # Test of the IFieldMatrixGui class
    #--------------------------------------------------------------------------
    win = tk.Tk()
    win.configure(bg='silver', highlightthickness=2, highlightcolor='green')
    win.title('Test of InfoModelGui class')
    #win.maxsize(width=1200, height=800)
    win.minsize(width=600, height=300)
    win.config(highlightbackground = "green", highlightcolor= "green")

    #--------------------------------------------------------------------------
    # Zaciatok testu
    #--------------------------------------------------------------------------
    matrix = InfoFieldMatrix('IFieldMatrix test')
    matrix.logger.frameDepth = 2

    matrixGui = IFieldMatrixGui(container=win, dat=matrix)
    matrixGui.pack(fill=tk.BOTH, expand=True, side=tk.TOP, anchor=tk.N)

    matrixGui.logger.setLevel('INFO')
    win.mainloop()

    matrixGui.logger.info('Stop of IFieldMatrixGui test')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------