'''
Created on 6 Nov. 2009

@author: coissac
'''
#@PydevCodeAnalysisIgnore

from _codonnws cimport * 


#TODO: change functions for translation and BLOSUM scores

#ftp://ftp.ncbi.nih.gov/entrez/misc/data/gc.prt
#
#Standard genetic code
#  name "Standard" ,
#  name "SGC0" ,
#  id 1 ,
#  ncbieaa  "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG",
#  sncbieaa "---M---------------M---------------M----------------------------"
#  -- Base1  TTTTTTTTTTTTTTTTCCCCCCCCCCCCCCCCAAAAAAAAAAAAAAAAGGGGGGGGGGGGGGGG
#  -- Base2  TTTTCCCCAAAAGGGGTTTTCCCCAAAAGGGGTTTTCCCCAAAAGGGGTTTTCCCCAAAAGGGG
#  -- Base3  TCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAGTCAG

#TODO : fonction completement cablee en dure a changer vite !
cdef char _translate(char c1, char c2, char c3):
    if c1=='a':
        if c2=='a':
            if c3=='a':
                return 'k'
            elif c3=='c':
                return 'n'
            elif c3=='g':
                return 'k'
            elif c3=='t':
                return 'n'
        elif c2=='c':
            if c3=='a':
                return 't'
            elif c3=='c':
                return 't'
            elif c3=='g':
                return 't'
            elif c3=='t':
                return 't'
        elif c2=='g':
            if c3=='a':
                return 'r'
            elif c3=='c':
                return 's'
            elif c3=='g':
                return 'r'
            elif c3=='t':
                return 's'
        elif c2=='t':
            if c3=='a':
                return 'i'
            elif c3=='c':
                return 'i'
            elif c3=='g':
                return 'm'
            elif c3=='t':
                return 'i'
    elif c1=='c':
        if c2=='a':
            if c3=='a':
                return 'q'
            elif c3=='c':
                return 'h'
            elif c3=='g':
                return 'q'
            elif c3=='t':
                return 'h'
        elif c2=='c':
            if c3=='a':
                return 'p'
            elif c3=='c':
                return 'p'
            elif c3=='g':
                return 'p'
            elif c3=='t':
                return 'p'
        elif c2=='g':
            if c3=='a':
                return 'r'
            elif c3=='c':
                return 'r'
            elif c3=='g':
                return 'r'
            elif c3=='t':
                return 'r'
        elif c2=='g':
            if c3=='a':
                return 'l'
            elif c3=='c':
                return 'l'
            elif c3=='g':
                return 'l'
            elif c3=='t':
                return 'l'
    elif c1=='g':
        if c2=='a':
            if c3=='a':
                return 'e'
            elif c3=='c':
                return 'd'
            elif c3=='g':
                return 'e'
            elif c3=='t':
                return 'd'
        elif c2=='c':
            if c3=='a':
                return 'a'
            elif c3=='c':
                return 'a'
            elif c3=='g':
                return 'a'
            elif c3=='t':
                return 'a'
        elif c2=='g':
            if c3=='a':
                return 'g'
            elif c3=='c':
                return 'g'
            elif c3=='g':
                return 'g'
            elif c3=='t':
                return 'g'
        elif c2=='t':
            if c3=='a':
                return 'v'
            elif c3=='c':
                return 'v'
            elif c3=='g':
                return 'v'
            elif c3=='t':
                return 'v'
    elif c1=='t':
        if c2=='a':
            if c3=='a':
                return '*'
            elif c3=='c':
                return 'y'
            elif c3=='g':
                return '*'
            elif c3=='t':
                return 'y'
        elif c2=='c':
            if c3=='a':
                return 's'
            elif c3=='c':
                return 's'
            elif c3=='g':
                return 's'
            elif c3=='t':
                return 's'
        elif c2=='g':
            if c3=='a':
                return '*'
            elif c3=='c':
                return 'c'
            elif c3=='g':
                return 'w'
            elif c3=='t':
                return 'c'
        elif c2=='t':
            if c3=='a':
                return 'l'
            elif c3=='c':
                return 'f'
            elif c3=='g':
                return 'l'
            elif c3=='t':
                return 'f'

    return '*'

