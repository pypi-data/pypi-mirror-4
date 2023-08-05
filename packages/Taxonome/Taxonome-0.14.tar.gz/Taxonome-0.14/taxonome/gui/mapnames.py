"""GUI Dialogs for mapping one set of names to another.
"""
import csv
import os.path
from functools import partial

from .qt import QtGui, QtCore

from taxonome.taxa import match_taxa
from taxonome.taxa import file_csv
from taxonome.taxa.collection import run_match_taxa
from taxonome import tracker
from .ui.map_names_wizard import Ui_MapNamesWizard
from .csvdialogs import CsvImportDialog, supported_encodings
from .iothread import Worker, makeloader

class MapNamesWizard(QtGui.QWizard, CsvImportDialog):
    def __init__(self, app=None):
        QtGui.QWizard.__init__(self, parent=app)
        self.ui = Ui_MapNamesWizard()
        self.ui.setupUi(self)
        
        # Hook up to main application
        self.app = app
        if app:
            self.lastdir = app.lastdir
            self.ui.taxa_dataset.setModel(app.datasets_model)
            self.ui.target_dataset.setModel(app.datasets_model)
        else:
            self.lastdir = os.path.expanduser("~")
        
        # When should we skip certain pages?
        self.ui.datasets_page.nextId = self.select_dataset_next_page
        self.ui.csv_import_page.nextId = self.csv_opts_next_page
        
        # Encoding switcher for CSV file
        # The signal from QComboBox is overloaded - we want the str form
        self.ui.csv_encoding.addItems(supported_encodings)
        QtCore.QObject.connect(self.ui.csv_encoding,
            QtCore.SIGNAL("currentIndexChanged(QString)"), self.encoding_changed)
        
        # Browse buttons for input & output files
        self.ui.from_csv_browse.clicked.connect(self.select_csv_in)
        self.ui.taxadata_browse.clicked.connect(self._select_save_location(self.ui.taxadata_file))
        self.ui.mappings_browse.clicked.connect(self._select_save_location(self.ui.mappings_file))
        self.ui.log_browse.clicked.connect(self._select_save_location(self.ui.log_file))
    
    def select_csv_in(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, "Select big CSV file",
                                    self.lastdir, "CSV (*.csv);;All files (*.*)")
        if not filename:
            return
        self.ui.from_csv_file.setText(filename)
        self.preview_file()
    
    @property
    def filename(self):
        """Return the CSV input filename, for the methods relating to that."""
        return self.ui.from_csv_file.text()
    
    def select_dataset_next_page(self):
        """Skip the CSV import page if we're using taxa from a local dataset."""
        if self.ui.from_csv.isChecked():
            return 1
        else:
            return self.csv_opts_next_page()
    
    def csv_opts_next_page(self):
        """Skip the matching options if we're using TNRS."""
        return 3 if self.ui.to_tnrs.isChecked() else 2

    def _select_save_location(self, destination):
        """Make a function to get an output filename and put it in a text box."""
        def inner():
            filename = QtGui.QFileDialog.getSaveFileName(self, "Save file to:",
                                self.lastdir, "CSV (*.csv);;All files (*.*)")
            if filename:
                if self.app:
                    self.app.lastdir = os.path.dirname(filename)
                
                if not os.path.splitext(filename)[1]:
                    filename += '.csv'
                destination.setText(filename)
        return inner
    
    # Properties to see which radio button is selected
    @property
    def upgrade_option(self):
        if self.ui.upgrade_all.isChecked():
            return 'all'
        elif self.ui.upgrade_none.isChecked():
            return 'none'
        else:
            return 'nominal'
    
    @property
    def preferaccepted_option(self):
        if self.ui.preferaccepted_all.isChecked():
            prefer_accepted = 'all'
        elif self.ui.preferaccepted_none.isChecked():
            prefer_accepted = 'none'
        else:
            prefer_accepted = 'noauth'

