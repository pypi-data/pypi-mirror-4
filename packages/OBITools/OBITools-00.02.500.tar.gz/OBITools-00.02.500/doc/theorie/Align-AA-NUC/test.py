GLTWQRMYGCDILEDNSTRGVYQYAYNGRDFIALDMDTMTFTAADAAAQITKRKWEEDGT
VAEQWQHYLANTCIEWLRKYVSYGQAVLGRTGEGETGPGA


ggggtctaacgtggcagcggatgtacggctgtgacatcctggaggacaacagcaccaggggggtttatcagtatgcctacaatgggagggacttcatcgccctcgacatggacacgatgacgttcaccgcggcggacgcagcggcacagatcaccaagaggaagtgggaggaggacgggacggtcgctgagcagtggcagcactacctggcgaacacgtgcatcgagtggctgaggaaatacgtgagctacgggcaggccgtgctgggcaggacaggtgagggcgagacgggtcccggggccgg

import obitools.align._nwsdnabyprot as a
import obitools.align._nws as n
import obitools as o
s1=o.NucSequence('ref','gggtctaacgtggcagcggatgtacggctgtgacatc')
s2=o.NucSequence('ref','ggtctaacccgtggcagcggatgtacggctgatgacatc')
t=a.NWSDNAByProt(startingFrame=2)
g=n.NWS()
t.seqA=s1
t.seqB=s2
g.seqA=s1
g.seqB=s2
print g()
ali = t()
print ali
print ali[1]['frame']

