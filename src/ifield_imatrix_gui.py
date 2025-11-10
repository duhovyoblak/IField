#==============================================================================
# Info tkChart library
#------------------------------------------------------------------------------
import tkinter                as tk
from   tkinter                import (ttk, font, PanedWindow)
from   tkinter.messagebox     import showinfo, askokcancel, askyesno

from   siqolib.logger           import SiqoLogger
from   siqolib.message          import SiqoMessage, askInt, askReal, askStr
from   siqo_imatrix_gui         import InfoMatrixGui
from   ifield_imatrix           import InfoFieldMatrix

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_VER            = '1.0'

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
        self.varL2E   = tk.IntVar   (value=dat.l2e  ) # Pocet posunu epochy pre jeden krok na osi Lambda = 1 / rychlost informacie
        self.varMaxL  = tk.IntVar   (value=dat.maxL ) # Maximalny pocet krokov na osi Lambda pri ziskani zoznamu stavov susednych bodov

        self.varSType = tk.StringVar(value=dat.sType) # Typ stavu
        self.varSAgg  = tk.StringVar(value=dat.sAgg ) # Spôsob agregácie stavov do jednej hodnoty
        self.varRule  = tk.StringVar(value=dat.rule ) # Pravidlo agregacie stavov susednych bodov

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
        "Show frame dedicated to child classes"

        #----------------------------------------------------------------------
        # Pocet posunu epochy pre jeden krok na osi Lambda = 1 / rychlost informacie
        #----------------------------------------------------------------------
        lbl = ttk.Label(container, text="L2E (epoch per lambda):")
        lbl.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)

        spinBox = ttk.Spinbox(container, from_=0, to=1000, textvariable=self.varL2E, width=10)
        spinBox['state'] = 'normal'
        spinBox.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)

        #----------------------------------------------------------------------
        # Maximalny pocet krokov na osi Lambda pri ziskani zoznamu stavov susednych bodov
        #----------------------------------------------------------------------
        lbl = ttk.Label(container, text="Neighbors' to consider")
        lbl.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)

        spinBox = ttk.Spinbox(container, from_=0, to=1000, textvariable=self.varMaxL, width=10)
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
        comboBox.bind('<<ComboboxSelected>>', lambda e: self.onSType())

        #----------------------------------------------------------------------
        # Spôsob agregácie stavov do jednej hodnoty
        #----------------------------------------------------------------------
        lbl = ttk.Label(container, text="Aggregation method:")
        lbl.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)
        comboBox = ttk.Combobox(container, textvariable=self.varSAgg, state='readonly')
        comboBox['values'] = self.dat.sAggs
        comboBox.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)
        comboBox.bind('<<ComboboxSelected>>', lambda e: self.onSAgg())

        #----------------------------------------------------------------------
        # Pravidlo agregacie stavov susednych bodov
        #----------------------------------------------------------------------
        lbl = ttk.Label(container, text="Neighbors' rule:")
        lbl.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)
        comboBox = ttk.Combobox(container, textvariable=self.varRule, state='readonly')
        comboBox['values'] = self.dat.rules
        comboBox.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)
        comboBox.bind('<<ComboboxSelected>>', lambda e: self.onRule())

    #--------------------------------------------------------------------------
    def updateChildFrame(self):
        "Update frame dedicated to child classes. This method is called in self.viewChanged()"

        pass

    #--------------------------------------------------------------------------
    def onSType(self):
        "Reaction to change of state type"

        self.dat.sType = self.varSType.get()
        self.logger.info(f'{self.name}.onSType: State type changed to {self.dat.sType}')

    #--------------------------------------------------------------------------
    def onSAgg(self):
        "Reaction to change of aggregation method"

        self.dat.sAgg = self.varSAgg.get()
        self.logger.info(f'{self.name}.onSAgg: Aggregation method changed to {self.dat.sAgg}')

    #--------------------------------------------------------------------------
    def onRule(self):
        "Reaction to change of neighbors' rule"

        self.dat.rule = self.varRule.get()
        self.logger.info(f'{self.name}.onRule: Neighbors\' rule changed to {self.dat.rule}')

    #--------------------------------------------------------------------------


#==============================================================================
#   Inicializacia kniznice
#------------------------------------------------------------------------------
print(f'SIQO IFieldMatrixGui library ver {_VER}')

if __name__ == '__main__':

    from   ifield_imatrix           import InfoFieldMatrix

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