# ==============================================================================
# Information field class GUI
# ------------------------------------------------------------------------------
import os
import sys
import time

# ------------------------------------------------------------------------------
import tkinter        as tk
from   tkinter        import ttk

from   inf_tkchart    import InfoChart
from   siqo_imodel    import InfoModel

#------------------------------------------------------------------------------
def resource_path(relative_path):
    """ Get absolute path to resource, works for .py and for exe """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

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
class IFieldGui(tk.Tk):

    # ==========================================================================
    # Static variables & methods
    # --------------------------------------------------------------------------

    # ==========================================================================
    # Constructor & utilities
    # --------------------------------------------------------------------------
    def __init__(self, journal, name):
        "Create and show GUI for Information field"

        self.journal = journal
        self.journal.I('IFieldGui constructor...')

        #----------------------------------------------------------------------
        # inicializacia tk.Tk
        #----------------------------------------------------------------------
        super().__init__()

        # ----------------------------------------------------------------------
        # Internal data
        # ----------------------------------------------------------------------
        self.name        = name                           # Name of the GUI
        self.model       = InfoModel(journal)             # Model object

        # ----------------------------------------------------------------------
        # State data
        # ----------------------------------------------------------------------
        self.tabSelected    = None                        # Identifikacia vybranej zalozky
        self.time           = 0                           # Global time, e.g., state of the structure in simulation
        self.str_time       = tk.StringVar()              # Time in right chart to show in left chart

        self.str_status_msg = tk.StringVar(value='')              # Message in status bar
        self.str_status_mod = tk.StringVar(value=self.model.name) # Active model

        #----------------------------------------------------------------------
        # Start GUI
        #----------------------------------------------------------------------
        self.journal.M(f"{self.name}.init: Start application")
        self.show()

        self.journal.O()

    #--------------------------------------------------------------------------
    def closeGui(self):
        "disconnect and close GUI"

        self.destroy()

    #--------------------------------------------------------------------------
    def show(self):

        self.journal.I(f"{self.name}.show:")

        #----------------------------------------------------------------------
        # Nastavenia root window
        #----------------------------------------------------------------------
        self.geometry('1435x780')
        self.minsize(1050,500)
        self.title('Information field')
        self.icon_path = resource_path('IField.ico')
        #self.iconbitmap(self.icon_path)
        self.protocol("WM_DELETE_WINDOW", self.closeGui)

        #----------------------------------------------------------------------
        # Nastavenia style
        #----------------------------------------------------------------------
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure('Treeview', background='grey98', foreground='black', rowheight=16, fieldbackground='grey',borderwidth=0 )
        self.style.configure('TNotebook', bordercolor='gray')

        self.style.map('TNotebook.Tab', background=[('selected', 'lightgray')])
        self.style.map('Treeview', background=[('selected','green')] )

        #----------------------------------------------------------------------
        # Status bar
        #----------------------------------------------------------------------
        self.statusBarShow()

        #----------------------------------------------------------------------
        # TABS as ttk.Notebook
        #----------------------------------------------------------------------
        self.tabSelected = 0

        self.tabs = ttk.Notebook(self, style='TNotebook')
        self.tabs.pack(expand=True, fill='both')
        self.tabs.enable_traversal()

        # Vytkreslenie jednotlivych tabs
        self.tabInfShow()
        self.tabSptShow()

        self.tabs.bind('<<NotebookTabChanged>>', self.tabChanged)
        self.tabs.select(self.tabSelected)

        # self binds
#        self.bind("<F1>"        , lambda x: self.menuHelp())
#        self.bind('<F5>'        , lambda x: self.refresh())
#        self.bind("<F12>"       , lambda x: self.menuAbout())
        self.bind('<Alt-Key-F4>', lambda x: self.closeGui())
        
        self.journal.O()

    #--------------------------------------------------------------------------
    def tabChanged(self, event):

        self.refresh()

    #--------------------------------------------------------------------------
    def refresh(self):

        #----------------------------------------------------------------------
        # get selected tab name
        #----------------------------------------------------------------------
        selected_tab_name = self.tabs.tab(self.tabs.select(), 'text')
        self.journal.I(f"{self.name}.refresh: tabSelected = {selected_tab_name}")

        #----------------------------------------------------------------------
        # Refreshnem aktivny tab v notebooku podla nazvu zalozky
        #----------------------------------------------------------------------
        if   selected_tab_name == 'Information'     : self.tabInfRefresh()
        elif selected_tab_name == 'SpaceTime'       : self.tabSptRefresh()

        #----------------------------------------------------------------------
        self.journal.O()

    #==========================================================================
    # Status bar
    #--------------------------------------------------------------------------
    def statusBarShow(self):

        self.journal.I(f"{self.name}.statusBarShow:")

        frame_status_bar = tk.Frame(self, relief=tk.RAISED, borderwidth=2, bg='silver')
        frame_status_bar.pack(side='bottom', anchor='s', fill='x')
        frame_status_bar.columnconfigure(0, weight=1)

        status_bar_msg = tk.Label(frame_status_bar, relief=tk.RAISED, bd=0,     textvariable=self.str_status_msg, bg='silver', anchor= 'w')
        status_bar_msg.grid(row = 0, column = 0, sticky = 'we' )

        status_bar_mod = tk.Label(frame_status_bar, relief=tk.RAISED, width=20, textvariable=self.str_status_mod, cursor="hand2", font = "Verdana 10 bold", bg='silver', anchor= 'e')
        status_bar_mod.grid(row = 0, column = 1, sticky = 'e' )
        status_bar_mod.bind("<Button-1>", lambda x: self.changeModel())

        self.journal.O()

    #--------------------------------------------------------------------------
    def setStatus(self, msg):

        self.journal.M(f"{self.name}.setStatus: {msg}")
        self.str_status_msg.set(msg)

    #--------------------------------------------------------------------------
    def changeModel(self):

        self.journal.I(f"{self.name}.changeModel:")

        #----------------------------------------------------------------------
        # Odpojenie od aktualneho modelu
        #----------------------------------------------------------------------



        #----------------------------------------------------------------------
        # Nastavenie noveho modelu
        #----------------------------------------------------------------------

        # Refresh
        self.setStatus(f'Model changed to {self.model.name}')
        self.refresh()

        #----------------------------------------------------------------------
        self.journal.O()
        return

    #==========================================================================
    # Tab Information
    #--------------------------------------------------------------------------
    def tabInfShow(self):

        self.journal.I(f"{self.name}.tabInfShow:")

        #----------------------------------------------------------------------
        # Vytvorim frame a skonfigurujem grid
        #----------------------------------------------------------------------
        frm = ttk.Frame(self.tabs)
        frm.columnconfigure(0, weight=40)

        frm.columnconfigure(1, weight=1)
        frm.columnconfigure(2, weight=5)

        frm.rowconfigure   (0, weight=1)
        frm.rowconfigure   (1, weight=1)
        frm.rowconfigure   (2, weight=1)
        frm.rowconfigure   (3, weight=1)
        frm.rowconfigure   (4, weight=1)
        frm.rowconfigure   (5, weight=1)
        frm.rowconfigure   (6, weight=1)
        frm.rowconfigure   (7, weight=1)
        frm.rowconfigure   (8, weight=1)

        # Vlozim frame do Tabs
        self.tabs.add(frm,    text='Information'   )

        #----------------------------------------------------------------------
        # Lavy stlpec - Information evolution
        #----------------------------------------------------------------------
