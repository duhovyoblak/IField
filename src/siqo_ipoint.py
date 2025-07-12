#==============================================================================
# Siqo class InfoPoint
#------------------------------------------------------------------------------
import math
import cmath
import random                 as rnd

from   siqolib.logger         import SiqoLogger

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_VER      = '3.04'

_IND      = '|  '                      # Info indentation
_F_SCHEMA = 1                          # Format for ipType
_F_TOTAL  = 6                          # Total number of digits in float number
_F_DECIM  = 3                          # Number of digits after decimal point in float number

_SCH_AXES = {}                         # Default axes for InfoPoint schema
_SCH_VALS = {}                         # Default values for InfoPoint schema    

_SCHEMA   = {'ipReal   ':{'axes':_SCH_AXES.copy()
                         ,'vals':_SCH_VALS.copy()
                         }
            ,'ipComplex':{'axes':{'None':'None', 'x':'os X', 'y':'os Y'}
                         ,'vals':{'r':'real Value'}
                         }
            }                          # Default built-in Schema for InfoPoint

#==============================================================================
# package's variables
#------------------------------------------------------------------------------
logger = SiqoLogger('InfoPoint test', level='INFO')

#==============================================================================
# InfoPoint
#------------------------------------------------------------------------------
class InfoPoint:

    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------
    _schema  = _SCHEMA.copy()                      # Schema for InfoPoint

    #--------------------------------------------------------------------------
    @staticmethod
    def resetSchema():
        "Resets schema of InfoPoint to default values"
        
        InfoPoint._schema = _SCHEMA.copy()
        logger.info("InfoPoint.resetSchema:")

    #--------------------------------------------------------------------------
    @staticmethod
    def checkSchema(ipType):
        """Checks if schema does exist for respective ipType. If schema for ipType 
           does not exist, create empty as {'axes':{}, 'vals':{}}
        """
        
        if ipType not in InfoPoint._schema.keys():
            InfoPoint._schema[ipType] = {'axes':_SCH_AXES.copy(), 'vals':_SCH_VALS.copy()}

    #--------------------------------------------------------------------------
    @staticmethod
    def clearSchema(ipType):
        "Clears schema of InfoPoint for respective ipType to {'axes':{}, 'vals':{}}"
        
        InfoPoint.checkSchema(ipType)
        InfoPoint._schema[ipType] = {'axes':_SCH_AXES.copy(), 'vals':_SCH_VALS.copy()}
        logger.info(f"InfoPoint.setAxe: clearSchema ipType '{ipType}'")

    #--------------------------------------------------------------------------
    @staticmethod
    def isInSchema(ipType, *, axes:list=None, vals:list=None):
        "Returns True if schema has defined all axes and vals otherwise returns False"

        if ipType not in InfoPoint._schema.keys():
            logger.warning(f"InfoPoint.isInSchema: ipType '{ipType}' is not defined InfoPoint type")
            return False
        
        #----------------------------------------------------------------------
        # Check axes    
        #----------------------------------------------------------------------        
        if axes is not None:

            for axe in axes:

                if axe not in InfoPoint._schema[ipType]['axes'].keys():
                    logger.warning(f"InfoPoint.isInSchema: Axe '{axe}' is not defined in schema axes {InfoPoint._schema[ipType]['axes']}")
                    return False

        #----------------------------------------------------------------------
        # Check values    
        #----------------------------------------------------------------------        
        if vals is not None:

            for val in vals:

                if val not in InfoPoint._schema[ipType]['vals'].keys():
                    logger.warning(f"InfoPoint.isInSchema: Value '{val}' is not defined in schema values {InfoPoint._schema[ipType]['vals']}")
                    return False
        
        #----------------------------------------------------------------------        
        return True

    #--------------------------------------------------------------------------
    @staticmethod
    def setAxe(ipType, key, name):
        "Sets axe's key and name for respective ipType. If axe exists already, redefine name."
        
        InfoPoint.checkSchema(ipType)
        InfoPoint._schema[ipType]['axes'][key] = name
        logger.debug(f"InfoPoint.setAxe: set key '{key}' for axe '{name}'")

    #--------------------------------------------------------------------------
    @staticmethod
    def getAxeIdx(ipType, key):
        "Returns axe's idx position in the dict of axes for respective key, othewise None"

        #----------------------------------------------------------------------
        # Check if ipType is defined    
        #----------------------------------------------------------------------        
        if ipType not in InfoPoint._schema.keys(): 
            logger.warning(f"InfoPoint.getAxeIdx: ipType '{ipType}' is not defined InfoPoint type")
            return None 

        #----------------------------------------------------------------------
        # Find index of the axe's key  
        #----------------------------------------------------------------------
        for i, keyAxe in enumerate(InfoPoint._schema[ipType]['axes'].keys()):
            if key==keyAxe: 
                logger.debug(f"InfoPoint.getAxeIdx: Key '{key}' found in axes {InfoPoint._schema[ipType]['axes']} at index {i}")
                return i

        #----------------------------------------------------------------------
        # Key not found     
        #----------------------------------------------------------------------
        logger.warning(f"InfoPoint.getAxeIdx: Key '{key}' not found in axes {InfoPoint._schema[ipType]['axes']}")
        return None
    
    #--------------------------------------------------------------------------
    @staticmethod
    def getAxeKey(ipType, idx):
        "Returns axe's key for respective idx position in the dict of axes, othewise None"

        #----------------------------------------------------------------------
        # Check if ipType is defined    
        #----------------------------------------------------------------------        
        if ipType not in InfoPoint._schema.keys(): 
            logger.warning(f"InfoPoint.getAxeKey: ipType '{ipType}' is not defined InfoPoint type")
            return None 

        #----------------------------------------------------------------------
        # Check if idx is not out of the range   
        #----------------------------------------------------------------------        
        if idx >= len(InfoPoint._schema[ipType]['axes'].keys()): 
            logger.warning(f"InfoPoint.getAxeKey: Idx '{idx}' is out of the range in {InfoPoint._schema[ipType]['axes']}")
            return None 

        #----------------------------------------------------------------------
        # Find key for index  
        #----------------------------------------------------------------------
        key = list(InfoPoint._schema[ipType]['axes'].keys())[idx]
        return key
    
    #--------------------------------------------------------------------------
    @staticmethod
    def getAxeName(ipType, key):
        "Returns axe's Name for respective key, othewise None"

        #----------------------------------------------------------------------
        # Check if ipType is defined    
        #----------------------------------------------------------------------        
        if ipType not in InfoPoint._schema.keys(): 
            logger.warning(f"InfoPoint.getAxeName: ipType '{ipType}' is not defined InfoPoint type")
            return None 

        #----------------------------------------------------------------------
        # Find name of the axe's key  
        #----------------------------------------------------------------------
        if key not in InfoPoint._schema[ipType]['axes'].keys():
            logger.warning(f"InfoPoint.getAxeName: Key '{key}' not found in axes {InfoPoint._schema[ipType]['axes']}")
            return None
        
        else:
            return InfoPoint._schema[ipType]['axes'][key]
    
    #--------------------------------------------------------------------------
    @staticmethod
    def setVal(ipType, key, name):
        "Sets value key and name for respective ipType. If value exists already, redefine name."
        
        InfoPoint.checkSchema(ipType) 
        InfoPoint._schema[ipType]['vals'][key] = name
        logger.debug(f"InfoPoint.setVal: set key '{key}' for value '{name}'")

    #--------------------------------------------------------------------------
    @staticmethod
    def getValIdx(ipType, key):
        "Returns value's idx position in the dict of values for respective key, othewise None"

        #----------------------------------------------------------------------
        # Check if ipType is defined    
        #----------------------------------------------------------------------        
        if ipType not in InfoPoint._schema.keys(): 
            logger.warning(f"InfoPoint.getValIdx: ipType '{ipType}' is not defined InfoPoint type")
            return None 

        #----------------------------------------------------------------------
        # Find index of the value's key  
        #----------------------------------------------------------------------
        for i, keyVal in enumerate(InfoPoint._schema[ipType]['vals'].keys()):
            if key==keyVal: return i

        #----------------------------------------------------------------------
        # Key not found     
        #----------------------------------------------------------------------
        logger.warning(f"InfoPoint.getValIdx: Key '{key}' not found in valus {InfoPoint._schema[ipType]['vals']}")
        return None
    
    #--------------------------------------------------------------------------
    @staticmethod
    def getValKey(ipType, idx):
        "Returns value's key in the dict of values for respective idx position, othewise None"

        #----------------------------------------------------------------------
        # Check if ipType is defined    
        #----------------------------------------------------------------------        
        if ipType not in InfoPoint._schema.keys(): 
            logger.warning(f"InfoPoint.getValKey: ipType '{ipType}' is not defined InfoPoint type")
            return None 

        #----------------------------------------------------------------------
        # Check if idx is not out of the range   
        #----------------------------------------------------------------------        
        if idx >= len(InfoPoint._schema[ipType]['vals'].keys()): 
            logger.warning(f"InfoPoint.getValKey: Idx '{idx}' is out of the range in {InfoPoint._schema[ipType]['vals']}")
            return None 

        #----------------------------------------------------------------------
        # Find key for index  
        #----------------------------------------------------------------------
        key = list(InfoPoint._schema[ipType]['vals'].keys())[idx]
        return key
    
    #--------------------------------------------------------------------------
    @staticmethod
    def getValName(ipType, key):
        "Returns value's Name for respective key, othewise None"

        #----------------------------------------------------------------------
        # Check if ipType is defined    
        #----------------------------------------------------------------------        
        if ipType not in InfoPoint._schema.keys(): 
            logger.warning(f"InfoPoint.getValName: ipType '{ipType}' is not defined InfoPoint type")
            return None 

        #----------------------------------------------------------------------
        # Find name of the value's key  
        #----------------------------------------------------------------------
        if key not in InfoPoint._schema[ipType]['vals'].keys():
            logger.warning(f"InfoPoint.getValName: Key '{key}' not found in valus {InfoPoint._schema[ipType]['vals']}")
            return None
        
        else:
            return InfoPoint._schema[ipType]['vals'][key]
    
    #--------------------------------------------------------------------------
    @staticmethod
    def getSchema(ipType):
        "Returns schema for respective InfoPoint type as dict {'axes':{}, 'vals':{}}"
        
        InfoPoint.checkSchema(ipType) 
        return InfoPoint._schema[ipType].copy()
    
    #--------------------------------------------------------------------------
    @staticmethod
    def getAxes(ipType):
        "Returns axes keys and names as dict {key: name} for respective ipType"
        
        InfoPoint.checkSchema(ipType) 
        return InfoPoint._schema[ipType]['axes'].copy()
    
    #--------------------------------------------------------------------------
    @staticmethod
    def getVals(ipType):
        "Returns values keys and names as dict {key: name} for respective ipType"

        InfoPoint.checkSchema(ipType) 
        return InfoPoint._schema[ipType]['vals'].copy()

    #--------------------------------------------------------------------------
    @staticmethod
    def mapShowMethods():
        "Returns map of methods returning float number from keyed value"

        return {'Float value'   : InfoPoint.fValue
               ,'Absolute value': InfoPoint.abs
               ,'Real value'    : InfoPoint.real
               ,'Imag value'    : InfoPoint.imag
               ,'Phase'         : InfoPoint.phase
               }

    #--------------------------------------------------------------------------
    @staticmethod
    def mapSetMethods():
        "Returns map of methods setting keyed value to function value for respective parameters"

        return {'Real constant'          : {'ftion':InfoPoint.fltConst,    'par':{'const' :0                                                 }}
               ,'Random uniform'         : {'ftion':InfoPoint.fltRandUni,  'par':{'min'   :0, 'max'   :1                                     }}
               ,'Random bit'             : {'ftion':InfoPoint.fltRandBit,  'par':{'prob1' :0.1                                               }}
               ,'Comp constant (re/im)'  : {'ftion':InfoPoint.cmpConstR,   'par':{'real'  :0, 'imag'  :0                                     }}
               ,'Comp constant (abs/phs)': {'ftion':InfoPoint.cmpConstP,   'par':{'abs'   :0, 'phase' :0                                     }}
               ,'Comp random (re/im)'    : {'ftion':InfoPoint.cmpRandUniR, 'par':{'reMin' :0, 'reMax' :1, 'imMin'   :0, 'imMax'   :1         }}
               ,'Comp random (abs/phs)'  : {'ftion':InfoPoint.cmpRandUniP, 'par':{'absMin':0, 'absMax':1, 'phaseMin':0, 'phaseMax':2*cmath.pi}}
               }

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, ipType:str, *, pos=None, vals=None):
        "Calls constructor of InfoPoint on respective position"
        
        InfoPoint.checkSchema(ipType)

        self._ipType = ipType # Type of InfoPoint (ipReal, ipComplex, ...)
        self._pos    = {}     # Dict of real numbers for position coordinates {'row':5, 'col':6, ...} defined by schema
        self._vals   = {}     # Dict of values of this InfoPoint defined by schema

        self.set(pos=pos, vals=vals)

    #--------------------------------------------------------------------------
    def __str__(self):
        "Prints info about this InfoPoint"

        return self.info()['msg']

    #--------------------------------------------------------------------------
    def _format(self, val):
        "Creates string representation of the value for respective format settings"

        if   val is None         : toRet = 'None'.ljust(_F_TOTAL)
        elif type(val) == int    : toRet = f"{val:#{_F_TOTAL}}"
        elif type(val) == float  : toRet = f"{val:#{_F_TOTAL}.{_F_DECIM}f}"
        elif type(val) == complex: toRet = f"({val.real:#{_F_TOTAL}.{_F_DECIM}f} {val.imag:#{_F_TOTAL}.{_F_DECIM}f}j)"
        else                     : toRet = f"{val:{_F_TOTAL}}"

        return toRet
    
    #--------------------------------------------------------------------------
    def _posStr(self):
        "Creates string representation of the position of this InfoPoint"

        toRet = '['
        
        i = 0
        for axe, axeName in InfoPoint._schema[self._ipType]['axes'].items():

            # Axe 'None' preskocim
            if axe == 'None': continue

            #----------------------------------------------------------------------
            # Retrieve position of this InfoPoint for axe with key 'axe'
            #----------------------------------------------------------------------
            if axe in self._pos.keys(): val = self._pos[axe]
            else                      : val = None

            #----------------------------------------------------------------------
            # Create string representation of the position of this InfoPoint
            #----------------------------------------------------------------------
            if i == 0: toRet +=  f"{axeName}={self._format(val)}"
            else     : toRet += f"|{axeName}={self._format(val)}"
            i += 1
 
        toRet += ']'
        return toRet
    
    #--------------------------------------------------------------------------
    def _valStr(self):
        "Creates string representation of the values of this InfoPoint"

        toRet = '{'
        
        i = 0
        for valKey in InfoPoint._schema[self._ipType]['vals'].keys():
            
            if valKey in self._vals.keys(): val = self._vals[valKey]
            else                          : val = None

            #----------------------------------------------------------------------
            # Create string representation of the data of this InfoPoint
            #----------------------------------------------------------------------
            if i == 0: toRet +=  f"{valKey}={self._format(val)}"
            else     : toRet += f"|{valKey}={self._format(val)}"
            i += 1  

        toRet += '}'

        return toRet
    
    #--------------------------------------------------------------------------
    def info(self, indent=0):
        "Creates info about this InfoPoint"
        
        msg = f"{indent*_IND}{self._ipType:{_F_SCHEMA}}{self._posStr()}: {self._valStr()}"

        return {'res':'OK', 'val':self._vals, 'msg':msg}
        
    #--------------------------------------------------------------------------
    def copy(self):
        "Creates copy of this InfoPoint"

        toRet = InfoPoint(self._ipType)

        toRet._pos  = self._pos.copy()
        toRet._vals = self._vals.copy()

        return toRet
        
    #==========================================================================
    # Value retrieval
    #--------------------------------------------------------------------------
    def pos(self, key:str):
        "Returns position for respective axis key"
        
        #----------------------------------------------------------------------
        # Key check
        #----------------------------------------------------------------------
        if key not in InfoPoint._schema[self._ipType]['axes'].keys():
            logger.warning(f"InfoPoint.get: Key '{key}' not found in axes {InfoPoint._schema[self._ipType]['axes']}")
            return None

        #----------------------------------------------------------------------
        # Return axe's value of this InfoPoint for respective key
        #----------------------------------------------------------------------
        return self._pos[key]

    #--------------------------------------------------------------------------
    def val(self, key:str=None):
        "Returns value of this InfoPoint for respective key"
        
        #----------------------------------------------------------------------
        # Return this InfoPoint for key is None
        #----------------------------------------------------------------------
        if key is None: return self

        #----------------------------------------------------------------------
        # Key check
        #----------------------------------------------------------------------
        if key not in InfoPoint._schema[self._ipType]['vals'].keys():
            logger.warning(f"InfoPoint.get: Key '{key}' not found in values {InfoPoint._schema[self._ipType]['vals']}")
            return None

        #----------------------------------------------------------------------
        # Return value of this InfoPoint for respective key
        #----------------------------------------------------------------------
        return self._vals[key]

    #==========================================================================
    # Dat Value modification
    #--------------------------------------------------------------------------
    def set(self, *, pos=None, vals=None):
        "Sets position and data of this InfoPoint"
        
        #----------------------------------------------------------------------
        # Set position of this InfoPoint
        #----------------------------------------------------------------------
        if pos is not None:

            try:
                # Zapisem poziciu vo vsetkych osiach schemy okrem NONE
                for key in InfoPoint._schema[self._ipType]['axes'].keys():
                    if key != 'None': self._pos[key] = pos[key]

            except KeyError:
                logger.error(f"InfoPoint.set: Position '{self._posStr()}' is not compatible with schema axes {InfoPoint._schema[self._ipType]['axes']}")
                return False
            
        #----------------------------------------------------------------------
        # Set values of this InfoPoint
        #----------------------------------------------------------------------
        if vals is not None:

            for key, val in vals.items():

                if key in InfoPoint._schema[self._ipType]['vals'].keys():
                    self._vals[key] = val    

                else:
                    logger.warning(f"InfoPoint.set: Key '{key}' not found in values {InfoPoint._schema[self._ipType]['vals']}")
                    return False
                
        #----------------------------------------------------------------------
        logger.debug(f"InfoPoint.set: pos={self._posStr()}, vals {self._valStr()}")
        return True
    
    #--------------------------------------------------------------------------
    def clear(self, *, vals:dict=None):
        "Sets all values to default values"
        
        if (vals is not None) and (len(vals) > 0):

            for key, val in vals.items():

                if key in InfoPoint._schema[self._ipType]['vals'].keys():
                    self._vals[key] = val    

                else:
                    logger.warning(f"InfoPoint.set: Key '{key}' not found in values {InfoPoint._schema[self._ipType]['vals']}")
                    return False

        else: self._vals = {}

        logger.debug(f"InfoPoint.clear: with vals {vals}")
        return self

    #==========================================================================
    # Methods returning float for keyed value
    #--------------------------------------------------------------------------
    def fValue(self, key:str):
        "Return float value or modul for respective key value"

        x = self.val(key)
        if x is not None:

            if   type(x) in (int, float): return x
            elif type(x) == complex     : return cmath.polar(x)[0]
            else                        : return x

        return x

    #--------------------------------------------------------------------------
    def abs(self, key:str):
        "Return absolute value or modul for respective key"

        x = self.val(key)
        if x is not None:

            if   type(x) in (int, float): return math.fabs(x)
            elif type(x) == complex     : return cmath.polar(x)[0]
            else                        : return x

        return x

    #--------------------------------------------------------------------------
    def real(self, key:str):
        "Return real part of value for respective key"

        x = self.val(key)
        if x is not None:

            if   type(x) in (int, float): return x
            elif type(x) == complex     : return x.real
            else                        : return x

        return x

    #--------------------------------------------------------------------------
    def imag(self, key:str):
        "Return imaginary part of value for respective key"

        x = self.val(key)
        if x is not None:

            if   type(x) in (int, float): return 0
            elif type(x) == complex     : return x.imag
            else                        : return x

        return x

    #--------------------------------------------------------------------------
    def phase(self, key:str):
        "Return phase in <-pi, pi> from +x axis for respective key"
        
        x = self.val(key)
        if x is not None:

            if   type(x) in (int, float): return 0
            elif type(x) == complex     : return cmath.phase(x)
            else                        : return x

        return x

    #==========================================================================
    # Methods generating keyed value
    #--------------------------------------------------------------------------
    def fltConst(self, key:str, par:dict):
        "Sets constant value for keyed value"

        self.set(vals={key:par['const']})

    #--------------------------------------------------------------------------
    def fltRandUni(self, key:str, par:dict):
        "Generates uniform random float value from interval for keyed value"

        if 'min' in par.keys(): min_val = par['min']
        else                  : min_val = 0

        if 'max' in par.keys(): max_val = par['max']
        else                  : max_val = 1

        val = rnd.uniform(min_val, max_val)

        self.set(vals={key:val})

    #--------------------------------------------------------------------------
    def fltRandBit(self, key:str, par:dict):
        "Sets value 0/1 with respective probability for keyed value"

        x = rnd.randint(0, 9999)
        
        if x <= par['prob1']*10000: val = 1
        else                      : val = 0

        self.set(vals={key:val})
        
    #--------------------------------------------------------------------------
    def cmpConstR(self, key:str, par:dict):
        "Sets constant real and imaginary value for keyed value"

        c = complex(par['real'], par['imag'])
        self.set(vals={key:c})

    #--------------------------------------------------------------------------
    def cmpConstP(self, key:str, par:dict):
        "Sets constant absolute value and phase value for keyed value"

        c = cmath.rect(par['abs'], par['phase'])
        self.set(vals={key:c})

    #--------------------------------------------------------------------------
    def cmpRandUniR(self, key:str, par:dict):
        "Generates random uniform real and imaginary values from respective intervals for keyed value"

        real = rnd.random()
        imag = rnd.random()
        c = complex(real, imag)

        self.set(vals={key:c})

    #--------------------------------------------------------------------------
    def cmpRandUniP(self, key:str, par:dict):
        "Generates random uniform absolute value and phase from respective intervals for keyed value"

        abs   = rnd.random()
        phase = rnd.random()
        c = cmath.rect(abs, phase)

        self.set(vals={key:c})

    #==========================================================================
    # Two-points methods
    #--------------------------------------------------------------------------
    def deltasTo(self, toP):
        "Returns list of differences between coordinates to other InfoPoint"
        
        #----------------------------------------------------------------------
        # Check if both InfoPoints have the same number of coordinates and create pairs of them
        #----------------------------------------------------------------------
        pairs = []

        try:
            for key, val in self._pos.items():
                pairs.append( (val, toP._pos[key]) )

        except KeyError:
            logger.error(f"InfoPoints have different number of coordinates!")
            return None
            
        #----------------------------------------------------------------------
        # Creates list of differences between coordinates for respective InfoPoint
        #----------------------------------------------------------------------
        toRet = [pair[1] - pair[0] for pair in pairs]
        return toRet

    #--------------------------------------------------------------------------
    def distSqrTo(self, toP):
        "Returns square of the distance to other InfoPoint"
        
        dlts  = self.deltasTo(toP)
        toRet = 0
        
        for dlt in dlts: toRet += dlt*dlt
        
        return toRet

    #--------------------------------------------------------------------------
    def distTo(self, toP):
        "Returns the distance to other InfoPoint"
        
        sqrDist = self.distSqrTo(toP)
        return math.sqrt(sqrDist)
    
