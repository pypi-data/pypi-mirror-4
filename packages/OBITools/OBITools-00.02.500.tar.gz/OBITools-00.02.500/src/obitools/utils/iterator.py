from itertools import chain

def uniqueChain(*args):
    see = set()
    for x in chain(*args):
        if x not in see:
            see.add(x)
            yield x