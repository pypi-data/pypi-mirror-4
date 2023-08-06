# -*- coding: utf8 -*-
from taxonome.taxa.base import Name
import csv
from collections import defaultdict

def _no_op(*args, **kwargs): pass

class NoopTracker:
    """This tracker doesn't do anything."""
    name_event = name_transform = start_taxon = reset = unreadable_name = _no_op

noop_tracker = NoopTracker()

class MultiTracker:
    """Holds a list of trackers, and calls the relevant methods of each of them
    when its methods are called."""
    def __init__(self, *args):
        self._trackers = list(args)
    
    def __getattr__(self, name):
        methods = [getattr(t, name) for t in self._trackers]
        def dispatch(*args, **kwargs):
            for m in methods:
                m(*args, **kwargs)
        return dispatch

def prepare_tracker(tracker):
    if isinstance(tracker, (list, tuple)):
        return MultiTracker(*tracker)
    if tracker is None:
        return noop_tracker
    return tracker

def add_tracker(current, new):
    if isinstance(current, MultiTracker):
        current._trackers.append(new)
        return current
    if current is noop_tracker:
        return new
    
    return MultiTracker(current, new)

def coroutine(func):
    """Decorator to prime coroutines"""
    def start(*args,**kwargs):
        cr = func(*args,**kwargs)
        next(cr)
        return cr
    return start

RESET = object()
@coroutine
def csvchainwriter(writer):
    """Coroutine to write lines to a csv file, incrementing a chain number until
    it's sent a reset signal."""
    chain = 0
    while True:
        line = (yield)
        if line is RESET:
            chain = 0
        else:
            writer.writerow((chain,) + tuple(line))
            chain += 1

def _flatten_name(name):
    if isinstance(name, Name):
        return name.plain, str(name.authority)
    return name, None

class CSVTracker(NoopTracker):
    """This writes events to a CSV file."""
    def __init__(self, fileobj, header=True):
        writer = csv.writer(fileobj)
        if header:
            writer.writerow(["sequence", "From name", "From authority", "To name", "To authority", "Event", "Details"])
        self.push = csvchainwriter(writer).send
        
    def name_event(self, name, event, **kwargs):
        self.push(_flatten_name(name) + (None, None, event, kwargs or None))
    
    def name_transform(self, name, newname, event, **kwargs):
        self.push(_flatten_name(name) + _flatten_name(newname) + (event, kwargs or None))
    
    def reset(self):
        self.push(RESET)
    
    def unreadable_name(self, rawname, error):
        self.push((rawname, None, None, None, 'error reading name', error))

class CSVListMatches(NoopTracker):
    """Writes the original name and final match to a CSV file."""
    fromname = None
    toname = None
    
    def __init__(self, fileobj, header=True):
        self.writer = csv.writer(fileobj)
        if header:
            self.writer.writerow(["Original Name","Original Authority","Name", "Authority", "Score"])
    
    def start_taxon(self, tax):
        self.fromname = tax.name
        self.fuzzyscore = 1
        
    def name_event(self, name, event):
        self.toname = None
    
    def name_transform(self, name, newname, event, **kwargs):
        self.toname = newname
        if event == 'fuzzy match':
            score = kwargs.get('score', 1)
            self.fuzzyscore = min(score, self.fuzzyscore)
    
    def reset(self):
        if self.fromname:
            score = (self.fuzzyscore,) if self.toname else (None,)
            self.writer.writerow(_flatten_name(self.fromname) + _flatten_name(self.toname) + score)
        self.fromname = None
        self.toname = None
    
    def unreadable_name(self, rawname, error):
        self.fromname = rawname

class Counter(NoopTracker):
    """Count the number of names seen so far. Callback with the number after
    every n (default 10).
    """
    def __init__(self, callback, every=10):
        self.callback = callback
        self.every = every
        self.n = 0
    
    def start_taxon(self, tax):
        self.n += 1
        if self.n % self.every == 0:
            self.callback(self.n)

class EventCounter(NoopTracker):
    def __init__(self):
        self.started = 0
        self.read_failed = 0
        self.events = defaultdict(int)
    
    def start_taxon(self, tax):
        self.started += 1
    
    def name_event(self, name, event):
        self.events[event] += 1
    
    def name_transform(self, name, newname, event, **kwargs):
        self.events[event] += 1
    
    def unreadable_name(self, rawname, error):
        self.read_failed += 1

class CSVTaxaTracker(NoopTracker):
    """Produces a list of the existing taxa data with the new names."""
    taxon = None
    newname = None
    
    def __init__(self, fileobj, fieldnames, header=True, include_unmatched=False):
        fieldnames = ["Name", "Authority", "Original name", "Original authority"]+fieldnames
        self.writer = csv.DictWriter(fileobj, fieldnames, extrasaction='ignore')
        if header:
            self.writer.writeheader()
        
        self.include_unmatched = include_unmatched
    
    def start_taxon(self, tax):
        self.taxon = tax
        self.fuzzyscore = 1
    
    def name_transform(self, name, newname, event, **kwargs):
        self.newname = newname
    
    def reset(self):
        if self.taxon and (self.newname or self.include_unmatched):
            d = dict(self.taxon.info)
            d['Original name'], d['Original authority'] = _flatten_name(self.taxon.name)
            d['Name'], d['Authority']= _flatten_name(self.newname)
            self.writer.writerow(d)
        
        self.taxon = None
        self.newname = None
    
    def unreadable_name(self, rawname, error):
        if self.include_unmatched:
            self.writer.writerow({'Original name':rawname})

class CacheTracker(NoopTracker):
    """For internal use: cache matching results so they can be reused."""
    def __init__(self):
        self.cache = {}
    
    def start_taxon(self, tax):
        self.fromname = tax.name
        self.toname = None
        self.events = []
    
    def reset(self):
        if self.fromname not in self.cache:
            self.cache[self.fromname] = self.events, self.toname
    
    def retrieve(self, fromname, tracker):
        """Retrieve a previously-seen name, and replay its events to the
        tracker.
        
        Raises KeyError if the name hasn't been seen before.
        """
        events, toname = self.cache[fromname]
        for meth, *args, kwargs in events:
            getattr(tracker, meth)(*args, **kwargs)
    
    def name_event(self, name, event, **kwargs):
        if event == 'no match':
            self.toname = None
        self.events.append(('name_event', name, event, kwargs))
    
    def name_transform(self, name, newname, event, **kwargs):
        self.toname = newname
        self.events.append(('name_transform', name, newname, event, kwargs))
        
        
        
        
        
        
        
        
        
        
        
        
        
        
