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

    cF = ComplexField.gener(journal, 'Test field', 4, 2, offMin=0.1, offMax=10, spread=_LOG)
    print(cF)
    for obj in cF: print(obj['cP'])
    
    cF.extend(count=5, offMin=8, offMax=16, spread=_LIN)
    print(cF)
    for obj in cF: print(obj['cP'])

    cF.extend(count=6, offMin=88, offMax=168, spread=_LOG)
    print(cF)
    for obj in cF: print(obj['cP'])
     
    
    # Vytvorim GUI
#    gui = IFieldGui(journal, name='IField GUI')
    
    journal.O('Main end')
#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
