#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re

def grabchunks(text, opener, closer):
    """
    Get 'chunks' as marked by the specified opener and closer. Only the first
    level of chunks will be returned. These may contain similar chunks, which
    can be extracted by running the function again.
    
    This is a generator: to get an indexable list of the chunks, use
    list(grabchunks(...))
    
    Example usage:
    foo = "green <eggs <and>> multicoloured <spam>."
    for chunk in grabchunks(foo, "<",">"):
        print(chunk)
    # eggs <and>
    # spam
    """
    assert opener != closer, "Opener and closer must be different"
    if opener not in text:
        return
    openpoints = [m.start() for m in re.finditer(re.escape(opener), text)]
    closepoints = [m.start() for m in re.finditer(re.escape(closer), text)]
    while closepoints[0] < openpoints[0]:
        closepoints.pop(0) # Ignore any closers before first opener
    chunkstart = openpoints.pop(0) + len(opener) # Exclude opening tag
    inlevel = 1
    while (closepoints or openpoints):
        if openpoints and (openpoints[0] < closepoints[0]):
            if inlevel <= 0:
                chunkstart = openpoints.pop(0) + len(opener)
                inlevel = 0 # Ensure it doesn't become negative
            else:
                openpoints.pop(0)
            inlevel += 1
        else:
            chunkend = closepoints.pop(0)
            inlevel -= 1
            if inlevel == 0:
                yield text[chunkstart:chunkend]
      
def splitwithout(text, spliton, containermarks = ['"']):
    """Splits text in a similar manner to text.split(spliton), but ignoring
    spliton where it occurs between start and end markers. E.g. 
    'a,<b,c>' could be split into ['a', '<b,c>'], rather than ['a', '<b', 'c>'].

    You can specify any number of containers, and the text will only be split 
    where the delimiter occurs outside all of them.
    For each container, specifying a single string will apply it as a toggle,
    as in "simple quotation marks", while a 2-tuple can contain separate start
    and end markers (e.g. brackets), which can be nested: (1 (2(...))).
    
    Example usage:
    foo = 'Green, "Eggs, Spam", etc.'
    splitwithout(foo, ',')
    # ['Green', ' "Eggs, Spam"', ' etc.']

    bar = "Do | {{Re | {{Mi | Fa }}}} | Sol | <La | Ti> | Do"
    splitwithout(bar,'|', [('{{','}}'), ('<','>')])
    # ['Do ', ' {{Re | {{Mi | Fa }}}} ', ' Sol ', ' <La | Ti> ', ' Do']"""
    posssplitpoints = [m.start() for m in re.finditer(re.escape(spliton), text)]
    for containers in containermarks:
        if isinstance(containers, str): # Same opener and closer
            opener = containers
            closer = None
        else:   # Different opener and closer.
            opener, closer = containers
        openpoints = [m.start() for m in re.finditer(re.escape(opener), text)]
        splitpoints = []
        if closer and (closer != opener): #Separate opener and closer (can be nested)
            closepoints = [m.start() for m in re.finditer(re.escape(closer), text)]
            inlevel = 0
            prevpoint = 0
            for point in posssplitpoints:
                while openpoints and (openpoints[0] < point):
                    openpoints.pop(0)
                    inlevel += 1
                while closepoints and (closepoints[0] < point):
                    closepoints.pop(0)
                    inlevel -= 1
                inlevel = max(inlevel, 0) #Stop it becoming negative.
                if inlevel == 0:
                    splitpoints.append(point)
        else: # Same opener and closer
            within = 0
            prevpoint = 0
            for point in posssplitpoints:
                togglecount = sum(x < point for x in openpoints)
                openpoints = openpoints[togglecount:]
                within = (togglecount + within) % 2
                if not within:
                    splitpoints.append(point)
        posssplitpoints = splitpoints
        
    sections = []
    prevpoint = 0
    for point in splitpoints:
        sections.append(text[prevpoint:point])
        prevpoint = point + len(spliton)
    return sections + [text[prevpoint:]]
    
            
