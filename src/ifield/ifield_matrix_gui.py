#==============================================================================
# Info tkChart library
#------------------------------------------------------------------------------
import tkinter                as tk
from   tkinter                import ttk

from   siqolib.message        import SiqoMessage

from   idata.idata_gui            import InfoDataGui

from   .                      import logger
from   .ifield_matrix         import InfoFieldMatrix

#==============================================================================
# Module's constants
#------------------------------------------------------------------------------
_VER            = '1.1.0'

_PADX           =  5
_PADY           =  5

#==============================================================================
# Module's variables
#------------------------------------------------------------------------------

#==============================================================================
# Class IFieldMatrixGui
#------------------------------------------------------------------------------
class IFieldMatrixGui(InfoDataGui):

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, container, data:InfoFieldMatrix):
        "Call constructor of IFieldMatrixGui and initialise it for respective data"

        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------
        self.varL2E   = tk.IntVar   (value=data.l2e  )
        self.varPhs   = tk.IntVar   (value=data.phs  )
        self.varL2P   = tk.IntVar   (value=data.l2p  )

        self.varSType = tk.StringVar(value=data.sType)
        self.varSAgg  = tk.StringVar(value=data.sAgg )
        self.varRule  = tk.StringVar(value=data.rule )
        self.varMaxL  = tk.IntVar   (value=data.maxL )

        #----------------------------------------------------------------------
        # Initialise InfoDataGui
        #----------------------------------------------------------------------
        super().__init__(container=container, data=data)

        #----------------------------------------------------------------------
        # Inicializacia
        #----------------------------------------------------------------------
        self.cbValName.set('State')
        self.viewChanged()

        #----------------------------------------------------------------------
        logger.audit(f'{self.name}.init: Done')

    #--------------------------------------------------------------------------
    def showChildFrame(self, container):
        """Show frame in parent container InfoDataGui dedicated to child classes."""

        lbl = ttk.Label(container, text="L2E (epoch per lambda):")
        lbl.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)

        spinBox = ttk.Spinbox(container, from_=0, to=100, textvariable=self.varL2E, width=10, command=self.updateChildFrame)
        spinBox['state'] = 'normal'
        spinBox.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)

        lbl = ttk.Label(container, text="Number of phases:")
        lbl.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)

        spinBox = ttk.Spinbox(container, from_=1, to=360, textvariable=self.varPhs, width=10, command=self.updateChildFrame)
        spinBox['state'] = 'normal'
        spinBox.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)

        lbl = ttk.Label(container, text="L2P (delta phase per lambda):")
        lbl.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)

        spinBox = ttk.Spinbox(container, from_=0, to=100, textvariable=self.varL2P, width=10, command=self.updateChildFrame)
        spinBox['state'] = 'normal'
        spinBox.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)

        ttk.Label(container, text="").pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, pady=_PADY)

        lbl = ttk.Label(container, text="State type:")
        lbl.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)

        comboBox = ttk.Combobox(container, textvariable=self.varSType, state='readonly')
        comboBox['values'] = self.data.sTypes
        comboBox.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)
        comboBox.bind('<<ComboboxSelected>>', lambda event: self.updateChildFrame())

        lbl = ttk.Label(container, text="Aggregation method:")
        lbl.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)
        comboBox = ttk.Combobox(container, textvariable=self.varSAgg, state='readonly')
        comboBox['values'] = self.data.sAggs
        comboBox.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)
        comboBox.bind('<<ComboboxSelected>>', lambda event: self.updateChildFrame())

        lbl = ttk.Label(container, text="Neighbors' rule:")
        lbl.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)
        comboBox = ttk.Combobox(container, textvariable=self.varRule, state='readonly')
        comboBox['values'] = self.data.rules
        comboBox.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)
        comboBox.bind('<<ComboboxSelected>>', lambda event: self.updateChildFrame())

        lbl = ttk.Label(container, text="Neighbors' to consider")
        lbl.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)

        spinBox = ttk.Spinbox(container, from_=0, to=1000, textvariable=self.varMaxL, width=10, command=self.updateChildFrame)
        spinBox['state'] = 'normal'
        spinBox.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)

    #--------------------------------------------------------------------------
    def updateChildFrame(self):
        """Update frame in parent container InfoDataGui dedicated to child classes."""

        if self.data.l2e != self.varL2E.get():
            logger.warning(f'{self.name}.updateChildFrame: L2E changed {self.data.l2e} -> {self.varL2E.get()}')
            self.data.l2e = self.varL2E.get()

        if self.data.phs != self.varPhs.get():
            logger.warning(f'{self.name}.updateChildFrame: Number of phases changed {self.data.phs} -> {self.varPhs.get()}')
            self.data.phs = self.varPhs.get()

        if self.data.l2p != self.varL2P.get():
            logger.warning(f'{self.name}.updateChildFrame: L2P changed {self.data.l2p} -> {self.varL2P.get()}')
            self.data.l2p = self.varL2P.get()

        if self.data.sType != self.varSType.get():
            logger.warning(f'{self.name}.updateChildFrame: State type changed {self.data.sType} -> {self.varSType.get()}')
            self.data.sType = self.varSType.get()

        if self.data.sAgg != self.varSAgg.get():
            logger.warning(f'{self.name}.updateChildFrame: Aggregation method changed {self.data.sAgg} -> {self.varSAgg.get()}')
            self.data.sAgg = self.varSAgg.get()

        if self.data.rule != self.varRule.get():
            logger.warning(f'{self.name}.updateChildFrame: Neighbors\' rule changed {self.data.rule} -> {self.varRule.get()}')
            self.data.rule = self.varRule.get()

        if self.data.maxL != self.varMaxL.get():
            logger.warning(f'{self.name}.updateChildFrame: Maximal number of neighbors changed {self.data.maxL} -> {self.varMaxL.get()}')
            self.data.maxL = self.varMaxL.get()

        logger.debug(f'{self.name}.updateChildFrame: Done')

    #--------------------------------------------------------------------------
    def onClickLeft(self, x, y):
        "Print information about mouse-given position"

        logger.info(f'{self.name}.onClick: left click for {self.actPoint}')

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

#==============================================================================
# Inicializacia modulu
#------------------------------------------------------------------------------
print(f'IFieldMatrixGui ver {_VER}')

if __name__ == '__main__':

    logger.info("Testing IFieldMatrixGui class")

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
