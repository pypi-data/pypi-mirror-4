# -*- coding: latin1 -*-



from obitools import SVGdraw
import math

class Map(object):
    """
        Map represente une instance d'une carte genetique physique.
        Une telle carte est definie par la longueur de la sequence
        qui lui est associe.
        
        A une carte est associe un certain nombre de niveaux (Level)
        eux meme decoupe en sous-niveau (SubLevel)
        Les sous niveaux contiennent eux des features 
    """
    def __init__(self,name,seqlength,scale=1):
        """
            Constructeur d'une nouvelle carte 
            
            *Param*:
            
                name
                    nom de la carte
                    
                seqlength
                    longueur de la sequence associee a la carte
                    
                scale
                    echelle de la carte indicant combien de pixel
                    correspondent a une unite de la carte
        """
        self.name = name
        self.seqlength = seqlength
        self.scale = scale
        self.levels = {}
        self.basicHSize = 10
        
    def __str__(self):
        return '<%s>' % self.name
        
    def __getitem__(self,level):
        """
            retourne le niveau *level* de la carte et
            le cree s'il n'existe pas
        """
        if not isinstance(level,int):
            raise TypeError('level must be an non Zero integer value')
        elif level==0:
            raise AssertionError('Level cannot be set to 0')
        try:
            return self.levels[level]
        except KeyError:
            self.levels[level] = Level(level,self)
        return self.levels[level] 
        
    def getBasicHSize(self):
        """
            retourne la hauteur de base d'un element de cartographie
            exprimee en pixel
        """
        return self.basicHSize
        
    def getScale(self):
        """
            Retourne l'echelle de la carte en nombre de pixels par
            unite physique de la carte
        """
        return self.scale
    
        
                
    def getNegativeBase(self):
        return reduce(lambda x,y:x-y,[self.levels[z].getHeight() 
                                          for z in self.levels
                                          if z < 0],self.getHeight())
                                          
    def getPositiveBase(self):
        return self.getNegativeBase() - 3 * self.getBasicHSize()
    
    def getHeight(self):
        return reduce(lambda x,y:x+y,[z.getHeight() for z in self.levels.values()],0) \
               + 4 * self.getBasicHSize()
        
    def toXML(self,file=None,begin=0,end=None):
        dessin = SVGdraw.drawing()
        if end==None:
            end = self.seqlength
        hauteur= self.getHeight()
        largeur=(end-begin+1)*self.scale
        svg    = SVGdraw.svg((begin*self.scale,0,largeur,hauteur),
                             '%fpx' % (self.seqlength * self.scale),
                             '%dpx' % hauteur)
                             
        centre = self.getPositiveBase() + (1 + 1/4) * self.getBasicHSize()
        svg.addElement(SVGdraw.rect(0,centre,self.seqlength * self.scale,self.getBasicHSize()/2))
        for e in self.levels.values():
            svg.addElement(e.getElement())
        dessin.setSVG(svg)
        return dessin.toXml(file)
        
class Feature(object):
    pass
    
class Level(object):

    def __init__(self,level,map):
        if not isinstance(map,Map):
            raise AssertionError('map is not an instance of class Map')
        if level in map.levels:
            raise AssertionError('Level %d already define for map %s' % (level,map))
        else:
            map.levels[level] = self
        self.map = map
        self.level = level
        self.sublevels = {}
        
    def __getitem__(self,sublevel):
        """
            retourne le niveau *sublevel* du niveau en
            le creant s'il n'existe pas
        """
        if not isinstance(sublevel,int):
            raise TypeError('sublevel must be a positive integer value')
        elif sublevel<0:
            raise AssertionError('Level cannot be negative')
        try:
            return self.sublevels[sublevel]
        except KeyError:
            self.sublevels[sublevel] = SubLevel(sublevel,self)
        return self.sublevels[sublevel] 

    def getBase(self):
        if self.level < 0:
            base = self.map.getNegativeBase()
            base += reduce(lambda x,y:x+y,[self.map.levels[z].getHeight() 
                                           for z in self.map.levels
                                           if z <0 and z >= self.level],0)
            return base
        else:
            base = self.map.getPositiveBase() 
            base -= reduce(lambda x,y:x+y,[self.map.levels[z].getHeight() 
                                           for z in self.map.levels
                                           if z >0 and z < self.level],0)
            return base

    def getElement(self):
        objet = SVGdraw.group('level%d' % self.level)
        for e in self.sublevels.values():
            objet.addElement(e.getElement())
        return objet
        
         
            
    def getHeight(self):
        return reduce(lambda x,y:x+y,[z.getHeight() for z in self.sublevels.values()],0) \
               + 2 * self.map.getBasicHSize()
        
