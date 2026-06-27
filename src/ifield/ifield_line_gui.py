#==============================================================================
# Info tkChart library
#------------------------------------------------------------------------------
import tkinter                as tk
from   tkinter                import ttk

from   siqolib.message        import SiqoMessage

from   idata.idata_gui            import InfoDataGui

from   .                      import logger
from   .ifield_line           import InfoFieldLine

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
# Class IFieldLineGui
#------------------------------------------------------------------------------
class IFieldLineGui(InfoDataGui):

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, container, data:InfoFieldLine):
        "Call constructor of IFieldLineGui and initialise it for respective data"

        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------
#        self.varL2E   = tk.IntVar   (value=dat.l2e  )

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

#        spinBox = ttk.Spinbox(container, from_=0, to=100, textvariable=self.varL2E, width=10, command=self.updateChildFrame)
#        spinBox['state'] = 'normal'
#        spinBox.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)


#        comboBox = ttk.Combobox(container, textvariable=self.varSType, state='readonly')
#        comboBox['values'] = self.dat.sTypes
#        comboBox.pack(fill=tk.X, expand=False, side=tk.TOP, anchor=tk.N, padx=_PADX, pady=_PADY)
#        comboBox.bind('<<ComboboxSelected>>', lambda event: self.updateChildFrame())

    #--------------------------------------------------------------------------
    def updateChildFrame(self):
        """Update frame in parent container InfoDataGui dedicated to child classes."""

#        if self.dat.l2e != self.varL2E.get():
#            logger.warning(f'{self.name}.updateChildFrame: L2E changed {self.dat.l2e} -> {self.varL2E.get()}')
#            self.dat.l2e = self.varL2E.get()

        logger.debug(f'{self.name}.updateChildFrame: Done')

    #--------------------------------------------------------------------------
    def onClickLeft(self, x, y):
        "Print information about mouse-given position"

        logger.info(f'{self.name}.onClick: left click for {self.actPoint}')

        valueKey=self.display['valKey']
        actState = self.actPoint.val(valueKey)

        text = [f'Information about nearest point to [{round(y,2)}, {round(x,2)}] for value "{valueKey}"']
        text.append('')

        idxs = self.data.lastPosIdxs()
        text.append(f"{str(self.actPoint)} at {idxs}")
        text.append('')

        msgWin = SiqoMessage(name=self.data.name, text=text, wpix=800)

#==============================================================================
# Inicializacia modulu
#------------------------------------------------------------------------------
print(f'IFieldLineGui ver {_VER}')

if __name__ == '__main__':

    logger.info("Testing IFieldLineGui class")

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
