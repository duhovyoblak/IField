#==============================================================================
# Info tkChart library
#------------------------------------------------------------------------------
from   copy                   import deepcopy

import tkinter                as tk
from   tkinter                import (ttk, font, PanedWindow)
from   tkinter.messagebox     import showinfo

from   siqolib.logger         import SiqoLogger
from   siqolib.message        import SiqoMessage, askInt, askReal, askStr, askOption

from   .                      import logger
from   idata.ipoint           import InfoPoint
from   idata.idata            import InfoData

#==============================================================================
# Module's constants
#------------------------------------------------------------------------------
_VER            = '1.2.1'
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
    def __init__(self, name, container, dataGui, **kwargs):
        "Call constructor of InfoDataCreateGui and initialise it for respective data"

        self.name     = name           # Name of this GUI
        self.changed  = False          # Flag indicating if counts have been changed
        self.data     = None           # InfoData to be created
        self.dataGui  = dataGui        # Data GUI that owns this create dialog

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

        self.idType = tk.StringVar()
        cmbType = ttk.Combobox(frmDisp, textvariable=self.idType, values=InfoData.iDataTypes(), state='readonly')
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
        # Vytvorenie novych dat a asociovanie data ku GUI
        #----------------------------------------------------------------------
        self.data = InfoData.new(name=name, iDataType=self.idType.get().strip())

        if self.data is None:
            logger.error(f"{self.name}.ok: InfoData of type '{self.idType.get().strip()}' was not created")
            showinfo(title="Create data", message=f"Dáta typu {self.idType.get().strip()} sa nepodarilo vytvoriť.")
            return

        #----------------------------------------------------------------------
        # GUI bez dat prevezme nove data, inak sa otvori nove okno pre nove data
        #----------------------------------------------------------------------
        if self.dataGui.data is None:
            self.dataGui.registerData(self.data)
            self.dataGui.refreshForData()
            targetGui = self.dataGui

        else:
            targetGui = self.dataGui.newGui(dataObj=self.data)

        self.changed = True

        #----------------------------------------------------------------------
        # Ziskanie class-specifickych parametrov pre nove data
        #----------------------------------------------------------------------
        crtParams = self.data.getCreateParams()

        #----------------------------------------------------------------------
        # ak params obsahuje kluc 'cnts', vyvolam dialog pre zadanie poctu bodov
        #----------------------------------------------------------------------
        if 'cnts' in crtParams:

            crtParams.remove('cnts')
            targetGui.onSchemaData()

        #----------------------------------------------------------------------
        # Postupne prechadzam cez vsetky parametre a nastavujem ich hodnoty
        #----------------------------------------------------------------------
        for key in crtParams:

            label = self.data.param[key]['label']
            value = self.data.param[key]['value']
            typ   = self.data.param[key]['type' ]

            if typ=='ComboBox': options = self.data.param[key]['options']

            #------------------------------------------------------------------
            # Zavolam dialog na zadanie hodnoty pre tento parameter
            #------------------------------------------------------------------
            if typ=='str':

                value = askStr(container=self, title="Parameter input", prompt=f"Zadajte hodnotu pre '{label}':", initialvalue=value)

                if value is not None: self.data.param[key]['value'] = value

            elif typ=='int':

                value = askInt(container=self, title="Parameter input", prompt=f"Zadajte hodnotu pre '{label}':", initialvalue=value)

                if value is not None: self.data.param[key]['value'] = value

            elif typ=='float':

                value = askReal(container=self, title="Parameter input", prompt=f"Zadajte hodnotu pre '{label}':", initialvalue=value)

                if value is not None: self.data.param[key]['value'] = value

            elif typ=='ComboBox':

                value = askOption(container=self, title="Parameter input", prompt=f"Zadajte hodnotu pre '{label}':", options=options, initialvalue=value)

                if value is not None: self.data.param[key]['value'] = value

            else:
                logger.warning(f"Unsupported parameter type '{typ}' for key '{key}'")

        #----------------------------------------------------------------------
        # Pouzite class-specifickych parametrov pre nove data
        #----------------------------------------------------------------------
        self.data.useCreateParams()

        #----------------------------------------------------------------------
        # Zobrazenie novych dat v GUI, bez ohladu na to ci sa volal dialog 'cnts'
        #----------------------------------------------------------------------
        targetGui.viewChanged(force=True)

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.ok: Created InfoData '{self.data.param['name']['value']}' of type '{self.data.param['idType']['value']}'")
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