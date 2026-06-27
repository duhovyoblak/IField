#==============================================================================
# Info tkChart library
#------------------------------------------------------------------------------
import tkinter                as tk
from   tkinter                import (ttk, font, PanedWindow)
from   tkinter.messagebox     import showinfo

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

#==============================================================================
# Module's variables
#------------------------------------------------------------------------------

#==============================================================================
# Class InfoDataDataGui
#------------------------------------------------------------------------------
class InfoDataDataGui(tk.Toplevel):

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name, container, data, **kwargs):
        "Call constructor of InfoDataDataGui and initialise it for respective data"

        logger.audit(f'{name}.init:')

        self.name     = name                      # Name of this GUI
        self.data     = data                      # Data type to work with

        #----------------------------------------------------------------------
        # Internal objects
        #----------------------------------------------------------------------
        self._cnts  = self.data._cnts.copy()      # _cnts  pre prikaz Apply
        self._rects = self.data._rects.copy()     # _rects pre prikaz Apply
        self._origs = self.data._origs.copy()     # _origs pre prikaz Apply

        self.origCnts  = self.data._cnts.copy()   # Original _cnts  pre prikaz Cancel
        self.origRects = self.data._rects.copy()  # Original _rects pre prikaz Cancel
        self.origOrigs = self.data._origs.copy()  # Original _origs pre prikaz Cancel

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
        self.showParams(self.tabCnts, 'cnts', self._cnts, lblParam='Axe', lblName='Points count')

        # TabRects
        self.tabRects = ttk.Frame(notebook)
        notebook.add(self.tabRects, text="Lengths of axes")
        self.showParams(self.tabRects, 'rects', self._rects, lblParam='Axe', lblName='Axe length')

        # TabOrigs
        self.tabOrigs = ttk.Frame(notebook)
        notebook.add(self.tabOrigs, text="Origins of axes")
        self.showParams(self.tabOrigs, 'origs', self._origs, lblParam='Axe', lblName='Axe origin')

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
        logger.audit(f'{name}.init: Done')

    #--------------------------------------------------------------------------

    #==========================================================================
    # Show the chart
    #--------------------------------------------------------------------------
    def showParams(self, tab, paramType:str, params:dict, lblParam='Parameter', lblName='Name'):
        "Show parameters in the respective tab"

        logger.debug(f'{self.name}.showParams:')

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

            logger.debug(f'{self.name}.showParams: {paramType}: {key} = {val}')

            lbl = ttk.Label(tab, text=str(key))
            lbl.grid(column=0, row=row, sticky=tk.W, padx=_PADX, pady=_PADY)

            ent = ttk.Entry(tab)
            ent.insert(0, str(val))
            ent.bind("<FocusOut>", lambda event, key=key, entry=ent: self.setParam(paramType, key, entry.get()))
            ent.grid(column=1, row=row, sticky=tk.W, padx=_PADX, pady=_PADY)

            row += 1

    #--------------------------------------------------------------------------
    def setParam(self, paramType:str, key:str, val:str):
        "Update or Add new parameter to the data setting"

        logger.debug(f'{self.name}.setParam: {paramType}[{key}] = {val}')

        #----------------------------------------------------------------------
        # Set cnts
        #----------------------------------------------------------------------
        if paramType == 'cnts':

            try:
                val = int(val)
                self._cnts[key] = val
                logger.info(f'{self.name}.setParam: {paramType}[{key}] = {val} was set')

            except ValueError:
                logger.error(f"{self.name}.setParam: '{val}' is not an integer, can not change counts of points")

            finally:
                self.showParams(self.tabCnts, 'cnts', self._cnts, lblParam='Axe', lblName='Points count')

        #----------------------------------------------------------------------
        # Set rects
        #----------------------------------------------------------------------
        elif paramType == 'rects':

            try:
                val = float(val)
                self._rects[key] = val
                logger.info(f'{self.name}.setParam: {paramType}[{key}] = {val} was set')

            except ValueError:
                logger.error(f"{self.name}.setParam: '{val}' is not a real value, can not change length of the axe")

            finally:
                self.showParams(self.tabRects, 'rects', self._rects, lblParam='Axe', lblName='Axe length')

        #----------------------------------------------------------------------
        # Set origs
        #----------------------------------------------------------------------
        elif paramType == 'origs':

            try:
                val = float(val)
                self._origs[key] = val
                logger.info(f'{self.name}.setParam: {paramType}[{key}] = {val} was set')

            except ValueError:
                logger.error(f"{self.name}.setParam: '{val}' is not a real value, can not change origin of the axe")

            finally:
                self.showParams(self.tabOrigs, 'origs', self._origs, lblParam='Axe', lblName='Axe origin')

        #----------------------------------------------------------------------
        # Unknown parameter type
        #----------------------------------------------------------------------
        else:
            logger.error(f'{self.name}.setParam: Unknown paramType {paramType}')

    #--------------------------------------------------------------------------
    def apply(self):
        "Apply inputs and initialise the data"

        self.data.init( cnts=self._cnts, rects=self._rects, origs=self._origs )

        logger.warning(f'{self.name}.apply: Changes were applied, data initialised')
        self.destroy()

    #--------------------------------------------------------------------------
    def cancel(self):
        "Cancel changes and restore original settings"

        self.data._cnts  = self.origCnts      # Original _cnts
        self.data._rects = self.origRects     # Original _rects
        self.data._origs = self.origOrigs     # Original _origs

        logger.info(f'{self.name}.cancel: Changes were cancelled, settings restored')
        self.destroy()

    #--------------------------------------------------------------------------

#==============================================================================
# Inicializacia modulu
#------------------------------------------------------------------------------
print(f'InfoDataDataGui ver {_VER}')

if __name__ == '__main__':


    logger.info("Testing InfoDataDataGui class")

    from   idata.ipoint           import InfoPoint
    from   idata.idata            import InfoData

    #--------------------------------------------------------------------------
    # Test of the InfoDataDataGui class
    #--------------------------------------------------------------------------
    win = tk.Tk()
    win.configure(bg='silver', highlightthickness=2, highlightcolor='green')
    win.title('Test of InfoDataDataGui class')
    #win.maxsize(width=900, height=800)
    win.minsize(width=400, height=300)
    win.config(highlightbackground = "green", highlightcolor= "green")

    #--------------------------------------------------------------------------
    # Zaciatok testu
    #--------------------------------------------------------------------------
    im = InfoData('Test data')
    logger.setLevel('DEBUG')
    logger.frameDepth = 2

    im.setIpType('ipTest')
    im.setSchema({'axes': {'l': 'Lambda', 'e': 'Epoch'}, 'vals': {'s': 'State'}})
    im.init(cnts={'l':30, 'e':10})

    matGui = InfoDataDataGui(name='Schema test', container=win, data=im)

    win.mainloop()
    logger.info('Stop of InfoDataDataGui test')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------