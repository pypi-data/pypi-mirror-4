class GeneticCode(object):
    '''
    
    '''
    def __init__(self,code):
        self.parse(code)
        
    def parse(self,code):
        lines = code.strip('{} ').split(',')
        lines = dict(x.split(" ",1) for x in lines)
        name  = lines[0][1]
        abbrev= lines[1][1]
        id    = lines[2][1]