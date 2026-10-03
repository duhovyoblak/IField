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
    # Vyber iDataType
    #--------------------------------------------------------------------------
    idTypes = InfoData.iDataTypes()
    print(f"Available iDataTypes: {idTypes}")

    print()
    for idType in idTypes:
        print(f"  {idType}")
    print()

    idType = '_xxx_'
    while idType not in idTypes:

        if idType != '_xxx_': print(f"Invalid iDataType '{idType}', please select from available iDataTypes.")
        idType = input('Select iDataType or Enter to quit: ')

        if idType == '': exit()

    print()

    #--------------------------------------------------------------------------
    # Vytvorenie InfoData
    #--------------------------------------------------------------------------
    iData = InfoData.new(name='Test', iDataType=idType)
    logger.setLevel('WARNING')

    print()
    print(80*'-')

    #--------------------------------------------------------------------------
    # Test IMarkov
    #--------------------------------------------------------------------------
    if idType == 'IMarkov':

        #----------------------------------------------------------------------
        # Nastavenie dim a pozorovacích hodnôt
        #----------------------------------------------------------------------
        iData.setDim(dim=3)

        print()
        print(80*'-')
        input('Dim set, Press Enter to continue...')

        for i in range(10_000):

            val = rnd.randint(0, 3)
            iData.observe(val=val)

            if i % 10_000 == 0: print(f'Observed {i:>6} values...')

        print()
        print(iData)
        print(80*'-')

        iData._INFO_HISTOGRAM = False

        #----------------------------------------------------------------------
        # Manualne pozorovanie hodnôt
        #----------------------------------------------------------------------
        while True:
            val = input('Enter value to observe (or <Enter> to quit): ')

            if val.lower() == '': break

            try:
                val_int = int(val)
                iData.observe(val=val_int)
                print(iData)
                print()
            except ValueError:
                print('Invalid input. Please enter an integer or "exit".')

        input('Done, Press Enter to continue...')
        print(80*'=')
        print()

        #----------------------------------------------------------------------
        # Vypis max forces
        #----------------------------------------------------------------------
        forces = iData.maxForce(minForce=0.01, minObs=5, maxPatterns=50)
        print(f"Max force:")

        for pattern, rec in forces.items():
            patStr = ', '.join(str(x) for x in pattern)
            print(f"  Pattern: ({patStr:<16}), Force: {rec['frc']:.5f}, Observations: {rec['obs']:5}, Probability: {rec['pro']:.5f}")

    #--------------------------------------------------------------------------
    # Test I
    #--------------------------------------------------------------------------


#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
