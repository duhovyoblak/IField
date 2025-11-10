#==============================================================================
# Siqo class InfoFieldMatrix
#------------------------------------------------------------------------------
import functools
import math
import cmath
import numpy                  as np
import random                 as rnd

from   siqolib.logger         import SiqoLogger
from   siqo_imatrix           import InfoMatrix

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_VER    = '1.0'

#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# InfoFieldMatrix
#------------------------------------------------------------------------------
class InfoFieldMatrix(InfoMatrix):

    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name):
        "Calls constructor of InfoFieldMatrix"

        self.logger = SiqoLogger(name, level='DEBUG')
        self.logger.info(f"InfoFieldMatrix.constructor: {name}")

        #----------------------------------------------------------------------
        # Super constructor
        #----------------------------------------------------------------------
        super().__init__(name)

        #----------------------------------------------------------------------
        # Private datove polozky triedy
        #----------------------------------------------------------------------
        self.l2e     = 0                           # Pocet posunu epochy pre jeden krok na osi Lambda = 1 / rychlost informacie
        self.maxL    = 10                          # Maximalny pocet krokov na osi Lambda pri ziskani zoznamu stavov susednych bodov

        self.sType   = 'bool'                      # Typ stavu
        self.sTypes  = ('bool'                     # Typ stavu je boolovska hodnota, False/True
                       ,'int'                      # Typ stavu je cele cislo, hodnoty su spocitatelne
                       ,'complex'                  # Typ stavu je komplexne cislo, hodnoty su spocitatelne, posun na osi Lambda meni fazu
                       )                           # Podoporovane typy stavov

        self.sAgg    = 'max'                       # Spôsob agregácie stavov do jednej hodnoty
        self.sAggs   = ('nearest'                  # Prva nenulova/notFalse hodnota v zozname
                       ,'min'                      # Minimalna hodnota v zozname, pre bool funguje ako AND
                       ,'max'                      # Maximalna hodnota v zozname, pre bool funguje ako OR
                       ,'sum'                      # Sucet hodnot v zozname     , pre bool funguje ako OR
                       ,'cnt'                      # Najcastejsia hodnota v zozname
                       )                           # Podoporovane sposoby agregacie stavov

        self.rule    = 'and'                       # Pravidlo agregacie stavov susednych bodov
        self.rules   = ('and'                      # Ak su stavy oboch susedov rovnake, nastavi sa tato hodnota
                       ,'xand'                     # Ak su stavy oboch susedov rovnake, nastavi sa opacna hodnota
                       )                           # Podoporovane pravidla agregacie stavov susednych bodov

        #----------------------------------------------------------------------
        # Inicializacia
        #----------------------------------------------------------------------
        self.setIpType('ipTest')
        self.setSchema({'axes': {'l': 'Lambda', 'e': 'Epoch'}, 'vals': {'s': 'State'}})
        self.init(cnts={'l':30, 'e':10})

        self.applyMatrixMethod(methodKey='Real constant', valueKey='s', params={'const': 0.0})

        #----------------------------------------------------------------------
        self.logger.info(f"{self.name}.constructor: done")

    #--------------------------------------------------------------------------
    # Method's methods
    #--------------------------------------------------------------------------
    def mapMethods(self) -> dict:
        "Returns map of methods setting keyed value to function value for respective parameters"

        methods = super().mapMethods()

        methods['IField epoch step'] = {'matrixMethod': self.epochStep, 'pointMethod':None,
                                        'params':{'lMax':10, 'eMax':10, 'eL':0, 'sType':'bool', 'sAggreg':'max', 'rule':'and'}}

        '''
        Agregovanie stavov do jednej hodnoty stavu:
        sAggreg:
            'nearest'     - hodnota stavu najblizsieho bodu v zozname
            'max'         - maximalna hodnota stavu v zozname
            'min'         - minimalna hodnota stavu v zozname
            'sum'         - sucet hodnot stavov v zozname

        Agregovanie stavov susednych bodov do jednej hodnoty statusu:
        rule:
            'and'         - ak su oba stavy rovnake, nastavi sa tato hodnota

        '''

        return methods

    #==========================================================================
    # Matrix methods to apply in Dynamics methods
    #--------------------------------------------------------------------------
    def epochStep(self, valueKey:str, params:dict):
        """Compute next epoch state.
        """

        self.logger.debug(f"{self.name}.epochStep: for key '{valueKey}' with params {params}")

        #----------------------------------------------------------------------
        # Kontrola parametrov
        #----------------------------------------------------------------------
        lMax = params.get('lMax',   None)
        eMax = params.get('eMax',   None)
        eL   = params.get('eL',     None)
        sType= params.get('sType',  None)
        sAgr = params.get('sAgr',   None)
        rule = params.get('rule',   None)

        #----------------------------------------------------------------------
        # Posuniem celu maticu o jeden epoch krok
        #----------------------------------------------------------------------
        self.moveByAxe(axeKey='e', deltaIdx=1, startIdx=0)

        #----------------------------------------------------------------------
        # Ziskam mnozinu pozicii cielovych bodov danej osi s indexom axeIdx
        #----------------------------------------------------------------------
        poss = self._possByAxeIdx(axeKey='e', axeIdx=0)

        #----------------------------------------------------------------------
        # Prejdem body l in <1, cnt-2> v epoch=0 a nastavim im hodnoty podla pravidla a susednych bodov
        #----------------------------------------------------------------------
        for l in range( 1, self.axeCntByKey('l')-1 ):

            actIdxs  = {'l':l, 'e':0}
            actPoint = self.pointByIdxs(actIdxs)
            actState = actPoint.val(valueKey)

            #--------------------------------------------------------------
            # Ziskam zoznamy stavov susednych bodov zlava a sprava +- lMax
            #--------------------------------------------------------------
            leftStates  = []
            rightStates = []

            for dL in range(1, lMax+1):

                leftPoint  = self.pointByIdxs( {'l':l - dL, 'e':0} )
                rightPoint = self.pointByIdxs( {'l':l + dL, 'e':0} )

                if leftPoint  is not None: leftPoint. append( leftPoint .val(valueKey) )
                if rightPoint is not None: rightPoint.append( rightPoint.val(valueKey) )

            #--------------------------------------------------------------
            # Agregujem zoznamy stavov do jednej hodnoty stavu
            #--------------------------------------------------------------
            leftState = self.aggState(leftStates, sType, sAgr)
            rightState= self.aggState(rightStates,sType, sAgr)

            #--------------------------------------------------------------
            # Agregujem stavy susednych bodov podla pravidla
            #--------------------------------------------------------------
            newState = self.aggNeighbors(actState, leftState, rightState, rule)

            #--------------------------------------------------------------
            # Nastavim novu hodnotu stavu spracovavaneho bodu
            #--------------------------------------------------------------
            actPoint.set(vals={valueKey: newState})

        #----------------------------------------------------------------------
        self.logger.debug(f"{self.name}.epochStep: done")

    #--------------------------------------------------------------------------
    def aggNeighbors(self, actState, leftState, rightState, rule):
        "Aggregates states of neighors into single state according to given rule"

        self.logger.debug(f"{self.name}.aggNeighbors: actState={actState}, leftState={leftState}, rightState={rightState}, rule={rule}")
        aggState = actState

        if rule == 'and':

            if (leftState == rightState): aggState = leftState


        else: self.logger.warning(f"{self.name}.aggNeighbors: Unknown rule '{rule}', returning actState")

        #----------------------------------------------------------------------
        self.logger.debug(f"{self.name}.aggNeighbors: {aggState}<-({actState},{leftState},{rightState})")
        return aggState

    #--------------------------------------------------------------------------
    def aggState(self, states:list, sType:str, sAgr:str):
        "Aggregates list of states into single state according to given type and aggregation method"

        self.logger.debug(f"{self.name}.aggState: states={states}, sType={sType}, sAgr={sAgr}")
        aggState = None

        #----------------------------------------------------------------------
        # Ak je zoznam stavov prazdny, vratim None
        #----------------------------------------------------------------------
        if len(states) == 0:
            self.logger.warning(f"{self.name}.aggState: empty states list, returning None")
            return aggState

        #----------------------------------------------------------------------
        # Agregujem podla zadaneho pravidla
        #----------------------------------------------------------------------
        if   sAgr == 'nearest': aggState = states[0]
        elif sAgr == 'min'    : aggState = min(states)
        elif sAgr == 'max'    : aggState = max(states)
        elif sAgr == 'sum'    : aggState = sum(states)

        #----------------------------------------------------------------------
        # Korekcia podla typu stavu
        #----------------------------------------------------------------------
        if   sType == 'bool'  : aggState = bool(aggState)
        elif sType == 'int'   : aggState = int (aggState)

        #----------------------------------------------------------------------
        self.logger.debug(f"{self.name}.aggState: {aggState}<-{states}")
        return aggState

    #==========================================================================
    # Persistency methods
    #--------------------------------------------------------------------------

