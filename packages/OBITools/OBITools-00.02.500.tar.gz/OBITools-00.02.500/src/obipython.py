#!/usr/local/bin/python
'''
Created on 23 janv. 2010

@author: coissac
'''
from IPython.Shell import IPShellEmbed    
from obitools.interactive import *

try:
    import numpy
    __with_numpy__=True
except ImportError:
    __with_numpy__=False
    
try:
    from matplotlib import *
    __with_matplotlib__=True
    matplotlib.interactive(True)
    from matplotlib.pyplot import *
except ImportError:
    __with_matplotlib__=False
    


obi_ns = dict(
    kissa = 15,
    koira = 16)

if __name__ == '__main__':
    ipshell = IPShellEmbed()
    ipshell.set_banner('OBIPython dev version')
    ipshell.old_banner2='coucou'
    ipshell()