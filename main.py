#==============================================================================
#  IField: main file
#------------------------------------------------------------------------------
import sys
sys.path.append('..\siqo_lib')

from   siqo_journal    import SiqoJournal

import inf_lib         as lib
from   inf_object      import IObject
from   inf_gui         import IFieldGui
from   siqo_cfield     import ComplexField, _LIN, _LOG

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_VALS_MAX  = 100000


#==============================================================================
# package's tools
#------------------------------------------------------------------------------

#==============================================================================
# Functions
#------------------------------------------------------------------------------
if __name__ =='__main__':
    
    journal = SiqoJournal('IField', debug=3)
    journal.I('Main loop')

    datL = ComplexField.gener(journal, 'Test field', count=4, offMin=0.1, offMax=10, dim=3, spread=_LOG)
    print(datL)

    datL.cut = [-1, -1, -1]
    datL.rndBit(0.5)


    datL.cut = [-1, 3, -1]
    for obj in datL: print(obj['cP'])


    d = datL.getData()
    print(d)
    
    # Vytvorim GUI
#    gui = IFieldGui(journal, name='IField GUI', dat=cF)
    
    
    journal.O('Main end')
#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
