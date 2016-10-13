import nwfind
import nwutils

print "Hello"

DEBUG_TXT = ""
  
# K(ey word)Lists are initialized with comma-separated strings
# thanks to Stack Exchange for idea of making it into a factory 
# and repository
class KList:
    instances={}
    def __init__(self, name, inString):
        self.name = name;    
        self.list = inString.split(',')
        KList.instances[name] = self    #syntax: klist = KList.instances[ name ]

    def var(self): #turn a KList into a VAR. Known as a "KList VAR"
        Z = VAR()
        Z.knames.append(self.name)
        return Z

                # the KList does not keep track of its last search result
                # it is the responsibility to the client to pass in ifound
                # This method returns True or False
    def findInText(self, tokens, itok, ifound):
        return nwfind._findInText(self, tokens, itok, ifound)
    
NULL_KLIST = KList("nullK","")

# design pattern is a bit strange: relatively concrete containers are used
# to generate more abstract ones that wrap them.

 # VARS are lists of keyword lists (actually just the names of keyword lists)
# with an attribute of "exclusive" if an input word can match just one
# of the KLists. If not "exclusive", an input word can match any KList

class VAR:
    def __init__(self):
        
        # ---these are constant in the VAR
        self.knames = []  # a VAR can always have its own KList
        self.exclusive = False
        self.parent = 0 # makes a VAR into a tree node, but tree info is lost by operators
        self.children = []

        # ---these are associated with reading text: startings at ground state then changed
            # a normal "detected" signal
        self.found = False 
            # to storeindices of tokens in text, with matches words of self's KLists.
        self.ifound= []   
            # to record what happened in the children
        self.foundInChildren = False
            # becomes false if kname after 1st is used
        self.polarity = True
             

    def clear(self):
        self.found = False
        self.ifound = []
        self.foundInChildren = False
        self.polarity = True
        
        for child in self.children:
            child.clear()

            # this allows re-use of the VAR in search functions
            # but leaves the self.found unchanged
    def clearIFound(self):
        self.ifound = []
        for child in self.children:
            child.clearIFound()

    # call this once, usually on the root node of the tree
    def copy(self):
        v = VAR()
        v.knames = self.knames
        v.exclusive = self.exclusive
        if self.parent==0 :
            v.parent = 0
        
        v.found = self.found
        v.ifound= self.ifound
        v.foundInChildren = self.foundInChildren
        v.polarity = self.polarity

        for child in self.children:
            newchild = child.copy()
            v.children.append(newchild)
                      
        return v

    def copyUsing(self,tree):
        name = self.knames[0]
        #print name, "\n"
        if not isinstance(tree, VAR):
            print "OOPS in copyUsing()"
            print name
            return
        else:
            x = tree.lookup(name) # find VAR with same name, in this tree           
        if x != NULL_VAR:
            return x # x.copy().
        else:
            return NULL_VAR
   
    

    # returns self, if kname in knames
    # or child with this name, else NULL_VAR
    def lookup(self,name):
        for kname in self.knames:     
            if name==kname:
                return self 
            
        for child in self.children:
            x = child.lookup(name)
            if x!=NULL_VAR:      
                return x
        return NULL_VAR          
    

                    # loops through text for every kname.
    def findInText( self, originaltokens):
        # ensure lower case
        tokens = []
        for tok in originaltokens:
            if tok==0:
                tokens.append(0)
            else:
                tokens.append(tok.lower())
            
        # for each token 
        for itok in range( len(tokens) ):
            ikname = 0 
            for kname in self.knames: # for each name in self's klist
                
                klist = KList.instances[ kname ]
                
                found = klist.findInText(tokens, itok, self.ifound) 
                if found:
                        self.found = True

                        # can switch frequently and reflects the last found token
                        if self.exclusive and ikname>0:
                            self.polarity = False
                        else:
                            self.polarity = True                          
                ikname += 1               
            
                    # all the way through the call stack, self.ifound updates
                    # a list of indices of tokens found. This will be
                    # confusing, as they may not sync with itok exactly,
                    # when multi-word KList entries are used.      

        # Search iteratively inside the children
        for child in self.children:
            foundC = child.findInText( tokens )
            if foundC :
                self.foundInChildren = True
                self.ifound.extend( child.ifound )
        
        # tell the caller that something below it was found
        # although self.found can be False
        return (self.found or self.foundInChildren)   
                
    ## can modify the .found  or .foundInChildren, but it protected from 
    # chagning ifound (oops! it changes the childern. Best to 
    # only use this for controls 
    def find(self,tok):
            ifound = self.ifound[:] 
            tokens = []
            tokens.append(tok)
            self.ifound = []
            self.findInText(tokens) 
            if len(self.ifound)>0:
                found = True
            else:
                found = False
            self.ifound = ifound[:] # restore
            return found

    # use Print() for recursive print, or Print(0,False) for non-recursive
    def Print(self, ntabs=0, recurs=True):
        tab = ""
        for i in range(ntabs):
            tab += "  "

        print(tab+"knames:"), 
        for name in self.knames:
            if not self.exclusive:
                print(name+" +"),
            else:
                print(name+" |"),
        if self.found:
            tmp = "*"
        else:
            tmp = ""
        print("\n" + tab+"found :"),tmp
        if self.foundInChildren:
            tmp = "*"
        else:
            tmp = ""
        print(tab + "foundC:"),tmp
        print(tab + "plrty :"), self.polarity
        if len( self.children )>0 :
            print(tab + "chldrn:")
        else:
            print("\n")
            
        if recurs:
            for child in self.children:
                child.Print(ntabs+1, recurs)

    def PrintSimple(self, ntabs=0):
        output = ""
        tab = ""
        for i in range(ntabs):
            tab += "  "

        output += tab
        #print(tab),      
        for name in self.knames:
            if not self.exclusive:
                output += name + " "
            else:
                output += name + "|"
        if self.found:
            output += "*"
        if self.polarity==False:
            output += "-"
        output += '\n'        
        #print "\n"
        for child in self.children:
            output += child.PrintSimple(ntabs+1)
        return output
                    
    ## operator '+'     # to match text against any Klist            
    def __add__(self, other ): 
        Z = VAR()
        Z.knames += self.knames
        Z.knames += other.knames
        Z.exclusive = False
        return Z
    
    ##  operator '|'    # to match text against just one KList
    ## matching text in more than one is considered a coding error but
    ## it could be a contradiction in the text. We'll see.
    def __or__(self, other ):    
        Z = VAR()
        Z.knames += self.knames
        Z.knames += other.knames
        Z.exclusive = True
        return Z

    ## connect with your children as in "addChild()"
    def sub(self, other): #to make other into a child of self
        other.parent = self
        self.children.append(other) 

    def numSlots(self):
        if self==NULL_VAR:
            return 0
        else:
            return 1
    def numSlotsUsed(self):
        if self.found or self.foundInChildren:
            return 1
        else:
            return 0

    # like a minimal "print". It is used by nar.string()
    def string(self, ntabs=0):
        return self.knames[0]
    
    # KList VARS are used to produce "KList" NARs below of order 0
    # So VAR become a class factory for NAR. 
    # All NARs built from these KList NARs will be of higher order>0
    def nar(self):
        p = NAR()
        p.order = 1
        p.blocked  = False
        p.polarity = True
        
        p.thing = self         # so isinstance(p.thing,VAR) is True
        p.action   = NULL_VAR
        p.relation = NULL_VAR
        p.value    = NULL_VAR    
        return p

    # note this does not climb up the tree of parents returning true if foundInChildren 
    # This only returns true for the self VAR's knames[0] argument
    def isA(self, name):
        if name==self.knames[0]:
            return True
        else:
            return False
        
