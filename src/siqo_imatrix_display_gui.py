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
_VER            = '1.0'
_WIN            = '800x540'
_DPI            = 100

_COMBO_WIDTH    = 12
_PADX           =  5
_PADY           =  5

#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# Class InfoMatrixDisplayGui
#------------------------------------------------------------------------------
class InfoMatrixDisplayGui(tk.Toplevel):

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name, container, matrix, **kwargs):
        "Call constructor of InfoMatrixDisplayGui and initialise it for respective data"

        self.logger = SiqoLogger(name)
        self.logger.audit(f'{name}.init:')

        self.name     = name               # Name of this chart
        self.matrix   = matrix             # Matrix type to work with

        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------
        self.axes     = self.matrix.getAxes()

        #----------------------------------------------------------------------
        # Initialise original tkInter.Tk
        #----------------------------------------------------------------------
        super().__init__(container)
        self.title(self.name)
        self.focus_set()

        #----------------------------------------------------------------------
        # Create Dispay options frame
        #----------------------------------------------------------------------
        frmDisp = ttk.Frame(self)
        frmDisp.pack(fill=tk.BOTH, expand=True, side=tk.TOP, anchor=tk.N)

        # Získaj mená (hodnoty) a kluce k nim z dict self.axes
        axeKeys  = list(self.axes.keys()  )
        axeKeys.append ('Not used')

        axeNames = list(self.axes.values())
        axeNames.append('Not used')

        #----------------------------------------------------------------------
        # List of axes
        #----------------------------------------------------------------------
        lblAxe = ttk.Label(frmDisp, text="Axe:")
        lblAxe.grid(column=0, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        row = 1
        for name in axeNames:
            lblAxe = ttk.Label(frmDisp, text=name)
            lblAxe.grid(column=0, row=row, sticky=tk.W, padx=_PADX, pady=_PADY)
            row += 1

        #----------------------------------------------------------------------
        # Show on X
        #----------------------------------------------------------------------
        self.selX = tk.StringVar(value=axeKeys[0] if len(axeNames)>0 else 'Not used')

        lbl = ttk.Label(frmDisp, text="on X")
        lbl.grid(column=1, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        row = 1
        for key in axeKeys:
            rbtn = ttk.Radiobutton(frmDisp, text='', variable=self.selX, value=key)
            rbtn.grid(column=1, row=row, sticky=tk.W, padx=_PADX, pady=_PADY)
            row += 1

        #----------------------------------------------------------------------
        # Show on Y
        #----------------------------------------------------------------------
        self.selY = tk.StringVar(value=axeKeys[1] if len(axeNames)>1 else 'Not used')

        lbl = ttk.Label(frmDisp, text="on Y")
        lbl.grid(column=2, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        row = 1
        for key in axeKeys:
            rbtn = ttk.Radiobutton(frmDisp, text='', variable=self.selY, value=key)
            rbtn.grid(column=2, row=row, sticky=tk.W, padx=_PADX, pady=_PADY)
            row += 1

        #----------------------------------------------------------------------
        # Show on Z
        #----------------------------------------------------------------------
        self.selZ = tk.StringVar(value=axeKeys[2] if len(axeNames)>2 else 'Not used')

        lbl = ttk.Label(frmDisp, text="on Z")
        lbl.grid(column=3, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        row = 1
        for key in axeKeys:
            rbtn = ttk.Radiobutton(frmDisp, text='', variable=self.selZ, value=key)
            rbtn.grid(column=3, row=row, sticky=tk.W, padx=_PADX, pady=_PADY)
            row += 1

        #----------------------------------------------------------------------
        # Run
        #----------------------------------------------------------------------
        self.selRun = tk.StringVar(value=axeKeys[3] if len(axeNames)>3 else 'Not used')

        lbl = ttk.Label(frmDisp, text="Run")
        lbl.grid(column=4, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        row = 1
        for key in axeKeys:
            rbtn = ttk.Radiobutton(frmDisp, text='', variable=self.selRun, value=key)
            rbtn.grid(column=4, row=row, sticky=tk.W, padx=_PADX, pady=_PADY)
            row += 1

        #----------------------------------------------------------------------
        # Freeze
        #----------------------------------------------------------------------
        self.selRun = tk.StringVar(value=axeKeys[3] if len(axeNames)>3 else 'Not used')

        lbl = ttk.Label(frmDisp, text="Freeze")
        lbl.grid(column=5, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)


        #----------------------------------------------------------------------
        # Create bottom buttons bar
        #----------------------------------------------------------------------
        frmBtn = ttk.Frame(self)
        frmBtn.pack(fill=tk.X, expand=True, side=tk.BOTTOM, anchor=tk.S)

        btnInit = ttk.Button(frmBtn, text="OK", command=self.ok)
        btnInit.pack(side=tk.RIGHT, padx=_PADX, pady=_PADY)

        btnCancel = ttk.Button(frmBtn, text="Cancel", command=self.cancel)
        btnCancel.pack(side=tk.RIGHT, padx=_PADX, pady=_PADY)

        #----------------------------------------------------------------------
        # Bind the close window event
        #----------------------------------------------------------------------
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        #----------------------------------------------------------------------
        # Initialisation
        #----------------------------------------------------------------------
        self.logger.audit(f'{name}.init: Done')

    #--------------------------------------------------------------------------

    #==========================================================================
    # Show the chart
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    def ok(self):
        "Apply inputs"


        self.logger.warning(f'{self.name}.ok: ')
        self.destroy()

    #--------------------------------------------------------------------------
    def cancel(self):
        "Cancel changes and restore original settings"

        self.logger.info(f'{self.name}.cancel: ')
        self.destroy()

    #--------------------------------------------------------------------------

#==============================================================================
#   Inicializacia kniznice
#------------------------------------------------------------------------------
print(f'SIQO InfoMatrixDisplayGui library ver {_VER}')

if __name__ == '__main__':

    from   siqo_ipoint            import InfoPoint
    from   siqo_imatrix           import InfoMatrix

    #--------------------------------------------------------------------------
    # Test of the InfoMatrixDisplayGui class
    #--------------------------------------------------------------------------
    win = tk.Tk()
    win.configure(bg='silver', highlightthickness=2, highlightcolor='green')
    win.title('Test of InfoMatrixDisplayGui class')
    #win.maxsize(width=900, height=800)
    win.minsize(width=400, height=300)
    win.config(highlightbackground = "green", highlightcolor= "green")

    #tk.Grid.columnconfigure(win, 1, weight=1)
    #tk.Grid.rowconfigure   (win, 2, weight=1)


    #--------------------------------------------------------------------------
    # Zaciatok testu
    #--------------------------------------------------------------------------
    im = InfoMatrix('Test matrix')
    im.setIpType('ipTest')
    im.logger.setLevel('DEBUG')
    im.logger.frameDepth = 2

    matGui = InfoMatrixDisplayGui(name='Display test', container=win, matrix=im)

    win.mainloop()
    matGui.logger.info('Stop of InfoMatrixDisplayGui test')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------