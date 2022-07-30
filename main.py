#==============================================================================
#  IField: main file
#------------------------------------------------------------------------------
import sys
sys.path.append('lib')

import settings
from   siqo_journal    import SiqoJournal
from   inf_object      import IObject

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
    IObject.journal = journal

    journal.I('Main loop')
    
    obj = IObject('Ahoj marmeláda. Toto bude asi omyl.')
    
    obj.encode()
    print(obj)

    journal.O('Main end')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
