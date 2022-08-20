#==============================================================================
#  IField: main file
#------------------------------------------------------------------------------
import sys
sys.path.append('lib')

import settings
import inf_lib         as lib

from   siqo_journal    import SiqoJournal
from   inf_object      import IObject
from   inf_gui         import IFieldGui

#==============================================================================
# package's constants
#------------------------------------------------------------------------------

#==============================================================================
# package's tools
#------------------------------------------------------------------------------

#==============================================================================
# Functions
#------------------------------------------------------------------------------
if __name__ =='__main__':
    
    journal = SiqoJournal('IField', debug=5)
    IObject.journal   = journal
    IFieldGui.journal = journal

    journal.I('Main loop')
    
    val = lib.valGen('AB', 10000)
    
    obj = IObject.getObj(val)
#    obj.analyse()
#    obj.infoAidMat()

    
    # Vytvorim GUI
    gui = IFieldGui(obj)
    
    journal.O('Main end')
#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