#-----------ZERO for VAR type
NULL_VAR   = NULL_KLIST.var()

def countVAR(array):
    count = 0
    for i in range(len(array)):
        if array[i]!=NULL_VAR:
            count += 1
    return count
        

####################### REFERENCE CONSTANTS for NAR class ################
NULL_NARTYPE  = 0  # for empty nar, like NULL_NAR
THING_NARTYPE = 1  # for nar without actioN or relation
ATTRIB_NARTYPE= 2  # non empty relation
EVENT_NARTYPE = 3  # user defined event
SO_NARTYPE    = 4  # cause/"so" nar ("so" is more for internal use)
THEN_NARTYPE  = 5  # sequence/"then" nar ("then is more for internal use)

def strNarType(type):
    if   type==NULL_NARTYPE:
        return "NULL"
    elif type==THING_NARTYPE:
        return "THING"
    elif type==ATTRIB_NARTYPE:
        return "ATTRIB"
    elif type==EVENT_NARTYPE:
        return "EVENT"
    elif type==SO_NARTYPE:
        return "CAUSE"
    elif type==THEN_NARTYPE:
        return "SEQ"


#######################################################################
#######################################################################
# this class stores several VAR-like entitites in its members. 
# But the implementation is TREE-like because "operators" of the form
#               self.thing = (some other self)
# can get recursive
class NAR:
    
    def __init__(self):
        self.order = 0 # the level of pattern-inside-pattern depth

        # between these two, we can consider the "whole" value of the narrative to be 
        # their product, specifically: if blocked then return polarity, else return !polarity
        self.blocked = 0
        self.polarity = True
        
        self.thing = NULL_VAR 
        self.action = NULL_VAR
        self.relation = NULL_VAR # like "color" (or "with")
        self.value = NULL_VAR    # like "red" (or an other.thing)
        # The concept of "value" is overloaded here, and is being forced on me
        # by a lack of programming ability. "value" works as an adjective,
        # or as an object, or as whatever


    # If x is a var, this calls .clear(), otherwise it calls into the sub narratives.
    def clear(self):
        self.blocked = 0
        self.polarity = True

        if self.thing != NULL_VAR: # and self.thing !=0:
            self.thing.clear()
        if self.action != NULL_VAR:  # self.action !=0:
            self.action.clear()
        if self.relation !=NULL_VAR: # self.relation !=0:
            self.relation.clear()
        if self.value != NULL_VAR: # self.value !=0:
            self.value.clear()
        
    def clearIFound(self):
        if ORDER(self)==0:
            self.clearIFound()
            return
        if self.thing != NULL_VAR: # and self.thing !=0:
            self.thing.clearIFound()
        if self.action != NULL_VAR:  # self.action !=0:
            self.action.clearIFound()
        if self.relation !=NULL_VAR: # self.relation !=0:
            self.relation.clearIFound()
        if self.value != NULL_VAR: # self.value !=0:
            self.value.clearIFound()



    # this copy uses the same VARs as the original
    def copy(self):
        n = NAR()
        n.order   = self.order
        n.blocked = self.blocked
        n.polarity = self.polarity
        n.thing   = self.thing
        n.action  = self.action
        n.relation= self.relation
        n.value   = self.value
        return n


    ## When this tree is a copy of the one where the NAR is defined,
    ## NAR.copyUsing returns a "copy" of the same name as self, but
    ## using VARs from a other tree 
    def copyUsing(self, tree ):
        if self==NAR_SO or self==NAR_THEN: # these do not get copied
            return self
        
        if self.order==0 and len(self.thing.knames)>0: # so it is a var
            name = self.thing.knames[0]       
            x = tree.lookup(name) # find VAR with same name, in this tree           
            if x != NULL_VAR:
                n = x.nar()
                return n
        elif self.order==0: # happens if parent had empty children (like so and so)
            return NULL_NAR

        n = NAR()
        n.order   = self.order
        n.blocked = self.blocked
        n.polarity = self.polarity
        
        # for the sub NARs
        n.thing   = self.thing.copyUsing(tree)

        # This is not really right but I do not want to make
        # copies of these "constant" NARs. It means
        # we should never rely on the found or ifound of the VARs beneath  
        # these "constants", since different users may also be using them
        if self.action==NAR_SO:
            n.action = NAR_SO  
        elif self.action==NAR_THEN:
            n.action = NAR_THEN
        else:
            n.action = self.action.copyUsing(tree)
            
        n.relation= self.relation.copyUsing(tree)
        n.value   = self.value.copyUsing(tree)
        return n   

    # Implements OPERATOR X* (i.e. negation/contrast to X)
    # in general block() is not idempotent. A double block() is not always 
    # an un-block(). For example: "she was not ready to swim"
    # Also, unlike other operators, it seems simpler for this one to modify 
    # an original NAR and does not produce a fresh copy, that is blocked.
    # (TODO: revisit this decision)
    def block(self):
        self.blocked += 1
        
    def unblock(self):
        if self.blocked>0 :
           self.blocked -= 1        
             

           # means the token is part of the narrative. This changes the state of underlying VARs 
           # but note it is prevented from changing the ifound
    def find(self,tok):
        if ORDER(self)==0 :
            tokens = []
            tokens.append(tok)
            return self.findInText(tokens) 
        t = self.thing.find(tok) 
        a = self.action.find(tok) 
        r = self.relation.find(tok) 
        v = self.value.find(tok)
        return t or a or r or v

    def numSlots(self):
        if isinstance(self, VAR):  
           return self.numSlots()
        n = 0
        n += self.thing.numSlots()
        n += self.action.numSlots() 
        n += self.relation.numSlots()  
        n += self.value.numSlots()
        return n

    def numSlotsUsed(self):
        if isinstance(self,VAR) and self.found:
            return 1
        elif isinstance(self,NAR):
            n = 0
            if self.thing  != 0:
                n += self.thing.numSlotsUsed()
            if self.action != 0:
                n += self.action.numSlotsUsed()
            if self.relation !=0:
                n += self.relation.numSlotsUsed()
            if self.value != 0:
                n += self.value.numSlotsUsed()
            return n
        else:
            return 0       

    def showUseRatio(self):
        s = self.numSlots()
        u = self.numSlotsUsed()
        print u, "/", s
        
    def getType(nar):
        thing    = nar.thing
        action   = nar.action
        relation = nar.relation  
        # nar.value not part of type

        if relation!=NULL_VAR:
            return ATTRIB_NARTYPE
        elif action==NAR_SO:
            return SO_NARTYPE
        elif action==NAR_THEN:
            return THEN_NARTYPE
        elif action!=NULL_VAR:
            return EVENT_NARTYPE
        elif thing!=NULL_VAR:
            return THING_NARTYPE
        else:
            return NULL_NARTYPE

    def printType(self):
        print strNarType( self.getType())

    def str(nar, ntabs=0):
        tab = ""
        for i in range(ntabs):
            tab += "  "

        if nar==NULL_NAR:
            return "nullN"

        x = ""
        if isinstance(nar,VAR):
            if nar.found:
                x += "*"
            x += nar.knames[0]       
        elif isinstance(nar,NAR):
            x += "\n"
            t = strNAR(nar.thing,    ntabs+1)
            r = strNAR(nar.relation, ntabs+1)
            a = strNAR(nar.action,   ntabs+1)
            v = strNAR(nar.value,    ntabs+1)

            x += tab+"T:" +t + "\n"
            x += tab+"R:" +r + "\n"
            x += tab+"A:" +a + "\n"
            x += tab+"V:" +v + "\n"
        return x

    def Print(nar, ntabs=0):
        s = nar.str(ntabs)
        print s
