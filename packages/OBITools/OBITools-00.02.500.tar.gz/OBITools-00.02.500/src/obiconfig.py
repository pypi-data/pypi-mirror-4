#!/usr/local/bin/python
'''
Created on 23 mai 2010

@author: coissac
'''

import sys
import os

if __name__ == '__main__':
    python = sys.executable
    os.execv(python, sys.argv[1:])
    