#http://www.ncbi.nlm.nih.gov/Class/FieldGuide/BLOSUM62.txt
#
##  Matrix made by matblas from blosum62.iij
##  * column uses minimum score
##  BLOSUM Clustered Scoring Matrix in 1/2 Bit Units
##  Blocks Database = /data/blocks_5.0/blocks.dat
##  Cluster Percentage: >= 62
##  Entropy =   0.6979, Expected =  -0.5209
#   A  R  N  D  C  Q  E  G  H  I  L  K  M  F  P  S  T  W  Y  V  B  Z  X  *
#A  4 -1 -2 -2  0 -1 -1  0 -2 -1 -1 -1 -1 -2 -1  1  0 -3 -2  0 -2 -1  0 -4 
#R -1  5  0 -2 -3  1  0 -2  0 -3 -2  2 -1 -3 -2 -1 -1 -3 -2 -3 -1  0 -1 -4 
#N -2  0  6  1 -3  0  0  0  1 -3 -3  0 -2 -3 -2  1  0 -4 -2 -3  3  0 -1 -4 
#D -2 -2  1  6 -3  0  2 -1 -1 -3 -4 -1 -3 -3 -1  0 -1 -4 -3 -3  4  1 -1 -4 
#C  0 -3 -3 -3  9 -3 -4 -3 -3 -1 -1 -3 -1 -2 -3 -1 -1 -2 -2 -1 -3 -3 -2 -4 
#Q -1  1  0  0 -3  5  2 -2  0 -3 -2  1  0 -3 -1  0 -1 -2 -1 -2  0  3 -1 -4 
#E -1  0  0  2 -4  2  5 -2  0 -3 -3  1 -2 -3 -1  0 -1 -3 -2 -2  1  4 -1 -4 
#G  0 -2  0 -1 -3 -2 -2  6 -2 -4 -4 -2 -3 -3 -2  0 -2 -2 -3 -3 -1 -2 -1 -4 
#H -2  0  1 -1 -3  0  0 -2  8 -3 -3 -1 -2 -1 -2 -1 -2 -2  2 -3  0  0 -1 -4 
#I -1 -3 -3 -3 -1 -3 -3 -4 -3  4  2 -3  1  0 -3 -2 -1 -3 -1  3 -3 -3 -1 -4 
#L -1 -2 -3 -4 -1 -2 -3 -4 -3  2  4 -2  2  0 -3 -2 -1 -2 -1  1 -4 -3 -1 -4 
#K -1  2  0 -1 -3  1  1 -2 -1 -3 -2  5 -1 -3 -1  0 -1 -3 -2 -2  0  1 -1 -4 
#M -1 -1 -2 -3 -1  0 -2 -3 -2  1  2 -1  5  0 -2 -1 -1 -1 -1  1 -3 -1 -1 -4 
#F -2 -3 -3 -3 -2 -3 -3 -3 -1  0  0 -3  0  6 -4 -2 -2  1  3 -1 -3 -3 -1 -4 
#P -1 -2 -2 -1 -3 -1 -1 -2 -2 -3 -3 -1 -2 -4  7 -1 -1 -4 -3 -2 -2 -1 -2 -4 
#S  1 -1  1  0 -1  0  0  0 -1 -2 -2  0 -1 -2 -1  4  1 -3 -2 -2  0  0  0 -4 
#T  0 -1  0 -1 -1 -1 -1 -2 -2 -1 -1 -1 -1 -2 -1  1  5 -2 -2  0 -1 -1  0 -4 
#W -3 -3 -4 -4 -2 -2 -3 -2 -2 -3 -2 -3 -1  1 -4 -3 -2 11  2 -3 -4 -3 -2 -4 
#Y -2 -2 -2 -3 -2 -1 -2 -3  2 -1 -1 -2 -1  3 -3 -2 -2  2  7 -1 -3 -2 -1 -4 
#V  0 -3 -3 -3 -1 -2 -2 -3 -3  3  1 -2  1 -1 -2 -2  0 -3 -1  4 -3 -2 -1 -4 
#B -2 -1  3  4 -3  0  1 -1  0 -3 -4  0 -3 -3 -2  0 -1 -4 -3 -3  4  1 -1 -4 
#Z -1  0  0  1 -3  3  4 -2  0 -3 -3  1 -1 -3 -1  0 -1 -3 -2 -2  1  4 -1 -4 
#X  0 -1 -1 -1 -2 -1 -1 -1 -1 -1 -1 -1 -1 -1 -2  0  0 -2 -1 -1 -1 -1 -1 -4 
#* -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4 -4  1 
#

