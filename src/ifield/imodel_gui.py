#==============================================================================
# InfoModel GUI
#------------------------------------------------------------------------------
import os
from   ast                      import literal_eval

import tkinter                  as tk
from   tkinter                  import (ttk, font, PanedWindow)
from   tkinter                  import (messagebox, filedialog, scrolledtext)

from   siqolib.logger           import SiqoLogger
from   .imodel                  import InfoModel

#==============================================================================
# Module's constants
#------------------------------------------------------------------------------
_VER            = '1.1.0'

_WIN            = '1300x740'
_DPI            = 100

_FIG_W          = 0.8    # Figure width
_FIG_H          = 1.0    # Figure height

_PADX           = 5
_PADY           = 5

#==============================================================================
# Module's variables
#------------------------------------------------------------------------------
logger = SiqoLogger(name='InfoModelGui')   # Logger for InfoModelGui

#==============================================================================
# Class InfoModelGui
#------------------------------------------------------------------------------
class InfoModelGui:

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, parent):
        "Call constructor of IFieldMatrixGui and initialise it for respective data"

        logger.info('InfoModelGui.init:')

        self.parent  = parent
        self.model   = InfoModel(logger)

        self.cwd     = os.getcwd()           # Lokalny folder pre pracu s datami



    #==========================================================================
    # Internal methods
    #--------------------------------------------------------------------------
    def formatJson(self, txt):

        logger.debug(f"{self.model.name}.formatJson:")

        try:
            txt = literal_eval(txt)

        except Exception as e:
            # SyntaxError: invalid syntax
            messagebox.showerror('Invalid input', 'Not a valid JSON',parent=self.parent)
            logger.info(f"{self.model.name}.formatJson: {e}")
            return False

        logger.debug(f"{self.model.name}.formatJson: done")
        return True

    #==========================================================================
    # GUI methods
    #--------------------------------------------------------------------------
    def load(self):

        logger.debug(f"{self.model.name}.load:")

        fileName = filedialog.askopenfilename(parent=self.parent, title='Select IMF file', initialdir=self.cwd,
                                              filetypes=(('IModel files', '*.imf'), ('All files', '*.*')) )

        if not fileName:
             logger.info('Load cancelled')

        else:
            self.cwd = os.path.normpath(os.path.split(fileName)[0])

            with open(fileName,'r',encoding='utf8',errors='ignore') as f:
                txt = f.read()

            if self.formatJson(txt):

                self.model = InfoModel(name='InfoModel', json=txt)


        return self.model

    #--------------------------------------------------------------------------
    def save(self):

        logger.debug(f"{self.model.name}.save:")

        fileName =  filedialog.asksaveasfilename(parent=self.parent, initialfile = fileName,
                                                 title='Select IMF file', initialdir=self.cwd, defaultextension=".imf",
                                                 filetypes=(('IMF files', '*.imf'), ('All files', '*.*')) )
        if fileName:

            self.cwd = os.path.normpath(os.path.split(fileName)[0])

            with open(fileName,'w',encoding='utf8') as f:
                f.write(self.model.toJson())

            logger.info(f"{self.model.name}.save: Saved into {fileName}")

        else:
            logger.info(f"{self.model.name}.save: Save cancelled")

#==============================================================================
# Inicializacia modulu
#------------------------------------------------------------------------------
print(f'InfoModelGui ver {_VER}')

if __name__ == '__main__':

    logger.info("Testing InfoModelGui class")

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------