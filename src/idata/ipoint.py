#==============================================================================
# Siqo class InfoPoint
#------------------------------------------------------------------------------
import copy
import math
import cmath
import random                 as rnd

from   .                      import logger

#==============================================================================
# Module's constants
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
# Module's variables
#------------------------------------------------------------------------------

#==============================================================================
# InfoPoint
#------------------------------------------------------------------------------
class InfoPoint:
    """Define InfoPoint as a dynamic data structure in the space defined by schema.
       Schema defines which axes and vals are defined for respective InfoPoint type <ipType>.
       Schema is one static structure for all type of InfoPoints and is defined as dict {ipType: {'axes':{key:name}, 'vals':{key:name}}}.
       Methods for manipulation of InfoPoint values are defined as static methods and can be mapped to method names in mapSetMethods() static method.
    """

    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------
    _schema = copy.deepcopy(_SCHEMA)  # Static schema for all InfoPoint types

    #--------------------------------------------------------------------------
    # Schema methods
    #--------------------------------------------------------------------------
    @staticmethod
    def resetSchema():
        """Resets schema to default values.
           Default schema is defined as dict {ipType: {'axes':{}, 'vals':{}}} where ipType is defined in _SCHEMA constant.
           This method has impact on all InfoPoints because schema is static variable for all type of InfoPoints.
        """

        InfoPoint._schema = copy.deepcopy(_SCHEMA)
        logger.info("InfoPoint.resetSchema:")

    #--------------------------------------------------------------------------
    @staticmethod
    def checkSchema(ipType):
        """Checks if schema is defined for respective ipType.
           If schema for ipType does not exist, create empty one as ipType:{'axes':{}, 'vals':{}}
        """

        if ipType not in InfoPoint._schema.keys():
            InfoPoint._schema[ipType] = {'axes':copy.deepcopy(_SCH_AXES), 'vals':copy.deepcopy(_SCH_VALS)}

    #--------------------------------------------------------------------------
    @staticmethod
    def clearSchema(ipType):
        """Clears schema of InfoPoint for respective ipType to empty one as ipType:{'axes':{}, 'vals':{}}
           This method has no impact on other InfoPoint types.
        """

        InfoPoint.checkSchema(ipType)
        InfoPoint._schema[ipType] = {'axes':copy.deepcopy(_SCH_AXES), 'vals':copy.deepcopy(_SCH_VALS)}
        logger.info(f"InfoPoint.clearSchema: clearSchema ipType '{ipType}'")

    #--------------------------------------------------------------------------
    @staticmethod
    def equalSchema(ipType, testSchema) -> dict:
        """Check if schema definition for ipType is equal to the testSchema as dict {ipType: {'axes':{}, 'vals':{}}}.
           Returns dict with keys 'exists', 'equalAxes', 'equalVals' and boolean values for respective checks.
        """

        toRet = {'exists':False, 'equalAxes':False, 'equalVals':False}

        #----------------------------------------------------------------------
        # Check if ipType is defined
        #----------------------------------------------------------------------
        if ipType not in InfoPoint._schema.keys():
            logger.warning(f"InfoPoint.equalSchema: ipType '{ipType}' is not defined InfoPoint type")
            return toRet

        else: toRet['exists'] = True

        #----------------------------------------------------------------------
        # Check axes
        #----------------------------------------------------------------------
        if 'axes' in testSchema.keys():
            if InfoPoint._schema[ipType]['axes'].keys() == testSchema['axes'].keys(): toRet['equalAxes'] = True

        #----------------------------------------------------------------------
        # Check vals
        #----------------------------------------------------------------------
        if 'vals' in testSchema.keys():
            if InfoPoint._schema[ipType]['vals'].keys() == testSchema['vals'].keys(): toRet['equalVals'] = True

        #----------------------------------------------------------------------
        return toRet

    #--------------------------------------------------------------------------
    @staticmethod
    def isInSchema(ipType, *, axeKeys:list=None, valKeys:list=None) -> bool:
        """Returns True if schema has defined all provided axe keys and val keys in respective lists otherwise returns False
        """

        if ipType not in InfoPoint._schema.keys():
            logger.warning(f"InfoPoint.isInSchema: ipType '{ipType}' is not defined InfoPoint type")
            return False

        #----------------------------------------------------------------------
        # Check axes
        #----------------------------------------------------------------------
        if axeKeys is not None:

            for axe in axeKeys:

                if axe not in InfoPoint._schema[ipType]['axes'].keys():
                    logger.warning(f"InfoPoint.isInSchema: Axe '{axe}' is not defined in schema axes {InfoPoint._schema[ipType]['axes']}")
                    return False

        #----------------------------------------------------------------------
        # Check values
        #----------------------------------------------------------------------
        if valKeys is not None:

            for val in valKeys:

                if val not in InfoPoint._schema[ipType]['vals'].keys():
                    logger.warning(f"InfoPoint.isInSchema: Value '{val}' is not defined in schema values {InfoPoint._schema[ipType]['vals']}")
                    return False

        #----------------------------------------------------------------------
        return True

    #--------------------------------------------------------------------------
    @staticmethod
    def getSchema(ipType) -> dict:
        """Returns copy of schema for respective InfoPoint type as dict {'axes':{}, 'vals':{}}
           If ipType is not defined in the schema yet, first create empty schema for this ipType.
        """

        InfoPoint.checkSchema(ipType)
        return copy.deepcopy(InfoPoint._schema[ipType])

    #--------------------------------------------------------------------------
    @staticmethod
    def setSchema(ipType, schema):
        """Set schema for respective InfoPoint type as dict {'axes':{}, 'vals':{}}
           If ipType is not defined in the schema yet, first create empty schema for this ipType.
           This method has no impact on InfoPoints of other ipTypes.
        """

        InfoPoint.checkSchema(ipType)
        InfoPoint._schema[ipType] = copy.deepcopy(schema)

    #--------------------------------------------------------------------------
    # Axes methods
    #--------------------------------------------------------------------------
    @staticmethod
    def getSchemaAxes(ipType) -> dict:
        """Returns axes keys and theirnames as dict {key: name} for respective ipType.
           If ipType is not defined in the schema yet, first create empty schema for this ipType.
        """

        InfoPoint.checkSchema(ipType)
        return copy.deepcopy(InfoPoint._schema[ipType]['axes'])

    #--------------------------------------------------------------------------
    @staticmethod
    def delSchemaAxe(ipType, key):
        """Delete an axe for respective key from the schema for respective ipType.
           If ipType is not defined in the schema yet, first create empty schema for this ipType.
           If key is not defined in the schema for this ipType, do nothing.
           This method has no impact on InfoPoints of other ipTypes.
        """

        InfoPoint.checkSchema(ipType)
        if key in InfoPoint._schema[ipType]['axes'].keys():
            InfoPoint._schema[ipType]['axes'].pop(key)

        logger.debug(f"InfoPoint.delSchemaAxe: key '{key}' was deleted from axes")

    #--------------------------------------------------------------------------
    @staticmethod
    def setSchemaAxe(ipType, key, name):
        """Sets axe's key and name for respective ipType.
           If ipType is not defined in the schema yet, first create empty schema for this ipType.
           If axe exists in the schema already, redefine name.
           This method has no impact on InfoPoints of other ipTypes.
        """

        InfoPoint.checkSchema(ipType)

        if (key not in InfoPoint._schema[ipType]['axes'].keys()) or (InfoPoint._schema[ipType]['axes'][key] != name):

            InfoPoint._schema[ipType]['axes'][key] = name
            logger.debug(f"InfoPoint.setSchemaAxe: set key '{key}' for axe '{name}'")
            return True

        else:
            logger.debug(f"InfoPoint.setSchemaAxe: axe '{name}' for key '{key}' is already defined, no change")
            return False

    #--------------------------------------------------------------------------
    @staticmethod
    def axeIdxByKey(ipType, key) -> int|None:
        """Returns axe's idx position in the dict of axes for respective key for respective ipType.
           If ipType is not defined in the schema, return None.
           If key is not defined in the schema for this ipType, return None.
        """

        #----------------------------------------------------------------------
        # Check if ipType is defined
        #----------------------------------------------------------------------
        if ipType not in InfoPoint._schema.keys():
            logger.warning(f"InfoPoint.axeIdxByKey: ipType '{ipType}' is not defined InfoPoint type")
            return None

        #----------------------------------------------------------------------
        # Find index of the axe's key
        #----------------------------------------------------------------------
        for i, keyAxe in enumerate(InfoPoint._schema[ipType]['axes'].keys()):
            if key==keyAxe:
                logger.debug(f"InfoPoint.axeIdxByKey: Key '{key}' found in axes {InfoPoint._schema[ipType]['axes']} at index {i}")
                return i

        #----------------------------------------------------------------------
        # Key not found
        #----------------------------------------------------------------------
        logger.warning(f"InfoPoint.axeIdxByKey: Key '{key}' not found in axes {InfoPoint._schema[ipType]['axes']}")
        return None

    #--------------------------------------------------------------------------
    @staticmethod
    def axeKeyByIdx(ipType, idx) -> str|None:
        """Returns axe's key for respective idx position in the dict of axes for respective ipType.
           If ipType is not defined in the schema, return None.
           If idx is out of the range of axes for this ipType, return None.
        """

        #----------------------------------------------------------------------
        # Check if ipType is defined
        #----------------------------------------------------------------------
        if ipType not in InfoPoint._schema.keys():
            logger.warning(f"InfoPoint.axeKeyByIdx: ipType '{ipType}' is not defined InfoPoint type")
            return None

        #----------------------------------------------------------------------
        # Check if idx is not out of the range
        #----------------------------------------------------------------------
        if idx >= len(InfoPoint._schema[ipType]['axes'].keys()):
            logger.warning(f"InfoPoint.axeKeyByIdx: Idx '{idx}' is out of the range in {InfoPoint._schema[ipType]['axes']}")
            return None

        #----------------------------------------------------------------------
        # Find key for index
        #----------------------------------------------------------------------
        key = list(InfoPoint._schema[ipType]['axes'].keys())[idx]
        return key

    #--------------------------------------------------------------------------
    @staticmethod
    def axeNameByKey(ipType, key) -> str|None:
        """Returns axe's Name for respective key for respective ipType
           If ipType is not defined in the schema, return None.
           If key is not defined in the schema for this ipType, return None.
        """

        #----------------------------------------------------------------------
        # Check if ipType is defined
        #----------------------------------------------------------------------
        if ipType not in InfoPoint._schema.keys():
            logger.warning(f"InfoPoint.axeNameByKey: ipType '{ipType}' is not defined InfoPoint type")
            return None

        #----------------------------------------------------------------------
        # Find name of the axe's key
        #----------------------------------------------------------------------
        if key not in InfoPoint._schema[ipType]['axes'].keys():
            logger.warning(f"InfoPoint.axeNameByKey: Key '{key}' not found in axes {InfoPoint._schema[ipType]['axes']}")
            return None

        else:
            return InfoPoint._schema[ipType]['axes'][key]

    #--------------------------------------------------------------------------
    @staticmethod
    def axeKeyByName(ipType, name) -> str|None:
        """Returns axe's key for respective Name for respective ipType
           If ipType is not defined in the schema, return None.
           If name is not defined in the schema for this ipType, return None.
        """

        #----------------------------------------------------------------------
        # Check if ipType is defined
        #----------------------------------------------------------------------
        if ipType not in InfoPoint._schema.keys():
            logger.warning(f"InfoPoint.axeNameByKey: ipType '{ipType}' is not defined InfoPoint type")
            return None

        #----------------------------------------------------------------------
        # Find the axe's key for the axe's name
        #----------------------------------------------------------------------
        for key, axeName in InfoPoint._schema[ipType]['axes'].items():

            if axeName == name:
                logger.debug(f"InfoPoint.axeKeyByName: Name '{name}' found in axes {InfoPoint._schema[ipType]['axes']} for key '{key}'")
                return key

        #----------------------------------------------------------------------
        logger.warning(f"InfoPoint.axeKeyByName: Name '{name}' not found in axes {InfoPoint._schema[ipType]['axes']}")
        return None

    #--------------------------------------------------------------------------
    # Values methods
    #--------------------------------------------------------------------------
    @staticmethod
    def getSchemaVals(ipType) -> dict:
        """Returns values keys and names as dict {key: name} for respective ipType.
           If ipType is not defined in the schema yet, first create empty schema for this ipType.
        """

        InfoPoint.checkSchema(ipType)
        return copy.deepcopy(InfoPoint._schema[ipType]['vals'])

    #--------------------------------------------------------------------------
    @staticmethod
    def delSchemaVal(ipType, key):
        """Delete value for respective key from the schema for respective ipType.
           If ipType is not defined in the schema, first create empty schema for this ipType.
           If key is not defined in the schema for this ipType, do nothing.
           This method has no impact on InfoPoints of other ipTypes.
        """

        InfoPoint.checkSchema(ipType)
        if key in InfoPoint._schema[ipType]['vals'].keys():
            InfoPoint._schema[ipType]['vals'].pop(key)

        logger.debug(f"InfoPoint.delSchemaVal: key '{key}' was deleted from values")

    #--------------------------------------------------------------------------
    @staticmethod
    def setSchemaVal(ipType, key, name):
        """Sets value key and name for respective ipType.
           If ipType is not defined in the schema, first create empty schema for this ipType.
           If value exists already, redefine name.
           This method has no impact on InfoPoints of other ipTypes.
        """

        InfoPoint.checkSchema(ipType)

        if (key not in InfoPoint._schema[ipType]['vals'].keys()) or (InfoPoint._schema[ipType]['vals'][key] != name):

            InfoPoint._schema[ipType]['vals'][key] = name
            logger.debug(f"InfoPoint.setSchemaVal: set key '{key}' for value '{name}'")
            return True

        else:
            logger.debug(f"InfoPoint.setSchemaVal: value '{name}' for key '{key}' is already defined, no change")
            return False

    #--------------------------------------------------------------------------
    @staticmethod
    def valIdxByKey(ipType, key) -> int|None:
        """Returns value's idx position in the dict of values for respective key for respective ipType.
           If ipType is not defined in the schema, return None.
           If key is not defined in the schema for this ipType, return None.
        """

        #----------------------------------------------------------------------
        # Check if ipType is defined
        #----------------------------------------------------------------------
        if ipType not in InfoPoint._schema.keys():
            logger.warning(f"InfoPoint.valIdxByKey: ipType '{ipType}' is not defined InfoPoint type")
            return None

        #----------------------------------------------------------------------
        # Find index of the value's key
        #----------------------------------------------------------------------
        for i, keyVal in enumerate(InfoPoint._schema[ipType]['vals'].keys()):
            if key==keyVal: return i

        #----------------------------------------------------------------------
        # Key not found
        #----------------------------------------------------------------------
        logger.warning(f"InfoPoint.valIdxByKey: Key '{key}' not found in valus {InfoPoint._schema[ipType]['vals']}")
        return None

    #--------------------------------------------------------------------------
    @staticmethod
    def valKeyByIdx(ipType, idx) -> str|None:
        """Returns value's key in the dict of values for respective idx position for respective ipType.
           If ipType is not defined in the schema, return None.
           If idx is not in the range, return None.
        """

        #----------------------------------------------------------------------
        # Check if ipType is defined
        #----------------------------------------------------------------------
        if ipType not in InfoPoint._schema.keys():
            logger.warning(f"InfoPoint.valKeyByIdx: ipType '{ipType}' is not defined InfoPoint type")
            return None

        #----------------------------------------------------------------------
        # Check if idx is not out of the range
        #----------------------------------------------------------------------
        if idx >= len(InfoPoint._schema[ipType]['vals'].keys()):
            logger.warning(f"InfoPoint.valKeyByIdx: Idx '{idx}' is out of the range in {InfoPoint._schema[ipType]['vals']}")
            return None

        #----------------------------------------------------------------------
        # Find key for index
        #----------------------------------------------------------------------
        key = list(InfoPoint._schema[ipType]['vals'].keys())[idx]
        return key

    #--------------------------------------------------------------------------
    @staticmethod
    def valNameByKey(ipType, key) -> str|None:
        """Returns value's Name for respective key for respective ipType.
           If ipType is not defined in the schema, return None.
           If key is not defined in the schema for this ipType, return None.
        """

        #----------------------------------------------------------------------
        # Check if ipType is defined
        #----------------------------------------------------------------------
        if ipType not in InfoPoint._schema.keys():
            logger.warning(f"InfoPoint.valNameByKey: ipType '{ipType}' is not defined InfoPoint type")
            return None

        #----------------------------------------------------------------------
        # Find name of the value's key
        #----------------------------------------------------------------------
        if key not in InfoPoint._schema[ipType]['vals'].keys():
            logger.warning(f"InfoPoint.valNameByKey: Key '{key}' not found in valus {InfoPoint._schema[ipType]['vals']}")
            return None

        else:
            return InfoPoint._schema[ipType]['vals'][key]

    #--------------------------------------------------------------------------
    @staticmethod
    def valKeyByName(ipType, name) -> str|None:
        """Returns val's key for respective Name for respective ipType.
           If ipType is not defined in the schema, return None.
           If name is not defined in the schema for this ipType, return None.
        """

        #----------------------------------------------------------------------
        # Check if ipType is defined
        #----------------------------------------------------------------------
        if ipType not in InfoPoint._schema.keys():
            logger.warning(f"InfoPoint.valKeyByName: ipType '{ipType}' is not defined InfoPoint type")
            return None

        #----------------------------------------------------------------------
        # Find the val's key for the val's name
        #----------------------------------------------------------------------
        for key, valName in InfoPoint._schema[ipType]['vals'].items():

            if valName == name:
                logger.debug(f"InfoPoint.valKeyByName: Name '{name}' found in values {InfoPoint._schema[ipType]['vals']} for key '{key}'")
                return key

        #----------------------------------------------------------------------
        logger.warning(f"InfoPoint.valKeyByName: Name '{name}' not found in values {InfoPoint._schema[ipType]['vals']}")
        return None

    #--------------------------------------------------------------------------
    # InfoPoint's methods
    #--------------------------------------------------------------------------
    @staticmethod
    def mapShowMethods() -> dict:
        """Returns map of methods returning float number from keyed value mainly used to show the value of the point.
           Returns dict of {showMethodName: callable_function}.
        """

        return {'Float value'   : InfoPoint.fValue
               ,'Absolute value': InfoPoint.abs
               ,'Real value'    : InfoPoint.real
               ,'Imag value'    : InfoPoint.imag
               ,'Phase'         : InfoPoint.phase

               ,'Complex value' : InfoPoint.complex
               }

    #--------------------------------------------------------------------------
    @staticmethod
    def mapSetMethods() -> dict:
        """Returns map of methods for one InfoPoint setting keyed value to function value for respective parameters.

        Structure:
            {pointMethodName: {
                              'pointMethod': callable_function,   -- method to be applied to each point in the active subdata
                              'params'     : {paramName: defaultValue},
                              'visible'    : False/True,
                              'paramAsk'   : False/True
                              'outType'    : 'valKey' / 'newData'}}

        where 'params' is dict of parameters for the method with default values.

        Note:
        - If paramAsk is True, parameters should be asked to user in GUI
        - If paramAsk is False, default values are used without asking
        - If visible is False, method should not be shown in GUI
        - If visible is True, method should be shown in GUI
        """

        return {'<Point Methods>'        : {'pointMethod':InfoPoint.nullMethod,    'params':{                                                           }, 'visible':True, 'paramAsk':False}
               ,'Integer constant'       : {'pointMethod':InfoPoint.intConst,      'params':{'const'  :0                                                }, 'visible':True, 'paramAsk':True}
               ,'Integer random uniform' : {'pointMethod':InfoPoint.intRandUni,    'params':{'min'    :0,   'max'   :1                                  }, 'visible':True, 'paramAsk':True}
               ,'Real constant'          : {'pointMethod':InfoPoint.fltConst,      'params':{'const'  :0                                                }, 'visible':True, 'paramAsk':True}
               ,'Real random uniform'    : {'pointMethod':InfoPoint.fltRandUni,    'params':{'min'    :0,   'max'   :1                                  }, 'visible':True, 'paramAsk':True}
               ,'Random bit'             : {'pointMethod':InfoPoint.fltRandBit,    'params':{'prob1'  :0.1                                              }, 'visible':True, 'paramAsk':True}
               ,'Comp constant (re/im)'  : {'pointMethod':InfoPoint.cmpConstR,     'params':{'real'   :0,   'imag'  :0                                  }, 'visible':True, 'paramAsk':True}
               ,'Comp constant (abs/phs)': {'pointMethod':InfoPoint.cmpConstP,     'params':{'abs'    :0,   'phase' :0                                  }, 'visible':True, 'paramAsk':True}
               ,'Comp random   (re/im)'  : {'pointMethod':InfoPoint.cmpRandUniR,   'params':{'reMin'  :0,   'reMax' :1, 'imMin'   :0, 'imMax'   :1      }, 'visible':True, 'paramAsk':True}
               ,'Comp random   (abs/phs)': {'pointMethod':InfoPoint.cmpRandUniP,   'params':{'absMin' :0,   'absMax':1, 'phaseMin':0, 'phaseMax':_CIRCLE}, 'visible':True, 'paramAsk':True}
               ,'Comp discrete phase'    : {'pointMethod':InfoPoint.cmpDiscPhases, 'params':{'probAbs':0.5, 'phases':2                                  }, 'visible':True, 'paramAsk':True}
               }

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    def __init__(self, ipType:str, *, pos=None, vals=None):
        """Calls constructor of InfoPoint on respective position
           ipType : is type of this InfoPoint defined in the schema, e.g. 'ipReal', 'ipComplex', ...
                    If ipType is not defined in the schema yet, first create empty schema for this ipType.
           pos    : is position of this InfoPoint defined as dict {axeKey: axeValue_float} or list/tuple of values mapped to axes in the order defined in the schema for this ipType.
           vals   : is values of this InfoPoint defined as dict {valKey: valValue} or list/tuple of values mapped to value keys in the order defined in the schema for this ipType.
           This method can modify schema for this ipType if ipType is not defined in the schema yet.
        """

        InfoPoint.checkSchema(ipType)

        self._ipType = ipType # Type of InfoPoint (ipReal, ipComplex, ...)
        self._pos    = {}     # Dict of real numbers for position coordinates {'row':5, 'col':6, ...} defined by schema
        self._vals   = {}     # Dict of values of this InfoPoint defined by schema

        self.set(pos=pos, vals=vals)

    #--------------------------------------------------------------------------
    def __str__(self) -> str:
        """Returns string representation of this InfoPoint object instance.
        """

        return self.info()['msg']

    #--------------------------------------------------------------------------
    def _format(self, val) -> str:
        """Creates string representation of the value for respective format settings
        """

        if   val is None         : toRet = 'None'.ljust(_F_TOTAL)
        elif type(val) == int    : toRet = f"{val:#{_F_TOTAL}}"
        elif type(val) == float  : toRet = f"{val:#{_F_TOTAL}.{_F_DECIM}f}"
        elif type(val) == complex: toRet = f"({val.real:#{_F_TOTAL}.{_F_DECIM}f} {val.imag:#{_F_TOTAL}.{_F_DECIM}f}j)"
        else                     : toRet = f"{val:{_F_TOTAL}}"

        return toRet

    #--------------------------------------------------------------------------
    def _posStr(self) -> str:
        """Creates string representation of the position of this InfoPoint.
        """

        toRet = '['

        i = 0
        for axe, axeName in InfoPoint._schema[self._ipType]['axes'].items():
            if i>0: toRet += ', '
            toRet += f"{axeName}={self._pos.get(axe, 0):{_F_POS}.1f}"
            i += 1

        toRet += ']'
        return toRet

    #--------------------------------------------------------------------------
    def _valsStr(self) -> str:
        """Creates string representation of the values of this InfoPoint.
        """

        toRet = '['

        i = 0
        for val, valName in InfoPoint._schema[self._ipType]['vals'].items():
            if i>0: toRet += ', '
            toRet += f"{valName}={self._format(self._vals.get(val, None))}"
            i += 1

        toRet += ']'
        return toRet

    #==========================================================================
    # InfoPoint Value's modification
    #--------------------------------------------------------------------------
    def clear(self, *, vals:dict={}) -> 'InfoPoint':
        """Iterates through all value keys and sets their values to values privided or to default values.
           vals : is dict of values for respective value keys as {valKey: valValue} to set for this InfoPoint.

           This method is vulnerable to wrong input data, e.g. if vals is dict but has keys which are not defined in the schema for this ipType,
           these keys are ignored without warning. FIX IN THE FUTURE
        """

        for keyVal in InfoPoint._schema[self._ipType]['vals'].keys():
            self._vals[keyVal] = vals.get(keyVal, 0)

        logger.debug(f"InfoPoint.clear: {self._vals}")
        return self

    #--------------------------------------------------------------------------
    def set(self, *, pos=None, vals=None):
        """Set position and values of this InfoPoint.

           pos    : is position of this InfoPoint defined as dict {axeKey: axeValue_float} or list/tuple of values mapped to axes in the order defined in the schema for this ipType.
           vals   : is values of this InfoPoint defined as dict {valKey: valValue} or list/tuple of values mapped to value keys in the order defined in the schema for this ipType.

           This method is vulnerable to wrong input data, e.g. if pos is list of values but number of values is higher than number of axes defined in the schema for this ipType,
           only first values are mapped to axes and rest of values are ignored without warning. FIX IN THE FUTURE
          """

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

    #==========================================================================
    # InfoPoint Value's retrieval
    #--------------------------------------------------------------------------
    def get(self, *, pos:bool=True, vals:bool=True):
        """Returns position and values of this InfoPoint as dict {'pos':_pos, 'vals':_vals}.
           pos  : if True, include position in the returned dict, if False, do not include position in the returned dict.
           vals : if True, include values in the returned dict, if False, do not include values in the returned dict.
        """

        toRet = {}
        if pos : toRet['pos' ] = self._pos.copy()
        if vals: toRet['vals'] = self._vals.copy()

        return toRet

    #--------------------------------------------------------------------------
    def pos(self, axeKey=None)->float|dict|None:
        """Returns position float value on respective axe or whole position dict for this InfoPoint.
           If axeKey is None, returns whole position dict {axeKey: axeValue_float}.
           If axeKey is not None, returns position float value for respective axeKey or None if axeKey is not defined in the schema for this ipType.
        """

        if axeKey is None:
            return self._pos.copy()

        else:
            return self._pos.get(axeKey, None)

    #--------------------------------------------------------------------------
    def val(self, valKey=None):
        """Returns value for respective key or whole values dict for this InfoPoint.
           If valKey is None, returns whole values dict {valKey: valValue}.
           If valKey is not None, returns value for respective valKey or None if valKey is not defined in the schema for this ipType.
        """

        if valKey is None:
            return self._vals.copy()

        else:
            return self._vals.get(valKey, None)

    #--------------------------------------------------------------------------
    def info(self, indent=0, full=False) -> dict:
        """Creates info about this InfoPoint.
           indent : is number of indents for the info message, each indent is defined as 4 spaces.
           full   : if True, creates full info message with all details, if False, creates short info message.
           Returns dict with keys 'res', 'dat' and 'msg' where
             'res' is 'OK' if info was created successfully, otherwise 'ERROR',
             'dat' is dict with info data and
             'msg' is string with info message.

             This method is vulnerable to wrong input data, e.g. if indent is negative,
             it will create info message with negative number of indents without warning.
             'dat' is in wrong structure FIX IN THE FUTURE
        """

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
    # Show methods - Returns float value (or representation as float) from InfoPoint values
    #--------------------------------------------------------------------------
    @staticmethod
    def fValue(val) -> float:
        """Returns value as float"""

        if val is None: return 0.0
        return float(val) if val else 0.0

    #--------------------------------------------------------------------------
    @staticmethod
    def abs(val) -> float:
        """Returns absolute of respective value"""

        if val is None: return 0.0
        return float(abs(val)) if val else 0.0

    #--------------------------------------------------------------------------
    @staticmethod
    def real(val) -> float:
        """Returns real part of complex value or value as float"""

        if val is None: return 0.0
        if type(val) == complex: return float(val.real)
        return float(val) if val else 0.0

    #--------------------------------------------------------------------------
    @staticmethod
    def imag(val) -> float:
        """Returns imaginary part of complex value"""

        if val is None: return 0.0
        if type(val) == complex: return float(val.imag)
        return 0.0

    #--------------------------------------------------------------------------
    @staticmethod
    def phase(val) -> float:
        """Returns phase of complex value"""

        if val is None: return 0.0
        if type(val) == complex: return cmath.phase(val)
        return 0.0

    #--------------------------------------------------------------------------
    @staticmethod
    def complex(val) -> complex:
        """Returns value as complex value"""

        if val is None: return complex(0, 0)
        return complex(val) if val else complex(0, 0)

    #==========================================================================
    # Set Methods to set keyed value of this InfoPoint for respective parameters.
    #--------------------------------------------------------------------------
    @staticmethod
    def nullMethod(infoPoint, outKey:str, params:dict) -> int:
        """Null method for testing.
           Retuns 1 if value was set, otherwise 0.
        """

        return 1

    #--------------------------------------------------------------------------
    @staticmethod
    def intConst(infoPoint, outKey:str, params:dict) -> int:
        """Set keyed value to constant integer value.
           params should have key 'const' with constant value to set.
           Retuns 1 if value was set, otherwise 0.
        """

        const = int(params.get('const', 0))
        infoPoint.set(vals={outKey: const})
        return 1

    #--------------------------------------------------------------------------
    @staticmethod
    def intRandUni(infoPoint, outKey:str, params:dict) -> int:
        """Set keyed value to random uniform integer value in range <min, max>.
           params should have keys 'min' and 'max' with range limits.
           Retuns 1 if value was set, otherwise 0.
        """

        minVal = int(params.get('min',  0))
        maxVal = int(params.get('max', 10))

        val = rnd.randint(minVal, maxVal)

        infoPoint.set(vals={outKey: val})
        return 1

    #--------------------------------------------------------------------------
    @staticmethod
    def fltConst(infoPoint, outKey:str, params:dict) -> int:
        """Set keyed value to constant float value.
           params should have key 'const' with constant value to set.
           Retuns 1 if value was set, otherwise 0.
        """

        const = float(params.get('const', 0))
        infoPoint.set(vals={outKey: const})
        return 1

    #--------------------------------------------------------------------------
    @staticmethod
    def fltRandUni(infoPoint, outKey:str, params:dict) -> int:
        """Set keyed value to random uniform float value in range <min, max>.
           params should have keys 'min' and 'max' with range limits.
           Retuns 1 if value was set, otherwise 0.
        """

        minVal = float(params.get('min', 0))
        maxVal = float(params.get('max', 1))

        val = rnd.uniform(minVal, maxVal)

        infoPoint.set(vals={outKey: val})
        return 1

    #--------------------------------------------------------------------------
    @staticmethod
    def fltRandBit(infoPoint, outKey:str, params:dict) -> int:
        """Set keyed value to random bit value (1 or 0) with probability prob1.
           params should have key 'prob1' with probability of setting value to 1.
           If params does not have key 'prob1', default probability is 0.5.
           Retuns 1 if value was set, otherwise 0."""

        prob1 = params.get('prob1', 0.5)
        val = 1 if rnd.random() < prob1 else 0

        infoPoint.set(vals={outKey: val})
        return 1

    #--------------------------------------------------------------------------
    @staticmethod
    def cmpConstR(infoPoint, outKey:str, params:dict) -> int:
        """Set keyed value to constant complex value given by real and imaginary parts.
           params should have keys 'real' and 'imag' with real and imaginary parts of the complex value to set.
           If params does not have key 'real' or 'imag', default value for respective part is 0.
           Retuns 1 if value was set, otherwise 0.
        """

        real = params.get('real', 0)
        imag = params.get('imag', 0)
        val  = complex(real, imag)

        infoPoint.set(vals={outKey: val})
        return 1

    #--------------------------------------------------------------------------
    @staticmethod
    def cmpConstP(infoPoint, outKey:str, params:dict) -> int:
        """Set keyed value to constant complex value given by absolute value and phase.
           params should have keys 'abs' and 'phase' with absolute value and phase of the complex value to set.
           If params does not have key 'abs' or 'phase', default value for respective part is 0.
           Retuns 1 if value was set, otherwise 0.
        """

        abs_val = params.get('abs' , 0)
        phase   = params.get('phase', 0)
        val     = abs_val * cmath.exp(complex(0, phase))

        infoPoint.set(vals={outKey: val})
        return 1

    #--------------------------------------------------------------------------
    @staticmethod
    def cmpRandUniR(infoPoint, outKey:str, params:dict) -> int:
        """Set keyed value to random complex value with uniform real and imaginary parts in given ranges.
           params should have keys 'reMin', 'reMax', 'imMin' and 'imMax' with ranges for real and imaginary parts of the complex value to set.
           If params does not have key 'reMin', 'reMax', 'imMin' or 'imMax', default value for respective part is 0 for minimum and 1 for maximum.
           Retuns 1 if value was set, otherwise 0.
        """

        reMin  = params.get('reMin' , 0)
        reMax  = params.get('reMax' , 1)
        imMin  = params.get('imMin' , 0)
        imMax  = params.get('imMax' , 1)

        real = reMin + (reMax - reMin) * rnd.random()
        imag = imMin + (imMax - imMin) * rnd.random()
        val  = complex(real, imag)

        infoPoint.set(vals={outKey: val})
        return 1

    #--------------------------------------------------------------------------
    @staticmethod
    def cmpRandUniP(infoPoint, outKey:str, params:dict) -> int:
        """Set keyed value to random complex value with uniform absolute value and phase in given ranges.
           params should have keys 'absMin', 'absMax', 'phaseMin' and 'phaseMax' with ranges for absolute value and phase of the complex value to set.
           If params does not have key 'absMin', 'absMax', 'phaseMin' or 'phaseMax', default value for respective part is 0 for minimum and 1 for maximum.
           Retuns 1 if value was set, otherwise 0.
        """

        absMin   = params.get('absMin'  , 0)
        absMax   = params.get('absMax'  , 1)
        phaseMin = params.get('phaseMin', 0)
        phaseMax = params.get('phaseMax', _CIRCLE)

        abs_val = absMin + (absMax - absMin) * rnd.random()
        phase   = phaseMin + (phaseMax - phaseMin) * rnd.random()
        val     = abs_val * cmath.exp(complex(0, phase))

        infoPoint.set(vals={outKey: val})
        return 1

    #--------------------------------------------------------------------------
    @staticmethod
    def cmpDiscPhases(infoPoint, outKey:str, params:dict) -> int:
        """Set keyed value to random complex value with discrete uniform phases.
           params should have keys 'probAbs' and 'phases' with probability of selecting non-zero absolute value and number of discrete phases.
           If params does not have key 'probAbs' or 'phases', default values are 0.5 and 2 respectively.
           Retuns 1 if value was set, otherwise 0.
        """

        probAbs = params.get('probAbs', 0.5)
        phases  = params.get('phases', 2)

        abs_val = 1 if rnd.random() < probAbs else 0
        phase_idx = rnd.randint(0, phases - 1)
        phase = phase_idx * _CIRCLE / phases
        val = abs_val * cmath.exp(complex(0, phase))

        infoPoint.set(vals={outKey: val})
        return 1

#==============================================================================
# Inicializacia modulu
#------------------------------------------------------------------------------
print(f"InfoPoint ver {_VER}")

if __name__ == '__main__':

    logger.info("Testing InfoPoint class")

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------
