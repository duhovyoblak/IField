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
_VER      = '3.2.2'

_IND      = '|  '                      # Info indentation
_F_SCHEMA = 1                          # Format for ipType
_F_TOTAL  = 6                          # Total number of digits in float number
_F_DECIM  = 3                          # Number of digits after decimal point in float number
_F_POS    = 4                          # Number of digits for position coordinates

_SCH_AXES = {}                         # Default axes for InfoPoint schema
_SCH_VALS = {}                         # Default values for InfoPoint schema

_SCHEMA   = {'ipReal'   :{'axes':_SCH_AXES.copy()
                         ,'vals':_SCH_VALS.copy()
                         }
            }                          # Default built-in Schema for InfoPoint

_CIRCLE      = 2*cmath.pi              # Full circle in radians
_PHASE_START = cmath.pi/2              # Start phase in radians
_CLOSE_ZERO  = 1e-12                   # Close to zero threshold

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
    _schema = copy.deepcopy(_SCHEMA)           # Schema for InfoPoint
    logger  = SiqoLogger(name='InfoPoint')     # Logger for InfoPoint

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
        InfoPoint.logger.info(f"InfoPoint.clearSchema: clearSchema ipType '{ipType}'")

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
    def getSchemaAxes(ipType) -> dict:
        "Returns axes keys and names as dict {key: name} for respective ipType"

        InfoPoint.checkSchema(ipType)
        return copy.deepcopy(InfoPoint._schema[ipType]['axes'])

    #--------------------------------------------------------------------------
    @staticmethod
    def delSchemaAxe(ipType, key):
        "Delete axe for respective key in the dict of axes for respective ipType"

        InfoPoint.checkSchema(ipType)
        if key in InfoPoint._schema[ipType]['axes'].keys():
            InfoPoint._schema[ipType]['axes'].pop(key)

        InfoPoint.logger.debug(f"InfoPoint.delSchemaAxe: key '{key}' was deleted from axes")

    #--------------------------------------------------------------------------
    @staticmethod
    def setSchemaAxe(ipType, key, name):
        "Sets axe's key and name for respective ipType. If axe exists already, redefine name."

        InfoPoint.checkSchema(ipType)

        if (key not in InfoPoint._schema[ipType]['axes'].keys()) or (InfoPoint._schema[ipType]['axes'][key] != name):

            InfoPoint._schema[ipType]['axes'][key] = name
            InfoPoint.logger.debug(f"InfoPoint.setSchemaAxe: set key '{key}' for axe '{name}'")
            return True

        else:
            InfoPoint.logger.debug(f"InfoPoint.setSchemaAxe: axe '{name}' for key '{key}' is already defined, no change")
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
    def getSchemaVals(ipType) -> dict:
        "Returns values keys and names as dict {key: name} for respective ipType"

        InfoPoint.checkSchema(ipType)
        return copy.deepcopy(InfoPoint._schema[ipType]['vals'])

    #--------------------------------------------------------------------------
    @staticmethod
    def delSchemaVal(ipType, key):
        "Delete value for respective key in the dict of values for respective ipType"

        InfoPoint.checkSchema(ipType)
        if key in InfoPoint._schema[ipType]['vals'].keys():
            InfoPoint._schema[ipType]['vals'].pop(key)

        InfoPoint.logger.debug(f"InfoPoint.delSchemaVal: key '{key}' was deleted from values")

    #--------------------------------------------------------------------------
    @staticmethod
    def setSchemaVal(ipType, key, name):
        "Sets value key and name for respective ipType. If value exists already, redefine name."

        InfoPoint.checkSchema(ipType)

        if (key not in InfoPoint._schema[ipType]['vals'].keys()) or (InfoPoint._schema[ipType]['vals'][key] != name):

            InfoPoint._schema[ipType]['vals'][key] = name
            InfoPoint.logger.debug(f"InfoPoint.setSchemaVal: set key '{key}' for value '{name}'")
            return True

        else:
            InfoPoint.logger.debug(f"InfoPoint.setSchemaVal: value '{name}' for key '{key}' is already defined, no change")
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
                InfoPoint.logger.debug(f"InfoPoint.valKeyByName: Name '{name}' found in values {InfoPoint._schema[ipType]['vals']} for key '{key}'")
                return key

        #----------------------------------------------------------------------
        InfoPoint.logger.warning(f"InfoPoint.valKeyByName: Name '{name}' not found in values {InfoPoint._schema[ipType]['vals']}")
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

               ,'Complex value' : InfoPoint.complex
               }

    #--------------------------------------------------------------------------
    @staticmethod
    def mapMethods() -> dict:
        "Returns map of methods for one InfoPoint setting keyed value to function value for respective parameters"

        return {'<Point Methods>'        : {'pointMethod':InfoPoint.nullMethod,    'params':{                                                           }, 'visible':True}
               ,'Real constant'          : {'pointMethod':InfoPoint.fltConst,      'params':{'const'  :0                                                }, 'visible':True, 'type':'ask'}
               ,'Random uniform'         : {'pointMethod':InfoPoint.fltRandUni,    'params':{'min'    :0,   'max'   :1                                  }, 'visible':True, 'type':'ask'}
               ,'Random bit'             : {'pointMethod':InfoPoint.fltRandBit,    'params':{'prob1'  :0.1                                              }, 'visible':True, 'type':'ask'}
               ,'Comp constant (re/im)'  : {'pointMethod':InfoPoint.cmpConstR,     'params':{'real'   :0,   'imag'  :0                                  }, 'visible':True, 'type':'ask'}
               ,'Comp constant (abs/phs)': {'pointMethod':InfoPoint.cmpConstP,     'params':{'abs'    :0,   'phase' :0                                  }, 'visible':True, 'type':'ask'}
               ,'Comp random   (re/im)'  : {'pointMethod':InfoPoint.cmpRandUniR,   'params':{'reMin'  :0,   'reMax' :1, 'imMin'   :0, 'imMax'   :1      }, 'visible':True, 'type':'ask'}
               ,'Comp random   (abs/phs)': {'pointMethod':InfoPoint.cmpRandUniP,   'params':{'absMin' :0,   'absMax':1, 'phaseMin':0, 'phaseMax':_CIRCLE}, 'visible':True, 'type':'ask'}
               ,'Comp discrete phase'    : {'pointMethod':InfoPoint.cmpDiscPhases, 'params':{'probAbs':0.5, 'phases':2                                  }, 'visible':True, 'type':'ask'}
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
            if i>0: toRet += ', '
            toRet += f"{axeName}={self._pos.get(axe, 0):{_F_POS}.1f}"
            i += 1

        toRet += ']'
        return toRet

    #--------------------------------------------------------------------------
    def _valsStr(self):
        "Creates string representation of the values of this InfoPoint"

        toRet = '['

        i = 0
        for val, valName in InfoPoint._schema[self._ipType]['vals'].items():
            if i>0: toRet += ', '
            toRet += f"{valName}={self._format(self._vals.get(val, None))}"
            i += 1

        toRet += ']'
        return toRet

    #--------------------------------------------------------------------------
    def get(self, *, pos:bool=True, vals:bool=True):
        "Get position and values of this InfoPoint"

        toRet = {}
        if pos : toRet['pos' ] = self._pos.copy()
        if vals: toRet['vals'] = self._vals.copy()

        return toRet

    #--------------------------------------------------------------------------
    def set(self, *, pos=None, vals=None):
        "Set position and values of this InfoPoint"

        #----------------------------------------------------------------------
        # Set position
        #----------------------------------------------------------------------
        if pos is not None:

            if type(pos) in (dict, tuple, list):

                #--------------------------------------------------------------
                # Ak pos je dict
                #--------------------------------------------------------------
                if type(pos) == dict:
                    self._pos.update(pos)

                #--------------------------------------------------------------
                # Ak pos je list alebo tuple, zmapujem osami
                #--------------------------------------------------------------
                else:
                    axeKeys = list(InfoPoint._schema[self._ipType]['axes'].keys())
                    for i, p in enumerate(pos):
                        if i < len(axeKeys):
                            self._pos[axeKeys[i]] = p

        #----------------------------------------------------------------------
        # Set values
        #----------------------------------------------------------------------
        if vals is not None:

            if type(vals) in (dict, tuple, list):

                #--------------------------------------------------------------
                # Ak vals je dict
                #--------------------------------------------------------------
                if type(vals) == dict:
                    self._vals.update(vals)

                #--------------------------------------------------------------
                # Ak vals je list alebo tuple, zmapujem s hodnotami
                #--------------------------------------------------------------
                else:
                    valKeys = list(InfoPoint._schema[self._ipType]['vals'].keys())
                    for i, v in enumerate(vals):
                        if i < len(valKeys):
                            self._vals[valKeys[i]] = v

    #--------------------------------------------------------------------------
    def pos(self, axeKey=None):
        "Get position value on respective axe or whole position"

        if axeKey is None:
            return self._pos.copy()

        else:
            return self._pos.get(axeKey, None)

    #--------------------------------------------------------------------------
    def val(self, valKey=None):
        "Get value for respective key or whole values"

        if valKey is None:
            return self._vals.copy()

        else:
            return self._vals.get(valKey, None)

    #--------------------------------------------------------------------------
    def info(self, indent=0, full=False):
        "Creates info about this InfoPoint"

        dat = {}
        msg = ''

        #----------------------------------------------------------------------
        # info o cele strukture
        #----------------------------------------------------------------------
        dat['type'  ] = self._ipType
        dat['pos'   ] = self._posStr()
        dat['vals'  ] = self._valsStr()

        if indent == 0: msg = f"{indent*_IND}{60*'='}\n"

        for key, val in dat.items():
            msg += f"{indent*_IND}{key:<15}: {val}\n"

        return {'res':'OK', 'dat':dat, 'msg':msg}

    #==========================================================================
    # Methods for manipulation
    #--------------------------------------------------------------------------

    #==========================================================================
    # Show methods - Returns float value (or representation as float) from InfoPoint values
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    @staticmethod
    def fValue(val):
        "Returns value as float"

        if val is None: return 0.0
        return float(val) if val else 0.0

    #--------------------------------------------------------------------------
    @staticmethod
    def abs(val):
        "Returns absolute value"

        if val is None: return 0.0
        return float(abs(val)) if val else 0.0

    #--------------------------------------------------------------------------
    @staticmethod
    def real(val):
        "Returns real part of complex value or value as float"

        if val is None: return 0.0
        if type(val) == complex: return float(val.real)
        return float(val) if val else 0.0

    #--------------------------------------------------------------------------
    @staticmethod
    def imag(val):
        "Returns imaginary part of complex value"

        if val is None: return 0.0
        if type(val) == complex: return float(val.imag)
        return 0.0

    #--------------------------------------------------------------------------
    @staticmethod
    def phase(val):
        "Returns phase of complex value"

        if val is None: return 0.0
        if type(val) == complex: return cmath.phase(val)
        return 0.0

    #--------------------------------------------------------------------------
    @staticmethod
    def complex(val):
        "Returns value as complex"

        if val is None: return complex(0, 0)
        return complex(val) if val else complex(0, 0)

    #==========================================================================
    # Point methods - apply to one point
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    @staticmethod
    def nullMethod(infoPoint, valueKey:str, params:dict):
        "Null method for testing"

        return 0

    #--------------------------------------------------------------------------
    @staticmethod
    def fltConst(infoPoint, valueKey:str, params:dict):
        "Set constant float value"

        const = params.get('const', 0)
        infoPoint.set(vals={valueKey: const})
        return 1

    #--------------------------------------------------------------------------
    @staticmethod
    def fltRandUni(infoPoint, valueKey:str, params:dict):
        "Set random uniform float value in range <min, max>"

        minVal = params.get('min', 0)
        maxVal = params.get('max', 1)

        val = minVal + (maxVal - minVal) * rnd.random()

        infoPoint.set(vals={valueKey: val})
        return 1

    #--------------------------------------------------------------------------
    @staticmethod
    def fltRandBit(infoPoint, valueKey:str, params:dict):
        "Set random bit value (1 or 0) with probability prob1 for 1"

        prob1 = params.get('prob1', 0.5)
        val = 1 if rnd.random() < prob1 else 0

        infoPoint.set(vals={valueKey: val})
        return 1

    #--------------------------------------------------------------------------
    @staticmethod
    def cmpConstR(infoPoint, valueKey:str, params:dict):
        "Set constant complex value given by real and imaginary parts"

        real = params.get('real', 0)
        imag = params.get('imag', 0)
        val  = complex(real, imag)

        infoPoint.set(vals={valueKey: val})
        return 1

    #--------------------------------------------------------------------------
    @staticmethod
    def cmpConstP(infoPoint, valueKey:str, params:dict):
        "Set constant complex value given by absolute value and phase"

        abs_val = params.get('abs' , 0)
        phase   = params.get('phase', 0)
        val     = abs_val * cmath.exp(complex(0, phase))

        infoPoint.set(vals={valueKey: val})
        return 1

    #--------------------------------------------------------------------------
    @staticmethod
    def cmpRandUniR(infoPoint, valueKey:str, params:dict):
        "Set random complex value with uniform real and imaginary parts in given ranges"

        reMin  = params.get('reMin' , 0)
        reMax  = params.get('reMax' , 1)
        imMin  = params.get('imMin' , 0)
        imMax  = params.get('imMax' , 1)

        real = reMin + (reMax - reMin) * rnd.random()
        imag = imMin + (imMax - imMin) * rnd.random()
        val  = complex(real, imag)

        infoPoint.set(vals={valueKey: val})
        return 1

    #--------------------------------------------------------------------------
    @staticmethod
    def cmpRandUniP(infoPoint, valueKey:str, params:dict):
        "Set random complex value with uniform absolute value and phase in given ranges"

        absMin   = params.get('absMin'  , 0)
        absMax   = params.get('absMax'  , 1)
        phaseMin = params.get('phaseMin', 0)
        phaseMax = params.get('phaseMax', _CIRCLE)

        abs_val = absMin + (absMax - absMin) * rnd.random()
        phase   = phaseMin + (phaseMax - phaseMin) * rnd.random()
        val     = abs_val * cmath.exp(complex(0, phase))

        infoPoint.set(vals={valueKey: val})
        return 1

    #--------------------------------------------------------------------------
    @staticmethod
    def cmpDiscPhases(infoPoint, valueKey:str, params:dict):
        "Set random complex value with discrete uniform phases"

        probAbs = params.get('probAbs', 0.5)
        phases  = params.get('phases', 2)

        abs_val = 1 if rnd.random() < probAbs else 0
        phase_idx = rnd.randint(0, phases - 1)
        phase = phase_idx * _CIRCLE / phases
        val = abs_val * cmath.exp(complex(0, phase))

        infoPoint.set(vals={valueKey: val})
        return 1

#------------------------------------------------------------------------------
print(f"InfoPoint ver {_VER}")

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
