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
        # Initialise InfoMatrixGui
        #----------------------------------------------------------------------
        super().__init__(container=container, dat=dat)

        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------


        #----------------------------------------------------------------------
        # Inicializacia
        #----------------------------------------------------------------------
        self.cbValName.set('State')
        self.viewChanged()


        #----------------------------------------------------------------------
        self.logger.audit(f'{self.name}.init: Done')

    #--------------------------------------------------------------------------
    def showChildFrame(self):
        "Show frame dedicated to child classes"

        lbl = ttk.Label(self.frmChild, text="Child frame not implemented", foreground="red")
        lbl.pack(fill=tk.X, expand=True, side=tk.TOP, anchor=tk.N)

    #--------------------------------------------------------------------------
    def updateChildFrame(self):
        "Update frame dedicated to child classes. This method is called in self.viewChanged()"

        pass


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