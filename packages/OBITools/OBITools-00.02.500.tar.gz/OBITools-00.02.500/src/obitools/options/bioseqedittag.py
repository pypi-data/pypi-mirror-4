import sys
from obitools.options.taxonomyfilter import loadTaxonomyDatabase
import math

def addSequenceEditTagOptions(optionManager):
    
    optionManager.add_option('--rank',
                             action="store_true", dest='addrank',
                             default=False,
                             help="add a rank attribute to the sequence "
                                  "indicating the sequence position in the input data")

    optionManager.add_option('-R','--rename-tag',
                             action="append", 
                             dest='renameTags',
                             metavar="<OLD_NAME:NEW_NAME>",
                             type="string",
                             default=[],
                             help="change tag name from OLD_NAME to NEW_NAME")

    optionManager.add_option('--delete-tag',
                             action="append", 
                             dest='deleteTags',
                             metavar="<TAG_NAME>",
                             type="string",
                             default=[],
                             help="delete tag TAG_NAME")

    optionManager.add_option('-S','--set-tag',
                             action="append", 
                             dest='setTags',
                             metavar="<TAG_NAME:PYTHON_EXPRESSION>",
                             type="string",
                             default=[],
                             help="Add a new tag named TAG_NAME with "
                                  "a value computed from PYTHON_EXPRESSION")

    optionManager.add_option('--set-identifier',
                             action="store", 
                             dest='setIdentifier',
                             metavar="<PYTHON_EXPRESSION>",
                             type="string",
                             default=None,
                             help="Set sequence identifier with "
                                  "a value computed from PYTHON_EXPRESSION")

    optionManager.add_option('--set-sequence',
                             action="store", 
                             dest='setSequence',
                             metavar="<PYTHON_EXPRESSION>",
                             type="string",
                             default=None,
                             help="Change the sequence itself with "
                                  "a value computed from PYTHON_EXPRESSION")

    optionManager.add_option('-T','--set-definition',
                             action="store", 
                             dest='setDefinition',
                             metavar="<PYTHON_EXPRESSION>",
                             type="string",
                             default=None,
                             help="Set sequence definition with "
                                  "a value computed from PYTHON_EXPRESSION")
    
    optionManager.add_option('-O','--only-valid-python',
                             action="store_true", 
                             dest='onlyValid',
                             default=False,
                             help="only valid python expressions are allowed")
    
    optionManager.add_option('-C','--clear',
                             action="store_true", 
                             dest='clear',
                             default=False,
                             help="clear all tags associated to the sequences")
    
    optionManager.add_option('-k','--keep',
                             action='append',
                             dest='keep',
                             default=[],
                             type="string",
                             help="only keep this tag")
    
    optionManager.add_option('--length',
                             action="store_true", 
                             dest='length',
                             default=False,
                             help="add seqLength tag with sequence length")
    
    optionManager.add_option('--with-taxon-at-rank',
                             action='append',
                             dest='taxonrank',
                             default=[],
                             type="string",
                             help="add taxonomy annotation at a speciefied rank level")
    
    optionManager.add_option('-m','--mcl',
                             action="store", dest="mcl",
                             metavar="<mclfile>",
                             type="string",
                             default=None,
                             help="split following mcl graph clustering partition")
    

def readMCLFile(file):
    partition=1
    parts = {}
    for l in file:
        for seq in l.strip().split():
            parts[seq]=partition
        partition+=1
    return parts
        



def sequenceTaggerGenerator(options):
    toDelete = options.deleteTags[:]
    toRename = [x.split(':',1) for x in options.renameTags if len(x.split(':',1))==2]
    toSet    = [x.split(':',1) for x in options.setTags if len(x.split(':',1))==2]
    newId    = options.setIdentifier
    newDef   = options.setDefinition
    newSeq   = options.setSequence
    clear    = options.clear
    keep     = set(options.keep)
    length   = options.length
    counter  = [0]
    loadTaxonomyDatabase(options)
    if options.taxonomy is not None:
        annoteRank=options.taxonrank
    else:
        annoteRank=[]

    if options.mcl is not None:
        parts = readMCLFile(open(options.mcl))
    else:
        parts = False
    
    def sequenceTagger(seq):
        
        if counter[0]>=0:
            counter[0]+=1
        
        if clear or keep:
            ks = seq.keys()
            for k in ks:
                if k not in keep:
                    del seq[k]
        else:
            for i in toDelete:
                if i in seq:
                    del seq[i]                
            for o,n in toRename:
                if o in seq:
                    seq[n]=seq[o]
                    del seq[o]
                    
        for rank in annoteRank:
            if 'taxid' in seq:
                taxid = seq['taxid']
                if taxid is not None:
                    rtaxid = options.taxonomy.getTaxonAtRank(taxid,rank)
                    if rtaxid is not None:
                        scn = options.taxonomy.getScientificName(rtaxid)
                    else:
                        scn=None
                    seq[rank]=rtaxid
                    seq["%s_name"%rank]=scn 
                    
        if parts and seq.id in parts:   
            seq['cluster']=parts[seq.id]
            
        if options.addrank:
            seq['rank']=counter[0]

        for i,v in toSet:
            try:
                if options.taxonomy is not None:
                    environ = {'taxonomy' : options.taxonomy,'sequence':seq, 'counter':counter[0], 'math':math}
                else:
                    environ = {'sequence':seq, 'counter':counter[0], 'math':math}
                
                val = eval(v,environ,seq)
            except Exception,e:
                if options.onlyValid:
                    raise e
                val = v
            seq[i]=val
            
        if length:
            seq['seqLength']=len(seq)
            
        if newId is not None:
            try:
                if options.taxonomy is not None:
                    environ = {'taxonomy' : options.taxonomy,'sequence':seq, 'counter':counter[0], 'math':math}
                else:
                    environ = {'sequence':seq, 'counter':counter[0], 'math':math}
                
                val = eval(newId,environ,seq)
            except Exception,e:
                if options.onlyValid:
                    raise e
                val = newId
            seq.id=val
        if newDef is not None:
            try:
                if options.taxonomy is not None:
                    environ = {'taxonomy' : options.taxonomy,'sequence':seq, 'counter':counter[0], 'math':math}
                else:
                    environ = {'sequence':seq, 'counter':counter[0], 'math':math}
                
                val = eval(newDef,environ,seq)
            except Exception,e:
                if options.onlyValid:
                    raise e
                val = newDef
            seq.definition=val
            
        if newSeq is not None:
            try:
                if options.taxonomy is not None:
                    environ = {'taxonomy' : options.taxonomy,'sequence':seq, 'counter':counter[0], 'math':math}
                else:
                    environ = {'sequence':seq, 'counter':counter[0], 'math':math}
                
                val = eval(newSeq,environ,seq)
            except Exception,e:
                if options.onlyValid:
                    raise e
                val = newSeq
            if hasattr(seq, '_seq'):
                seq._seq=str(val).lower()
                if 'seqLength' in seq:
                    seq['seqLength']=len(seq)
            
        return seq
    
    return sequenceTagger