cdef double _blosum62(char c1_1, char c1_2, char c1_3, char c2_1, char c2_2, char c2_3):

    cdef char aa1 = _translate(c1_1, c1_2, c1_3)
    cdef char aa2 = _translate(c2_1, c2_2, c2_3)

    if aa1=="a" and aa2=="a":
        return 4
    if aa1=="a" and aa2=="r":
        return -1
    if aa1=="a" and aa2=="n":
        return -2
    if aa1=="a" and aa2=="d":
        return -2
    if aa1=="a" and aa2=="c":
        return 0
    if aa1=="a" and aa2=="q":
        return -1
    if aa1=="a" and aa2=="e":
        return -1
    if aa1=="a" and aa2=="g":
        return 0
    if aa1=="a" and aa2=="h":
        return -2
    if aa1=="a" and aa2=="i":
        return -1
    if aa1=="a" and aa2=="l":
        return -1
    if aa1=="a" and aa2=="k":
        return -1
    if aa1=="a" and aa2=="m":
        return -1
    if aa1=="a" and aa2=="f":
        return -2
    if aa1=="a" and aa2=="p":
        return -1
    if aa1=="a" and aa2=="s":
        return 1
    if aa1=="a" and aa2=="t":
        return 0
    if aa1=="a" and aa2=="w":
        return -3
    if aa1=="a" and aa2=="y":
        return -2
    if aa1=="a" and aa2=="v":
        return 0
    if aa1=="a" and aa2=="b":
        return -2
    if aa1=="a" and aa2=="z":
        return -1
    if aa1=="a" and aa2=="x":
        return 0
    if aa1=="a" and aa2=="*":
        return -4
    if aa1=="r" and aa2=="a":
        return -1
    if aa1=="r" and aa2=="r":
        return 5
    if aa1=="r" and aa2=="n":
        return 0
    if aa1=="r" and aa2=="d":
        return -2
    if aa1=="r" and aa2=="c":
        return -3
    if aa1=="r" and aa2=="q":
        return 1
    if aa1=="r" and aa2=="e":
        return 0
    if aa1=="r" and aa2=="g":
        return -2
    if aa1=="r" and aa2=="h":
        return 0
    if aa1=="r" and aa2=="i":
        return -3
    if aa1=="r" and aa2=="l":
        return -2
    if aa1=="r" and aa2=="k":
        return 2
    if aa1=="r" and aa2=="m":
        return -1
    if aa1=="r" and aa2=="f":
        return -3
    if aa1=="r" and aa2=="p":
        return -2
    if aa1=="r" and aa2=="s":
        return -1
    if aa1=="r" and aa2=="t":
        return -1
    if aa1=="r" and aa2=="w":
        return -3
    if aa1=="r" and aa2=="y":
        return -2
    if aa1=="r" and aa2=="v":
        return -3
    if aa1=="r" and aa2=="b":
        return -1
    if aa1=="r" and aa2=="z":
        return 0
    if aa1=="r" and aa2=="x":
        return -1
    if aa1=="r" and aa2=="*":
        return -4
    if aa1=="n" and aa2=="a":
        return -2
    if aa1=="n" and aa2=="r":
        return 0
    if aa1=="n" and aa2=="n":
        return 6
    if aa1=="n" and aa2=="d":
        return 1
    if aa1=="n" and aa2=="c":
        return -3
    if aa1=="n" and aa2=="q":
        return 0
    if aa1=="n" and aa2=="e":
        return 0
    if aa1=="n" and aa2=="g":
        return 0
    if aa1=="n" and aa2=="h":
        return 1
    if aa1=="n" and aa2=="i":
        return -3
    if aa1=="n" and aa2=="l":
        return -3
    if aa1=="n" and aa2=="k":
        return 0
    if aa1=="n" and aa2=="m":
        return -2
    if aa1=="n" and aa2=="f":
        return -3
    if aa1=="n" and aa2=="p":
        return -2
    if aa1=="n" and aa2=="s":
        return 1
    if aa1=="n" and aa2=="t":
        return 0
    if aa1=="n" and aa2=="w":
        return -4
    if aa1=="n" and aa2=="y":
        return -2
    if aa1=="n" and aa2=="v":
        return -3
    if aa1=="n" and aa2=="b":
        return 3
    if aa1=="n" and aa2=="z":
        return 0
    if aa1=="n" and aa2=="x":
        return -1
    if aa1=="n" and aa2=="*":
        return -4
    if aa1=="d" and aa2=="a":
        return -2
    if aa1=="d" and aa2=="r":
        return -2
    if aa1=="d" and aa2=="n":
        return 1
    if aa1=="d" and aa2=="d":
        return 6
    if aa1=="d" and aa2=="c":
        return -3
    if aa1=="d" and aa2=="q":
        return 0
    if aa1=="d" and aa2=="e":
        return 2
    if aa1=="d" and aa2=="g":
        return -1
    if aa1=="d" and aa2=="h":
        return -1
    if aa1=="d" and aa2=="i":
        return -3
    if aa1=="d" and aa2=="l":
        return -4
    if aa1=="d" and aa2=="k":
        return -1
    if aa1=="d" and aa2=="m":
        return -3
    if aa1=="d" and aa2=="f":
        return -3
    if aa1=="d" and aa2=="p":
        return -1
    if aa1=="d" and aa2=="s":
        return 0
    if aa1=="d" and aa2=="t":
        return -1
    if aa1=="d" and aa2=="w":
        return -4
    if aa1=="d" and aa2=="y":
        return -3
    if aa1=="d" and aa2=="v":
        return -3
    if aa1=="d" and aa2=="b":
        return 4
    if aa1=="d" and aa2=="z":
        return 1
    if aa1=="d" and aa2=="x":
        return -1
    if aa1=="d" and aa2=="*":
        return -4
    if aa1=="c" and aa2=="a":
        return 0
    if aa1=="c" and aa2=="r":
        return -3
    if aa1=="c" and aa2=="n":
        return -3
    if aa1=="c" and aa2=="d":
        return -3
    if aa1=="c" and aa2=="c":
        return 9
    if aa1=="c" and aa2=="q":
        return -3
    if aa1=="c" and aa2=="e":
        return -4
    if aa1=="c" and aa2=="g":
        return -3
    if aa1=="c" and aa2=="h":
        return -3
    if aa1=="c" and aa2=="i":
        return -1
    if aa1=="c" and aa2=="l":
        return -1
    if aa1=="c" and aa2=="k":
        return -3
    if aa1=="c" and aa2=="m":
        return -1
    if aa1=="c" and aa2=="f":
        return -2
    if aa1=="c" and aa2=="p":
        return -3
    if aa1=="c" and aa2=="s":
        return -1
    if aa1=="c" and aa2=="t":
        return -1
    if aa1=="c" and aa2=="w":
        return -2
    if aa1=="c" and aa2=="y":
        return -2
    if aa1=="c" and aa2=="v":
        return -1
    if aa1=="c" and aa2=="b":
        return -3
    if aa1=="c" and aa2=="z":
        return -3
    if aa1=="c" and aa2=="x":
        return -2
    if aa1=="c" and aa2=="*":
        return -4
    if aa1=="q" and aa2=="a":
        return -1
    if aa1=="q" and aa2=="r":
        return 1
    if aa1=="q" and aa2=="n":
        return 0
    if aa1=="q" and aa2=="d":
        return 0
    if aa1=="q" and aa2=="c":
        return -3
    if aa1=="q" and aa2=="q":
        return 5
    if aa1=="q" and aa2=="e":
        return 2
    if aa1=="q" and aa2=="g":
        return -2
    if aa1=="q" and aa2=="h":
        return 0
    if aa1=="q" and aa2=="i":
        return -3
    if aa1=="q" and aa2=="l":
        return -2
    if aa1=="q" and aa2=="k":
        return 1
    if aa1=="q" and aa2=="m":
        return 0
    if aa1=="q" and aa2=="f":
        return -3
    if aa1=="q" and aa2=="p":
        return -1
    if aa1=="q" and aa2=="s":
        return 0
    if aa1=="q" and aa2=="t":
        return -1
    if aa1=="q" and aa2=="w":
        return -2
    if aa1=="q" and aa2=="y":
        return -1
    if aa1=="q" and aa2=="v":
        return -2
    if aa1=="q" and aa2=="b":
        return 0
    if aa1=="q" and aa2=="z":
        return 3
    if aa1=="q" and aa2=="x":
        return -1
    if aa1=="q" and aa2=="*":
        return -4
    if aa1=="e" and aa2=="a":
        return -1
    if aa1=="e" and aa2=="r":
        return 0
    if aa1=="e" and aa2=="n":
        return 0
    if aa1=="e" and aa2=="d":
        return 2
    if aa1=="e" and aa2=="c":
        return -4
    if aa1=="e" and aa2=="q":
        return 2
    if aa1=="e" and aa2=="e":
        return 5
    if aa1=="e" and aa2=="g":
        return -2
    if aa1=="e" and aa2=="h":
        return 0
    if aa1=="e" and aa2=="i":
        return -3
    if aa1=="e" and aa2=="l":
        return -3
    if aa1=="e" and aa2=="k":
        return 1
    if aa1=="e" and aa2=="m":
        return -2
    if aa1=="e" and aa2=="f":
        return -3
    if aa1=="e" and aa2=="p":
        return -1
    if aa1=="e" and aa2=="s":
        return 0
    if aa1=="e" and aa2=="t":
        return -1
    if aa1=="e" and aa2=="w":
        return -3
    if aa1=="e" and aa2=="y":
        return -2
    if aa1=="e" and aa2=="v":
        return -2
    if aa1=="e" and aa2=="b":
        return 1
    if aa1=="e" and aa2=="z":
        return 4
    if aa1=="e" and aa2=="x":
        return -1
    if aa1=="e" and aa2=="*":
        return -4
    if aa1=="g" and aa2=="a":
        return 0
    if aa1=="g" and aa2=="r":
        return -2
    if aa1=="g" and aa2=="n":
        return 0
    if aa1=="g" and aa2=="d":
        return -1
    if aa1=="g" and aa2=="c":
        return -3
    if aa1=="g" and aa2=="q":
        return -2
    if aa1=="g" and aa2=="e":
        return -2
    if aa1=="g" and aa2=="g":
        return 6
    if aa1=="g" and aa2=="h":
        return -2
    if aa1=="g" and aa2=="i":
        return -4
    if aa1=="g" and aa2=="l":
        return -4
    if aa1=="g" and aa2=="k":
        return -2
    if aa1=="g" and aa2=="m":
        return -3
    if aa1=="g" and aa2=="f":
        return -3
    if aa1=="g" and aa2=="p":
        return -2
    if aa1=="g" and aa2=="s":
        return 0
    if aa1=="g" and aa2=="t":
        return -2
    if aa1=="g" and aa2=="w":
        return -2
    if aa1=="g" and aa2=="y":
        return -3
    if aa1=="g" and aa2=="v":
        return -3
    if aa1=="g" and aa2=="b":
        return -1
    if aa1=="g" and aa2=="z":
        return -2
    if aa1=="g" and aa2=="x":
        return -1
    if aa1=="g" and aa2=="*":
        return -4
    if aa1=="h" and aa2=="a":
        return -2
    if aa1=="h" and aa2=="r":
        return 0
    if aa1=="h" and aa2=="n":
        return 1
    if aa1=="h" and aa2=="d":
        return -1
    if aa1=="h" and aa2=="c":
        return -3
    if aa1=="h" and aa2=="q":
        return 0
    if aa1=="h" and aa2=="e":
        return 0
    if aa1=="h" and aa2=="g":
        return -2
    if aa1=="h" and aa2=="h":
        return 8
    if aa1=="h" and aa2=="i":
        return -3
    if aa1=="h" and aa2=="l":
        return -3
    if aa1=="h" and aa2=="k":
        return -1
    if aa1=="h" and aa2=="m":
        return -2
    if aa1=="h" and aa2=="f":
        return -1
    if aa1=="h" and aa2=="p":
        return -2
    if aa1=="h" and aa2=="s":
        return -1
    if aa1=="h" and aa2=="t":
        return -2
    if aa1=="h" and aa2=="w":
        return -2
    if aa1=="h" and aa2=="y":
        return 2
    if aa1=="h" and aa2=="v":
        return -3
    if aa1=="h" and aa2=="b":
        return 0
    if aa1=="h" and aa2=="z":
        return 0
    if aa1=="h" and aa2=="x":
        return -1
    if aa1=="h" and aa2=="*":
        return -4
    if aa1=="i" and aa2=="a":
        return -1
    if aa1=="i" and aa2=="r":
        return -3
    if aa1=="i" and aa2=="n":
        return -3
    if aa1=="i" and aa2=="d":
        return -3
    if aa1=="i" and aa2=="c":
        return -1
    if aa1=="i" and aa2=="q":
        return -3
    if aa1=="i" and aa2=="e":
        return -3
    if aa1=="i" and aa2=="g":
        return -4
    if aa1=="i" and aa2=="h":
        return -3
    if aa1=="i" and aa2=="i":
        return 4
    if aa1=="i" and aa2=="l":
        return 2
    if aa1=="i" and aa2=="k":
        return -3
    if aa1=="i" and aa2=="m":
        return 1
    if aa1=="i" and aa2=="f":
        return 0
    if aa1=="i" and aa2=="p":
        return -3
    if aa1=="i" and aa2=="s":
        return -2
    if aa1=="i" and aa2=="t":
        return -1
    if aa1=="i" and aa2=="w":
        return -3
    if aa1=="i" and aa2=="y":
        return -1
    if aa1=="i" and aa2=="v":
        return 3
    if aa1=="i" and aa2=="b":
        return -3
    if aa1=="i" and aa2=="z":
        return -3
    if aa1=="i" and aa2=="x":
        return -1
    if aa1=="i" and aa2=="*":
        return -4
    if aa1=="l" and aa2=="a":
        return -1
    if aa1=="l" and aa2=="r":
        return -2
    if aa1=="l" and aa2=="n":
        return -3
    if aa1=="l" and aa2=="d":
        return -4
    if aa1=="l" and aa2=="c":
        return -1
    if aa1=="l" and aa2=="q":
        return -2
    if aa1=="l" and aa2=="e":
        return -3
    if aa1=="l" and aa2=="g":
        return -4
    if aa1=="l" and aa2=="h":
        return -3
    if aa1=="l" and aa2=="i":
        return 2
    if aa1=="l" and aa2=="l":
        return 4
    if aa1=="l" and aa2=="k":
        return -2
    if aa1=="l" and aa2=="m":
        return 2
    if aa1=="l" and aa2=="f":
        return 0
    if aa1=="l" and aa2=="p":
        return -3
    if aa1=="l" and aa2=="s":
        return -2
    if aa1=="l" and aa2=="t":
        return -1
    if aa1=="l" and aa2=="w":
        return -2
    if aa1=="l" and aa2=="y":
        return -1
    if aa1=="l" and aa2=="v":
        return 1
    if aa1=="l" and aa2=="b":
        return -4
    if aa1=="l" and aa2=="z":
        return -3
    if aa1=="l" and aa2=="x":
        return -1
    if aa1=="l" and aa2=="*":
        return -4
    if aa1=="k" and aa2=="a":
        return -1
    if aa1=="k" and aa2=="r":
        return 2
    if aa1=="k" and aa2=="n":
        return 0
    if aa1=="k" and aa2=="d":
        return -1
    if aa1=="k" and aa2=="c":
        return -3
    if aa1=="k" and aa2=="q":
        return 1
    if aa1=="k" and aa2=="e":
        return 1
    if aa1=="k" and aa2=="g":
        return -2
    if aa1=="k" and aa2=="h":
        return -1
    if aa1=="k" and aa2=="i":
        return -3
    if aa1=="k" and aa2=="l":
        return -2
    if aa1=="k" and aa2=="k":
        return 5
    if aa1=="k" and aa2=="m":
        return -1
    if aa1=="k" and aa2=="f":
        return -3
    if aa1=="k" and aa2=="p":
        return -1
    if aa1=="k" and aa2=="s":
        return 0
    if aa1=="k" and aa2=="t":
        return -1
    if aa1=="k" and aa2=="w":
        return -3
    if aa1=="k" and aa2=="y":
        return -2
    if aa1=="k" and aa2=="v":
        return -2
    if aa1=="k" and aa2=="b":
        return 0
    if aa1=="k" and aa2=="z":
        return 1
    if aa1=="k" and aa2=="x":
        return -1
    if aa1=="k" and aa2=="*":
        return -4
    if aa1=="m" and aa2=="a":
        return -1
    if aa1=="m" and aa2=="r":
        return -1
    if aa1=="m" and aa2=="n":
        return -2
    if aa1=="m" and aa2=="d":
        return -3
    if aa1=="m" and aa2=="c":
        return -1
    if aa1=="m" and aa2=="q":
        return 0
    if aa1=="m" and aa2=="e":
        return -2
    if aa1=="m" and aa2=="g":
        return -3
    if aa1=="m" and aa2=="h":
        return -2
    if aa1=="m" and aa2=="i":
        return 1
    if aa1=="m" and aa2=="l":
        return 2
    if aa1=="m" and aa2=="k":
        return -1
    if aa1=="m" and aa2=="m":
        return 5
    if aa1=="m" and aa2=="f":
        return 0
    if aa1=="m" and aa2=="p":
        return -2
    if aa1=="m" and aa2=="s":
        return -1
    if aa1=="m" and aa2=="t":
        return -1
    if aa1=="m" and aa2=="w":
        return -1
    if aa1=="m" and aa2=="y":
        return -1
    if aa1=="m" and aa2=="v":
        return 1
    if aa1=="m" and aa2=="b":
        return -3
    if aa1=="m" and aa2=="z":
        return -1
    if aa1=="m" and aa2=="x":
        return -1
    if aa1=="m" and aa2=="*":
        return -4
    if aa1=="f" and aa2=="a":
        return -2
    if aa1=="f" and aa2=="r":
        return -3
    if aa1=="f" and aa2=="n":
        return -3
    if aa1=="f" and aa2=="d":
        return -3
    if aa1=="f" and aa2=="c":
        return -2
    if aa1=="f" and aa2=="q":
        return -3
    if aa1=="f" and aa2=="e":
        return -3
    if aa1=="f" and aa2=="g":
        return -3
    if aa1=="f" and aa2=="h":
        return -1
    if aa1=="f" and aa2=="i":
        return 0
    if aa1=="f" and aa2=="l":
        return 0
    if aa1=="f" and aa2=="k":
        return -3
    if aa1=="f" and aa2=="m":
        return 0
    if aa1=="f" and aa2=="f":
        return 6
    if aa1=="f" and aa2=="p":
        return -4
    if aa1=="f" and aa2=="s":
        return -2
    if aa1=="f" and aa2=="t":
        return -2
    if aa1=="f" and aa2=="w":
        return 1
    if aa1=="f" and aa2=="y":
        return 3
    if aa1=="f" and aa2=="v":
        return -1
    if aa1=="f" and aa2=="b":
        return -3
    if aa1=="f" and aa2=="z":
        return -3
    if aa1=="f" and aa2=="x":
        return -1
    if aa1=="f" and aa2=="*":
        return -4
    if aa1=="p" and aa2=="a":
        return -1
    if aa1=="p" and aa2=="r":
        return -2
    if aa1=="p" and aa2=="n":
        return -2
    if aa1=="p" and aa2=="d":
        return -1
    if aa1=="p" and aa2=="c":
        return -3
    if aa1=="p" and aa2=="q":
        return -1
    if aa1=="p" and aa2=="e":
        return -1
    if aa1=="p" and aa2=="g":
        return -2
    if aa1=="p" and aa2=="h":
        return -2
    if aa1=="p" and aa2=="i":
        return -3
    if aa1=="p" and aa2=="l":
        return -3
    if aa1=="p" and aa2=="k":
        return -1
    if aa1=="p" and aa2=="m":
        return -2
    if aa1=="p" and aa2=="f":
        return -4
    if aa1=="p" and aa2=="p":
        return 7
    if aa1=="p" and aa2=="s":
        return -1
    if aa1=="p" and aa2=="t":
        return -1
    if aa1=="p" and aa2=="w":
        return -4
    if aa1=="p" and aa2=="y":
        return -3
    if aa1=="p" and aa2=="v":
        return -2
    if aa1=="p" and aa2=="b":
        return -2
    if aa1=="p" and aa2=="z":
        return -1
    if aa1=="p" and aa2=="x":
        return -2
    if aa1=="p" and aa2=="*":
        return -4
    if aa1=="s" and aa2=="a":
        return 1
    if aa1=="s" and aa2=="r":
        return -1
    if aa1=="s" and aa2=="n":
        return 1
    if aa1=="s" and aa2=="d":
        return 0
    if aa1=="s" and aa2=="c":
        return -1
    if aa1=="s" and aa2=="q":
        return 0
    if aa1=="s" and aa2=="e":
        return 0
    if aa1=="s" and aa2=="g":
        return 0
    if aa1=="s" and aa2=="h":
        return -1
    if aa1=="s" and aa2=="i":
        return -2
    if aa1=="s" and aa2=="l":
        return -2
    if aa1=="s" and aa2=="k":
        return 0
    if aa1=="s" and aa2=="m":
        return -1
    if aa1=="s" and aa2=="f":
        return -2
    if aa1=="s" and aa2=="p":
        return -1
    if aa1=="s" and aa2=="s":
        return 4
    if aa1=="s" and aa2=="t":
        return 1
    if aa1=="s" and aa2=="w":
        return -3
    if aa1=="s" and aa2=="y":
        return -2
    if aa1=="s" and aa2=="v":
        return -2
    if aa1=="s" and aa2=="b":
        return 0
    if aa1=="s" and aa2=="z":
        return 0
    if aa1=="s" and aa2=="x":
        return 0
    if aa1=="s" and aa2=="*":
        return -4
    if aa1=="t" and aa2=="a":
        return 0
    if aa1=="t" and aa2=="r":
        return -1
    if aa1=="t" and aa2=="n":
        return 0
    if aa1=="t" and aa2=="d":
        return -1
    if aa1=="t" and aa2=="c":
        return -1
    if aa1=="t" and aa2=="q":
        return -1
    if aa1=="t" and aa2=="e":
        return -1
    if aa1=="t" and aa2=="g":
        return -2
    if aa1=="t" and aa2=="h":
        return -2
    if aa1=="t" and aa2=="i":
        return -1
    if aa1=="t" and aa2=="l":
        return -1
    if aa1=="t" and aa2=="k":
        return -1
    if aa1=="t" and aa2=="m":
        return -1
    if aa1=="t" and aa2=="f":
        return -2
    if aa1=="t" and aa2=="p":
        return -1
    if aa1=="t" and aa2=="s":
        return 1
    if aa1=="t" and aa2=="t":
        return 5
    if aa1=="t" and aa2=="w":
        return -2
    if aa1=="t" and aa2=="y":
        return -2
    if aa1=="t" and aa2=="v":
        return 0
    if aa1=="t" and aa2=="b":
        return -1
    if aa1=="t" and aa2=="z":
        return -1
    if aa1=="t" and aa2=="x":
        return 0
    if aa1=="t" and aa2=="*":
        return -4
    if aa1=="w" and aa2=="a":
        return -3
    if aa1=="w" and aa2=="r":
        return -3
    if aa1=="w" and aa2=="n":
        return -4
    if aa1=="w" and aa2=="d":
        return -4
    if aa1=="w" and aa2=="c":
        return -2
    if aa1=="w" and aa2=="q":
        return -2
    if aa1=="w" and aa2=="e":
        return -3
    if aa1=="w" and aa2=="g":
        return -2
    if aa1=="w" and aa2=="h":
        return -2
    if aa1=="w" and aa2=="i":
        return -3
    if aa1=="w" and aa2=="l":
        return -2
    if aa1=="w" and aa2=="k":
        return -3
    if aa1=="w" and aa2=="m":
        return -1
    if aa1=="w" and aa2=="f":
        return 1
    if aa1=="w" and aa2=="p":
        return -4
    if aa1=="w" and aa2=="s":
        return -3
    if aa1=="w" and aa2=="t":
        return -2
    if aa1=="w" and aa2=="w":
        return 11
    if aa1=="w" and aa2=="y":
        return 2
    if aa1=="w" and aa2=="v":
        return -3
    if aa1=="w" and aa2=="b":
        return -4
    if aa1=="w" and aa2=="z":
        return -3
    if aa1=="w" and aa2=="x":
        return -2
    if aa1=="w" and aa2=="*":
        return -4
    if aa1=="y" and aa2=="a":
        return -2
    if aa1=="y" and aa2=="r":
        return -2
    if aa1=="y" and aa2=="n":
        return -2
    if aa1=="y" and aa2=="d":
        return -3
    if aa1=="y" and aa2=="c":
        return -2
    if aa1=="y" and aa2=="q":
        return -1
    if aa1=="y" and aa2=="e":
        return -2
    if aa1=="y" and aa2=="g":
        return -3
    if aa1=="y" and aa2=="h":
        return 2
    if aa1=="y" and aa2=="i":
        return -1
    if aa1=="y" and aa2=="l":
        return -1
    if aa1=="y" and aa2=="k":
        return -2
    if aa1=="y" and aa2=="m":
        return -1
    if aa1=="y" and aa2=="f":
        return 3
    if aa1=="y" and aa2=="p":
        return -3
    if aa1=="y" and aa2=="s":
        return -2
    if aa1=="y" and aa2=="t":
        return -2
    if aa1=="y" and aa2=="w":
        return 2
    if aa1=="y" and aa2=="y":
        return 7
    if aa1=="y" and aa2=="v":
        return -1
    if aa1=="y" and aa2=="b":
        return -3
    if aa1=="y" and aa2=="z":
        return -2
    if aa1=="y" and aa2=="x":
        return -1
    if aa1=="y" and aa2=="*":
        return -4
    if aa1=="v" and aa2=="a":
        return 0
    if aa1=="v" and aa2=="r":
        return -3
    if aa1=="v" and aa2=="n":
        return -3
    if aa1=="v" and aa2=="d":
        return -3
    if aa1=="v" and aa2=="c":
        return -1
    if aa1=="v" and aa2=="q":
        return -2
    if aa1=="v" and aa2=="e":
        return -2
    if aa1=="v" and aa2=="g":
        return -3
    if aa1=="v" and aa2=="h":
        return -3
    if aa1=="v" and aa2=="i":
        return 3
    if aa1=="v" and aa2=="l":
        return 1
    if aa1=="v" and aa2=="k":
        return -2
    if aa1=="v" and aa2=="m":
        return 1
    if aa1=="v" and aa2=="f":
        return -1
    if aa1=="v" and aa2=="p":
        return -2
    if aa1=="v" and aa2=="s":
        return -2
    if aa1=="v" and aa2=="t":
        return 0
    if aa1=="v" and aa2=="w":
        return -3
    if aa1=="v" and aa2=="y":
        return -1
    if aa1=="v" and aa2=="v":
        return 4
    if aa1=="v" and aa2=="b":
        return -3
    if aa1=="v" and aa2=="z":
        return -2
    if aa1=="v" and aa2=="x":
        return -1
    if aa1=="v" and aa2=="*":
        return -4
    if aa1=="b" and aa2=="a":
        return -2
    if aa1=="b" and aa2=="r":
        return -1
    if aa1=="b" and aa2=="n":
        return 3
    if aa1=="b" and aa2=="d":
        return 4
    if aa1=="b" and aa2=="c":
        return -3
    if aa1=="b" and aa2=="q":
        return 0
    if aa1=="b" and aa2=="e":
        return 1
    if aa1=="b" and aa2=="g":
        return -1
    if aa1=="b" and aa2=="h":
        return 0
    if aa1=="b" and aa2=="i":
        return -3
    if aa1=="b" and aa2=="l":
        return -4
    if aa1=="b" and aa2=="k":
        return 0
    if aa1=="b" and aa2=="m":
        return -3
    if aa1=="b" and aa2=="f":
        return -3
    if aa1=="b" and aa2=="p":
        return -2
    if aa1=="b" and aa2=="s":
        return 0
    if aa1=="b" and aa2=="t":
        return -1
    if aa1=="b" and aa2=="w":
        return -4
    if aa1=="b" and aa2=="y":
        return -3
    if aa1=="b" and aa2=="v":
        return -3
    if aa1=="b" and aa2=="b":
        return 4
    if aa1=="b" and aa2=="z":
        return 1
    if aa1=="b" and aa2=="x":
        return -1
    if aa1=="b" and aa2=="*":
        return -4
    if aa1=="z" and aa2=="a":
        return -1
    if aa1=="z" and aa2=="r":
        return 0
    if aa1=="z" and aa2=="n":
        return 0
    if aa1=="z" and aa2=="d":
        return 1
    if aa1=="z" and aa2=="c":
        return -3
    if aa1=="z" and aa2=="q":
        return 3
    if aa1=="z" and aa2=="e":
        return 4
    if aa1=="z" and aa2=="g":
        return -2
    if aa1=="z" and aa2=="h":
        return 0
    if aa1=="z" and aa2=="i":
        return -3
    if aa1=="z" and aa2=="l":
        return -3
    if aa1=="z" and aa2=="k":
        return 1
    if aa1=="z" and aa2=="m":
        return -1
    if aa1=="z" and aa2=="f":
        return -3
    if aa1=="z" and aa2=="p":
        return -1
    if aa1=="z" and aa2=="s":
        return 0
    if aa1=="z" and aa2=="t":
        return -1
    if aa1=="z" and aa2=="w":
        return -3
    if aa1=="z" and aa2=="y":
        return -2
    if aa1=="z" and aa2=="v":
        return -2
    if aa1=="z" and aa2=="b":
        return 1
    if aa1=="z" and aa2=="z":
        return 4
    if aa1=="z" and aa2=="x":
        return -1
    if aa1=="z" and aa2=="*":
        return -4
    if aa1=="x" and aa2=="a":
        return 0
    if aa1=="x" and aa2=="r":
        return -1
    if aa1=="x" and aa2=="n":
        return -1
    if aa1=="x" and aa2=="d":
        return -1
    if aa1=="x" and aa2=="c":
        return -2
    if aa1=="x" and aa2=="q":
        return -1
    if aa1=="x" and aa2=="e":
        return -1
    if aa1=="x" and aa2=="g":
        return -1
    if aa1=="x" and aa2=="h":
        return -1
    if aa1=="x" and aa2=="i":
        return -1
    if aa1=="x" and aa2=="l":
        return -1
    if aa1=="x" and aa2=="k":
        return -1
    if aa1=="x" and aa2=="m":
        return -1
    if aa1=="x" and aa2=="f":
        return -1
    if aa1=="x" and aa2=="p":
        return -2
    if aa1=="x" and aa2=="s":
        return 0
    if aa1=="x" and aa2=="t":
        return 0
    if aa1=="x" and aa2=="w":
        return -2
    if aa1=="x" and aa2=="y":
        return -1
    if aa1=="x" and aa2=="v":
        return -1
    if aa1=="x" and aa2=="b":
        return -1
    if aa1=="x" and aa2=="z":
        return -1
    if aa1=="x" and aa2=="x":
        return -1
    if aa1=="x" and aa2=="*":
        return -4
    if aa1=="*" and aa2=="a":
        return -4
    if aa1=="*" and aa2=="r":
        return -4
    if aa1=="*" and aa2=="n":
        return -4
    if aa1=="*" and aa2=="d":
        return -4
    if aa1=="*" and aa2=="c":
        return -4
    if aa1=="*" and aa2=="q":
        return -4
    if aa1=="*" and aa2=="e":
        return -4
    if aa1=="*" and aa2=="g":
        return -4
    if aa1=="*" and aa2=="h":
        return -4
    if aa1=="*" and aa2=="i":
        return -4
    if aa1=="*" and aa2=="l":
        return -4
    if aa1=="*" and aa2=="k":
        return -4
    if aa1=="*" and aa2=="m":
        return -4
    if aa1=="*" and aa2=="f":
        return -4
    if aa1=="*" and aa2=="p":
        return -4
    if aa1=="*" and aa2=="s":
        return -4
    if aa1=="*" and aa2=="t":
        return -4
    if aa1=="*" and aa2=="w":
        return -4
    if aa1=="*" and aa2=="y":
        return -4
    if aa1=="*" and aa2=="v":
        return -4
    if aa1=="*" and aa2=="b":
        return -4
    if aa1=="*" and aa2=="z":
        return -4
    if aa1=="*" and aa2=="x":
        return -4
    if aa1=="*" and aa2=="*":
        return 1