#------------------------------------------------------------------------------
print(f"InfoFieldMatrix ver {_VER}")

#==============================================================================
# Unit testy
#------------------------------------------------------------------------------
if __name__ == '__main__':

    #--------------------------------------------------------------------------
    # Test of the InfoFieldMatrix class
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # Vytvorenie, generovanie osi
    #--------------------------------------------------------------------------
    im = InfoFieldMatrix('Test matrix')
    print(im)
    input('Press Enter to continue...')

    im.init()
    input('Press Enter to continue...')

    im.setIpType('ipTest')
    im.init()
    input('Press Enter to continue...')


    im.setSchemaAxe('a', 'Os A')
    im.setSchemaAxe('a', 'Os A')
    print(im.info(full=True)['msg'])
    input('Press Enter to continue...')

    im.init()
    print(im.info(full=True)['msg'])
    input('Press Enter to continue...')

    im.setSchemaVal('m', 'Hodnota M')
    print(im.info(full=True)['msg'])


    #--------------------------------------------------------------------------
    # generovanie hodnot
    #--------------------------------------------------------------------------
    im.applyPointMethod('BRandom fuuniform', 'm', params={'all':True, 'min':0, 'max':5})
    im.applyPointMethod('Random uniform', 'm', params={'all':True, 'min':0, 'max':5})
    print(im.info(full=True)['msg'])
    input('Press Enter to continue...')

    #--------------------------------------------------------------------------
    # Submatrix
    #--------------------------------------------------------------------------



#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------