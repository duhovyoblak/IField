#==============================================================================
# Siqo library for IObject
#------------------------------------------------------------------------------
# from  datetime import datetime, timedelta
import random
import math
import numpy             as np

#==============================================================================
# package's constants
#------------------------------------------------------------------------------

#==============================================================================
# package's variables
#------------------------------------------------------------------------------

#==============================================================================
# Methods for Objects's value
#------------------------------------------------------------------------------
def valGen(base, length):
    "Returns string of randomly chosen values from base"
    
    toRet  = ''
    posMax = len(base)-1
    
    for i in range(length):
        
        pos = random.randint(0, posMax)
        toRet += base[pos]
        
    return toRet

#------------------------------------------------------------------------------
def valFromText(fName, enc):
    "Returns value string from text file"
    
    toRet  = ''
    
    f = open(fName, "r", encoding = enc)
    for line in f:
        toRet += line.rstrip()
        toRet += ' '
        
    f.close()
  
    return toRet

#==============================================================================
# Methods for plotable data
#------------------------------------------------------------------------------
def squareData(baseObj, vec):
    "Transform vector of particular objects into square plotable data"
    
    x = []
    y = []
    u = []

    lenX = math.sqrt( len(vec) )
    lenX = round(lenX + 0.5)
    
    i  = 0
    for obj in vec:
            
        x.append(i %  lenX)                      # stlpec = modulo lenX
        y.append(i // lenX)                      # riadok = integer division lenX
        u.append(baseObj.charVal( obj.objId ))   # charakteristicka hodnota
        i += 1
        
    X = np.array(x)
    Y = np.array(y)
    U = np.array(u)

    return (X, Y, U)

#------------------------------------------------------------------------------
def spiralData(baseObj, vec):
    "Transform vector of particular objects into spiral plotable data"
    
    x = []
    y = []
    u = []

    maxX = 0
    maxY = 0
    posX = 0
    posY = 0
    pos  = 0
    lenV = len(vec)

    #--------------------------------------------------------------------------
    # Nstartujem nekonecnu spiralu
    #--------------------------------------------------------------------------
    vecEnd = False
    
    while not vecEnd:
        
        #----------------------------------------------------------------------
        # rozsirim okno doprava a prejdem az na kraj
        #----------------------------------------------------------------------
        maxX += 1
        while (posX <= maxX) and (not vecEnd):
            
            if pos<lenV:
                x.append(posX)
                y.append(posY)
                u.append(baseObj.charVal( vec[pos].objId ))
                pos  += 1
                posX += 1
                
            else: vecEnd =True
        posX -= 1
        posY += 1
        
        #----------------------------------------------------------------------
        # rozsirim okno hore a prejdem az na kraj
        #----------------------------------------------------------------------
        maxY += 1
        while (posY <= maxY) and (not vecEnd):
            
            if pos<lenV:
                x.append(posX)
                y.append(posY)
                u.append(baseObj.charVal( vec[pos].objId ))
                pos  += 1
                posY += 1
                
            else: vecEnd =True
        posY -= 1
        posX -= 1
        
        #----------------------------------------------------------------------
        # prejdem az na lavy kraj
        #----------------------------------------------------------------------
        while (posX >= -maxX) and (not vecEnd):
            
            if pos<lenV:
                x.append(posX)
                y.append(posY)
                u.append(baseObj.charVal( vec[pos].objId ))
                pos  += 1
                posX -= 1
                
            else: vecEnd =True
        posX += 1
        posY -= 1
        
        #----------------------------------------------------------------------
        # prejdem az dole
        #----------------------------------------------------------------------
        while (posY >= -maxY) and (not vecEnd):
            
            if pos<lenV:
                x.append(posX)
                y.append(posY)
                u.append(baseObj.charVal( vec[pos].objId ))
                pos  += 1
                posY -= 1
                
            else: vecEnd =True
        posY += 1
        posX += 1
        
    #--------------------------------------------------------------------------
    X = np.array(x)
    Y = np.array(y)
    U = np.array(u)

    return (X, Y, U)

#==============================================================================
# Methods for Indentity Vectors
#------------------------------------------------------------------------------
def vecIdent(base, test, delta):
    "Returns vector of identities between base and test shifted by [delta] positions"
    
    toRet = []
    testLen = len(test)
    
    #--------------------------------------------------------------------------
    # Prejdem cely base vector
    #--------------------------------------------------------------------------
    for pos in range(len(base)):
        
        baseObj = base[pos]
        testObj = test[(pos+delta) % testLen]
        
        if id(baseObj)==id(testObj): toRet.append(1)
        else                       : toRet.append(0)
    
    #--------------------------------------------------------------------------
    return toRet

#------------------------------------------------------------------------------
def vecParts(aidVec):
    "Returns vector of parts found in aidVector as tuple(begin, end)"
    
    toRet   = []
    inPart  = False
    partBeg = 0
    partEnd = 0
    
    #--------------------------------------------------------------------------
    # Prejdem cely base vector
    #--------------------------------------------------------------------------
    for pos in range(len(aidVec)):
        
        # Ak sa nachadzam v part
        if inPart:
            
            # Ak val==1, posuniem koniec spracovavanej part
            if aidVec[pos]==1:
               partEnd = pos
                
            # inak ukoncim part a ulozim do zoznamu parts ak obsahuje min 
            else:
                inPart = False
                toRet.append((partBeg, partEnd+1))
            
        # Ak sa nenachadzam v part
        else:
            # Ak val==1, nastartujem novu part
            if aidVec[pos]==1:
               partBeg = pos
               partEnd = pos
               inPart  = True
                
            # inak pokracujem v hladani
            else: pass
    
    # ???? A co s poslednou nezapisanou part
    if inPart: toRet.append((partBeg, partEnd+1))
    
    #--------------------------------------------------------------------------
    return toRet

#------------------------------------------------------------------------------
print('inf_lib ver 0.01')

#==============================================================================
#                              END OF FILE
#------------------------------------------------------------------------------