#####################################################        
        
#------------ZERO for NAR() type
NULL_NAR = NULL_VAR.nar() # used as a default arg

## NOTE: NULL_VAR is used to indicate an uninitialized NAR
## and NULL_NAR is used to indicate a NAR that is empty. NULL_NAR
## is used as a deliberate place holder

#----------- UTILITIES FOR VARS AND NARS
def ORDER( X ):
    if isinstance(X, VAR ):
        return 0
    else:
        return X.order


#----------- OPERATORS that should have been methods of NAR() but I could not
# figure out how to program them. Their default args need to be globals that are
# not acceptable to the VAR() class.
#
# These are narratives of higher order than their members. Eg order 1 for KList NARs
#
# The proccessing priority is: attribute, event, cause, sequence - implemented in the read methods


#-------implements:  "X_REL_/A" - the adjective relation. X,A, and REL are NARs
#  ATTN! only use the REL variable if it is defined with A  
## TODO: put in a check for this

def attribute( X, A, REL=NULL_NAR):
    n = NAR()
    n.thing    = X   #"noise"   
    n.relation = REL #"outside"
    n.action   = NULL_VAR
    n.value    = A   #"loud"

    n.order = max( ORDER(X), ORDER(REL), ORDER(A) ) + 1
    return n

#-------implements:  "X-ACT->Y" - the verb relation
def event( X, Y, ACT):
    n = NAR()
    n.thing  = X     #"I"
    n.relation = NULL_VAR
    n.action = ACT   #"see"
    n.value  = Y     #"bird"
    
    n.order = max( ORDER(X), ORDER(ACT), ORDER(Y) ) + 1
    return n


