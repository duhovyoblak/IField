#==============================================================================
# Siqo class InfoFieldMatrix
#------------------------------------------------------------------------------
from   siqo_imatrix           import InfoMatrix

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_VER    = '1.0'

_LAMBDA = 120       # Default points for Lambda axis
_EPOCH  =  60       # Default points for Epoch axis

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

        #----------------------------------------------------------------------
        # Super constructor
        #----------------------------------------------------------------------
        super().__init__(name)

        #----------------------------------------------------------------------
        # Private datove polozky triedy
        #----------------------------------------------------------------------
        self.l2e     = 1                           # Pocet posunu epochy pre jeden krok na osi Lambda = 1 / rychlost informacie
        self.maxL    = 10                          # Maximalny pocet krokov na osi Lambda pri ziskani zoznamu stavov susednych bodov

        self.sType   = 'bool'                      # Typ stavu
        self.sTypes  = ('bool'                     # Typ stavu je boolovska hodnota, False/True
                       ,'int'                      # Typ stavu je cele cislo, hodnoty su spocitatelne
                       ,'complex'                  # Typ stavu je komplexne cislo, hodnoty su spocitatelne, posun na osi Lambda meni fazu
                       )                           # Podoporovane typy stavov

        self.sAgg    = 'nearest'                   # Spôsob agregácie stavov do jednej hodnoty
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
        self.init(cnts={'l':_LAMBDA, 'e':_EPOCH})

        self.applyMatrixMethod(methodKey='Real constant', valueKey='s', params={'const': 0.0})

        #----------------------------------------------------------------------
        self.logger.info(f"{self.name}.constructor: done")

    #--------------------------------------------------------------------------
    # Method's methods
    #--------------------------------------------------------------------------
    def mapMethods(self) -> dict:
        "Returns map of methods setting keyed value to function value for respective parameters"

        methods = super().mapMethods()

        methods['IField random Bool'] = {'matrixMethod': self.rndBool,   'pointMethod':None, 'params':{'prob True':0.5}}
        methods['IField epoch step' ] = {'matrixMethod': self.epochStep, 'pointMethod':None, 'params':{}}

        return methods

    #==========================================================================
    # Matrix methods to apply in Dynamics methods
    #--------------------------------------------------------------------------
    def rndBool(self, valueKey:str, params:dict):
        """Clear all model and set state as random Boolean values.
        """

        self.logger.debug(f"{self.name}.rndBool: for key '{valueKey}' with params {params}")
        pts = 0

        #----------------------------------------------------------------------
        # Clear all model
        #----------------------------------------------------------------------
        self.clear(defs={valueKey: False})

        #----------------------------------------------------------------------
        # Set Active matrix to e = 0 and generate random Boolean values
        #----------------------------------------------------------------------
        self.actSubmatrix( {'e': 0} )

        pointParams = {'prob1':params.get('prob True', 0.5)}
        pts = self.applyMatrixMethod(methodKey='Random bit', valueKey=valueKey, params=pointParams)

        #----------------------------------------------------------------------
        # Reset Active matrix whole matrix
        #----------------------------------------------------------------------
        self.actSubmatrix()

        #----------------------------------------------------------------------
        self.logger.info(f"{self.name}.rndBool: {pts} InfoPoints was set to random Boolean values for key '{valueKey}'")

    #--------------------------------------------------------------------------
    def epochStep(self, valueKey:str, params:dict):
        """Compute next epoch state.
        """

        self.logger.debug(f"{self.name}.epochStep: for key '{valueKey}' with params {params}")
        pts = 0

        #----------------------------------------------------------------------
        # Kontrola parametrov
        #----------------------------------------------------------------------

        #----------------------------------------------------------------------
        # Posuniem celu maticu o jeden epoch krok
        #----------------------------------------------------------------------
        self.moveByAxe(axeKey='e', deltaIdx=1, startIdx=0)

        #----------------------------------------------------------------------
        # Prejdem body l in <1, cnt-2> v epoch=0 a nastavim im hodnoty podla pravidla a susednych bodov
        #----------------------------------------------------------------------
        for l in range( 0, self.axeCntByKey('l') ):

            actPoint = self.pointByIdxs([l, 0])
            actState = actPoint.val(valueKey)

            #--------------------------------------------------------------
            # Ziskam zoznamy stavov susednych bodov zlava a sprava +- lMax
            #--------------------------------------------------------------
            leftStates, rightStates = self.getNeighStates(valueKey, l)

            #--------------------------------------------------------------
            # Agregujem zoznamy stavov do jednej hodnoty stavu
            #--------------------------------------------------------------
            leftState = self.aggStates(leftStates )
            rightState= self.aggStates(rightStates)

            #--------------------------------------------------------------
            # Agregujem stavy susednych bodov podla pravidla
            #--------------------------------------------------------------
            newState = self.aggNeighbors(leftState, actState, rightState)

            #--------------------------------------------------------------
            # Nastavim novu hodnotu stavu spracovavaneho bodu
            #--------------------------------------------------------------
            actPoint.set(vals={valueKey: newState})
            pts += 1

        #----------------------------------------------------------------------
        self.logger.info(f"{self.name}.epochStep: {pts} InfoPoints was updated for key '{valueKey}' in epoch step")

    #==========================================================================
    # Internal tools
    #--------------------------------------------------------------------------
    def getNeighStates(self, valueKey:str, l:int, e:int=0):
        "Returns list of states of neighbor points along given axis at given position"

        self.logger.debug(f"{self.name}.getNeighStates: For {valueKey} at [{l}, {e}]")

        cntLambda = self.axeCntByKey('l')
        cntEpoch  = self.axeCntByKey('e')

        leftStates  = []
        rightStates = []

        #----------------------------------------------------------------------
        # Ziskam zoznamy stavov susednych bodov zlava a sprava +- lMax
        #----------------------------------------------------------------------
        for dL in range(1, self.maxL+1):

            #------------------------------------------------------------------
            # Ziskam hodnotu Epoch podla dL a l2e
            #------------------------------------------------------------------
            eH = e + (dL * self.l2e)
            if eH >= cntEpoch: break

            #------------------------------------------------------------------
            if (l-dL) > 0:
                leftPoint  = self.pointByIdxs( [l-dL, eH] )
                leftStates.append( leftPoint .val(valueKey) )

            if (l+dL) < cntLambda:
                rightPoint = self.pointByIdxs( [l+dL, eH] )
                rightStates.append( rightPoint.val(valueKey) )

        #----------------------------------------------------------------------
        self.logger.debug(f"{self.name}.getNeighStates: leftStates={leftStates}, rightStates={rightStates}")
        return leftStates, rightStates

    #--------------------------------------------------------------------------
    def aggNeighbors(self, leftState, actState, rightState):
        "Aggregates states of neighors into single state according to given rule"

        self.logger.debug(f"{self.name}.aggNeighbors: leftState={leftState}, actState={actState}, rightState={rightState}, rule={self.rule}")
        aggState = actState

        if self.rule == 'and':

            if (leftState == rightState): aggState = leftState


        else: self.logger.warning(f"{self.name}.aggNeighbors: Unknown rule '{self.rule}', returning actState")

        #----------------------------------------------------------------------
        self.logger.debug(f"{self.name}.aggNeighbors: {aggState}<-({leftState},{actState},{rightState})")
        return aggState

    #--------------------------------------------------------------------------
    def aggStates(self, states:list):
        "Aggregates list of states into single state according to given type and aggregation method"

        self.logger.debug(f"{self.name}.aggStates: states={states}, sType={self.sType}, sAgg={self.sAgg}")
        aggState = None

        #----------------------------------------------------------------------
        # Ak je zoznam stavov prazdny, vratim None
        #----------------------------------------------------------------------
        if len(states) == 0:
            self.logger.warning(f"{self.name}.aggStates: empty states list, returning None")
            return aggState

        #----------------------------------------------------------------------
        # Agregujem podla zadaneho pravidla
        #----------------------------------------------------------------------
        if   self.sAgg == 'nearest':

            for state in states:

                if state:
                    aggState = state
                    break

        elif self.sAgg == 'min'    : aggState = min(states)
        elif self.sAgg == 'max'    : aggState = max(states)
        elif self.sAgg == 'sum'    : aggState = sum(states)

        #----------------------------------------------------------------------
        # Korekcia podla typu stavu
        #----------------------------------------------------------------------
        if   self.sType == 'bool'  : aggState = bool(aggState)
        elif self.sType == 'int'   : aggState = int (aggState)

        #----------------------------------------------------------------------
        self.logger.debug(f"{self.name}.aggStates: {aggState}<-{states}")
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

    from   siqolib.logger         import SiqoLogger

    #--------------------------------------------------------------------------
    # Test of the InfoFieldMatrix class
    #--------------------------------------------------------------------------
    logger = SiqoLogger(name='InfoFieldMatrix test')
    logger.setLevel('DEBUG')

    #--------------------------------------------------------------------------
    # Vytvorenie, generovanie osi
    #--------------------------------------------------------------------------
    im = InfoFieldMatrix('Test matrix')
    print(im)
    input('Press Enter to continue...')

    print('Methods map:')
    for methodKey, rec in im.mapMethods().items():
        print(f"  {methodKey:<25s}: {rec['params']}")
    input('Press Enter to continue...')

    #--------------------------------------------------------------------------
    # generovanie hodnot
    #--------------------------------------------------------------------------
    #im.applyMatrixMethod(methodKey='BRandom fuuniform',   valueKey='s', params={'min':0, 'max':5})
    #im.applyMatrixMethod(methodKey='Random uniform',      valueKey='s', params={'min':0, 'max':5})
    #print(im.info(full=True)['msg'])
    #input('Press Enter to continue...')



    im.applyMatrixMethod(methodKey='IField random Bool',  valueKey='s', params={'min':0, 'max':5})
    print(im.info(full=True)['msg'])
    input('Press Enter to continue...')
    #--------------------------------------------------------------------------
    # Submatrix
    #--------------------------------------------------------------------------



#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------