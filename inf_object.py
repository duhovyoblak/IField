#==============================================================================
# Siqo class IObject
#------------------------------------------------------------------------------
# from  datetime import datetime, timedelta

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

    #--------------------------------------------------------------------------
    @staticmethod
    def valToId(val):
        "Returns or creates objId for respective value"
        
        return 0

    #--------------------------------------------------------------------------
    @staticmethod
    def objByVal(val, create=False):
        "Returns or creates objects for respective objVal"

        # Ak existuje objekt so zadanym value
        if val in IObject.vals.keys(): return IObject.vals[val]
        
        # ak taky objekt neexistuje
        else:
            if create: return IObject(val)
            else     : return None

    #==========================================================================
    # Constructor & utilities
    #--------------------------------------------------------------------------
    #
    # objId - generic integer as primary key for IObject
    # cont  - complex number for base type IObject
    #       - list of objId [objId] for structural type of IObject
    #--------------------------------------------------------------------------
    def __init__(self, cont=None):
        "Calls constructor of IObject for respective content"

        IObject.journal.I("IObject.constructor:")
        
        # Default hodnota je komplexna nula
        if cont is None: cont = complex()

        #----------------------------------------------------------------------
        # datove polozky triedy
        #----------------------------------------------------------------------
        self.objId = len(IObject.oids)+1   # Unique object Id
        self.cont  = cont
        
        if type(self.cont) == complex: self.isBase = True
        else                         : self.isBase = False
        
        if self.isBase: self.setAlias( self.contStr()  )
        else          : self.setAlias( self.cont.alias )
        
        #----------------------------------------------------------------------
        # Update zoznamov a indexov
        #----------------------------------------------------------------------
        IObject.oids[self.objId] = self
        IObject.alas[self.alias] = self
        
        IObject.journal.O(f'{self.objId}.constructor: done with alias {self.alias}')

    #--------------------------------------------------------------------------
    def __str__(self):
        "Prints info about this object"

        toRet = ''
        for line in self.info()['msg']: toRet += line +'\n'

        return toRet

    #--------------------------------------------------------------------------
    def contStr(self):
        "Returns string representation of object's content"
        
        if self.isBase: return str(self.cont)
        else          : return ';'.join(self.cont)
        
    #--------------------------------------------------------------------------
    def setAlias(self, alias):
        "Reset alias for this object"
        
        # Delete current alias from alas{}
        if alias in IObject.alas.keys(): IObject.alas.pop(self.alias)
        
        # Set new alias for this object
        self.alias = alias
        IObject.alas[self.alias] = self
    
    #--------------------------------------------------------------------------
    def info(self):
        "Returns info about this Object"

        info = {}
        msg  = []
        
        info['objId'] = self.objId
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

    #==========================================================================
    # Internal Methods
    #--------------------------------------------------------------------------
    def encode(self):
        "Encode objVal into prtLst using existing/new Objects in objs"
        
        IObject.journal.I(f"{self.objId}.encode: '{self.objVal[:80]}...'")
        
        self.prtLst.clear()
        
        #----------------------------------------------------------------------
        # Prejdem vsetky pozicie v objVal
        #----------------------------------------------------------------------
        pos   =  0
        vLen  =  len(self.objVal)
        
        while pos < vLen:
            
            # Najdem njdlhsiu sekvenciu ktora sa nachadza vo vals
            val = ''
            while (val=='' or IObject.isObj(val) ) and (pos < vLen):
                val += self.objVal[pos]
                pos += 1
            
            # Korekcia posledneho znaku ak existuje aspon jednoznakova sekvencia
            if len(val)>1:
                val = val[:-1]
                pos -= 1
                
            # Ziskam objekt s prislusnou objVal
            part = IObject.getObj(val, create=True)
        
            # Vlozim partObject do zoznamu
            self.prtLst.append(part)
        
        IObject.journal.O(f'{self.objId}.encode: Identified {len(self.prtLst)} parts')
    
    #==========================================================================
    # Persistency methods
    #--------------------------------------------------------------------------
    def fromJson(self, json):
        "Loads Object from json structure"

        IObject.journal.I(f'{self.objId}.fromJson:')

        #----------------------------------------------------------------------
        IObject.journal.O(f'{self.objId}.fromJson: Loaded')

    #--------------------------------------------------------------------------
    def toJson(self):
        "Converts Object into json structure"
        
        IObject.journal.I(f'{self.objId}.toJson:')
        
        toRet = {}

        IObject.journal.O(f'{self.objId}.toJson: Converted')
        return toRet

#------------------------------------------------------------------------------
print('IObject ver 0.01')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------