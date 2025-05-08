#==============================================================================
# InfoModel GUI
#------------------------------------------------------------------------------
import os
from   ast                    import literal_eval

import tkinter                as tk
from   tkinter                import (ttk, font, PanedWindow)
from   tkinter                import (messagebox, filedialog, scrolledtext)


from   siqo_imodel    import InfoModel

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_WIN            = '1300x740'
_DPI            = 100

_FIG_W          = 0.8    # Figure width
_FIG_H          = 1.0    # Figure height

_PADX           = 5
_PADY           = 5

#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# Class InfoModelGui
#------------------------------------------------------------------------------
class InfoModelGui:
    
    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, journal, parent):
        "Call constructor of InfoChart and initialise it for respective data"

        journal.I('InfoModelGui.init:')

        self.journal = journal
        self.parent  = parent
        self.model   = InfoModel(journal)

        self.cwd     = os.getcwd()           # Lokalny folder pre pracu s datami

        self.journal.O()

    #==========================================================================
    # Internal methods
    #--------------------------------------------------------------------------
    def formatJson(self, txt):
            
        self.journal.I(f"{self.model.name}.formatJson:")

        try:
            txt = literal_eval(txt)

        except Exception as e:
            # SyntaxError: invalid syntax
            messagebox.showerror('Invalid input', 'Not a valid JSON',parent=self.parent)
            self.journal.M(f"{self.model.name}.formatJson: {e}", True)
            return False
        
        self.journal.O(f"{self.model.name}.formatJson: done")
        return True

    #==========================================================================
    # GUI methods
    #--------------------------------------------------------------------------
    def load(self):

        self.journal.I(f"{self.model.name}.load:")

        fileName = filedialog.askopenfilename(parent=self.parent, title='Select IMF file', initialdir=self.importDir, 
                                              filetypes=(('IModel files', '*.imf'), ('All files', '*.*')) )

        if not fileName:
             self.journal.M('Load cancelled')
           
        else:   
            self.cwd = os.path.normpath(os.path.split(fileName)[0])
            
            with open(fileName,'r',encoding='utf8',errors='ignore') as f:
                txt = f.read()

            if self.formatJson(txt):

                self.model = InfoModel(self.journal, name='InfoModel', json=txt)

        self.journal.O()
        return self.model
    
    #--------------------------------------------------------------------------
    def save(self):
            
        self.journal.I(f"{self.model.name}.save:")

        fileName =  filedialog.asksaveasfilename(parent=self.parent, initialfile = fileName, 
                                                 title='Select IMF file', initialdir=self.cwd, defaultextension=".imf", 
                                                 filetypes=(('IMF files', '*.imf'), ('All files', '*.*')) )
        if fileName:

            self.cwd = os.path.normpath(os.path.split(fileName)[0])

            with open(fileName,'w',encoding='utf8') as f:
                f.write(self.model.toJson())

            self.journal.M(f"{self.model.name}.save: Saved into {fileName}")

        else:
            self.journal.M(f"{self.model.name}.save: Save cancelled")

        self.journal.O()

#==============================================================================
#   Inicializacia kniznice
#------------------------------------------------------------------------------
print('SIQO InfoModelGui library ver 1.00')

if __name__ == '__main__':

    from   siqolib.journal          import SiqoJournal
    journal = SiqoJournal('IModelGui component test', debug=4)

    #--------------------------------------------------------------------------
    # Test of the InfoModelGui class
    #--------------------------------------------------------------------------
    journal.I('Test of InfoMatrix class')





    win = tk.Toplevel(bg='silver',highlightthickness=2,highlightcolor='green')
    win.title('Import Json metadata')

    win.maxsize(width=1200, height=800)
    win.minsize(width=600, height=300)
    win.config(highlightbackground = "green", highlightcolor= "green")
    #win.bind('<Escape>', close_popup)
    win.focus()
    win.grab_set()

    modelGui = InfoModelGui(journal, parent=win)

    btn_load = tk.Button(win, text = 'Load'        , width=10, command = modelGui.load)

    #grid
    tk.Grid.columnconfigure(win, 1, weight=1)
    tk.Grid.rowconfigure(win, 2, weight=1)

    btn_load.grid(row=1, column=0, sticky='nw', padx=5, pady=5)

    win.mainloop()

    journal.O()



#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------