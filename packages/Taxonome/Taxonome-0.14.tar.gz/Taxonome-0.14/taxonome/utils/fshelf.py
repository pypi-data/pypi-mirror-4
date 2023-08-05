#!/usr/bin/python3
# -*- coding: utf-8 -*-
import shelve
import datetime
DEFAULT_EXPIRY = datetime.timedelta(days=7)

class ForgetfulShelf(shelve.DbfilenameShelf):
    def __init__(self, filename, flag='c', protocol=None, writeback=False,
                    expiry=DEFAULT_EXPIRY):
        super().__init__(filename, flag, protocol, writeback)
        self.expiry = expiry
        
    def __setitem__(self, key, value):
        value = (value, datetime.datetime.now())
        super().__setitem__(key, value)
    
    def __getitem__(self, key):
        value, timestamp = super().__getitem__(key)
        if (datetime.datetime.now() - timestamp) > self.expiry:
            del self[key]
            raise KeyError("Item expired in cache")
        return value
        
    def _get_with_timestamp(self, key):
        """Returns a 2-tuple of the value and the timestamp (as a
        datetime.datetime object).
        
        This will work even if the item has expired, but only if it hasn't
        been deleted. Attempting to access expired items with Cache[key] will
        delete them.
        """
        return super().__getitem__(key)
    
    def _set_with_timestamp(self, key, value, timestamp):
        """Override the automatic timestamping, using a datetime.datetime."""
        super().__setitem__(key, (value, timestamp))
    
    def _get_timestamp(self, key):
        """Just return the timestamp of a key in the database (whether or not
        it has expired).
        
        Will raise a KeyError if the key isn't there."""
        return self._get_with_timestamp(key)[1]
    
    def __contains__(self, key):
        if super().__contains__(key) and \
            (datetime.datetime.now() - self._get_timestamp(key)) < self.expiry:
                return True
        return False
    
    def append_to(self, key, value):
        """Add an item to a mutable list on the shelf. Simply retrieving
        and modifying a value will not write it back to the disk.
        
        If the key is not found on the shelf, it will be created, with
        the value in a new list.
        
        The timestamp will remain that of the oldest item."""
        if key in self:
            temp, timestamp = self._get_with_timestamp(key)
            temp.append(value)
                # Setting self[key] would use a new timestamp, so:
            self._set_with_timestamp(key, temp, timestamp)
        else: # Start a new list
            self[key] = [value]
        
    def clean_outdated(self):
        """Delete all items on the Shelf older than the expiry time. Returns
        the number of items deleted.
        
        This may be slow, as it scans every item in the database."""
        deleted = 0
        for key in self:
            print(key)
            if (datetime.datetime.now() - self._get_timestamp(key)) > self.expiry:
                del self[key]
                deleted += 1
        return deleted
                        