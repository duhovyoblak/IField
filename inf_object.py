#==============================================================================
# Siqo class IObject
#------------------------------------------------------------------------------
# from  datetime import datetime, timedelta

import  siqo_general     as     gen
# import inf_lib         as lib

#==============================================================================
# package's constants
#------------------------------------------------------------------------------
_ID_LEN     =   12  # Max length of objId
_OUT_MAX    =   80  # Max characters per output

#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# IObject
#------------------------------------------------------------------------------
class IObject:

    #==========================================================================
    # Static variables & methods
    #--------------------------------------------------------------------------
    journal = None   # Pointer to global journal
    oids    = {}     # Zoznam objektov per objId     {objId: obj}
    alas    = {}     # Zoznam objektov per alias     {alias: obj}

    #--------------------------------------------------------------------------
    @staticmethod
    def infoAll():
        "Returns info about Objects"

        info = {}
        out  = []
        
        out.append('{} {}'.format(90*'=', 'Objects:'))
        
        for objId, obj in IObject.objs.items():
            info[objId] = obj.objVal[:_OUT_MAX]
            
        #----------------------------------------------------------------------
        # Output
        for key, val in info.items(): out.append(f'{key.ljust(_ID_LEN+3)} = {val}')

        #----------------------------------------------------------------------
        return {'res':'OK', 'info':info, 'out':out, 'obj':None}

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    #
    # objId - generic integer as primary key for IObject
    # cont  - complex number or IStruct 
    #
    #--------------------------------------------------------------------------
    def __init__(self, cont=None):
        "Calls constructor of IObject for respective content"

        IObject.journal.I("IObject.constructor:")
        
        #----------------------------------------------------------------------
        # datove polozky triedy
        #----------------------------------------------------------------------
        self.name    = len(IObject.oids)+1  # Unique object Id
        self.cont    = None                 # complex number or IStruct
        self.isBase  = None                 # If this Object is complex number
        self.alias   = ''                   # Mnemotechnic alias for this object
        self.len     = 0                    # Total length of the object
        self.itPos   = -1                   # Position of the iterator
        
        self.setCont(cont)
        
        #----------------------------------------------------------------------
        # Update zoznamov a indexov
        #----------------------------------------------------------------------
        IObject.oids[self.name] = self
        IObject.alas[self.alias] = self
        
        IObject.journal.O(f'{self.name}.constructor: done with alias {self.alias}')

    #--------------------------------------------------------------------------
    def __str__(self):
        "Prints info about this object"

        toRet = ''
        for line in self.info()['msg']: toRet += line +'\n'

        return toRet

    #--------------------------------------------------------------------------
    def __iter__(self):
        "Creates iterator for this object"
        
        self.itPos = 0
        
        if self.isBase: return self
        else          : return iter(self.cont)

    #--------------------------------------------------------------------------
    def __next__(self):
        "Returns next item in ongoing iteration"
        
        #----------------------------------------------------------------------
        # Next sa da volat iba pre base object
        #----------------------------------------------------------------------
        if self.isBase: 
            
            # Pri prvom volani vratim hodnotu cont
            if self.itPos==0:
                
                self.itPos += 1
                return self.cont
            
            # Pri druhom volani ukoncim iterator
            else: raise StopIteration
            
        #----------------------------------------------------------------------
        # Tu nastala chyba... Next sa da volat iba pre base object
        #----------------------------------------------------------------------
        else:
            IObject.journal.O(f'{self.name}.__next__: ERROR No base object')
            raise StopIteration
        
    #--------------------------------------------------------------------------
    def isBase(self):
        "Returns isBase flag for this object"
        
        return self.isBase
        
    #--------------------------------------------------------------------------
    def idStr(self):
        "Returns string representation of object's IDs"
        
        if self.isBase: return str(self.name)
        else          : return self.cont.idStr()
        
    #--------------------------------------------------------------------------
    def alStr(self):
        "Returns string representation of object's aliases"
        
        return self.alias
        
    #--------------------------------------------------------------------------
    def setCont(self, cont=None):
        "Reset content for this object"
        
        #----------------------------------------------------------------------
        # Default hodnota je komplexna nula
        #----------------------------------------------------------------------
        if cont is None: cont = complex()

        #----------------------------------------------------------------------
        # Nastavenie contentu [complex number / IStruct]
        #----------------------------------------------------------------------
        self.cont = cont

        #----------------------------------------------------------------------
        # Nastavenie vlastnosti
        #----------------------------------------------------------------------
        if type(self.cont) == complex: self.isBase = True
        else                         : self.isBase = False
        
        if self.isBase: self.setAlias( self.idStr()    )
        else          : self.setAlias( self.cont.alias )
        
        if self.isBase: self.length = 1
        else          : self.length = gen.deepLen( self.cont.objs )
        
    #--------------------------------------------------------------------------
    def setAlias(self, alias):
        "Reset alias for this object"
        
        # Delete current alias from alas{}
        if alias in IObject.alas.keys(): IObject.alas.pop(alias)
        
        # Set new alias for this object
        self.alias = alias
        IObject.alas[self.alias] = self
    
    #--------------------------------------------------------------------------
    def info(self):
        "Returns info about this Object"

        info = {}
        msg  = []
        
        info['objId'] = self.name
        info['cont' ] = self.contStr() [:_OUT_MAX]
        info['alias'] = self.alias     [:_OUT_MAX]
        
        #----------------------------------------------------------------------
        # Output
        for key, val in info.items(): msg.append(f'{key.ljust(_ID_LEN)} = {val}')

        return {'res':'OK', 'info':info, 'msg':msg, 'obj':self}

    #==========================================================================
    # API
    #--------------------------------------------------------------------------
    def amp(self):
        "Returns amplitude of the Object"

        if self.isBase(): return self.objVal
        else            : return self.objVal.amp()

    #--------------------------------------------------------------------------
    def prob(self):
        "Returns probability of the amplitude of the Object"

        if self.isBase(): return self.objVal * self.objVal.conjugate()
        else            : return self.objVal.prob()

    #--------------------------------------------------------------------------
    def toJson(self):
        "Converts Object into json structure"
        
        IObject.journal.I(f'{self.name}.toJson:')
        
        toRet = {}

        IObject.journal.O(f'{self.name}.toJson: Converted')
        return toRet

#------------------------------------------------------------------------------
print('IObject ver 0.01')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------