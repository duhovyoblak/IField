#==============================================================================
#  IField: main file
#------------------------------------------------------------------------------
from   siqolib.journal          import SiqoJournal

from   inf_gui                  import IFieldGui
#from   siqo_ifield              import InfoField, _LIN, _LOG
from   siqo_imatrix             import InfoMatrix

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

    dat = InfoMatrix(journal, 'Test field')

#    dat.gener(count=200, offMin=0.1, offMax=20, dim=2, spread=_LIN)

#    print(dat)
#    dat = InfoField.gener(journal, 'Test field', count=200, offMin=0.0, offMax=20, dim=1, spread=_LIN)
#    dat.extend(count=200, offMin=0.1, offMax=20, spread=_LIN)
#    print(dat)

#    dat.cut = [-1, -1, -1]
#    dat.rndBit(0.5)

    
    # Vytvorim GUI
    journal.setDepth(3)
    gui = IFieldGui(journal, name='IField GUI', dat=dat)
    
    journal.O('Main end')
    
#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
