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
# Class InfoPointGui
#------------------------------------------------------------------------------
class InfoPointGui(tk.Toplevel):

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name, container, ipType, **kwargs):
        "Call constructor of InfoPointGui and initialise it for respective data"

        self.logger = SiqoLogger(name)
        self.logger.audit(f'{name}.init:')

        self.name     = name               # Name of this chart
        self.ipType   = ipType             # InfoPoint type to work with
        self.axeChg   = False              # True if axes were changed
        self.valChg   = False              # True if values were changed

        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------
        self.origSchema = InfoPoint.getSchema(self.ipType)  # Original schema pre prikaz Cancel

        #----------------------------------------------------------------------
        # Initialise original tkInter.Tk
        #----------------------------------------------------------------------
        super().__init__(container)
        self.title(self.name)
        self.focus_set()

        #----------------------------------------------------------------------
        # Create tabs for axes and values
        #----------------------------------------------------------------------
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        # TabAxes
        self.tabAxe = ttk.Frame(notebook)
        notebook.add(self.tabAxe, text="Axes definition")
        self.showParams(self.tabAxe, 'axes', InfoPoint.getAxes(self.ipType), lblParam='Axe', lblName='Axe Name')

        # TabValues
        self.tabVal = ttk.Frame(notebook)
        notebook.add(self.tabVal, text="Values definition")
        self.showParams(self.tabVal, 'vals', InfoPoint.getVals(self.ipType), lblParam='Value', lblName='Value Name')

        #----------------------------------------------------------------------
        # Create bottom buttons bar
        #----------------------------------------------------------------------
        frmBtn = ttk.Frame(self)
        frmBtn.pack(fill=tk.X, expand=True, side=tk.BOTTOM, anchor=tk.S)

        btnOk = ttk.Button(frmBtn, text="OK", command=self.destroy)
        btnOk.pack(side=tk.RIGHT, padx=_PADX, pady=_PADY)

        btnCancel = ttk.Button(frmBtn, text="Cancel", command=self.cancel)
        btnCancel.pack(side=tk.RIGHT, padx=_PADX, pady=_PADY)

        #----------------------------------------------------------------------
        # Initialisation
        #----------------------------------------------------------------------
        self.logger.audit(f'{name}.init: Done')

    #--------------------------------------------------------------------------

    #==========================================================================
    # Show the chart
    #--------------------------------------------------------------------------
    def showParams(self, tab, paramType:str, params:dict, lblParam='Parameter', lblName='Name'):
        "Show parameters in the respective tab"

        self.logger.debug(f'{self.name}.showParams:')

        #----------------------------------------------------------------------
        # Clear the tab
        #----------------------------------------------------------------------
        for widget in tab.winfo_children():
            widget.destroy()

        #----------------------------------------------------------------------
        # Show header
        #----------------------------------------------------------------------
        lbl = ttk.Label(tab, text=lblParam)
        lbl.grid(column=0, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        lbl = ttk.Label(tab, text=lblName)
        lbl.grid(column=1, row=0, sticky=tk.W, padx=_PADX, pady=_PADY)

        #----------------------------------------------------------------------
        # Show parameters
        #----------------------------------------------------------------------
        row = 1
        for key, val in params.items():

            self.logger.debug(f'{self.name}.showParams: {key} : {val}')

            lbl = ttk.Label(tab, text=str(key))
            lbl.grid(column=0, row=row, sticky=tk.W, padx=_PADX, pady=_PADY)

            ent = ttk.Entry(tab)
            ent.insert(0, str(val))
            ent.bind("<FocusOut>", lambda event, key=key, entry=ent: self.setParam(paramType, key, entry.get()))
            ent.grid(column=1, row=row, sticky=tk.W, padx=_PADX, pady=_PADY)

            btnDelete = ttk.Button(tab, text="Delete", command=lambda key=key: self.delParam(paramType, key))
            btnDelete.grid(column=2, row=row, sticky=tk.W, padx=_PADX, pady=_PADY)

            row += 1

        #----------------------------------------------------------------------
        # Add button for new parameter
        #----------------------------------------------------------------------
        separator = ttk.Separator(tab, orient='horizontal')
        separator.grid(column=0, row=row, columnspan=3, sticky=tk.EW, padx=_PADX, pady=_PADY)
        row += 1

        entPar = ttk.Entry(tab)
        entPar.insert(0, 'NewParam')
        entPar.grid(column=0, row=row, sticky=tk.W, padx=_PADX, pady=_PADY)

        entNam = ttk.Entry(tab)
        entNam.insert(0, 'New Param Name')
        entNam.grid(column=1, row=row, sticky=tk.W, padx=_PADX, pady=_PADY)

        btnAdd = ttk.Button(tab, text="Add new", command=lambda: self.setParam(paramType, entPar.get(), entNam.get()))
        btnAdd.grid(column=2, row=row, sticky=tk.W, padx=_PADX, pady=_PADY)

    #--------------------------------------------------------------------------
    def setParam(self, paramType:str, key:str, val:str):
        "Update or Add new parameter to the InfoPoint"

        self.logger.debug(f'{self.name}.setParam: {paramType} : {key} : {val}')

        #----------------------------------------------------------------------
        # Add Axe
        #----------------------------------------------------------------------
        if paramType == 'axes':

            self.axeChg = InfoPoint.setAxe(self.ipType, key, val) or self.axeChg
            self.showParams(self.tabAxe, 'axes', InfoPoint.getAxes(self.ipType), lblParam='Axe', lblName='Axe Name')

        #----------------------------------------------------------------------
        # Add Value
        #----------------------------------------------------------------------
        elif paramType == 'vals':

            self.valChg = InfoPoint.setVal(self.ipType, key, val) or self.valChg
            self.showParams(self.tabVal, 'vals', InfoPoint.getVals(self.ipType), lblParam='Value', lblName='Value Name')

        #----------------------------------------------------------------------
        # Unknown parameter type
        #----------------------------------------------------------------------
        else:
            self.logger.error(f'{self.name}.setParam: Unknown paramType {paramType}')
            return

        self.logger.info(f'{self.name}.setParam: {paramType} {key} : {val} was set')

    #--------------------------------------------------------------------------
    def delParam(self, paramType:str, key:str):
        "Delete parameter from the InfoPoint"

        self.logger.debug(f'{self.name}.delParam: {paramType} : {key}')

        #----------------------------------------------------------------------
        # Add Axe
        #----------------------------------------------------------------------
        if paramType == 'axes':
            InfoPoint.delAxe(self.ipType, key)
            self.axeChg = True
            self.showParams(self.tabAxe, 'axes', InfoPoint.getAxes(self.ipType), lblParam='Axe', lblName='Axe Name')

        #----------------------------------------------------------------------
        # Add Value
        #----------------------------------------------------------------------
        elif paramType == 'vals':
            InfoPoint.delVal(self.ipType, key)
            self.valChg = True
            self.showParams(self.tabVal, 'vals', InfoPoint.getVals(self.ipType), lblParam='Value', lblName='Value Name')

        #----------------------------------------------------------------------
        # Unknown parameter type
        #----------------------------------------------------------------------
        else:
            self.logger.error(f'{self.name}.delParam: Unknown paramType {paramType}')
            return

        self.logger.info(f'{self.name}.delParam: {paramType} {key} deleted')

    #--------------------------------------------------------------------------
    def cancel(self):
        "Cancel changes and restore original schema"

        self.logger.debug(f'{self.name}.cancel:')

        if self.axeChg or self.valChg:

            InfoPoint.setSchema(self.ipType, self.origSchema)
            self.logger.info(f'{self.name}.cancel: Changes were cancelled')

        else:
            self.logger.info(f'{self.name}.cancel: No changes to cancel')

        self.destroy()

    #--------------------------------------------------------------------------

#==============================================================================
#   Inicializacia kniznice
#------------------------------------------------------------------------------
print(f'SIQO InfoPointGui library ver {_VER}')

if __name__ == '__main__':

    from   siqo_ipoint           import InfoPoint

    #--------------------------------------------------------------------------
    # Test of the InfoPointGui class
    #--------------------------------------------------------------------------
    win = tk.Tk()
    win.configure(bg='silver', highlightthickness=2, highlightcolor='green')
    win.title('Test of InfoPointGui class')
    #win.maxsize(width=900, height=800)
    win.minsize(width=400, height=300)
    win.config(highlightbackground = "green", highlightcolor= "green")

    #tk.Grid.columnconfigure(win, 1, weight=1)
    #tk.Grid.rowconfigure   (win, 2, weight=1)

    #--------------------------------------------------------------------------
    # Zaciatok testu
    #--------------------------------------------------------------------------
    ipn = InfoPoint(ipType='ipComplex')
    ipn.logger.setLevel('DEBUG')
    ipn.logger.frameDepth = 2

    ipnGui = InfoPointGui(name='Schema test', container=win, ipType='ipComplex')

    win.mainloop()
    ipnGui.logger.info('Stop of InfoPointGui test')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------