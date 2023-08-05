#!/usr/local/bin/python
# -*- coding: iso-8859-1 -*-
'''
Created on 8 juin 2009

@author: coissac

                    ': sls (type milieu)
                    : fourrages (type milieu) ---> recode en @
                    (: mŽgaphorbiais (type milieu)
                    -: Žboulis (type milieu)
                    
                    i: individu masquŽ
                    u: individu visible
                    
                    j: bouche masquŽe
                    k: bouche visible
                    
                    b: tte en bas
                    h: tte en haut
                    
                    c: couchŽ
                    d: debout
                    
                    m: nursing
                    l: arrt nursing
                    p: interaction
                    o: arrt interaction
                    t: miction
                    r: arrt miction
                    
                    a: bouchŽe
                    n: pas
                    
                    f: scratching
                    z: mastication
                    w: vigilance
                    x: grooming

'''

from obitools.options import getOptionManager
from obitools.utils import ColumnFile

accentgrave=chr(0xe8)
milieu={      "'" : "sls",
      "@" : "fourrage",
      "(" : "mŽegaphorbiais",
      "-" : "eboulis"
       }

instantanee = {'a': 'bouchee',
       'n': 'pas'
              }

actions =     { 'f': 'scratching',
                'z': 'mastication',
                'w': 'vigilance',
                'x': 'grooming'
              }

changementetat={
            'j': ('bouche',False),
            'k': ('bouche',True),
            
            'b': ('tete','basse'),
            'h': ('tete','haute'),
            
            'c': ('debout',False),
            'd': ('debout',True),
            
            'm': ('nursing',True),
            'l': ('nursing',False),
            
            'p': ('interaction',True),
            'o': ('interaction',False),
            
            't': ('miction',True),
            'r': ('miction',False)
}

visible='u'
invisible='i'
    
    
def printAnimal(animal):
    
    if animal['bouche']>=0:
        dbouche=animal['heure']-animal['bouche']
    else:
        dbouche=-1
    
    print '\t'.join(["%6.2f" % float(animal['heure']-animal['start']),
                     "%20s"  % animal['action'],
                     "%6.2f" % float(animal['duree']),
                     "%10s"  % animal['milieu'],
                     "%6.2f" % float(float(dbouche)),
                     ])


if __name__ == '__main__':

    optionParser = getOptionManager([], 
                                    entryIterator=None)
    
    (options, entries) = optionParser()
    
    data = ColumnFile(entries, ',', True, (str,str))
    colunmName = data.next()
    data = ColumnFile(entries, ',', True, (int,str))

    animal={
            'heure'  :None,
            'action' :None,
            'duree'  :None,
            'bouche' :None,
            'tete'   :None,
            'debout' :None,
            'nursing':False,
            'interaction':False,
            'miction':False,
            'milieu':None,
            'start':None
            }
    
    waiting=None
    cache=None
    bouche=0
    
    print "time\taction\tduration\tmilieu\thidden_mouth"
    
    for heure,action in data:
        
        if action=="EOF":
            break
        
        if animal['start'] is None:
            animal['start']=heure
                
        if cache is not None and action!=visible and action not in milieu:
            raise SyntaxError,"Visible action missing at time %d (action=%s)" % (heure,action)
        
        if cache is not None and action==visible:
#            assert action==visible,"Visible action must follow hidden action at time %d" % heure
            animal['action']="hidden"
            animal['heure']=cache[1]
            animal['duree']=(heure - cache[1])
            printAnimal(animal)
            cache=None
            
        elif action==visible:
            cache==None
            pass
        else:
            
            if waiting is not None:
                animal['action']=actions[waiting[0]]
                animal['heure']=waiting[1]
                animal['duree']=(heure - waiting[1])
                waiting=None
                
                if animal['action']=='mastication':
                    assert animal['bouche'],'action on hidden mouth'
                    
                printAnimal(animal)
                
            if action==accentgrave or action=='è':
                action='@'
            
            if action==invisible:
                cache=(action,heure)
                
            elif action in milieu:
                animal['milieu']=milieu[action]
                
            elif action in changementetat:
                animal[changementetat[action][0]]=changementetat[action][1]
                
                if changementetat[action][0]=="bouche" :
                    if changementetat[action][1]:
                        if bouche==1:
                            animal['action']='hidden_mouth'
                            animal['heure']=animal['bouche']
                            animal['duree']=(heure - animal['bouche'])
                            printAnimal(animal)
                        
                        bouche=0
                        animal['bouche']=-1
                    else:
                        animal['bouche']=heure
            elif action in actions:
                waiting=(action,heure)
            elif action in instantanee:
                animal['action']=instantanee[action]
                animal['heure']=heure
                animal['duree']=0
                
                if animal['action']=='bouchee':
                    assert animal['bouche'],'action on hidden mouth'

                printAnimal(animal)
            else:
                raise SyntaxError,"Unknown action %s at time %d" % (action,heure)    
