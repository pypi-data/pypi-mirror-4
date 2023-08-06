#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import shelve

from .collection import TaxonSet

class TaxonShelf(TaxonSet):
    """A persistent version of TaxonSet, storing items using the shelve module.
    
    Initialise using the the name of a database, e.g.:
    mygenus = taxonome.taxon.TaxonShelf("mygenus")
    
    The database consists of two files, with the suffixes "-names" and "-taxa".
    If they do not exist, they will be created.
    
    Modifying taxa on the shelf won't work--instead, make a temporary
    copy of the taxon, then put it back on the shelf:
    temp = myshelf[Name("Lablab purpureus","(L.) Sweet")]
    temp.distribution.add("Somewhere")
    myshelf.add(temp)
    
    N.B. If you change the accepted name of a taxon, you will need to remove
    the old taxon
    """
    def __init__(self, db_name):
        self.names = shelve.open(db_name+"-names")
        self.taxa = shelve.open(db_name+"-taxa")
        
    def sync(self):
        self.names.sync()
        self.taxa.sync()
    
    def __del__(self):
        self.names.close()
        self.taxa.close()
        
    def _add_qname(self, qname, acceptedname=None):
        """Add a qualified name to the index. To add a synonym, specify an
        acceptedname to which it maps. The acceptedname should refer to a taxon
        which is in the set.
        """
        if not acceptedname:
            acceptedname = qname
        if not qname.plain in self.names:
            self.names[qname.plain] = [(qname, acceptedname)]
        else:
            temp = self.names[qname.plain]
            temp.append((qname, acceptedname))
            self.names[qname.plain] = temp
            
    def _del_qname(self, qname):
        """Remove a qualified name from the index. Taxa with no remaining
        names in the index will still take up space, but cannot easily be
        accessed, so you should ensure that at least one name remains for each.
        """
        temp = self.names[qname.plain]
        for namematch in temp:
            if namematch[0] == qname:
                temp.remove(namematch)
                if temp:
                    self.names[qname.plain] = temp
                else:
                    del self.names[qname.plain]
                return namematch[1]
        raise KeyError(qname)
