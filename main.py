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
    
    journal = SiqoJournal('IField', debug=4)
    

    cF = ComplexField.gener(journal, 'Test field', 3, 4, offMin=0.1, offMax=100, spread=_LOG)
    print(cF)

    journal.I('Main loop')
    
#    val = 'abrakadabra'
#    val = lib.valGen('ABCD', _VALS_MAX)
 #   val = lib.valFromText('text/Coleida cp1250.txt', '1250')
    
#    obj = IObject.getObj(val[:_VALS_MAX])
#    obj.analyse()
    
#    obj.info()['out']
#    obj.infoAidMat()
 
    
    # Vytvorim GUI
#    gui = IFieldGui(journal, name='IField GUI')
    
    journal.O('Main end')
#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
