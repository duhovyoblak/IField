#==============================================================================
# Info tkChart library
#------------------------------------------------------------------------------
from   copy                   import deepcopy

import tkinter                as tk
from   tkinter                import (ttk, font, PanedWindow)
from   tkinter.messagebox     import showinfo

from   siqolib.logger         import SiqoLogger
from   siqolib.message        import SiqoMessage, askInt, askReal

from   .                      import logger, iDataTypes
from   idata.ipoint           import InfoPoint
from   idata.idata            import InfoData

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
# Class InfoDataCreateGui
#------------------------------------------------------------------------------
class InfoDataCreateGui(tk.Toplevel):

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name, container, **kwargs):
        "Call constructor of InfoDataCreateGui and initialise it for respective data"

        self.name     = name           # Name of this GUI
        self.changed  = False          # Flag indicating if counts have been changed
        self.data     = None           # InfoData to be created

        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------

        #----------------------------------------------------------------------
        # Initialise original tkInter.Tk
        #----------------------------------------------------------------------
        super().__init__(container)
        self.title(f"Create data for {self.name}")
        self.minsize(width=_MIN_W, height=_MIN_H)
        self.focus_set()

        #----------------------------------------------------------------------
        # Create options frame
        #----------------------------------------------------------------------
        frmDisp = ttk.Frame(self)
        frmDisp.pack(fill=tk.BOTH, expand=True, side=tk.TOP, anchor=tk.N)

        #----------------------------------------------------------------------
        # Choosing name for new data
        #----------------------------------------------------------------------
        lblName = ttk.Label(frmDisp, text="Data Name:")
        lblName.grid(column=0, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.dataName = tk.StringVar()
        entName = ttk.Entry(frmDisp, textvariable=self.dataName)
        entName.grid(column=1, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        #----------------------------------------------------------------------
        # Choosing IDataType from available types in iDataTypes
        #----------------------------------------------------------------------
        lblType = ttk.Label(frmDisp, text="Data Type:")
        lblType.grid(column=0, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)

        self.selectedType = tk.StringVar()
        cmbType = ttk.Combobox(frmDisp, textvariable=self.selectedType, values=list(iDataTypes.keys()))
        cmbType.grid(column=1, row=1, sticky=tk.W, padx=_PADX, pady=_PADY)
        cmbType.current(0)

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
        "Create new InfoData of the type selected by user and close the dialog"

        #----------------------------------------------------------------------
        # Kontrola ci user zadal meno pre nove data
        #----------------------------------------------------------------------
        name = self.dataName.get().strip()
        if not name:
            showinfo(title="Invalid name", message="Zadajte platné meno dát.")
            return

        #----------------------------------------------------------------------
        # Ak nie je meno unikatne, upozornim ho a vratim ho do hlavneho dialogu
        #----------------------------------------------------------------------
        if InfoData.getData(name) is not None:
            showinfo(title="Invalid name", message="Meno dát už existuje.")
            return

        #----------------------------------------------------------------------
        # Vyhodnotenie vyberu iDataType od usera
        #----------------------------------------------------------------------
        iDataType = self.selectedType.get().strip()

        if iDataType not in iDataTypes:
            logger.warning(f"{self.name}.ok: Unknown iDataType {iDataType!r}")
            showinfo(title="Invalid data type", message="Vyberte platný typ dát.")
            return

        #----------------------------------------------------------------------
        # Vytvorenie novych dat
        #----------------------------------------------------------------------
        self.data = InfoData.new(name=name, iDataType=iDataType)

        if self.data is None:
            logger.error(f"{self.name}.ok: InfoData of type '{iDataType}' was not created")
            showinfo(title="Create data", message=f"Dáta typu {iDataType} sa nepodarilo vytvoriť.")
            return

        self.changed = True

        #----------------------------------------------------------------------
        # Upozornenie userovi, ze data boli vytvorene s nulovou dlzkou a treba ich nastavit
        # v dialogu Schema DataProperties
        #----------------------------------------------------------------------
        showinfo(title="Create data", message="Dáta boli vytvorené s nulovou dlžkou. Nastavte ich v dialogu Schema DataProperties.")

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.ok: Created InfoData '{self.data.name}' of type '{iDataType}'")
        self.destroy()

    #--------------------------------------------------------------------------
    def cancel(self):
        "Cancel creation of the data and close the dialog"

        self.data    = None
        self.changed = False
        logger.info(f'{self.name}.cancel: Creation of data was cancelled')
        self.destroy()

    #--------------------------------------------------------------------------

#==============================================================================
# Inicializacia modulu
#------------------------------------------------------------------------------
print(f'InfoDataCreateGui ver {_VER}')

if __name__ == '__main__':

    logger.info("Testing InfoDataCreateGui class")

    from   idata.ipoint           import InfoPoint

    #--------------------------------------------------------------------------
    # Test of the InfoDataCreateGui class
    #--------------------------------------------------------------------------
    win = tk.Tk()
    win.configure(bg='silver', highlightthickness=2, highlightcolor='green')
    win.title('Test of InfoDataCreateGui class')
    #win.maxsize(width=900, height=800)
    win.minsize(width=400, height=300)
    win.config(highlightbackground = "green", highlightcolor= "green")

    #tk.Grid.columnconfigure(win, 1, weight=1)
    #tk.Grid.rowconfigure   (win, 2, weight=1)


    #--------------------------------------------------------------------------
    # Zaciatok testu
    #--------------------------------------------------------------------------
    logger.setLevel('DEBUG')

    matGui = InfoDataCreateGui(name='Data create test', container=win)

    win.mainloop()
    logger.info('Stop of InfoDataCreateGui test')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------