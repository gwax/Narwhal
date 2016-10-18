from nwtypes import * # brings in nwutils and nwfind
from nwutils import *
from nwcontrol import *

# The "vault" (NarVault below) is a repository for instances of a 
# narrative, encountered in the course of reading a text. 
# It consists of an array of NarRecords.

# The NarRecord reflects a collapsing of the data that has been kept 
# as separate count of numSlotsUsed() and ifound (the indices of found tokens) 
# during the reading process. Here it gets scored and perhaps saved or "vaulted".
# There is a poetic analogy with how superposition of waves is
# additive until an event is observed. Events are not additive.  
# "GOF" means "goodness of fit" between narrative and text

class NarRecord:
    def __init__(self, nar, ifound, tokens):
        self.nused = nar.numSlotsUsed()   # num slots used in nar since nar.clear() erases this info.
        self.ifound = ifound[:]           # indices that have already been read  
        self.blocked = False
        self.GOF = self.gof(nar,tokens)

    def block(self):
        self.blocked = True

        # "goodness of fit"
    def gof(self, nar, tokens):  
        u = self.nused;
        n = nar.numSlots()
        L = len(tokens)
        jfound = discountControls(tokens, self.ifound)
        jfound = cleanFound(jfound)
        r = histo( jfound, L )
        f = getFoundRange(jfound,L)
        if f==0 or n==0:
            print "error in NarRecord.gof()"
        else:
            G = (float(u)/float(n))*(float(r)/float(f))  # one  of several possibilities.
            return G


# This is currently defined in terms of the above NarRecord. 
# Probably it could be more general.
class NarVault:
    def __init__(self):
        self._vault = []         
        self.pre   = 0
        self.preblock = False

# self.pre is or will be what is proposed for vaulting. 
# It is "previous" to vaulting.
# You can block self.pre before or after you encounter the nar
# that proposes data into it. This gives rise to awkward phrases like
# "pre-preblocking" and "post-preblocking". The point is that
# Pre can be blocked while still empty

    def clear(self):
        self._vault = []
        self.pre   = 0
        self.preblock = False 
          
    def vault(self):
        #if self.pre.GOF<=0.1:
        #    print "Aborting vault for lack of fit"
        gofStr = ""
        if self.pre!=0 and self.pre.GOF>0.1:
            if self.preblock:
                self.pre.block() #apply any pre blockage
            self._vault.append( self.pre )    
            gofStr = str(self.pre.GOF)
        self.pre = 0
        self.preblock = False
        return gofStr
                     
    def propose(self, nar, ifound,tokens, readstart):
        if len(ifound)==0:
            return;       
        ifound = cleanFound(ifound) 
        # re-consistute the original ifound when readstart was zero
        jfound = []
        for i in range(len(ifound)):
            jfound.append( ifound[i]+readstart )      
        #Aself.pre = NarRecord(nar, ifound,tokens)
        self.pre = NarRecord(nar, jfound,tokens)
                
    def abandonPre(self):
        self.pre = 0
        
    def blockPre(self):
        self.preblock = True 
         
    def unblockPre(self):  
        self.preblock = False