# The next two OPERATORS have the same syntax but different text matching rules.
# They both describe sequential events X and Y but the cause(X,Y) function describes them  
# as causally connected, and the seq(X,Y) function describes them purely as a sequential.
# Note "SO" is used internally for cause and "THEN" and "AND" for sequence.

#-------Implements:  causal "X::Y" . This operator indicates transformation, becoming, causality,
# and is a bit like logical "therefor". Words in text like "so", "because", or "but"
# are listed in internal KLists and are not needed from the client
# Worth mentioning (as part of another rant below) that these words in English are
# translated by logicians into "therefor" - which is supposed to be timeless
#  - exactly opposite to the usage here.

NAR_SO  = KList("so","").var().nar() # a dummy to identify the "cause" type of statement
                                     # the correct word searching is handled by internal lists

def cause(X,Y):
    n = NAR()
    n.thing = X      #"we were happy"

    n.action= NAR_SO #(encode a "so" operation)
    n.value = Y      #"we laughed"
    n.order = max( ORDER(X), ORDER(Y) )+1
    return n


##----Implements: sequence "X,Y" . Words like "and" or "or" or "then A then B then C" are handled internally
## Screw the symbolic logicians who co-opted "then" for use only in "if..then..". Its natural use
## is closer to some versions of "and". Meanwhile they co-opted "or" and created the straw horse
## of "and not both". Further, don't tell me that chronology "X,Y" can be co-opted as a bi-
## directional relation like logical "or" and "and", or as a sub-part of an "if then" (which has
## lost its connection to chronology) So here, for a change, it means chronology. To achieve bi-directionalty,
## for now requires using both X,Y and Y,X and you can design code making them equivalent
NAR_THEN = KList("then","").var().nar() # used to identify the "and"/"then" type of statement

def sequence(X,Y):   
    n = NAR()
    n.thing = X         #"we ate cookies"
    n.action = NAR_THEN #(encode a "then" operation)
    n.value = Y         #"we ate pie"
    n.order = max( ORDER(X), ORDER(Y) )+1    
    return n

##########################################

def strNAR(nar, ntabs=0):
    tab = ""
    for i in range(ntabs):
        tab += "  "

    if nar==NULL_NAR:
        return "nullN"

    x = ""
    if isinstance(nar,VAR):
        if nar.found:
            x += "*"
        x += nar.knames[0]       
    elif isinstance(nar,NAR):
        x += "\n"
        t = strNAR(nar.thing,    ntabs+1)
        r = strNAR(nar.relation, ntabs+1)
        a = strNAR(nar.action,   ntabs+1)
        v = strNAR(nar.value,    ntabs+1)

        x += tab+"T:" +t + "\n"
        x += tab+"R:" +r + "\n"
        x += tab+"A:" +a + "\n"
        x += tab+"V:" +v + "\n"
    return x

def printNAR(nar, ntabs=0):
    s = strNAR(nar,ntabs)
    print s
