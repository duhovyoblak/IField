# ==============================================================================
# Information field class GUI
# ------------------------------------------------------------------------------
#
# ------------------------------------------------------------------------------
from   inf_tkchart  import InfoChart
from   tkinter      import ttk
import tkinter      as tk

# ==============================================================================
# package's constants
# ------------------------------------------------------------------------------
_WIN = '1400x800'
_MAX_ROWS = 250
_MAX_COLS = 500

_PADX = 5
_PADY = 5

_SC_RED = 1.4

_BTN_AXE_W = 0.81
_BTN_AXE_H = 0.03

_BTN_VAL_W = 0.81
_BTN_VAL_H = 0.10

_BTN_DIS_W = 0.1
_BTN_DIS_H = 0.025

# ==============================================================================
# class IFieldGui
# ------------------------------------------------------------------------------
class IFieldGui():

    # ==========================================================================
    # Static variables & methods
    # --------------------------------------------------------------------------
    journal = None   # Pointer to global journal

    # ==========================================================================
    # Constructor & utilities
    # --------------------------------------------------------------------------
    def __init__(self, journal, name, dat):
        "Create and show GUI for Information field"

        self.journal = journal
        self.journal.I('IFieldGui constructor...')

        # ----------------------------------------------------------------------
        # Internal data
        # ----------------------------------------------------------------------
        self.name = name
        self.dat  = dat
        self.time = 0      # Global time, e.g., state of the structure in simulation

        # ----------------------------------------------------------------------
        # Initialise main window
        # ----------------------------------------------------------------------
        self.win = tk.Tk()

        self.win.title(self.name)
        self.win.geometry(_WIN)
        self.win.resizable(True, True)

        self.style = ttk.Style(self.win)
        self.style.theme_use('classic')

        self.str_time = tk.StringVar()   # Time in right chart to show in left chart

        # ----------------------------------------------------------------------
        # Staus bar
        # ----------------------------------------------------------------------

        # ----------------------------------------------------------------------
        # Right over bar
        # ----------------------------------------------------------------------
        frmOver = ttk.Frame(self.win, borderwidth=5,
                            relief='groove')  # , width=100
        frmOver.pack(fill=tk.Y, expand=True, side=tk.RIGHT, anchor=tk.E)

        btn_forw = ttk.Button(frmOver, text='Forward', command=self.forward)
        btn_forw.pack(padx=_PADX, pady=_PADX, fill=tk.X)

        btn_backw = ttk.Button(frmOver, text='Backward', command=self.backward)
        btn_backw.pack(padx=_PADX, pady=_PADX, fill=tk.X)

        self.cbTorus = ttk.Checkbutton(
            frmOver, text='Torus topology', command=self.show)
        self.cbTorus.pack(padx=_PADX, pady=_PADX, fill=tk.X)

        btn_evolve = ttk.Button(frmOver, text='Evolve', command=self.evolve)
        btn_evolve.pack(padx=_PADX, pady=_PADX, fill=tk.X)

        #----------------------------------------------------------------------
        lbl_time = ttk.Label(frmOver, relief=tk.FLAT, text='I will edit Time:' )
        lbl_time.pack(padx=_PADX, pady=_PADX, fill=tk.X)

        self.str_time.set(self.time)
        str_time = ttk.Spinbox(frmOver, from_=0, to=99999, textvariable=self.str_time, width=3)
        str_time.pack(padx=_PADX, pady=_PADX, fill=tk.X)

        btn_showMe = ttk.Button(frmOver, text='Show me the Time', command=self.showMe)
        btn_showMe.pack(padx=_PADX, pady=_PADX, fill=tk.X)

        # ----------------------------------------------------------------------
        # Panned window with charts
        # ----------------------------------------------------------------------
        self.pnw = ttk.PanedWindow(self.win, orient=tk.HORIZONTAL)

        # ----------------------------------------------------------------------
        # Left Chart
        self.left = InfoChart(self.journal, 'Left IField visualisation',
                              container=self.win, dat=dat, axX='0', axY='1', val='re')
        self.left.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.pnw.add(self.left)

        # ----------------------------------------------------------------------
        # Right chart
        self.right = InfoChart(self.journal, 'Right IField visualisation',
                               container=self.win, dat=dat, axX='2', axY='1', val='re')
        self.right.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
        self.pnw.add(self.right)

        # ----------------------------------------------------------------------
        # place the panedwindow on the root window
        self.pnw.pack(fill=tk.BOTH, expand=True)

#        print(self.pnw.sashpos(0))
#        print( self.pnw.sash_coord(0) )
        #self.pnw.sash_place(index=0, x=100, y=100)

#        self.show()   # Initial drawing
        self.journal.O('IFieldGui created for Object {}'.format(self.name))

        self.win.mainloop()       # Start listening for events

    # --------------------------------------------------------------------------
    def forward(self):

        if 'selected' in self.cbTorus.state():
            torus = True
        else:
            torus = False

        self.dat.applyRays(dimLower=1, start=0, stop=0, forward=True, torus=torus)
        self.show()

    # --------------------------------------------------------------------------
    def backward(self):

        if 'selected' in self.cbTorus.state():
            torus = True
        else:
            torus = False

        self.dat.applyRays(dimLower=1, start=0, stop=0, forward=False, torus=torus)
        self.show()

    # --------------------------------------------------------------------------
    def evolve(self):

        self.dat.evolve(srcCut=['*'], inf=0, start=0, stop=400)
        self.show()

    # --------------------------------------------------------------------------
    def setData(self, dat):
        "Clears data and set new data"

        self.left. setData(dat)
        self.right.setData(dat)

    # --------------------------------------------------------------------------
    def showMe(self):
        "Copy time slice from the right pane to the left"

        if self.str_time.get() != '': self.time = int(self.str_time.get())
        
        self.dat.copySlice(dim=2, pos=self.time)
        self.left.show()
        
        self.setTime(self.time+1)

    # --------------------------------------------------------------------------
    def setTime(self, time):
        "Sets new value for global time"
        
        self.time = time
        self.str_time.set(self.time)

    #--------------------------------------------------------------------------
    def timeChanged(self, widget, blank, mode):
        
        if self.str_time.get() != '': tmpTime = int(self.str_time.get())
        else                        : tmpTime = 0
        
        # Ak nastala zmena periody
        if tmpTime != self.time:
            
            self.time = tmpTime
        
            # Ak je perioda vacsia ako maximalna perioda v historii planety
#            if self.period > self.planet.getMaxPeriod():
#                self.period = self.planet.getMaxPeriod()
#                self.str_period.set(self.period)
                
#            # Vykreslim zmenenu periodu
#            self.setStatus(f'Selected period is {self.period}')
#            self.mapShow()
        
    # ==========================================================================
    # GUI methods
    # --------------------------------------------------------------------------
    def show(self):
        "Show Information field "

        self.journal.I(f'IFieldGui{self.name}.show')

        self.left.show()
        self.right.show()

        self.journal.O(f'IFieldGui {self.name}.show done')

    # --------------------------------------------------------------------------


# ------------------------------------------------------------------------------
print('Information field class GUI ver 0.30')
# ==============================================================================
#                              END OF FILE
# ------------------------------------------------------------------------------
