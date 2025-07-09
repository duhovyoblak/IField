#==============================================================================
#  IField: main file
#------------------------------------------------------------------------------
from   siqolib.logger          import Siqologger

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
    
    logger = Siqologger('IField', debug=3)
    logger.I('Main loop')

#    dat = InfoMatrix(logger, 'Test field')

#    dat.gener(count=200, offMin=0.1, offMax=20, dim=2, spread=_LIN)

#    print(dat)
#    dat = InfoField.gener(logger, 'Test field', count=200, offMin=0.0, offMax=20, dim=1, spread=_LIN)
#    dat.extend(count=200, offMin=0.1, offMax=20, spread=_LIN)
#    print(dat)

#    dat.cut = [-1, -1, -1]
#    dat.rndBit(0.5)

    
    # Vytvorim GUI
    logger.setDepth(3)
    gui = IFieldGui(logger, name='IField GUI')
    gui.mainloop()
    
    logger.O('Main end')
    
#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