class SubLevel(object):

    def __init__(self,sublevel,level):
        if not isinstance(level,Level):
            raise AssertionError('level is not an instance of class Level')
        if level in level.sublevels:
            raise AssertionError('Sublevel %d already define for level %s' % (sublevel,level))
        else:
            level.sublevels[sublevel] = self
        self.level = level
        self.sublevel = sublevel
        self.features = {}
        
    def getHeight(self):
        return max([x.getHeight() for x in self.features.values()]+[0]) + 4 * self.level.map.getBasicHSize()

    def getBase(self):
        base = self.level.getBase()
        if self.level.level < 0:
            base -= self.level.getHeight() - 2 * self.level.map.getBasicHSize()
            base += reduce(lambda x,y:x+y,[self.level.sublevels[z].getHeight() 
                                           for z in self.level.sublevels
                                           if z <= self.sublevel],0)
            base -= 2* self.level.map.getBasicHSize()
        else:
            base -= reduce(lambda x,y:x+y,[self.level.sublevels[z].getHeight() 
                                           for z in self.level.sublevels
                                           if z < self.sublevel],0)
            base -= self.level.map.getBasicHSize()
        return base
    
    def getElement(self):
        base = self.getBase()
        objet = SVGdraw.group('sublevel%d' % self.sublevel)
        for e in self.features.values():
            objet.addElement(e.getElement(base))
        return objet
        
    def add(self,feature):
        if not isinstance(feature,Feature):
            raise TypeError('feature must be an instance oof Feature')
        if feature.name in self.features:
            raise AssertionError('A feature with the same name (%s) have already be insert in this sublevel'
                                 % feature.name)
        self.features[feature.name]=feature
        feature.sublevel=self
        
class SimpleFeature(Feature):
    
    def __init__(self,name,begin,end,visiblename=False,color=0):
        self.begin    = begin
        self.end      = end
        self.name     = name
        self.color    = color
        self.sublevel = None 
        self.visiblename=visiblename
        
    def getHeight(self):
        if not self.sublevel:
            raise AssertionError('Not affected Simple feature')
        if self.visiblename:
            return self.sublevel.level.map.getBasicHSize() * 2
        else:
            return self.sublevel.level.map.getBasicHSize() 
            
    def getElement(self,base):
        scale = self.sublevel.level.map.getScale()
        y     = base - self.sublevel.level.map.getBasicHSize()
        x     = self.begin * scale
        width = (self.end - self.begin + 1) * scale
        heigh = self.sublevel.level.map.getBasicHSize()
        
        objet = SVGdraw.rect(x,y,width,heigh,stroke=self.color)
        objet.addElement(SVGdraw.description(self.name))
        
        return objet

class BoxFeature(SimpleFeature):

    def getHeight(self):
        if not self.sublevel:
            raise AssertionError('Not affected Box feature')
        if self.visiblename:
            return self.sublevel.level.map.getBasicHSize() * 4
        else:
            return self.sublevel.level.map.getBasicHSize() * 3 
            
    def getElement(self,base):
        scale = self.sublevel.level.map.getScale()
        y     = base - self.sublevel.level.map.getBasicHSize() * 2
        x     = self.begin * scale
        width = (self.end - self.begin + 1) * scale
        height = self.sublevel.level.map.getBasicHSize() * 3
        
        objet = SVGdraw.rect(x,y,width,height,stroke=self.color,fill="none")
        objet.addElement(SVGdraw.description(self.name))
        
        return objet
         
