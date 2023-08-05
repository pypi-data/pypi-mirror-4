cpdef object fastaParser(bytes  seq,
                         object bioseqfactory,
                         object tagparser,
                         bytes  rawparser,
                         object joinseq=?)

cpdef object fastFastaParser(bytes  seq,
                             object tagparser,
                             bytes  rawparser)
                             
cpdef tuple fastParseFastaDescription(bytes ds)
cpdef tuple parseFastaDescription(bytes ds, object tagparser)                             
                         