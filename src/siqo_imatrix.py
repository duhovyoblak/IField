#==============================================================================
# Siqo class InfoMatrix
#------------------------------------------------------------------------------
import math
import cmath
import numpy                  as np
import random                 as rnd

from   siqolib.logger         import SiqoLogger
from   siqo_ipoint            import InfoPoint

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_VER    = '3.03'
_IND    = '|  '       # Info indentation
_UPP    = 10          # distance units per period

_F_POS  =  8          # Format for position

#==============================================================================
# package's variables
#------------------------------------------------------------------------------
logger = SiqoLogger('InfoMatrix test', level='INFO')

#==============================================================================
# InfoMatrix
#------------------------------------------------------------------------------
class InfoMatrix:

    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, name, ipType):
        "Calls constructor of InfoMatrix"

        logger.info(f"InfoMatrix.constructor: {name}")
        
        #----------------------------------------------------------------------
        # Public datove polozky triedy
        #----------------------------------------------------------------------
        self.name       = name     # Name of the InfoMatrix
        self.ipType     = ipType   # Type of the InfoPoint in this InfoMatrix
        self.staticEdge = False    # Static edge means value of the edge points is fixed in some methods
        self.points     = []       # List of InfoPoints

        self.actVal     = None     # Key of the current InfoPoint's dat value
        self.actSub     = {}       # Current active submatrix definition as dict of freezed axesKeys with values
        self.actList    = []       # Current active list of points in submatrix
        self.actChanged = True     # Current sub settings was changed and actSub needs refresh
        
        #----------------------------------------------------------------------
        # Private datove polozky triedy
        #----------------------------------------------------------------------
        self._cnts      = {}       # Number of InfoPoints in respective axes
        self._origs     = {}       # Origin's coordinates of the InfoMatrix for respective axes in lambda units
        self._rects     = {}       # Lenghts of the InfoMatrix for respective axes in lambda units
        self._diffs     = {}       # Distance between two points in respective axes in lambda units

        #----------------------------------------------------------------------
        # Inicializacia
        #----------------------------------------------------------------------
        logger.info(f"{self.name}.constructor: done")

    #--------------------------------------------------------------------------
    def __str__(self):
        "Prints info about this InfoMatrix"

        toRet = ''
        for line in self.info()['msg']: toRet += line +'\n'
        return toRet

    #--------------------------------------------------------------------------
    def __array__(self):
        "Returns InfoMatrix as 2D numpy array"
 
        mtrx = self.actSubmatrix(keyVal=self.actVal)

        #----------------------------------------------------------------------
        # Kontrola existencie vybranej 2D matice
        #----------------------------------------------------------------------
        if mtrx is None:
            logger.error(f"{self.name}.__array__: actMatrix is None")
            return None

        #----------------------------------------------------------------------
        # Vratim skonvertovane do np.array
        #----------------------------------------------------------------------
        return np.array(mtrx)

    #--------------------------------------------------------------------------
    def reset(self, ipType=None):
        "Resets all InfoMatrix's data and destroys all points. Count of points will be 0"
        
        logger.warning(f"{self.name}.reset: ipType={ipType}")
        
        if ipType is not None: self.ipType = ipType

        self.points     = []       # List of rows of lists of InfoPoints
        self.staticEdge = False    # Static edge means value of the edge nodes is fixed        

        self.actVal     = None     # Key of the InfoPoint's current dat value
        self.actSub     = {}       # Current active submatrix defined as dict of freezed axesKeys with values
        self.actList    = []       # Current active submatrix/subvector
        self.actChanged = True     # Current sub settings was changed and actSub needs refresh

        self._cnts      = {}       # Number of InfoPoints in respective axes
        self._origs     = {}       # Origin's coordinates of the InfoMatrix
        self._rects     = {}       # Lenghts of the InfoMatrix for respective axes in lambda units
        self._diffs     = {}       # Distance between two points in respective axes in lambda units

        logger.info(f"{self.name}.reset: done")

    #--------------------------------------------------------------------------
    def info(self, indent=0):
        "Creates info about this InfoMatrix"
        
        dat = {}
        msg = []

        #----------------------------------------------------------------------
        # info o celej strukture
        #----------------------------------------------------------------------
        if indent == 0:
            msg.append(f"{indent*_IND}{60*'='}")
            dat['name'          ] = self.name
            dat['ipType'        ] = self.ipType
            dat['schema'        ] = InfoPoint.getSchema(self.ipType)
            dat['cnt of points' ] = self.count()
            dat['len(points)'   ] = len(self.points)
            dat['staticEdge'    ] = self.staticEdge

            dat['actVal'        ] = self.actVal
            dat['actSub'        ] = self.actSub
            dat['cnt of actList'] = len(self.actList)
            dat['actChanged'    ] = self.actChanged

            dat['cnts'          ] = self._cnts
            dat['origs'         ] = self._origs
            dat['rects'         ] = self._rects
            dat['diffs'         ] = self._diffs
            dat['subProducts'   ] = self._subProducts()

        for key, val in dat.items(): msg.append(f"{indent*_IND}{key:<15}: {val}")

        #----------------------------------------------------------------------
        # info o vsetkych bodoch
        #----------------------------------------------------------------------
        for pos, point in enumerate(self.points):
            idxs = self._idxByPos(pos)
            msg.append(f"{pos:{_F_POS}} {idxs} {str(point)}")
        
        #----------------------------------------------------------------------
        return {'res':'OK', 'dat':dat, 'msg':msg}
        
    #--------------------------------------------------------------------------
    def count(self):
        "Returns Count of points in this InfoMatrix"
        
        if len(self._cnts) == 0: return 0

        toRet = 1
        for cnt in self._cnts.values():
            toRet *= cnt

        return toRet

    #--------------------------------------------------------------------------
    def copy(self, name):
        "Creates copy of this InfoMatrix"
        
        logger.debug(f"{self.name}.copy: to {name}")

        #----------------------------------------------------------------------
        # Create new InfoMatrix with the same dimensions
        #----------------------------------------------------------------------
        toRet = InfoMatrix(name, self.ipType)

        toRet.points     = []                  # List of InfoPoints
        toRet.ipType     = self.ipType         # Type of the InfoPoint in this InfoMatrix
        toRet.staticEdge = self.staticEdge     # Static edge means value of the edge nodes is fixed

        toRet.actVal     = self.actVal         # Key of the InfoPoint's dat value
        toRet.actSub     = self.actSub.copy()  # Current active submatrix defined as dict of freezed axesKeys with values
        toRet.actList    = []                  # Current active submatrix/subvector
        toRet.actChanged = True                # Current sub settings was changed and actSub needs refresh

        toRet._cnts      = self._cnts.copy()   # Number of InfoPoints in respective axes
        toRet._origs     = self._origs.copy()  # Origin's coordinates of the InfoMatrix 
        toRet._rects     = self._rects.copy()  # Lengths of the InfoMatrix's axes 
        toRet._diffs     = self._diffs.copy()  # Distance between two points in respective axes in lambda units

        #----------------------------------------------------------------------
        # Copy all points from this InfoMatrix to the new one
        #----------------------------------------------------------------------
        for point in self.points:
            toRet.points.append(self.copy())

        #----------------------------------------------------------------------
        return toRet
        
    #==========================================================================
    # Proxy tools for InfoPoint schema
    #--------------------------------------------------------------------------
    def clearSchema(self):
        "Clears schema of InfoPoint for respective ipType to {'axes':{'None':'None'}, 'vals':{}}"

        self.reset()

        return InfoPoint.clearSchema(self.ipType)
    
    #--------------------------------------------------------------------------
    def isInSchema(self, *, axes:list=None, vals:list=None):

        return InfoPoint.isInSchema(self.ipType, axes=axes, vals=vals)

    #--------------------------------------------------------------------------
    def setAxe(self, key, name):
        "Add axe key and name"

        if key not in self._cnts. keys(): self._cnts [key] = 0
        if key not in self._origs.keys(): self._origs[key] = 0
        if key not in self._rects.keys(): self._rects[key] = 0
        if key not in self._diffs.keys(): self._origs[key] = 0

        return InfoPoint.setAxe(self.ipType, key, name)
    
    #--------------------------------------------------------------------------
    def getAxeIdx(self, key):
        "Returns axe's idx for respective key as position in the list of axes othewise None"
        return InfoPoint.getAxeIdx(self.ipType, key)
    
    #--------------------------------------------------------------------------
    def getAxeKey(self, idx):
        "Returns axe's key for respective position in the list of axes othewise None"
        return InfoPoint.getAxeKey(self.ipType, idx)

    #--------------------------------------------------------------------------
    def getAxeName(self, key):
        "Returns axe's Name for respective key as string othewise None"
        return InfoPoint.getAxeName(self.ipType, key)
    
    #--------------------------------------------------------------------------
    def setVal(self, key, name):
        "Sets value key and name"
        return InfoPoint.setVal(self.ipType, key, name)

    #--------------------------------------------------------------------------
    def getValIdx(self, key):
        "Returns value's idx for respective key as position in the list of axes othewise None"
        return InfoPoint.getValIdx(self.ipType, key)
    
    #--------------------------------------------------------------------------
    def getValKey(self, idx):
        "Returns value's key for respective position in the list of valus othewise None"
        return InfoPoint.getValKey(self.ipType, idx)

    #--------------------------------------------------------------------------
    def getValName(self, key):
        "Returns value's Name for respective key as string othewise None"
        return InfoPoint.getValName(self.ipType, key)
    
    #--------------------------------------------------------------------------
    def getSchema(self):
        "Returns schema for respective InfoPoint type as dict {'axes':{}, 'vals':{}}"
        return InfoPoint.getSchema(self.ipType)
    
    #--------------------------------------------------------------------------
    def getAxes(self):
        "Returns axes keys and names as dict {key: name}"
        return InfoPoint.getAxes(self.ipType)
    
    #--------------------------------------------------------------------------
    def getVals(self):
        "Returns values keys and names as dict {key: name}"
        return InfoPoint.getVals(self.ipType)

    #--------------------------------------------------------------------------
    def mapFloatMethods(self):
        "Returns map of methods returning float number from keyed value"
        return InfoPoint.mapFloatMethods()

    #--------------------------------------------------------------------------
    def mapSetMethods(self):
        "Returns map of methods setting keyed value to function value for respective parameters"
        return InfoPoint.mapSetMethods()

    #==========================================================================
    # Position and indices tools
    #--------------------------------------------------------------------------
    def _subProducts(self):
        "Returns list of subproducts of _cnts [1, A, AB, ABC, ...]"

        toRet = [1]

        for cnt in self._cnts.values():
            toRet.append( cnt * toRet[-1] )

        #----------------------------------------------------------------------
        # Remove last element which is the product of all dimensions
        #----------------------------------------------------------------------
        toRet.pop()
        return toRet

    #--------------------------------------------------------------------------
    def _subPeriods(self, axeKey:str):
        "Returns period,serie & groups for respective axe"

        subs   = self._subProducts()
        axePos = self.getAxeIdx(axeKey)
        count  = self.count()

        serie  = subs[axePos  ]                            # Pocet Points v jednej grupe
        if axePos+1>=len(subs): period = count  
        else                  : period = subs[axePos+1]    # Perioda v akej sa opakuju grupy
        groups = self.count() // period                   # Pocet grup s indexom axeIdx v osi axeKey

        return period, serie, groups

    #--------------------------------------------------------------------------
    def _possForAxeVal(self, axeKey:str, axeIdx:int):
        "Returns list of positions of Points belonging to the axe with respective index axeIdx"

        #----------------------------------------------------------------------
        # Zistim hodnoty serie, period a groups pre danu os axeKey
        #----------------------------------------------------------------------
        period, serie, groups = self._subPeriods(axeKey)
        toRet = []

        #----------------------------------------------------------------------
        # Prejdem vsetky grupy
        #-----------------------------------------------------------------------
        for grp in range(groups):

            #------------------------------------------------------------------
            # Vypocitam zaciatok a koniec grupy
            #------------------------------------------------------------------
            start = (grp * period) + (axeIdx * serie)
            stop  = start + serie
            
            #------------------------------------------------------------------
            # Vlozim Points s indexom axeIdx do zoznamu toRet
            #------------------------------------------------------------------
            for pos in range(start, stop):
                toRet.append(pos)
        
        #-----------------------------------------------------------------------
        return toRet

    #--------------------------------------------------------------------------
    def _posByIdx(self, idxs:list):
        "Returns position of the InfoPoint in the list for respective indices"

        subProd = self._subProducts()

        pos = 0
        for i, idx in enumerate(idxs):
            pos += idx * subProd[i]

        return pos

    #--------------------------------------------------------------------------
    def _idxByPos(self, pos:int):
        "Returns indices of the InfoPoint for respective position in the list"

        #----------------------------------------------------------------------
        # Inicializacia
        #----------------------------------------------------------------------
        toRet = []
        subs  = self._subProducts()

        #----------------------------------------------------------------------
        # Prechadzam reverzne vsetky dimenzie
        #----------------------------------------------------------------------
        for sub in reversed(subs):

            #------------------------------------------------------------------
            # Zistim index a novu poziciu ako zostatok pre danu dimenziu
            #------------------------------------------------------------------
            idx = pos // sub
            pos = pos %  sub
            
            #------------------------------------------------------------------
            # Vlozim index na zaciatok zoznamu idxs
            #------------------------------------------------------------------
            toRet.insert(0, idx)

        #----------------------------------------------------------------------
        return toRet

    #--------------------------------------------------------------------------
    def _idxByCoord(self, coord):
        "Returns index in axe for respective coordinate"

        #----------------------------------------------------------------------
        # Coord is before pos[0]
        #----------------------------------------------------------------------



        #----------------------------------------------------------------------
        # Coord is between pos[0] and pos[cnt]
        #----------------------------------------------------------------------



        #----------------------------------------------------------------------
        # Coord is after pos[cnt]
        #----------------------------------------------------------------------

    #==========================================================================
    # InfoPoint retrieval
    #--------------------------------------------------------------------------
    def pointByPos(self, pos:int):
        "Returns InfoPoint in field for respective position"

        toRet = self.points[pos]
        return toRet

    #--------------------------------------------------------------------------
    def pointByIdx(self, idxs:list):
        "Returns InfoPoint in field at respective indexes"
        
        pos = self._posByIdx(idxs)
        return self.pointByPos(pos)
        
    #--------------------------------------------------------------------------
    def pointByCoord(self, coord:list):
        "Returns nearest InfoPoint in field to respective coordinates"
        
        pos = self._posByCoord(coord)
        return self.pointByPos(pos)
        
    #==========================================================================
    # Active submatrix tools
    #--------------------------------------------------------------------------
    # Active subsmatrix definition
    #--------------------------------------------------------------------------
    def actSubSet(self, actSub:dict):
        """Sets active submatrix definition as dict of freezed axesKeys with values.
           If actSub definition changed from current definition, sets actChanged to True.
        """

        logger.info(f"{self.name}.actSubSet: To {actSub}")

        #----------------------------------------------------------------------
        # Doplnenie definicie o nezmrazene osi
        #----------------------------------------------------------------------
        for key in self._cnts.keys():
            if key not in actSub.keys():
                actSub[key] = None

        #----------------------------------------------------------------------
        # Kontrola zmeny definicie
        #----------------------------------------------------------------------
        if self.actSub == actSub: 
            logger.debug(f"{self.name}.actSubSet: actSub definition was not changed")
            return
        
        #----------------------------------------------------------------------
        # Nastavenie aktivnej submatice
        #----------------------------------------------------------------------
        self.actSub = actSub.copy()
        self.actChanged = True

        #----------------------------------------------------------------------
        logger.debug(f"{self.name}.actSubSet: definition was changed to {self.actSub}")

    #--------------------------------------------------------------------------
    def _actPossBySub(self, axesLeft:list= None):
        "Return list of position in self.points for respective deifinition self.actSub"

        toRet = []
        idxs  = []

        #----------------------------------------------------------------------
        # Inicializacia rekurzie: vytvorim list klucov ku vsetkym osiam ['a', 'b', 'c', ...]
        #----------------------------------------------------------------------
        if axesLeft is None: axesLeft = list(self._cnts.keys())

        #----------------------------------------------------------------------
        # Odoberiem zo zonamu osi prvu os axe = 'a'
        #----------------------------------------------------------------------
        axe = axesLeft.pop(0)

        #----------------------------------------------------------------------
        # Prejdem vsetky hodnoty idx v spracovavanej osi
        #----------------------------------------------------------------------
        for idx in self._cnts[axe]:

            #------------------------------------------------------------------
            # Ak sa aktualna hodnota rovna zmrazenej alebo neurcenej hodnote  
            #------------------------------------------------------------------
            if (self.actSub[axe] is None) or (self.actSub[axe]==idx):

                #--------------------------------------------------------------
                # Trivialne riesenie: ak uz nezostali dalsie osi, pridam idx do zoznamu
                #--------------------------------------------------------------
                if len(axesLeft) == 0:

                    toRet.append(idx)

                #--------------------------------------------------------------
                # Rekurzia: ak este zostali nejake osy 
                #--------------------------------------------------------------
                if len(axesLeft) > 0:

                    #----------------------------------------------------------
                    # Pridam aktualny index do zoznamu idxs
                    #----------------------------------------------------------
                    idxs.append(idx)
                    subPoss = self._actPossBySub(axesLeft.copy())

                    #----------------------------------------------------------
                    # Pridam vsetky pozicie z podmatice do vysledneho zoznamu
                    #----------------------------------------------------------
                    for pos in subPoss: toRet.append(pos)

                #--------------------------------------------------------------
                # Odstranim posledny index z idxs pre dalsie iteracie
                #--------------------------------------------------------------
                idxs.pop()

            pass

        #_posByIdx(self, idxs:list)

    #--------------------------------------------------------------------------
    # Active subsmatrix retrieval
    #--------------------------------------------------------------------------
    def actSubmatrix(self, actSub=None, force=False):
        """Returns active submatrix of InfoPoints in field as list of InfoPoints
        """

        #----------------------------------------------------------------------
        # Nastavenie aktivnej submatice ak bola dodana definicia
        #----------------------------------------------------------------------
        if actSub is not None: self.actSubSet(actSub)

        #----------------------------------------------------------------------
        # Kontrola potreby obnovenia
        #----------------------------------------------------------------------
        if not self.actChanged and not force:
            logger.debug(f"{self.name}.actSubmatrix: subMatrix definition was not changed, no need to refresh")
            return self.actList

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.actSubmatrix: actSub={self.actSub}, force={force}")
        self.actList = []
        
        #----------------------------------------------------------------------
        # Ziskam list pozicii bodov patriacich hladanemu vektoru
        #----------------------------------------------------------------------
        poss = self._actPossBySub()
        
        if poss is None:
            logger.error(f"{self.name}.actSubmatrix: Can not obtain positions for desired subset and structure")
            return self.actList
        
        #----------------------------------------------------------------------
        # Create vector of InfoPoints/Values for respective positions
        #----------------------------------------------------------------------
        for pos in poss:
            self.actList.append(self.pointByPos(pos))

        #----------------------------------------------------------------------
        return self.actList    
    
    #==========================================================================
    # Value modification
    #--------------------------------------------------------------------------
    def clear(self, *, defs:dict={}):
        "Set all InfoPoint's values to default value"
        
        logger.info(f"{self.name}.clear: defs={defs}")

        for point in self.points: point.clear(dat=defs)

    #--------------------------------------------------------------------------
    def gener(self, *, cnts:dict, origs:dict, rects:dict, ipType:str=None, defs:dict={} ):
        """Creates new InfoMatrix with respective cnts, origs and rect. Expecting valid 
           ipType scheme. If ipType is not in arguments, uses existing ipType"""
        
        if ipType is not None: self.ipType = ipType
        logger.debug(f"{self.name}.gener: {cnts} points of type {self.ipType} on rect {rects} from {origs} with values {defs}")

        #----------------------------------------------------------------------
        # Check validity of InfoPoint's schema 
        #--- -------------------------------------------------------------------
        if not self.isInSchema(axes=list(cnts.keys()), vals=list(defs.keys())):
            logger.error(f"{self.name}.gener: Schema for {self.ipType} is not comaptible with arguments")
            return

        #----------------------------------------------------------------------
        # Destroy old data
        #----------------------------------------------------------------------
        self.points.clear()                    # Clear all points in the InfoMatrix

        #----------------------------------------------------------------------
        # InfoMatrix settings
        #----------------------------------------------------------------------
        self._cnts     = cnts.copy()              # List of number of InfoPoints in respective axes     
        self._origs    = origs.copy()             # List of origin's coordinates of the InfoMatrix
        self._rects    = rects.copy()             # List of lenghts of the InfoMatrix's axes

        self._diffs    = {}                       # List of distances between two points in respective axes in lambda units
        for key, cnt in self._cnts.items():
            self._diffs[key] = self._rects[key]/(cnt-1)  # Distance between two points in respective axes in lambda units
                
        self.actCol    = None                     # Current axes in role of the columns for 2D matrix
        self.actRow    = None                     # Current axes in role of the rows for 2D matrix
        if len(self._cnts) <= 1: self.actRow = list(self._cnts.keys())[0]
        if len(self._cnts) == 2: self.actCol = list(self._cnts.keys())[1]   

        #----------------------------------------------------------------------
        # Generate InfoPoints at respective positions
        #----------------------------------------------------------------------
        point = None
        for pos in range(self.count()):

            #------------------------------------------------------------------
            # Compute coordinates of the InfoPoint for respective position and indices
            #------------------------------------------------------------------
            idxs = self._idxByPos(pos)          # Get indices of the InfoPoint for respective position
            coos = {}

            for i, key in enumerate(self._cnts.keys()):
                coos[key] = self._origs[key] + (idxs[i] * self._diffs[key])

            #------------------------------------------------------------------
            # Create new row of InfoPoint at respective coordinates
            #------------------------------------------------------------------
            point = InfoPoint(self.ipType, pos=coos, vals=defs)
            self.points.append(point)
            
        #----------------------------------------------------------------------
        # Final adjustments
        #----------------------------------------------------------------------
         
        
    #--------------------------------------------------------------------------

    #==========================================================================
    # Methods application
    #--------------------------------------------------------------------------
    def copyFrom(self, src, *, key=None, tgtSlice=(0,0,0,0), srcFrom=(0,0)):
        "Copy point's values from srcs 2D matrix into tgts 2D matrix"
        
        logger.info(f"{self.name}.copyFrom: From {src.name} starting at {srcFrom} to nodes {tgtSlice} for key={key}")

        #----------------------------------------------------------------------
        # Slice settings
        #----------------------------------------------------------------------
        tgtRowFrom = tgtSlice[0]
        tgtColFrom = tgtSlice[1]
        tgtRowTo   = tgtSlice[2] if tgtSlice[2] > 0 else self._rows-1
        tgtColTo   = tgtSlice[3] if tgtSlice[3] > 0 else self._cols-1
        
        srcRowFrom = srcFrom[0]
        srcColFrom = srcFrom[1]

        i = 0

        #----------------------------------------------------------------------
        # Target rows from tgtRowFrom to tgtRowTo
        #----------------------------------------------------------------------
        for tgtRow in range(tgtRowFrom, tgtRowTo+1): 
            
            #------------------------------------------------------------------
            # Target columns from tgtColFrom to tgtColTo
            #------------------------------------------------------------------
            for tgtCol in range(tgtColFrom, tgtColTo+1):
                
                #--------------------------------------------------------------
                # Get target node
                #--------------------------------------------------------------
                tgtPoint = self.pointByIdx([tgtRow, tgtCol])
                if tgtPoint is None:
                    logger.error(f"{self.name}.copyFrom: Target point[{tgtRow},{tgtCol}] does not exists")
                    break
                
                #--------------------------------------------------------------
                # Trying to get source node
                #--------------------------------------------------------------
                try:
                    srcPoint = src.pointByIdx([srcRowFrom+tgtRow-tgtRowFrom, srcColFrom+tgtCol-tgtColFrom])
                except IndexError:
                    logger.error(f"{self.name}.copyFrom: Source point[{srcRowFrom+tgtRow-tgtRowFrom}, {srcColFrom+tgtCol-tgtColFrom}] does not exists")
                    break   
                
                #--------------------------------------------------------------
                # Copy value from source to target node
                #--------------------------------------------------------------
                srcDat = srcPoint.get(key=key)
                tgtPoint.set(dat=srcDat)
                i += 1

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.copyFrom: Copied {i} points")
        return self
        
    #--------------------------------------------------------------------------
    def pointSetFunction(self, keyFtion, key:str, par:dict=None):
        "Apply respective function for all points or points in active substructure"

        logger.info(f"{self.name}.pointSetFunction: {keyFtion}(key={key}, par={par}) for {len(self.actList)} active Points]")
        
        #----------------------------------------------------------------------
        # Ziskanie vykonavanej funkcie
        #----------------------------------------------------------------------
        if keyFtion in self.mapSetMethods().keys(): 
            function = self.mapSetMethods()[keyFtion]['ftion']

        else:
            logger.error(f"{self.name}.pointSetFunction: '{keyFtion}' is not in defined functions")
            return False

        #----------------------------------------------------------------------
        # Ziskanie listu bodov na aplikovanie funkcie
        #----------------------------------------------------------------------
        if 'all' in par.keys() and par['all'] == True:
            tgtStr = 'all'
            tgtList = self.points

        else:
            tgtStr = 'active subset'
            tgtList = self.actList

        #----------------------------------------------------------------------
        # Vykonanie funkcie
        #----------------------------------------------------------------------
        pts = 0  # Counter of points

        for point in tgtList:
            function(self=point, key=key, par=par)
            pts += 1

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.pointSetFunction: {keyFtion} was applied to {tgtStr} {pts} InfoPoints")
        return True

    #==========================================================================
    # Normalisation methods
    #--------------------------------------------------------------------------
    def normAbs(self, nods, norm=None):
        "Normalise set of the nodes by sum of absolute values"
        
        logger.info(f"{self.name}.normAbs: ")
        
        #----------------------------------------------------------------------
        # Initialisation
        #----------------------------------------------------------------------
        sumAbs = 0
        for node in nods: sumAbs += node['cP'].abs()

        #----------------------------------------------------------------------
        # If norm does exists will be sumAbs
        #----------------------------------------------------------------------
        if norm is None: norm = sumAbs

        #----------------------------------------------------------------------
        # Iterate over nodes and apply norm if possible
        #----------------------------------------------------------------------
        if norm > 0:
            for node in nods: node['cP'].c /= norm
            
        else: norm = 1

        #----------------------------------------------------------------------
        logger.info(f"{self.name}.normAbs: norm = {norm} for {len(nods)} points")

    #==========================================================================
    # Persistency methods
    #--------------------------------------------------------------------------
    def toJson(self):
        "Converts node into json structure"
        
        logger.debug(f'{self.name}.toJson:')
        
        toRet = {}

        logger.debug(f'{self.name}.toJson: Converted')
        return toRet

