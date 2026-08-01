#==============================================================================
#  IData: test file
#------------------------------------------------------------------------------
from   siqolib.logger           import SiqoLogger
import random                   as rnd
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
    logger.setLevel('INFO')


    print()
    print()
    print(80*'-')
#    input('IMarkov created, Press Enter to continue...')
    print()

    im.setDim(dim=3)
    print()
    print()
    print(80*'-')
#    input('Dim set, Press Enter to continue...')
    print()

    for i in range(1000):

        val = rnd.randint(0, 7)
        im.observe(val=val)

    print()
    print(im)
    print(80*'-')


#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