class MultiPartFeature(Feature):
    
    def __init__(self,name,*args,**kargs):
        self.limits    = args
        self.name     = name
        try:
            self.color    = kargs['color']
        except KeyError:
            self.color    = "black"
                    
        try:
            self.visiblename=kargs['visiblename']
        except KeyError:
            self.visiblename=None

        try:
            self.flatlink=kargs['flatlink']
        except KeyError:
            self.flatlink=False

        try:
            self.roundlink=kargs['roundlink']
        except KeyError:
            self.roundlink=False

        self.sublevel = None 


    def getHeight(self):
        if not self.sublevel:
            raise AssertionError('Not affected Simple feature')
        if self.visiblename:
            return self.sublevel.level.map.getBasicHSize() * 3
        else:
            return self.sublevel.level.map.getBasicHSize() * 2

    def getElement(self,base):
        scale = self.sublevel.level.map.getScale()

        y     = base - self.sublevel.level.map.getBasicHSize()
        height = self.sublevel.level.map.getBasicHSize()
        objet = SVGdraw.group(self.name)
        for (debut,fin) in self.limits:
            x     = debut * scale
            width = (fin - debut + 1) * scale
            part = SVGdraw.rect(x,y,width,height,fill=self.color)
            objet.addElement(part)
            
        debut = self.limits[0][1]
        for (fin,next) in self.limits[1:]:
            debut*=scale
            fin*=scale
            path = SVGdraw.pathdata(debut,y + height / 2)
            delta = height / 2
            if self.roundlink:
                path.qbezier((debut+fin)/2, y - delta,fin,y + height / 2)
            else:
                if self.flatlink:
                    delta = - height / 2
                path.line((debut+fin)/2, y - delta)
                path.line(fin,y + height / 2)
            path = SVGdraw.path(path,fill="none",stroke=self.color)
            objet.addElement(path)
            debut = next
            
        objet.addElement(SVGdraw.description(self.name))
        
        return objet

class TagFeature(Feature):
    
    def __init__(self,name,begin,length,ratio,visiblename=False,color=0):
        self.begin    = begin
        self.length   = length
        self.ratio    = ratio
        self.name     = name
        self.color    = color
        self.sublevel = None 
        self.visiblename=visiblename
        
    def getHeight(self):
        if not self.sublevel:
            raise AssertionError('Not affected Tag feature')
        
        return self.sublevel.level.map.getBasicHSize()*11
             
    def getElement(self,base):
        scale = self.sublevel.level.map.getScale()
        height = math.floor(max(1,self.sublevel.level.map.getBasicHSize()* 10 * self.ratio))
        y     = base + self.sublevel.level.map.getBasicHSize() - height
        x     = self.begin * scale
        width = self.length * scale
        objet = SVGdraw.rect(x,y,width,height,stroke=self.color)
        objet.addElement(SVGdraw.description(self.name))
        
        return objet
         
if __name__ == '__main__':
    carte = Map('essai',20000,scale=0.5)
    carte[-1][0].add(SimpleFeature('toto',100,300))
    carte[1][0].add(SimpleFeature('toto',100,300))
    carte[1][1].add(SimpleFeature('toto',200,1000))

    carte[1][0].add(MultiPartFeature('bout',(1400,1450),(1470,1550),(1650,1800),color='red',flatlink=True))
    carte[1][0].add(MultiPartFeature('titi',(400,450),(470,550),(650,800),color='red',flatlink=True))
    carte[-1][1].add(MultiPartFeature('titi',(400,450),(470,550),(650,800),color='green'))
    carte[-1][2].add(MultiPartFeature('titi',(400,450),(470,550),(650,800),color='purple',roundlink=True))

    carte[-1][1].add(BoxFeature('tutu',390,810,color='purple'))
    carte[1][0].add(BoxFeature('tutu',390,810,color='red'))
    carte[2][0].add(TagFeature('t1',1400,20,0.8))
    carte[2][0].add(TagFeature('t2',1600,20,0.2))
    carte.basicHSize=6
    print carte.toXML('truc.svg',begin=0,end=1000)
    print carte.toXML('truc2.svg',begin=460,end=2000)

            
            
