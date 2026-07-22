#==============================================================================
#  IData: test file
#------------------------------------------------------------------------------
from   siqolib.logger           import SiqoLogger
from   idata.idata              import InfoData

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

    logger = SiqoLogger(name='ISeries', level='INFO')
    logger.frameDepth = 2
    print(f'logger.frameDepth = {logger.frameDepth}')

    #--------------------------------------------------------------------------
    # Vytvorenie, generovanie osi
    #--------------------------------------------------------------------------
    im = InfoData('Test data')
    logger.setLevel('DEBUG')

    im.setIpType('ipTest')
    im.setSchemaAxe('x', 'Os X')

    im.init(cnts=(0,))
    print()
    print(im.info(full=True)['msg'])
    print(80*'-')
    input('Press Enter to continue...')

    im.initAdd(axeVal=2.5)
    print()
    print(im.info(full=True)['msg'])
    print(80*'-')
    input('Press Enter to continue...')

    im.initAdd(axeVal=3)
    print()
    print(im.info(full=True)['msg'])
    print(80*'-')
    input('Press Enter to continue...')

    im.initAdd(axeVal=1)
    print()
    print(im.info(full=True)['msg'])
    print(80*'-')
    input('Press Enter to continue...')



#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