#        self.stv_srvs = SiqoTreeView(journal=self.journal, name='Services', frame=frm, cursor='hand2')
#        self.stv_srvs.bind('<<SiqoTreeView-DoubleLeftClick>>', self.tabSrvLogRefresh )
#        self.stv_srvs.grid(row=0, column=0, rowspan=4, sticky='nswe')

#        self.stv_srvLog = SiqoTreeView(journal=self.journal, name='Service Log (Double-click on Service header above)', frame=frm, cursor='hand2')
#        self.stv_srvLog.grid(row=4, column=0, rowspan=5, sticky='nswe')

        #----------------------------------------------------------------------
        # Pravy stlpec
        #----------------------------------------------------------------------
        lbl_srv = ttk.Label(frm, relief=tk.FLAT, text='I will work with service:' )
        lbl_srv.grid(row=0, column=2, sticky='ws', padx=_PADX, pady=_PADY)


        sep = ttk.Separator(frm, orient='horizontal')
        sep.grid(row=2, column=2, columnspan=2, sticky='we')


        self.journal.O()

    #--------------------------------------------------------------------------
    def tabInfRefresh(self, event=None):

        self.journal.I(f"{self.name}.tabInfRefresh:")



        self.journal.O()

    #==========================================================================
    # Tab SpaceTime
    #--------------------------------------------------------------------------
    def tabSptShow(self):

        self.journal.I(f"{self.name}.tabSptShow:")

        #----------------------------------------------------------------------
        # Vytvorim frame a skonfigurujem grid
        #----------------------------------------------------------------------
        frm = ttk.Frame(self.tabs)
        frm.columnconfigure(0, weight=40)

        frm.columnconfigure(1, weight=1)
        frm.columnconfigure(2, weight=5)

        frm.rowconfigure   (0, weight=1)
        frm.rowconfigure   (1, weight=1)
        frm.rowconfigure   (2, weight=1)
        frm.rowconfigure   (3, weight=1)
        frm.rowconfigure   (4, weight=1)
        frm.rowconfigure   (5, weight=1)
        frm.rowconfigure   (6, weight=1)
        frm.rowconfigure   (7, weight=1)
        frm.rowconfigure   (8, weight=1)

        # Vlozim frame do Tabs
        self.tabs.add(frm,    text='SpaceTime'   )

        #----------------------------------------------------------------------
        # Lavy stlpec - Information evolution
        #----------------------------------------------------------------------
#        self.stv_srvs = SiqoTreeView(journal=self.journal, name='Services', frame=frm, cursor='hand2')
#        self.stv_srvs.bind('<<SiqoTreeView-DoubleLeftClick>>', self.tabSrvLogRefresh )
#        self.stv_srvs.grid(row=0, column=0, rowspan=4, sticky='nswe')

#        self.stv_srvLog = SiqoTreeView(journal=self.journal, name='Service Log (Double-click on Service header above)', frame=frm, cursor='hand2')
#        self.stv_srvLog.grid(row=4, column=0, rowspan=5, sticky='nswe')

        #----------------------------------------------------------------------
        # Pravy stlpec
        #----------------------------------------------------------------------



        self.journal.O()

    #--------------------------------------------------------------------------
    def tabSptRefresh(self):

        self.journal.I(f"{self.name}.tabSptRefresh:")


        self.journal.O()
        return True

    #--------------------------------------------------------------------------
    #==========================================================================

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
    # --------------------------------------------------------------------------


# ------------------------------------------------------------------------------
print('Information field class GUI ver 1.00')

# ==============================================================================
#                              END OF FILE
# ------------------------------------------------------------------------------
