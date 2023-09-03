#==============================================================================
#  IField: main file
#------------------------------------------------------------------------------
import sys
sys.path.append('..\siqo_lib')

from   siqo_journal    import SiqoJournal

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
    journal.I('Main loop')

    dat = ComplexField(journal, 'Test field')

#    dat.gener(count=200, offMin=0.1, offMax=20, dim=2, spread=_LIN)

    dat.gener(count=100, offMin=0.0, offMax=20, offType=_LIN)
    dat.extend(count=200, offMin=0.1, offMax=20, offType=_LIN)


#    dat = ComplexField.gener(journal, 'Test field', count=200, offMin=0.0, offMax=20, dim=1, spread=_LIN)
#    dat.extend(count=200, offMin=0.1, offMax=20, spread=_LIN)
#    print(dat)

#    dat.cut = [-1, -1, -1]
#    dat.rndBit(0.5)

    
    # Vytvorim GUI
    gui = IFieldGui(journal, name='IField GUI', dat=dat)
    
    journal.O('Main end')
    
#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
