#==============================================================================
# Info tkChart library
#------------------------------------------------------------------------------
import tkinter                as tk
from   tkinter                import (ttk, font, PanedWindow)
from   tkinter.messagebox     import showinfo

from   siqolib.logger         import SiqoLogger
from   siqolib.message        import SiqoMessage, askInt, askReal
from   siqo_ipoint            import InfoPoint

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_VER            = '1.1'
_WIN            = '800x540'
_DPI            = 100

_COMBO_WIDTH    = 12
_PADX           =  5
_PADY           =  5

#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# Class InfoMatrixMethodGui
#------------------------------------------------------------------------------
class InfoMatrixMethodGui(tk.Toplevel):

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name, container, params, **kwargs):
        "Call constructor of InfoMatrixMethodGui and initialise it for respective data"

        self.logger = SiqoLogger(name)
        self.logger.audit(f'{name}.init: {params}')

        self.name     = name                    # Name of this chart
        self.params   = params                  # Display options to be edited

        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------
        self.origParams = self.params.copy()    # Original parameters to restore on cancel

        #----------------------------------------------------------------------
        # Initialise original tkInter.Tk
        #----------------------------------------------------------------------
        super().__init__(container)
        self.title(self.name)
        self.focus_set()

        #----------------------------------------------------------------------
        # Create Params options frame
        #----------------------------------------------------------------------
        frmParams = ttk.Frame(self)
        frmParams.pack(fill=tk.BOTH, expand=True, side=tk.TOP, anchor=tk.N)

        #----------------------------------------------------------------------
        # Show header
        #----------------------------------------------------------------------
        lbl = ttk.Label(frmParams, text='Parameter name')
        lbl.grid(column=0, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        lbl = ttk.Label(frmParams, text='Parameter value')
        lbl.grid(column=1, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        #----------------------------------------------------------------------
        # Show parameters
        #----------------------------------------------------------------------
        row = 1
        for key, val in params.items():

            self.logger.debug(f"{self.name}.showParams: '{key}' = '{val}'")

            lbl = ttk.Label(frmParams, text=str(key))
            lbl.grid(column=0, row=row, sticky=tk.W, padx=_PADX, pady=_PADY)

            ent = ttk.Entry(frmParams)
            ent.insert(0, str(val))
            ent.bind("<FocusOut>", lambda event, key=key, entry=ent: self.setParam(key, entry.get()))
            ent.grid(column=1, row=row, sticky=tk.W, padx=_PADX, pady=_PADY)

            row += 1

        #----------------------------------------------------------------------
        # Create bottom buttons
        #----------------------------------------------------------------------
        btnCancel = ttk.Button(frmParams, text="Cancel", command=self.cancel)
        btnCancel.grid(column=1, row=row+1, sticky=tk.E, padx=_PADX, pady=_PADY)

        btnOk = ttk.Button(frmParams, text="OK", command=self.ok)
        btnOk.grid(    column=2, row=row+1, sticky=tk.W, padx=_PADX, pady=_PADY)

        #----------------------------------------------------------------------
        # Bind the close window event
        #----------------------------------------------------------------------
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        #----------------------------------------------------------------------
        # Initialisation
        #----------------------------------------------------------------------
        self.logger.audit(f'{name}.init: Done')

    #==========================================================================
    # Show the chart
    #--------------------------------------------------------------------------
    def setParam(self, key:str, val:str):
        "Update parameter with user iput value"

        self.params[key] = val
        self.logger.info(f"{self.name}.setParam: '{key}' : '{val}' updated")

    #--------------------------------------------------------------------------
    def cancel(self):
        "Cancel changes and restore original settings"

        self.params = self.origParams.copy()
        self.logger.info(f'{self.name}.cancel: Parameters restored to {self.params}')
        self.destroy()

    #--------------------------------------------------------------------------
    def ok(self):
        "Apply changes and close the dialog"

        self.logger.info(f'{self.name}.ok: Parameters are set to {self.params}')
        self.destroy()

    #--------------------------------------------------------------------------

#==============================================================================
#   Inicializacia kniznice
#------------------------------------------------------------------------------
print(f'SIQO InfoMatrixMethodGui library ver {_VER}')

if __name__ == '__main__':

    #--------------------------------------------------------------------------
    # Test of the InfoMatrixMethodGui class
    #--------------------------------------------------------------------------
    win = tk.Tk()
    win.configure(bg='silver', highlightthickness=2, highlightcolor='green')
    win.title('Test of InfoMatrixMethodGui class')
    #win.maxsize(width=900, height=800)
    win.minsize(width=400, height=300)
    win.config(highlightbackground = "green", highlightcolor= "green")

    #--------------------------------------------------------------------------
    # Zaciatok testu
    #--------------------------------------------------------------------------
    params   = {'type'     : '2D'   # Actual type of the chart
               ,'needShow' : False  # Flag to show the chart, True means data changed and need to be shown
               ,'keyS'     : 'None' # key for methods for value to show
               ,'int param': 2 # key for value to show
               ,'keyX'     : 'None' # key for Axis X to show
               ,'keyY'     : 'None' # key for Axis Y to show
            }

    gui = InfoMatrixMethodGui(name='Method parameters set', container=win, params=params)

    win.mainloop()
    gui.logger.info('Stop of InfoMatrixMethodGui test')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------