cdef class CodonNWS(NWS):
            
    def __init__(self,match=2,mismatch=-3,opengap=-4,extgap=-1, phasedA = -1, phasedB = -1):#, AAmatrix=_blosum62, translationtable=None):
        NWS.__init__(self,match, mismatch, opengap, extgap)
        self._phasedA = -1 if phasedA == -1 else phasedA%3
        self._phasedB = -1 if phasedB == -1 else phasedB%3
        
    cdef double matchCodon(self, int h, int v):
        cdef double score
        cdef double match
        score = 0

        for i in range(3):
            match = iupacPartialMatch(self.hSeq.sequence[h-i-1],self.vSeq.sequence[v-i-1])
            score += match * self._match + (1-match) * self._mismatch
        bl = _blosum62(self.hSeq.sequence[h-1], self.hSeq.sequence[h-2], self.hSeq.sequence[h-3], self.vSeq.sequence[v-1], self.vSeq.sequence[v-2], self.vSeq.sequence[v-3])
        #print "MatchCodon","h=",h,"v=",v, "   ",\
        #                   ''.join(['%c'%(self.hSeq.sequence[h-3],),\
        #                   '%c'%(self.hSeq.sequence[h-2],),\
        #                   '%c'%(self.hSeq.sequence[h-1],)]),\
        #                   "  ",                           \
        #                   ''.join(['%c'%(self.vSeq.sequence[v-3],),\
        #                   '%c'%(self.vSeq.sequence[v-2],),\
        #                   '%c'%(self.vSeq.sequence[v-1])])
        #print '--> score = %d + %d'%(score,bl)                                           

        score += bl 
        return score

    cdef inline int colindex(self, int idx):
        return idx%(self._hlen()+1)
        
    cdef inline int rowindex(self, int idx):
        return idx/(self._hlen()+1)


    #on change la signification des infos dans la matrice path
    #on met l'indice de la cellule d'origine
    
    cdef double doAlignment(self) except? 0:
        cdef int i  # vertical index
        cdef int j  # horizontal index
        cdef int idx
        cdef int jump
        cdef int delta
        cdef double score 
        cdef double scoremax
        cdef int    path

        
        if self.needToCompute:
            self.allocate()
            self.reset()
            
            for j in range(1,self._hlen()+1):
                idx = self.index(j,0)
                self.matrix.matrix[idx].score = self._opengap + (self._extgap * (j-1))
                self.matrix.matrix[idx].path  = 0
                                
            for i in range(1,self._vlen()+1):
                idx = self.index(0,i)
                self.matrix.matrix[idx].score = self._opengap + (self._extgap * (i-1))
                self.matrix.matrix[idx].path  = 0
                
            for i in range(1,self._vlen()+1):
                for j in range(1,self._hlen()+1):
                    
                    # 1 - came from diagonal
                    idx = self.index(j-1,i-1)
                    # print "computing cell : %d,%d --> %d/%d" % (j,i,self.index(j,i),self.matrix.msize),
                    scoremax = self.matrix.matrix[idx].score + \
                               self.matchScore(j,i)
                    path = idx

                    # print "so=%f sd=%f sm=%f" % (self.matrix.matrix[idx].score,self.matchScore(j,i),scoremax),

                    # 1.1 - came from diagonal by aligning a codon with a codon
                    #print i, i%3, self._phasedB, i%3==self._phasedB
                    if (j-3)>=0 and (i-3)>=0 and (self._phasedB==-1 or (i%3)==self._phasedB) and (self._phasedA==-1 or (j%3)==self._phasedA):
                        idx = self.index(j-3,i-3)
                        contrib = self.matchCodon(j,i)
                        score = self.matrix.matrix[idx].score + \
                                contrib
                        
                        #print "so=%f sd=%f score=%f sm=%f" % (self.matrix.matrix[idx].score,contrib,score, scoremax)
                        
                        if score > scoremax : 
                            #print "putain trop bien !"
                            scoremax = score
                            path = idx


                    # 2 - open horizontal gap
                    idx = self.index(j-1,i)
                    score = self.matrix.matrix[idx].score + \
                            self._opengap
                    if score > scoremax : 
                        scoremax = score
                        path = idx
                    
                    # 3 - open vertical gap
                    idx = self.index(j,i-1)
                    score = self.matrix.matrix[idx].score + \
                            self._opengap
                    if score > scoremax : 
                        scoremax = score
                        path = idx
                        
                    # 4 - extend horizontal gap
                    jump = self.matrix.bestHJump[i]
                    if jump >= 0:
                        idx = self.index(jump,i)
                        delta = j-jump
                        score = self.matrix.matrix[idx].score + \
                                self._extgap * delta
                        if score > scoremax :
                            scoremax = score
                            path = idx 
                            
                    # 5 - extend vertical gap
                    jump = self.matrix.bestVJump[j]
                    if jump >= 0:
                        idx = self.index(j,jump)
                        delta = i-jump
                        score = self.matrix.matrix[idx].score + \
                                self._extgap * delta
                        if score > scoremax :
                            scoremax = score
                            path = idx 
    
                    idx = self.index(j,i)
                    self.matrix.matrix[idx].score = scoremax
                    self.matrix.matrix[idx].path  = path 

                    #si on a choisi l'ouverture de gap                    
                    if path == self.index(j,i-1):
                        self.matrix.bestVJump[j]=i
                    elif path == self.index(j-1,i):
                        self.matrix.bestHJump[i]=j
                    
        self.sequenceChanged=False
        self.scoreChanged=False

        idx = self.index(self._hlen(),self._vlen())
        return self.matrix.matrix[idx].score


    cdef void backtrack(self):
        #cdef list path=[]
        cdef int i
        cdef int j 
        cdef int p
        
        self.doAlignment()
        i=self._vlen()
        j=self._hlen()
        self.path=allocatePath(i,j,self.path)
        
        while (i or j):
            idx=self.matrix.matrix[self.index(j,i)].path
            ori_j = self.colindex(idx)
            ori_i = self.rowindex(idx)

            #print i,j

            if i-ori_i == 3 and j-ori_j == 3:
                #print 'on passe par un codon'
                p = 0
                
                self.path.path[self.path.length]=p
                self.path.length+=1

                self.path.path[self.path.length]=p
                self.path.length+=1
                
            elif i-ori_i == 1 and j-ori_j == 1:
                #print 'on passe par un match'
                p = 0
            elif i-ori_i == 0:
                #print 'on passe par un gap'
                p = (j-ori_j)
            elif j-ori_j == 0:
                #print 'on passe par un gap'
                p = -(i-ori_i)
            else:
                print "badaboum !"
 
            i = ori_i
            j = ori_j
           
            #print '->', i, j
           
            self.path.path[self.path.length]=p
            self.path.length+=1

        self.path.hStart=0
        self.path.vStart=0
        
                           
    property match:
        def __get__(self):
            return self._match
        
        def __set__(self,match):
            self._match=match 
            self.scoreChanged=True
            
    property mismatch:
        def __get__(self):
            return self._mismatch
        
        def __set__(self,mismatch):
            self._mismatch=mismatch 
            self.scoreChanged=True
 
        
           

