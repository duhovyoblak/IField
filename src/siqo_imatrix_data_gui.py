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
# Class InfoMatrixDataGui
#------------------------------------------------------------------------------
class InfoMatrixDataGui(tk.Toplevel):

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name, container, matrix, **kwargs):
        "Call constructor of InfoMatrixDataGui and initialise it for respective data"

        self.logger = SiqoLogger(name)
        self.logger.audit(f'{name}.init:')

        self.name     = name               # Name of this chart
        self.matrix   = matrix             # Matrix type to work with

        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------
        self.origCnts  = self.matrix._cnts.copy()   # Original _cnts  pre prikaz Cancel
        self.origRects = self.matrix._rects.copy()  # Original _rects pre prikaz Cancel
        self.origOrigs = self.matrix._origs.copy()  # Original _origs pre prikaz Cancel

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

        # TabCnts
        self.tabCnts = ttk.Frame(notebook)
        notebook.add(self.tabCnts, text="Points counts")
        self.showParams(self.tabCnts, 'cnts', matrix._cnts, lblParam='Axe', lblName='Points count')

        # TabRects
        self.tabRects = ttk.Frame(notebook)
        notebook.add(self.tabRects, text="Lengths of axes")
        self.showParams(self.tabRects, 'rects', matrix._rects, lblParam='Axe', lblName='Axe length')

        # TabOrigs
        self.tabOrigs = ttk.Frame(notebook)
        notebook.add(self.tabOrigs, text="Origins of axes")
        self.showParams(self.tabOrigs, 'origs', matrix._origs, lblParam='Axe', lblName='Axe origin')

        #----------------------------------------------------------------------
        # Create bottom buttons bar
        #----------------------------------------------------------------------
        frmBtn = ttk.Frame(self)
        frmBtn.pack(fill=tk.X, expand=True, side=tk.BOTTOM, anchor=tk.S)

        btnInit = ttk.Button(frmBtn, text="Initialise", command=self.apply)
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

            self.logger.debug(f'{self.name}.showParams: {paramType}: {key} = {val}')

            lbl = ttk.Label(tab, text=str(key))
            lbl.grid(column=0, row=row, sticky=tk.W, padx=_PADX, pady=_PADY)

            ent = ttk.Entry(tab)
            ent.insert(0, str(val))
            ent.bind("<FocusOut>", lambda event, key=key, entry=ent: self.setParam(paramType, key, entry.get()))
            ent.grid(column=1, row=row, sticky=tk.W, padx=_PADX, pady=_PADY)

            row += 1

    #--------------------------------------------------------------------------
    def setParam(self, paramType:str, key:str, val:str):
        "Update or Add new parameter to the matrix setting"

        self.logger.debug(f'{self.name}.setParam: {paramType} : {key} : {val}')

        #----------------------------------------------------------------------
        # Set cnts
        #----------------------------------------------------------------------
        if paramType == 'cnts':

            try:
                val = int(val)
                self.matrix.axeCntByKey(key) = val
                self.logger.info(f'{self.name}.setParam: {paramType}: {key}={val} was set')

            except ValueError:
                self.logger.error(f"{self.name}.setParam: '{val}' is not an integer, can not change counts of points")

            finally:
                self.showParams(self.tabCnts, 'cnts', self.matrix._cnts, lblParam='Axe', lblName='Points count')

        #----------------------------------------------------------------------
        # Set rects
        #----------------------------------------------------------------------
        elif paramType == 'rects':

            try:
                val = float(val)
                self.matrix._rects[key] = val
                self.logger.info(f'{self.name}.setParam: {paramType}: {key}={val} was set')

            except ValueError:
                self.logger.error(f"{self.name}.setParam: '{val}' is not a real value, can not change length of the axe")

            finally:
                self.showParams(self.tabRects, 'rects', self.matrix._rects, lblParam='Axe', lblName='Axe length')

        #----------------------------------------------------------------------
        # Set origs
        #----------------------------------------------------------------------
        elif paramType == 'origs':

            try:
                val = float(val)
                self.matrix._origs[key] = val
                self.logger.info(f'{self.name}.setParam: {paramType}: {key}={val} was set')

            except ValueError:
                self.logger.error(f"{self.name}.setParam: '{val}' is not a real value, can not change origin of the axe")

            finally:
                self.showParams(self.tabOrigs, 'origs', self.matrix._origs, lblParam='Axe', lblName='Axe origin')

        #----------------------------------------------------------------------
        # Unknown parameter type
        #----------------------------------------------------------------------
        else:
            self.logger.error(f'{self.name}.setParam: Unknown paramType {paramType}')

    #--------------------------------------------------------------------------
    def apply(self):
        "Apply inputs and initialise the matrix"

        self.matrix.init()

        self.logger.warning(f'{self.name}.apply: Changes were applied, matrix initialised')
        self.destroy()

    #--------------------------------------------------------------------------
    def cancel(self):
        "Cancel changes and restore original settings"

        self.matrix._cnts  = self.origCnts      # Original _cnts
        self.matrix._rects = self.origRects     # Original _rects
        self.matrix._origs = self.origOrigs     # Original _origs

        self.logger.info(f'{self.name}.cancel: Changes were cancelled, settings restored')
        self.destroy()

    #--------------------------------------------------------------------------

#==============================================================================
#   Inicializacia kniznice
#------------------------------------------------------------------------------
print(f'SIQO InfoMatrixDataGui library ver {_VER}')

if __name__ == '__main__':

    from   siqo_ipoint            import InfoPoint
    from   siqo_imatrix           import InfoMatrix

    #--------------------------------------------------------------------------
    # Test of the InfoMatrixDataGui class
    #--------------------------------------------------------------------------
    win = tk.Tk()
    win.configure(bg='silver', highlightthickness=2, highlightcolor='green')
    win.title('Test of InfoMatrixDataGui class')
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

    matGui = InfoMatrixDataGui(name='Schema test', container=win, matrix=im)

    win.mainloop()
    matGui.logger.info('Stop of InfoMatrixDataGui test')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------