def wizard_map_names(app):
    """Match a big dataset (a CSV file, can be too big to hold in memory) against
    one of the loaded datasets.
    
    Presents the user with a set of options for controlling input, matching and
    output.
    """
    wizard = MapNamesWizard(app)
    
    # Run the wizard
    if not wizard.exec_():
        return False
    
    # Get the options ---------------------------------------------------------
    seln = wizard.ui.target_dataset.currentIndex()       # 1. From & to
    target = app.datasets_model.item(seln)
    if wizard.ui.from_csv.isChecked():
        csv_filename = wizard.ui.from_csv_file.text()
        from_csv = True
    else:
        seln = wizard.ui.taxa_dataset.currentIndex()
        dataset_item = app.datasets_model.item(seln)
        taxa_dataset = dataset_item.ds
        from_csv = False
    to_tnrs = wizard.ui.to_tnrs.isChecked()
    
    namefield = wizard.ui.namefield.currentText()         # 2. CSV
    authfield = wizard.get_auth_field()
    csv_encoding = wizard.ui.csv_encoding.currentText()
    
    upgrade = wizard.upgrade_option                       # 3. Matching options
    prefer_accepted = wizard.preferaccepted_option
    strict_authority = not wizard.ui.auth_lax.isChecked()
    user_choice = wizard.ui.user_choice.isChecked()
    
    taxadata_file, mappings_file, log_file = None, None, None  # 4. Output
    if wizard.ui.taxadata.isChecked():
        taxadata_file = wizard.ui.taxadata_file.text()
    if wizard.ui.mappings.isChecked():
        mappings_file = wizard.ui.mappings_file.text()
    if wizard.ui.log.isChecked():
        log_file = wizard.ui.log_file.text()
    matched_ds = wizard.ui.matched_ds.isChecked()
    
    # Prepare for matching ----------------------------------------------------
    nameselector = app.gui_select_name if user_choice else app.silent_select_name
    
    trackers = []
    files = []
    if mappings_file:
        f = open(mappings_file, "w", encoding='utf-8', newline='')
        files.append(f)
        trackers.append(tracker.CSVListMatches(f))
    if log_file:
        f = open(log_file, "w", encoding='utf-8', newline='')
        files.append(f)
        trackers.append(tracker.CSVTracker(f))
    if taxadata_file:
        if from_csv:
            with open(csv_filename, encoding=csv_encoding, errors='replace', newline='') as f:
                fields = next(csv.reader(f))
            fields.remove(namefield)
            if isinstance(authfield, str):
                fields.remove(authfield)
        else:
            fields = set()
            for t in taxa_dataset: fields.update(t.info)
            fields = list(fields)
        f = open(taxadata_file, "w", encoding='utf-8', newline='')
        files.append(f)
        trackers.append(tracker.CSVTaxaTracker(f, fields))
    
    def _run(progress=None):
        """Called in a separate thread to run the matching."""
        if from_csv:
            csvfile = open(csv_filename, encoding=csv_encoding, errors='replace')
            files.append(csvfile)
            data_in = file_csv.iter_taxa(csvfile, namefield=namefield, authfield=authfield, tracker=trackers, progress=progress)
        else:
            if progress:
                trackers.append(tracker.Counter(progress))
            data_in = taxa_dataset
        
        if to_tnrs:
            # Match to TNRS
            if from_csv:
                csvfile2 = open(csv_filename, encoding=csv_encoding, errors='replace')
                files.append(csvfile2)
                data_in2 = file_csv.iter_taxa(csvfile2, namefield=namefield, authfield=authfield)
            else:
                data_in2 = None
            
            from taxonome.services import tnrs
            # Do we want the output as a dataset?
            matchfunc = tnrs.match_taxa if matched_ds else tnrs.run_match_taxa
            # Run the matching
            res = matchfunc(data_in, data_in2, tracker=trackers)
        
        else:
            # Match to dataset
            
            # Do we want the output as a dataset?
            matchfunc = match_taxa if matched_ds else run_match_taxa
            # Run the matching
            res = matchfunc(data_in, target.ds, upgrade_subsp=upgrade,
                strict_authority=strict_authority, nameselector=nameselector, tracker=trackers)
        
        for f in files: f.close()
        return res
    
    # Run the matching in another thread --------------------------------------
    steps = os.stat(csv_filename).st_size if from_csv else len(taxa_dataset)
    if matched_ds:
        fromname = os.path.basename(csv_filename) if from_csv else dataset_item.name
        ds_name = "{} mapped to {}".format(fromname, target.name)
        makeloader(app, _run, ds_name, steps)
    else:
        thread = Worker(_run, app)
        thread.error_raised.connect(app.show_error)
        thread.withprogress(app, steps)
        thread.start()
