class MemStorage:
    def __init__(self,sequence,identifier,definition):
        self._sequence = sequence
        self._identifier = identifier
        self._definition = definition
        self._keys       = {}
        
    def getIdentifier(self):
        return self._identifier
    
    def setIdentifier(self,value):
        self._identifier=value
        
    def getDefinition(self):
        return self._definition
    
    def setDefinition(self,value):
        self._definition=value
    
    def getKey(self,key):
        return self._keys[key]
    
    def setKey(self,key,value):
        self._keys[key]=value
        
    def getSequence(self,begin,end):
        return self._sequence[begin:end]
    
    def getSymboleAt(self,pos):
        return self._sequence[pos]
    
    