#------------------------------------------------------------------------------
print(f'InfoPoint ver {_VER}')

#==============================================================================
# Unit tests
#------------------------------------------------------------------------------
if __name__ == '__main__':

    from   siqolib.logger          import SiqoLogger
    logger = SiqoLogger('InfoPoint test', level='INFO')


    if True:
 
        print(40*'=')
        print('Schema creating')
        print(40*'-')

        InfoPoint.setAxe('ipTest', 'x', 'os X')    
        InfoPoint.setAxe('ipTest', 'y', 'os Y')    
        InfoPoint.setVal('ipTest', 'm', 'hmotnost')
        InfoPoint.setVal('ipTest', 'v', 'rychlost')

        print('Test of InfoPoint class')
        print('_IND      =', _IND)
        print('schema    =', InfoPoint._schema)

        print()
        print('Schema for ipTest')
        print('axes      =', InfoPoint.getAxes('ipTest'))   
        print('vals      =', InfoPoint.getVals('ipTest')) 

    if True:
 
        print(40*'=')
        print('Schema tools')
        print(40*'-')

        print('idx for keyAxe x =', InfoPoint.getAxeIdx('ipTest', 'x'))
        print('key for keyAxe 0 =', InfoPoint.getAxeKey('ipTest', 0 ))
        print('idx for keyAxe y =', InfoPoint.getAxeIdx('ipTest', 'y'))
        print('key for keyAxe 1 =', InfoPoint.getAxeKey('ipTest', 1 ))
        print('idx for keyAxe z =', InfoPoint.getAxeIdx('ipTest', 'z'))
        print('key for keyAxe 2 =', InfoPoint.getAxeKey('ipTest', 2 ))

        print('idx for keyVal x =', InfoPoint.getValIdx('ipTest', 'x'))
        print('key for keyVal 0 =', InfoPoint.getValKey('ipTest', 0))
        print('idx for keyVal v =', InfoPoint.getValIdx('ipTest', 'v'))
        print('key for keyVal 1 =', InfoPoint.getValKey('ipTest', 1))
        print('key for keyVal 2 =', InfoPoint.getValKey('ipTest', 2))

        print('name for keyAxe x =', InfoPoint.getAxeName('ipTest', 'x'))
        print('name for keyAxe y =', InfoPoint.getAxeName('ipTest', 'y'))
        print('name for keyAxe z =', InfoPoint.getAxeName('ipTest', 'z'))
        print('name for keyVal x =', InfoPoint.getValName('ipTest', 'x'))
        print('name for keyVal v =', InfoPoint.getValName('ipTest', 'v'))

    if True:

        print(40*'=')
        print('Creating, copying InfoPoint')
        print(40*'-')

        p1 = InfoPoint('ipTest')
        print(p1)

        p2 = InfoPoint('ipTest', pos={'x':1, 'y':1.2}, vals={'m':3, 'v':-4.567891234})
        print(p2)

        print('m =', p2.val('m'))
        print('v2 =', p2.val('v2'))  
        print('no key', p2.val())  
        print('axe(x) ', p2.pos('x'))
        print('axe(y) ', p2.pos('y'))
        print('axe(r) ', p2.pos('r'))
        print()

        pc = p2.copy()
        print('Copied ', pc)

        pc = pc.clear()
        print('Cleared ', pc)

        pc = pc.clear(vals={'m':3})
        print('Cleared ', pc)

        pc = pc.clear(vals={})
        print('Cleared ', pc)

        pc = pc.clear(vals={'r':4})
        print('Cleared ', pc)

    if False:

        print('Methods returning float')
        print(InfoPoint.floatMethodx())
        print('v.get', p2.get('v'))
        print('v.abs', p2.abs('v'))

        ab = InfoPoint.abs

        print('??? ', ab(p2, 'v'))



#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------