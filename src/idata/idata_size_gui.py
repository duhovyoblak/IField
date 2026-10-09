#==============================================================================
# Info tkChart library
#------------------------------------------------------------------------------
from   copy                   import deepcopy

import tkinter                as tk
from   tkinter                import (ttk, font, PanedWindow)
from   tkinter.messagebox     import showinfo

from   siqolib.logger         import SiqoLogger
from   siqolib.message        import SiqoMessage, askInt, askReal

from   .                      import logger
from   idata.ipoint           import InfoPoint

#==============================================================================
# Module's constants
#------------------------------------------------------------------------------
_VER            = '1.1.0'
_WIN            = '800x540'
_DPI            = 100

_COMBO_WIDTH    = 12
_PADX           =  5
_PADY           =  5
_MIN_W          = 320    # Minimal dialog width so the title is visible in the title bar
_MIN_H          = 120
_OFFSET_X       = 50     # Dialog offset from parent window's left edge
_OFFSET_Y       = 100    # Dialog offset from parent window's top edge, below the menu bar

#==============================================================================
# Module's variables
#------------------------------------------------------------------------------

#==============================================================================
# Class InfoDataSizeGui
#------------------------------------------------------------------------------
class InfoDataSizeGui(tk.Toplevel):

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name, container, data, **kwargs):
        "Call constructor of InfoDataSizeGui and initialise it for respective data"

        axes = data.getSchemaAxes()
        cnts = {key: data._cnts.get(key, 0) for key in axes}
        logger.audit(f'{name}.init: Axes = {axes}, Counts = {cnts}')

        self.name     = name           # Name of this GUI
        self.changed  = False          # Flag indicating if counts have been changed
        self.data     = data           # InfoData whose axis counts are being edited
        self.axes     = axes           # Axis keys mapped to display names
        self.cnts     = cnts.copy()    # Counts of the data for respective axes, to be edited

        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------
        self.origCnts = self.cnts.copy()  # Original counts of the points for respective axes
        self.countEntries = {}

        #----------------------------------------------------------------------
        # Initialise original tkInter.Tk
        #----------------------------------------------------------------------
        super().__init__(container)
        self.title(data.name)
        self.minsize(width=_MIN_W, height=_MIN_H)
        self.focus_set()

        #----------------------------------------------------------------------
        # Create Dispay options frame
        #----------------------------------------------------------------------
        frmDisp = ttk.Frame(self)
        frmDisp.pack(fill=tk.BOTH, expand=True, side=tk.TOP, anchor=tk.N)

        #----------------------------------------------------------------------
        # List of axe's names in rows
        #----------------------------------------------------------------------
        lblAxe = ttk.Label(frmDisp, text="Axe:")
        lblAxe.grid(column=0, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        row = 1
        for key, axeName in self.axes.items():
            lblAxe = ttk.Label(frmDisp, text=axeName)
            lblAxe.grid(column=0, row=row, sticky=tk.W, padx=_PADX, pady=_PADY)

            entCnt = ttk.Entry(frmDisp)
            entCnt.insert(0, str(self.cnts[key]))
            entCnt.grid(column=1, row=row, sticky=tk.W, padx=_PADX, pady=_PADY)
            self.countEntries[key] = entCnt
            row += 1


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
        # Position the dialog below the menu bar of the parent window
        #----------------------------------------------------------------------
        root = container.winfo_toplevel()
        root.update_idletasks()
        self.geometry(f'+{root.winfo_rootx() + _OFFSET_X}+{root.winfo_rooty() + _OFFSET_Y}')

        #----------------------------------------------------------------------
        # Initialisation
        #----------------------------------------------------------------------
        logger.audit(f'{name}.init: Done')

    #--------------------------------------------------------------------------

    #==========================================================================
    # Show the chart
    #--------------------------------------------------------------------------
    def ok(self):
        "Parse user inputs into counts of points and close the dialog"

        #----------------------------------------------------------------------
        # Vyhodnotenie vstupov od usera pre kazdu axe
        #----------------------------------------------------------------------
        newCnts = {}
        for key, entry in self.countEntries.items():
            value = entry.get().strip()
            if not value.isdecimal():
                logger.warning(f"{self.name}.ok: Invalid non-negative integer for axis '{key}': {value!r}")
                showinfo(title="Invalid point count", message="Zadajte pre každú os nezáporné celé číslo.")
                entry.focus_set()
                entry.selection_range(0, tk.END)
                return
            newCnts[key] = int(value)

        #----------------------------------------------------------------------
        # Ak sa zmenili pocty bodov pre niektoru osu, nastav flag changed
        #----------------------------------------------------------------------
        self.cnts = newCnts
        self.changed = self.cnts != self.origCnts


        #----------------------------------------------------------------------
        logger.info(f'{self.name}.ok: Counts={self.cnts}, changed={self.changed}')
        self.destroy()

    #--------------------------------------------------------------------------
    def cancel(self):
        "Cancel changes and restore original settings"

        self.cnts = self.origCnts.copy()
        logger.info(f'{self.name}.cancel: Counts of points restored to {self.cnts}')
        self.destroy()

    #--------------------------------------------------------------------------

#==============================================================================
# Inicializacia modulu
#------------------------------------------------------------------------------
print(f'InfoDataSizeGui ver {_VER}')

if __name__ == '__main__':

    logger.info("Testing InfoDataSizeGui class")

    from   idata.ipoint           import InfoPoint
    from   idata.idata            import InfoData

    #--------------------------------------------------------------------------
    # Test of the InfoDataSizeGui class
    #--------------------------------------------------------------------------
    win = tk.Tk()
    win.configure(bg='silver', highlightthickness=2, highlightcolor='green')
    win.title('Test of InfoDataSizeGui class')
    #win.maxsize(width=900, height=800)
    win.minsize(width=400, height=300)
    win.config(highlightbackground = "green", highlightcolor= "green")

    #tk.Grid.columnconfigure(win, 1, weight=1)
    #tk.Grid.rowconfigure   (win, 2, weight=1)


    #--------------------------------------------------------------------------
    # Zaciatok testu
    #--------------------------------------------------------------------------
    im = InfoData('Test data')
    im.setIpType('ipTest')
    im.init(cnts={key: 1 for key in im.getSchemaAxes()})
    im.logger.setLevel('DEBUG')
    im.logger.frameDepth = 2


    matGui = InfoDataSizeGui(name='Data size test', container=win, data=im)

    win.mainloop()
    matGui.logger.info('Stop of InfoDataSizeGui test')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------