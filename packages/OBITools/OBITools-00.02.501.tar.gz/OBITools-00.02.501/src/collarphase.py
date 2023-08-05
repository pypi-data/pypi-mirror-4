#!/usr/local/bin/python
'''
Created on 25 mai 2010

@author: coissac
'''
from obitools.options import getOptionManager
from obitools.utils import ColumnFile
import datetime

def collarDate(s):
    return datetime.datetime.strptime(s,"%d.%m.%Y")

def collarTime(s):
    return datetime.datetime.strptime(s,"%H:%M:%S")

class CollarFileIterator(ColumnFile):
    def __init__(self,stream):
        ColumnFile.__init__(self,
                            stream, None, True, 
                              (collarDate,collarTime,
                               collarDate,collarTime,
                               int,int,int), "#")
        self._first=True
        
    def next(self):
        if self._first:
            self._first=False
            x="@@@@i"
            while (x[0:4]!='----'):
                x=self._stream.next()
            x=self._stream.next()
                
        gmtd,gmtt,lmtd,lmtt,x,y,c = ColumnFile.next(self)
        gmt = datetime.datetime.combine(gmtd,gmtt.time())
        lmt = datetime.datetime.combine(lmtd,lmtt.time())
        return {'GMT':gmt,'LMT':lmt,'x':x,'y':y,'temp':c}
    
def timeHash(t):
    return (t.minute + t.hour * 60) / 5 

if __name__ == '__main__':

    optionParser = getOptionManager([])
                                    
    (options, entries) = optionParser()
    
    data={}
    for entry in entries:
    