#------------------------------------------------------------------------------
print(f"InfoMatrix ver {_VER}")

#==============================================================================
# Unit testy
#------------------------------------------------------------------------------
if __name__ == '__main__':

    #--------------------------------------------------------------------------
    # Test of the InfoMatrix class
    #--------------------------------------------------------------------------
    logger.debug('Test of InfoMatrix class')

    #--------------------------------------------------------------------------
    # Vytvorenie, generovanie osi
    #--------------------------------------------------------------------------
    im = InfoMatrix('Test matrix', ipType='ipTest')
    print(im)
    input('Press Enter to continue...')

    im.gener(cnts={'a':5}, origs={'a':0.0}, rects={'a':1.0})
    print(im)
    input('Press Enter to continue...')

    im.setAxe('a', 'Os A')
    im.setAxe('a', 'Os A')
    print(im)
    input('Press Enter to continue...')

    im.gener(cnts={'a':3}, origs={'a':0.0}, rects={'a':1.0})
    print(im)
    input('Press Enter to continue...')

    im.setAxe('b', 'Os B')
    im.gener(cnts={'a':3, 'b':4}, origs={'a':0.0, 'b':0}, rects={'a':10, 'b':10})
    print(im)
    input('Press Enter to continue...')

    im.setAxe('c', 'Os C')
    im.gener(cnts={'a':3, 'b':4, 'c':2}, origs={'a':0.0, 'b':0, 'c':0}, rects={'a':1.0, 'b':2, 'c':3})
    im.setVal('v', 'Rýchlosť')
    im.setVal('m', 'Hmotnosť')
    input('Press Enter to continue...')
    print()

    print(im)
    print('possA0', im._possForAxeVal(axeKey='a', axeIdx=0))
    print('possA1', im._possForAxeVal(axeKey='a', axeIdx=1))
    print()
    print('possB0', im._possForAxeVal(axeKey='b', axeIdx=0))
    print('possB1', im._possForAxeVal(axeKey='b', axeIdx=1))
    print()
    print('possC0', im._possForAxeVal(axeKey='c', axeIdx=0))
    print('possC1', im._possForAxeVal(axeKey='c', axeIdx=1))
    input('Press Enter to continue...')
    print()

    #--------------------------------------------------------------------------
    # generovanie hodnot
    #--------------------------------------------------------------------------
    im.pointSetFunction('BRandom fuuniform', 'm', par={'all':True, 'min':0, 'max':5})
    im.pointSetFunction('Random uniform', 'm', par={'all':True, 'min':0, 'max':5})
    print(im)
    input('Press Enter to continue...')

    #--------------------------------------------------------------------------
    # generovanie hodnot
    #--------------------------------------------------------------------------
    print('point')
    print('pos=16 ', im.pointByPos(16))
    input('Press Enter to continue...')
   

    print('[1, 3, 0] ', im.pointByIdx([1, 3, 0]))
    input('Press Enter to continue...')

    #--------------------------------------------------------------------------
    # Submatrix
    #--------------------------------------------------------------------------
    im.actSubSet({'b':1})
    input('Press Enter to continue...')



#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------