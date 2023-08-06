"""GUI Tools for doing things (e.g. loading big files) in a background thread.

Instead of blocking the GUI for long running operations, we do them in a
separate thread, and show a progress bar for them.
"""
from .qt import QtCore, QtGui
from functools import partial
import os

from taxonome.taxa import file_jsonlines, file_csv

class ProgressTracker(QtCore.QObject):
    """An object to signal the progress of a long running operation.
    
    Designed to be connected to a QProgressBar.
    """
    done_steps = QtCore.Signal(int)
    new_max = QtCore.Signal(int)
    def __call__(self, done):
        "Signal how many steps are complete."
        self.done_steps.emit(done)
    
    def max(self, n):
        self.new_max.emit(n)

class Worker(QtCore.QThread):
    """A simple worker thread. Runs the passed function.
    """
    error_raised = QtCore.Signal(object)
    def __init__(self, func, parent=None):
        super().__init__(parent)
        self.func = func
    
    def __del__(self):
        self.wait()
    
    def run(self):
        try:
            self.func()
        except Exception as e:
            self.error_raised.emit(e)
    
    def withprogress(self, app, steps=0):
        """Add a QProgressBar to the statusbar of app to track the progress
        of this thread. The progress bar will count from 0 to steps.
        """
        progressbar = QtGui.QProgressBar(app)
        progressbar.setRange(0, steps)
        progressbar.setMaximumSize(150, 20)
        app.ui.statusbar.addPermanentWidget(progressbar)
        
        if steps:
            progresstracker = ProgressTracker()
            progresstracker.done_steps.connect(progressbar.setValue)
            progresstracker.new_max.connect(progressbar.setMaximum)
            self.func = partial(self.func, progress=progresstracker)
        else:
            progresstracker = None
        
        def _stopped():
            app.ui.statusbar.removeWidget(progressbar)
            app.ui.statusbar.clearMessage()
            app.workerthreads.discard(self)
            
        self.finished.connect(_stopped)
        self.terminated.connect(_stopped)
        app.workerthreads.add(self)

class Loader(Worker):
    """A worker thread to load a dataset and send it via an 'output' signal."""
    output = QtCore.Signal(str, object)
    
    def __init__(self, func, ds_name, parent=None):
        super().__init__(func, parent)
        self.ds_name = ds_name
    
    def run(self):
        try:
            out = self.func()
        except Exception as e:
            self.error_raised.emit(e)
        else:
            self.output.emit(self.ds_name, out)

def makeloader(app, loadfunc, ds_name, steps=0):
    """Load a dataset into app using a separate thread, showing a progress bar."""
    thread = Loader(loadfunc, ds_name)
    thread.withprogress(app, steps)
    thread.output.connect(app.add_dataset)
    thread.error_raised.connect(app.show_error)
    thread.start()
    
def load_csv(app, ds_name, filename, encoding, namefield, authfield):
    steps = os.stat(filename).st_size
    fileobj = open(filename, encoding=encoding, errors='replace', newline='')
    loadfunc = partial(file_csv.load_taxa, fileobj, namefield=namefield,
                                                           authfield=authfield)
    app.ui.statusbar.showMessage("Loading taxa from {} ...".format(filename))
    return makeloader(app, loadfunc, ds_name, steps)

def load_csv_synonyms(app, ds_name, filename, encoding, **kwargs):
    steps = os.stat(filename).st_size
    fileobj = open(filename, encoding=encoding, errors='replace', newline='')
    loadfunc = partial(file_csv.load_synonyms, fileobj, **kwargs)
    app.ui.statusbar.showMessage("Loading synonymy from {} ...".format(filename))
    return makeloader(app, loadfunc, ds_name, steps)

def load_csv_individuals(app, ds_name, filename, encoding, **kwargs):
    steps = os.stat(filename).st_size
    fileobj = open(filename, encoding=encoding, errors='replace', newline='')
    loadfunc = partial(file_csv.load_individuals, fileobj, **kwargs)
    app.ui.statusbar.showMessage("Loading individual records from {} ...".format(filename))
    return makeloader(app, loadfunc, ds_name, steps)

def load_jsonlines(app, ds_name, filename):
    steps = os.stat(filename).st_size
    fileobj = open(filename, encoding='utf-8', errors='replace')
    loadfunc = partial(file_jsonlines.load_taxa, fileobj)
    app.ui.statusbar.showMessage("Loading taxa from {} ...".format(filename))
    return makeloader(app, loadfunc, ds_name, steps)
