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
    im = InfoData.new(name='Markov', iDataType='IMarkov')
    logger.setLevel('DEBUG')
    print()
    print(im.info(full=True)['msg'])
    print(80*'-')
    input('Press Enter to continue...')
    print()

    im.setDim(dim=3)
    print()
    print(im.info(full=True)['msg'])
    print(80*'-')
    input('Press Enter to continue...')
    print()

    im.observe(val=3)
    print()
    print(im.info(full=True)['msg'])
    print(80*'-')
    input('Press Enter to continue...')
    print()

    im.observe(val=-1)
    print()
    print(im.info(full=True)['msg'])
    print(80*'-')
    input('Press Enter to continue...')
    print()

    im.observe(val=10)
    print()
    print(im.info(full=True)['msg'])
    print(80*'-')
    input('Press Enter to continue...')
    print()

    im.observe(val=3)
    print()
    print(im.info(full=True)['msg'])
    print(80*'-')
    input('Press Enter to continue...')
    print()


#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
