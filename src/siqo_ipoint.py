#==============================================================================
# Siqo class InfoPoint
#------------------------------------------------------------------------------
import copy
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

_SCHEMA   = {'ipReal'   :{'axes':_SCH_AXES.copy()
                         ,'vals':_SCH_VALS.copy()
                         }
            ,'ipTest'   :{'axes':{'x':'os X', 'y':'os Y', 'z':'os Z'}
                         ,'vals':{'a':'real Value A', 'b':'real Value B'}
                         }
            }                          # Default built-in Schema for InfoPoint

#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# InfoPoint
#------------------------------------------------------------------------------
class InfoPoint:

    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------
    _schema = copy.deepcopy(_SCHEMA)                               # Schema for InfoPoint
    logger  = SiqoLogger('InfoPoint test', level='INFO')   # Logger for InfoPoint

    #--------------------------------------------------------------------------
    # Schema methods
    #--------------------------------------------------------------------------
    @staticmethod
    def resetSchema():
        "Resets schema of InfoPoint to default values"

        InfoPoint._schema = copy.deepcopy(_SCHEMA)
        InfoPoint.logger.info("InfoPoint.resetSchema:")

    #--------------------------------------------------------------------------
    @staticmethod
    def checkSchema(ipType):
        """Checks if schema does exist for respective ipType. If schema for ipType
           does not exist, create empty as {'axes':{}, 'vals':{}}
        """

        if ipType not in InfoPoint._schema.keys():
            InfoPoint._schema[ipType] = {'axes':copy.deepcopy(_SCH_AXES), 'vals':copy.deepcopy(_SCH_VALS)}

    #--------------------------------------------------------------------------
    @staticmethod
    def clearSchema(ipType):
        "Clears schema of InfoPoint for respective ipType to {'axes':{}, 'vals':{}}"

        InfoPoint.checkSchema(ipType)
        InfoPoint._schema[ipType] = {'axes':copy.deepcopy(_SCH_AXES), 'vals':copy.deepcopy(_SCH_VALS)}
        InfoPoint.logger.info(f"InfoPoint.setAxe: clearSchema ipType '{ipType}'")

    #--------------------------------------------------------------------------
    @staticmethod
    def equalSchema(ipType, schema) -> bool:
        "Check if schema is equal to the schema of respective InfoPoint type"

        toRet = {'exists':False, 'equalAxes':False, 'equalVals':False}

        #----------------------------------------------------------------------
        # Check if ipType is defined
        #----------------------------------------------------------------------
        if ipType not in InfoPoint._schema.keys():
            InfoPoint.logger.warning(f"InfoPoint.equalSchema: ipType '{ipType}' is not defined InfoPoint type")
            return toRet

        else: toRet['exists'] = True

        #----------------------------------------------------------------------
        # Check axes
        #----------------------------------------------------------------------
        if 'axes' in schema.keys():
            if InfoPoint._schema[ipType]['axes'].keys() == schema['axes'].keys(): toRet['equalAxes'] = True

        #----------------------------------------------------------------------
        # Check vals
        #----------------------------------------------------------------------
        if 'vals' in schema.keys():
            if InfoPoint._schema[ipType]['vals'].keys() == schema['vals'].keys(): toRet['equalVals'] = True

        #----------------------------------------------------------------------
        return toRet

    #--------------------------------------------------------------------------
    @staticmethod
    def isInSchema(ipType, *, axes:list=None, vals:list=None):
        "Returns True if schema has defined all axes and vals otherwise returns False"

        if ipType not in InfoPoint._schema.keys():
            InfoPoint.logger.warning(f"InfoPoint.isInSchema: ipType '{ipType}' is not defined InfoPoint type")
            return False

        #----------------------------------------------------------------------
        # Check axes
        #----------------------------------------------------------------------
        if axes is not None:

            for axe in axes:

                if axe not in InfoPoint._schema[ipType]['axes'].keys():
                    InfoPoint.logger.warning(f"InfoPoint.isInSchema: Axe '{axe}' is not defined in schema axes {InfoPoint._schema[ipType]['axes']}")
                    return False

        #----------------------------------------------------------------------
        # Check values
        #----------------------------------------------------------------------
        if vals is not None:

            for val in vals:

                if val not in InfoPoint._schema[ipType]['vals'].keys():
                    InfoPoint.logger.warning(f"InfoPoint.isInSchema: Value '{val}' is not defined in schema values {InfoPoint._schema[ipType]['vals']}")
                    return False

        #----------------------------------------------------------------------
        return True

    #--------------------------------------------------------------------------
    @staticmethod
    def getSchema(ipType) -> dict:
        "Returns schema for respective InfoPoint type as dict {'axes':{}, 'vals':{}}"

        InfoPoint.checkSchema(ipType)
        return copy.deepcopy(InfoPoint._schema[ipType])

    #--------------------------------------------------------------------------
    @staticmethod
    def setSchema(ipType, schema):
        "Set schema for respective InfoPoint type as dict {'axes':{}, 'vals':{}}"

        InfoPoint.checkSchema(ipType)
        InfoPoint._schema[ipType] = copy.deepcopy(schema)

    #--------------------------------------------------------------------------
    # Axes methods
    #--------------------------------------------------------------------------
    @staticmethod
    def getAxes(ipType) -> dict:
        "Returns axes keys and names as dict {key: name} for respective ipType"

        InfoPoint.checkSchema(ipType)
        return copy.deepcopy(InfoPoint._schema[ipType]['axes'])

    #--------------------------------------------------------------------------
    @staticmethod
    def delAxe(ipType, key):
        "Delete axe for respective key in the dict of axes for respective ipType"

        InfoPoint.checkSchema(ipType)
        if key in InfoPoint._schema[ipType]['axes'].keys():
            InfoPoint._schema[ipType]['axes'].pop(key)

        InfoPoint.logger.debug(f"InfoPoint.delAxe: key '{key}' was deleted from axes")

    #--------------------------------------------------------------------------
    @staticmethod
    def setAxe(ipType, key, name):
        "Sets axe's key and name for respective ipType. If axe exists already, redefine name."

        InfoPoint.checkSchema(ipType)

        if (key not in InfoPoint._schema[ipType]['axes'].keys()) or (InfoPoint._schema[ipType]['axes'][key] != name):

            InfoPoint._schema[ipType]['axes'][key] = name
            InfoPoint.logger.debug(f"InfoPoint.setAxe: set key '{key}' for axe '{name}'")
            return True

        else:
            InfoPoint.logger.debug(f"InfoPoint.setAxe: axe '{name}' for key '{key}' is already defined, no change")
            return False

    #--------------------------------------------------------------------------
    @staticmethod
    def axeIdxByKey(ipType, key) -> int:
        "Returns axe's idx position in the dict of axes for respective key, othewise None"

        #----------------------------------------------------------------------
        # Check if ipType is defined
        #----------------------------------------------------------------------
        if ipType not in InfoPoint._schema.keys():
            InfoPoint.logger.warning(f"InfoPoint.axeIdxByKey: ipType '{ipType}' is not defined InfoPoint type")
            return None

        #----------------------------------------------------------------------
        # Find index of the axe's key
        #----------------------------------------------------------------------
        for i, keyAxe in enumerate(InfoPoint._schema[ipType]['axes'].keys()):
            if key==keyAxe:
                InfoPoint.logger.debug(f"InfoPoint.axeIdxByKey: Key '{key}' found in axes {InfoPoint._schema[ipType]['axes']} at index {i}")
                return i

        #----------------------------------------------------------------------
        # Key not found
        #----------------------------------------------------------------------
        InfoPoint.logger.warning(f"InfoPoint.axeIdxByKey: Key '{key}' not found in axes {InfoPoint._schema[ipType]['axes']}")
        return None

    #--------------------------------------------------------------------------
    @staticmethod
    def axeKeyByIdx(ipType, idx) -> str:
        "Returns axe's key for respective idx position in the dict of axes, othewise None"

        #----------------------------------------------------------------------
        # Check if ipType is defined
        #----------------------------------------------------------------------
        if ipType not in InfoPoint._schema.keys():
            InfoPoint.logger.warning(f"InfoPoint.axeKeyByIdx: ipType '{ipType}' is not defined InfoPoint type")
            return None

        #----------------------------------------------------------------------
        # Check if idx is not out of the range
        #----------------------------------------------------------------------
        if idx >= len(InfoPoint._schema[ipType]['axes'].keys()):
            InfoPoint.logger.warning(f"InfoPoint.axeKeyByIdx: Idx '{idx}' is out of the range in {InfoPoint._schema[ipType]['axes']}")
            return None

        #----------------------------------------------------------------------
        # Find key for index
        #----------------------------------------------------------------------
        key = list(InfoPoint._schema[ipType]['axes'].keys())[idx]
        return key

    #--------------------------------------------------------------------------
    @staticmethod
    def axeNameByKey(ipType, key) -> str:
        "Returns axe's Name for respective key, othewise None"

        #----------------------------------------------------------------------
        # Check if ipType is defined
        #----------------------------------------------------------------------
        if ipType not in InfoPoint._schema.keys():
            InfoPoint.logger.warning(f"InfoPoint.axeNameByKey: ipType '{ipType}' is not defined InfoPoint type")
            return None

        #----------------------------------------------------------------------
        # Find name of the axe's key
        #----------------------------------------------------------------------
        if key not in InfoPoint._schema[ipType]['axes'].keys():
            InfoPoint.logger.warning(f"InfoPoint.axeNameByKey: Key '{key}' not found in axes {InfoPoint._schema[ipType]['axes']}")
            return None

        else:
            return InfoPoint._schema[ipType]['axes'][key]

    #--------------------------------------------------------------------------
    @staticmethod
    def axeKeyByName(ipType, name) -> str:
        "Returns axe's key for respective Name, othewise None"

        #----------------------------------------------------------------------
        # Check if ipType is defined
        #----------------------------------------------------------------------
        if ipType not in InfoPoint._schema.keys():
            InfoPoint.logger.warning(f"InfoPoint.axeNameByKey: ipType '{ipType}' is not defined InfoPoint type")
            return None

        #----------------------------------------------------------------------
        # Find the axe's key for the axe's name
        #----------------------------------------------------------------------
        for key, axeName in InfoPoint._schema[ipType]['axes'].items():

            if axeName == name:
                InfoPoint.logger.debug(f"InfoPoint.axeKeyByName: Name '{name}' found in axes {InfoPoint._schema[ipType]['axes']} for key '{key}'")
                return key

        #----------------------------------------------------------------------
        InfoPoint.logger.warning(f"InfoPoint.axeKeyByName: Name '{name}' not found in axes {InfoPoint._schema[ipType]['axes']}")
        return None

    #--------------------------------------------------------------------------
    # Values methods
    #--------------------------------------------------------------------------
    @staticmethod
    def getVals(ipType) -> dict:
        "Returns values keys and names as dict {key: name} for respective ipType"

        InfoPoint.checkSchema(ipType)
        return copy.deepcopy(InfoPoint._schema[ipType]['vals'])

    #--------------------------------------------------------------------------
    @staticmethod
    def delVal(ipType, key):
        "Delete value for respective key in the dict of values for respective ipType"

        InfoPoint.checkSchema(ipType)
        if key in InfoPoint._schema[ipType]['vals'].keys():
            InfoPoint._schema[ipType]['vals'].pop(key)

        InfoPoint.logger.debug(f"InfoPoint.delVal: key '{key}' was deleted from values")

    #--------------------------------------------------------------------------
    @staticmethod
    def setVal(ipType, key, name):
        "Sets value key and name for respective ipType. If value exists already, redefine name."

        InfoPoint.checkSchema(ipType)

        if (key not in InfoPoint._schema[ipType]['vals'].keys()) or (InfoPoint._schema[ipType]['vals'][key] != name):

            InfoPoint._schema[ipType]['vals'][key] = name
            InfoPoint.logger.debug(f"InfoPoint.setVal: set key '{key}' for value '{name}'")
            return True

        else:
            InfoPoint.logger.debug(f"InfoPoint.setVal: value '{name}' for key '{key}' is already defined, no change")
            return False

    #--------------------------------------------------------------------------
    @staticmethod
    def valIdxByKey(ipType, key) -> int:
        "Returns value's idx position in the dict of values for respective key, othewise None"

        #----------------------------------------------------------------------
        # Check if ipType is defined
        #----------------------------------------------------------------------
        if ipType not in InfoPoint._schema.keys():
            InfoPoint.logger.warning(f"InfoPoint.valIdxByKey: ipType '{ipType}' is not defined InfoPoint type")
            return None

        #----------------------------------------------------------------------
        # Find index of the value's key
        #----------------------------------------------------------------------
        for i, keyVal in enumerate(InfoPoint._schema[ipType]['vals'].keys()):
            if key==keyVal: return i

        #----------------------------------------------------------------------
        # Key not found
        #----------------------------------------------------------------------
        InfoPoint.logger.warning(f"InfoPoint.valIdxByKey: Key '{key}' not found in valus {InfoPoint._schema[ipType]['vals']}")
        return None

    #--------------------------------------------------------------------------
    @staticmethod
    def valKeyByIdx(ipType, idx) -> str:
        "Returns value's key in the dict of values for respective idx position, othewise None"

        #----------------------------------------------------------------------
        # Check if ipType is defined
        #----------------------------------------------------------------------
        if ipType not in InfoPoint._schema.keys():
            InfoPoint.logger.warning(f"InfoPoint.valKeyByIdx: ipType '{ipType}' is not defined InfoPoint type")
            return None

        #----------------------------------------------------------------------
        # Check if idx is not out of the range
        #----------------------------------------------------------------------
        if idx >= len(InfoPoint._schema[ipType]['vals'].keys()):
            InfoPoint.logger.warning(f"InfoPoint.valKeyByIdx: Idx '{idx}' is out of the range in {InfoPoint._schema[ipType]['vals']}")
            return None

        #----------------------------------------------------------------------
        # Find key for index
        #----------------------------------------------------------------------
        key = list(InfoPoint._schema[ipType]['vals'].keys())[idx]
        return key

    #--------------------------------------------------------------------------
    @staticmethod
    def valNameByKey(ipType, key) -> str:
        "Returns value's Name for respective key, othewise None"

        #----------------------------------------------------------------------
        # Check if ipType is defined
        #----------------------------------------------------------------------
        if ipType not in InfoPoint._schema.keys():
            InfoPoint.logger.warning(f"InfoPoint.valNameByKey: ipType '{ipType}' is not defined InfoPoint type")
            return None

        #----------------------------------------------------------------------
        # Find name of the value's key
        #----------------------------------------------------------------------
        if key not in InfoPoint._schema[ipType]['vals'].keys():
            InfoPoint.logger.warning(f"InfoPoint.valNameByKey: Key '{key}' not found in valus {InfoPoint._schema[ipType]['vals']}")
            return None

        else:
            return InfoPoint._schema[ipType]['vals'][key]

    #--------------------------------------------------------------------------
    @staticmethod
    def valKeyByName(ipType, name) -> str:
        "Returns val's key for respective Name, othewise None"

        #----------------------------------------------------------------------
        # Check if ipType is defined
        #----------------------------------------------------------------------
        if ipType not in InfoPoint._schema.keys():
            InfoPoint.logger.warning(f"InfoPoint.valKeyByName: ipType '{ipType}' is not defined InfoPoint type")
            return None

        #----------------------------------------------------------------------
        # Find the val's key for the val's name
        #----------------------------------------------------------------------
        for key, valName in InfoPoint._schema[ipType]['vals'].items():

            if valName == name:
                InfoPoint.logger.debug(f"InfoPoint.valKeyByName: Name '{name}' found in axes {InfoPoint._schema[ipType]['vals']} for key '{key}'")
                return key

        #----------------------------------------------------------------------
        InfoPoint.logger.warning(f"InfoPoint.valKeyByName: Name '{name}' not found in axes {InfoPoint._schema[ipType]['vals']}")
        return None

    #--------------------------------------------------------------------------
    # Method's methods
    #--------------------------------------------------------------------------
    @staticmethod
    def mapShowMethods() -> dict:
        "Returns map of methods returning float number from keyed value"

        return {'Float value'   : InfoPoint.fValue
               ,'Absolute value': InfoPoint.abs
               ,'Real value'    : InfoPoint.real
               ,'Imag value'    : InfoPoint.imag
               ,'Phase'         : InfoPoint.phase
               }

    #--------------------------------------------------------------------------
    @staticmethod
    def mapSetMethods() -> dict:
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

        toRet._pos  = copy.deepcopy(self._pos)
        toRet._vals = copy.deepcopy(self._vals)

        return toRet

    #--------------------------------------------------------------------------
    def ipType(self):
        "Returns type of this InfoPoint"

        return self._ipType

    #==========================================================================
    # Value retrieval
    #--------------------------------------------------------------------------
    def pos(self, key:str) -> float:
        "Returns position for respective axis key"

        #----------------------------------------------------------------------
        # Key check
        #----------------------------------------------------------------------
        if key not in InfoPoint._schema[self._ipType]['axes'].keys():
            self.logger.warning(f"InfoPoint.get: Key '{key}' not found in axes {InfoPoint._schema[self._ipType]['axes']}")
            return None

        #----------------------------------------------------------------------
        # Return axe's value of this InfoPoint for respective key
        #----------------------------------------------------------------------
        return self._pos[key]

    #--------------------------------------------------------------------------
    def posName(self, key:str) -> str:
        "Returns name for respective axis key"

        #----------------------------------------------------------------------
        # Key check
        #----------------------------------------------------------------------
        if key not in InfoPoint._schema[self._ipType]['axes'].keys():
            self.logger.warning(f"InfoPoint.get: Key '{key}' not found in axes {InfoPoint._schema[self._ipType]['axes']}")
            return None

        #----------------------------------------------------------------------
        # Return axe's name of this InfoPoint for respective key
        #----------------------------------------------------------------------
        return InfoPoint._schema[self._ipType]['axes'][key]

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
            self.logger.warning(f"InfoPoint.get: Key '{key}' not found in values {InfoPoint._schema[self._ipType]['vals']}")
            return None

        #----------------------------------------------------------------------
        # Return value of this InfoPoint for respective key
        #----------------------------------------------------------------------
        return self._vals[key]

    #--------------------------------------------------------------------------
    def valName(self, key:str=None) -> str:
        "Returns value's name of this InfoPoint for respective key"

        #----------------------------------------------------------------------
        # Return this InfoPoint for key is None
        #----------------------------------------------------------------------
        if key is None: return self

        #----------------------------------------------------------------------
        # Key check
        #----------------------------------------------------------------------
        if key not in InfoPoint._schema[self._ipType]['vals'].keys():
            self.logger.warning(f"InfoPoint.get: Key '{key}' not found in values {InfoPoint._schema[self._ipType]['vals']}")
            return None

        #----------------------------------------------------------------------
        # Return value's name of this InfoPoint for respective key
        #----------------------------------------------------------------------
        return InfoPoint._schema[self._ipType]['vals'][key]

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
                self.logger.error(f"InfoPoint.set: Position '{self._posStr()}' is not compatible with schema axes {InfoPoint._schema[self._ipType]['axes']}")
                return False

        #----------------------------------------------------------------------
        # Set values of this InfoPoint
        #----------------------------------------------------------------------
        if vals is not None:

            for key, val in vals.items():

                if key in InfoPoint._schema[self._ipType]['vals'].keys():
                    self._vals[key] = val

                else:
                    self.logger.warning(f"InfoPoint.set: Key '{key}' not found in values {InfoPoint._schema[self._ipType]['vals']}")
                    return False

        #----------------------------------------------------------------------
        #self.logger.debug(f"InfoPoint.set: @{id(self)} pos: {pos}->{self._posStr()}, vals: {vals}->{self._valStr()}")
        return True

    #--------------------------------------------------------------------------
    def clear(self, *, vals:dict=None):
        "Sets all values to default values"

        if (vals is not None) and (len(vals) > 0):

            for key, val in vals.items():

                if key in InfoPoint._schema[self._ipType]['vals'].keys():
                    self._vals[key] = val

                else:
                    self.logger.warning(f"InfoPoint.set: Key '{key}' not found in values {InfoPoint._schema[self._ipType]['vals']}")
                    return False

        else: self._vals = {}

        self.logger.debug(f"InfoPoint.clear: with vals {vals}")
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
            self.logger.error(f"InfoPoints have different number of coordinates!")
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

        print('idx for keyAxe x =', InfoPoint.axeIdxByKey('ipTest', 'x'))
        print('key for keyAxe 0 =', InfoPoint.axeKeyByIdx('ipTest', 0 ))
        print('idx for keyAxe y =', InfoPoint.axeIdxByKey('ipTest', 'y'))
        print('key for keyAxe 1 =', InfoPoint.axeKeyByIdx('ipTest', 1 ))
        print('idx for keyAxe z =', InfoPoint.axeIdxByKey('ipTest', 'z'))
        print('key for keyAxe 2 =', InfoPoint.axeKeyByIdx('ipTest', 2 ))

        print('idx for keyVal x =', InfoPoint.valIdxByKey('ipTest', 'x'))
        print('key for keyVal 0 =', InfoPoint.valKeyByIdx('ipTest', 0))
        print('idx for keyVal v =', InfoPoint.valIdxByKey('ipTest', 'v'))
        print('key for keyVal 1 =', InfoPoint.valKeyByIdx('ipTest', 1))
        print('key for keyVal 2 =', InfoPoint.valKeyByIdx('ipTest', 2))

        print('name for keyAxe x =', InfoPoint.axeNameByKey('ipTest', 'x'))
        print('name for keyAxe y =', InfoPoint.axeNameByKey('ipTest', 'y'))
        print('name for keyAxe z =', InfoPoint.axeNameByKey('ipTest', 'z'))
        print('name for keyVal x =', InfoPoint.valNameByKey('ipTest', 'x'))
        print('name for keyVal v =', InfoPoint.valNameByKey('ipTest', 'v'))

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

        pc = copy.deepcopy(p2)
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