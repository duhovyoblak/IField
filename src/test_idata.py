#==============================================================================
#  IData: test file
#------------------------------------------------------------------------------
import math

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
    logger.setLevel('WARNING')


    print()
    print()
    print(80*'-')
#    input('IMarkov created, Press Enter to continue...')
    print()

    im.setDim(dim=6)
    print()
    print()
    print(80*'-')
    input('Dim set, Press Enter to continue...')
    print()

    for i in range(500_000):

        val = rnd.randint(0, 7)
        im.observe(val=val)

        if i % 10_000 == 0:
            print(f'Observed {i:>6} values...')

    print()
    print(im)
    print(80*'-')

    im._INFO_HISTOGRAM = False

    while True:
        val = input('Enter value to observe (or <Enter> to quit): ')

        if val.lower() == '': break

        try:
            val_int = int(val)
            prob, gain = im.observe(val=val_int)
            print(im)
            print()
            print(f"Observed value: {val_int}, Probability: {prob:.5f}, Gain: {gain:.5f}")

        except ValueError:
            print('Invalid input. Please enter an integer or "exit".')

    input('Done, Press Enter to continue...')
    print(80*'=')
    print()

    im._probActualise()
    print(im)
    input('Prob actualised, Press Enter to continue...')

    gains = im.maxGain(minGain=1.2, minObs=10, maxPatterns=50)
    print(f"Max gain:")

    for pattern, rec in gains.items():
        patStr = ', '.join(str(x) for x in pattern)
        print(f"  Pattern: ({patStr:<16}), Gain: {rec['gain']:.5f}, Observations: {rec['obs']:5}, Probability: {rec['pro']:.5f}, log2(gain): {math.log2(rec['gain']):+7.5f}")

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
