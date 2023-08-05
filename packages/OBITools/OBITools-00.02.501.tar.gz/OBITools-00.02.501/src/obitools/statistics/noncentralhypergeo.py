from decimal import *
from math import log

#from obitools.utils import moduleInDevelopment

#moduleInDevelopment(__name__)

# from : http://www.programmish.com/?p=25

def dec_log(self, base=10):
    cur_prec = getcontext().prec
    getcontext().prec += 2
    baseDec = Decimal(10)
    retValue = self

    if isinstance(base, Decimal):
        baseDec = base
    elif isinstance(base, float):
        baseDec = Decimal("%f" % (base))
    else:
        baseDec = Decimal(base)

    integer_part = Decimal(0)
    while retValue < 1:
        integer_part = integer_part - 1
        retValue = retValue * baseDec
    while retValue >= baseDec:
        integer_part = integer_part + 1
        retValue = retValue / baseDec

    retValue = retValue ** 10
    decimal_frac = Decimal(0)
    partial_part = Decimal(1)
    while cur_prec > 0:
        partial_part = partial_part / Decimal(10)
        digit = Decimal(0)
        while retValue >= baseDec:
            digit += 1
            retValue = retValue / baseDec
        decimal_frac = decimal_frac + digit * partial_part
        retValue = retValue ** 10
        cur_prec -= 1
    getcontext().prec -= 2

    return integer_part + decimal_frac

class Interval(object):
    def __init__(self,begin,end,facteur=1):
        self._begin = begin
        self._end = end
        self._facteur=facteur

    def __str__(self):
        return '[%d,%d] ^ %d' % (self._begin,self._end,self._facteur)
    
    def __repr__(self):
        return 'Interval(%d,%d,%d)' % (self._begin,self._end,self._facteur)
    
    def begin(self):
        return (self._begin,self._facteur,True)
    
    def end(self):
        return (self._end,-self._facteur,False)
    
    
def cmpb(i1,i2):
    x= cmp(i1[0],i2[0])
    if x==0:
        x = cmp(i2[2],i1[2])
    return x
    
class Product(object):
    def __init__(self,i=None):
        if i is not None:
            self.prod=[i]
        else:
            self.prod=[]
        self._simplify()    
        
    def _simplify(self):
        bornes=[]
        prod  =[]
        
        if self.prod:
            
            for i in self.prod:
                bornes.append(i.begin())
                bornes.append(i.end())
            bornes.sort(cmpb)
                        
            
            j=0
            r=len(bornes)
            for i in xrange(1,len(bornes)):
                if bornes[i][0]==bornes[j][0] and bornes[i][2]==bornes[j][2]:
                    bornes[j]=(bornes[j][0],bornes[j][1]+bornes[i][1],bornes[i][2])
                    r-=1
                else:
                    j+=1
                    bornes[j]=bornes[i]
                    
            bornes=bornes[0:r]

            facteur=0
            close=1
            
            for b,level,open in bornes:
                if not open:
                    close=0
                else:
                    close=1
                if facteur:
                    prod.append(Interval(debut,b-close,facteur))
                debut=b+1-close  
                facteur+=level
                
        self.prod=prod
            
            
        
                
    def __mul__(self,p):
        res = Product()
        res.prod=list(self.prod)
        res.prod.extend(p.prod)
        res._simplify()
        return res
    
    def __div__(self,p):
        np = Product()
        np.prod = [Interval(x._begin,x._end,-x._facteur) for x in p.prod]
        return self * np
            
    def __str__(self):
        return str(self.prod)   
    
    def log(self):   
        p=Decimal(0)
        for k in self.prod:
            p+= Decimal(k._facteur) * reduce(lambda x,y:x+dec_log(Decimal(y),Decimal(10)),xrange(k._begin,k._end+1),Decimal(0))
        return p  

    def product(self):
        p=Decimal(1)
        for k in self.prod:
            p*= reduce(lambda x,y:x*Decimal(y),xrange(k._begin,k._end+1),Decimal(1)) ** Decimal(k._facteur)
        return p  

    def __call__(self,log=True):
        if log:
            return self.log()
        else:
            return self.product()
   
  
def fact(n):
    return Product(Interval(1,n))

def cnp(n,p):
    return fact(n)/fact(p)/fact(n-p)

def hypergeometic(x,n,M,N):
    '''
    
    @param x: Variable aleatoire
    @type x:  int
    @param n: taille du tirage
    @type n:  int
    @param M: boule gagnante
    @type M:  int
    @param N: nombre total dans l'urne
    @type N:  int
    
    p(x)=  cnp(M,x)  * cnp(N-M,n-x)  / cnp(N,n)
    '''
    return cnp(M,x)  * cnp(N-M,n-x)  / cnp(N,n)

def nchypergeometique(x,n,M,N,r):
    '''
    
    @param x: Variable aleatoire
    @type x:  int
    @param n: taille du tirage
    @type n:  int
    @param M: boule gagnante
    @type M:  int
    @param N: nombre total dans l'urne
    @type N:  int
    @param r: odd ratio
    @type r: float 
    
    p(x)=  cnp(M,x)  * cnp(N-M,n-x)  / cnp(N,n)
    '''
    
    xmin = max(0,n-N+M)
    xmax = min(n,M)
    lr   =  dec_log(r)
    xlr  = x * lr
    num  = cnp(M,x) * cnp(N-M,n-x)
    den  = [cnp(M,y) * cnp(N-M,n-y) / num for y in xrange(xmin,xmax+1)]
    fden = [lr * y - xlr for y in xrange(xmin,xmax+1)]
    
    inverse=reduce(lambda x,y : x+y,
                   map(lambda i,j: i(False) * 10**j ,den,fden))
    return 1/inverse


        