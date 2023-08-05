# -*- coding: utf-8 -*-
"""
   Module de calcules statistiques.

   Le module `statistics` contient des fonctions permettant le calcule
   des probabilités associées à la loi hypergéométrique et 
   hypergéométrique cumulée, ainsi d'une méthode de correction pour les
   tests multiples. 
   
"""

from decimal import *

getcontext().prec = 28


def _hyper0(N,n,r):
    """
        Fonction interne permetant le calcule du terme 0 de la loi hypergéométrique.
        
        Le calcule est réalisé selon la méthode décrite dans l'article
        
             Trong Wu, An accurate computation of the hypergeometric distribution function, 
             ACM Trans. Math. Softw. 19 (1993), no. 1, 33–43.
             
        Paramètres:
        
        - `N` : La taille de la population
        - `n` : Le nombre d'éléments marqués
        - `r` : La taille de l'echantillon
            
        Retourne un *float* indiquant la probabilité de récupérer 0 élément
        marqué parmi *n* dans une population de taille *N* lors du tirage
        d'un échantillon de taille *r*
    """
    
    #
    # au numerateur nous avons :
    #    [N -r + 1 -n;N - n + 1[
    #
    # au denominateur :
    #    [N - r + 1; N + 1]
    #
    # avec X = N - r + 1
    #   et Y = N + 1
    #
    # Numerateur   -> [ X - n; Y - n [
    # Denominateur -> [ X    ; Y [
    #
    # On peut donc siplifier 
    #
    # Numerateur    -> [X - n; X [
    # Denominateur  -> [Y - n; Y [
    
    numerateur  = xrange(N - r + 1 - n, N - r + 1)
    denominateur= xrange(N + 1 - n, N + 1)
#
#    version original
#  
#    m = N - n
#    numerateur   = set(range(m-r+1,m+1))
#    denominateur = set(range(N-r+1,N+1))
#    simplification = numerateur & denominateur
#    numerateur -= simplification
#    denominateur -= simplification
#    numerateur = list(numerateur)
#    denominateur=list(denominateur)
#    numerateur.sort()
#    denominateur.sort()
    
    
    p = reduce(lambda x,y:x*y,map(lambda i,j:Decimal(i)/Decimal(j),numerateur,denominateur))
    return p


def hypergeometric(x,N,n,r):
    """
        Calcule le terme *x* d'une loi hypergéométrique
        
        Le calcule est réalisé selon la méthode décrite dans l'article

        Trong Wu, An accurate computation of the hypergeometric distribution function, 
        ACM Trans. Math. Softw. 19 (1993), no. 1, 33–43.
         
        Paramètres:
        
        - `x` : Nombre d'éléments marqués attendu
        - `N` : La taille de la population
        - `n` : Le nombre d'éléments marqués
        - `r` : La taille de l'echantillon
            
        Retourne un *float* indiquant la probabilité de récupérer *x* éléments
        marqués parmi *n* dans une population de taille *N* lors du tirage
        d'un échantillon de taille *r*        
    """
    if n < r:
        s = n
        n = r
        r = s
    assert x>=0 and x <= r,"x out of limits"
    if x > 0 :
        return hypergeometric(x-1,N,n,r) * (n - x + 1)/x * (r - x + 1)/(N-n-r+x)
    else:
        return _hyper0(N,n,r)
        
def chypergeometric(xmin,xmax,N,n,r):
    """
        Calcule le terme *x* d'une loi hypergéométrique
        
        Le calcule est réalisé selon la méthode décrite dans l'article
        
        Trong Wu, An accurate computation of the hypergeometric distribution function, 
        ACM Trans. Math. Softw. 19 (1993), no. 1, 33–43.
             
        Paramètres:
        
        - `xmin` : Nombre d'éléments marqués minimum attendu
        - `xmax` : Nombre d'éléments marqués maximum attendu
        - `N` : La taille de la population
        - `n` : Le nombre d'éléments marqués
        - `r` : La taille de l'echantillon
            
        Retourne un *float* indiquant la probabilité de récupérer entre
        *xmin* et *xmax* éléments marqués parmi *n* dans une population 
        de taille *N* lors du tirage d'un échantillon de taille *r*     
    """
    if n < r:
        s = n
        n = r
        r = s
    assert xmin>=0 and xmin <= r and xmax>=0 and xmax <= r and xmin <=xmax,"x out of limits"
    hg  = hypergeometric(xmin,N,n,r)
    rep = hg
    for x in xrange(xmin+1,xmax+1):
        hg = hg * (n - x + 1)/x * (r - x + 1)/(N-n-r+x)
        rep+=hg
    return rep
    
def multipleTest(globalPvalue,testList):
    """
        Correction pour les tests multiples.
    
        Séléctionne parmis un ensemble de test le plus grand sous ensemble
        telque le risque global soit inférieur à une pvalue déterminée.

        Paramètres:
        
        - `globalPvalue` : Risque global à prendre pour l'ensemble des tests
        - `testList` : un élément itérable sur un ensemble de tests. 
          Chaque test est une liste ou un tuple dont le dernier élément
          est la pvalue associée au test
        
        Retourne une liste contenant le sous ensemble des tests selectionnés dans
        `testList`
    """
    testList=list(testList)
    testList.sort(lambda x,y:cmp(x[-1],y[-1]))
    h0=1.0-globalPvalue
    p=1.0
    rep = []
    for t in testList:
      p*=1.0-t[-1]
      if p > h0:
        rep.append(t)
    return rep
        