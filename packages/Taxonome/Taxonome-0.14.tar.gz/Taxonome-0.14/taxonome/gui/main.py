# -*- coding: utf-8 -*-

"""The user interface for our app"""

import csv
import os.path
import traceback
import sys
import warnings
from base64 import b64encode

from .qt import QtCore, QtGui, QtWebKit

from .ui.mainwindow import Ui_MainWindow
from . import (selectname, mapnames, combine, webservices, iothread, csvdialogs,
               prevchoices)
from .objects import DatasetItem, TaxonItem, TaxaItemModel

from taxonome import TaxonSet
from taxonome.taxa import name_selector
from taxonome.taxa import file_csv, file_jsonlines

# Create a class for our main window
class Main(QtGui.QMainWindow):
    
    active_dataset = None
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Keep a reference to worker threads so they don't get destroyed
        # prematurely.
        self.workerthreads = set()
        self.warning.connect(self.showwarning)
        
        self.lastdir = os.path.expanduser("~")
        
        # List of datasets
        self.datasets_model = QtGui.QStandardItemModel()
        self.ui.datasets.setModel(self.datasets_model)
        self.ui.datasets.clicked.connect(self.select_dataset)
        self.datasets_model.itemChanged.connect(DatasetItem.update_name)
        
        # Preview pane
        blank_preview = TaxaItemModel(self)
        self.ui.taxa_list.setModel(blank_preview)
        self.ui.taxa_list.setColumnWidth(0, 200)
        self.ui.taxa_list.setColumnWidth(1, 100)
        self.ui.taxa_list.clicked.connect(self.select_taxon)
        
        # HTML taxon preview
        websettings = QtWebKit.QWebSettings.globalSettings()
        styles = b"body {font-family: sans-serif;}"
        stylesheet = "data:text/css;charset=utf-8;base64," + b64encode(styles).decode('ascii')
        websettings.setUserStyleSheetUrl(QtCore.QUrl(stylesheet))
        
        # Set up menus
        #  File:
        self.ui.actionNew_ds.triggered.connect(self.empty_ds)
        self.ui.actionLoad_CSV_taxa.triggered.connect(self.load_csv)
        self.ui.actionLoad_CSV_synonyms.triggered.connect(self.load_csv_synonyms)
        self.ui.actionLoad_CSV_individuals.triggered.connect(self.load_csv_individuals)
        self.ui.actionLoad_JSONlines.triggered.connect(self.load_jsonlines)
        self.ui.actionSave_CSV_taxa.triggered.connect(self.save_csv)
        self.ui.actionSave_CSV_synonyms.triggered.connect(self.save_csv_synonyms)
        self.ui.actionSave_CSV_individuals.triggered.connect(self.save_csv_individuals)
        self.ui.actionSave_JSONlines.triggered.connect(self.save_jsonlines)
        #  Taxa:
        self.ui.actionMatch_names.triggered.connect(self.map_names)
        self.ui.actionCombine_datasets.triggered.connect(self.combine_datasets)
        self.ui.actionPrevious_choices.triggered.connect(self.edit_prevchoices)
        #  Web services:
        self.ui.actionFetch_taxa.triggered.connect(self.fetch_taxa)
        self.ui.actionLook_up_name.triggered.connect(self.find_taxon_web)
        
        # Status bar
        self.ui.statusbar.showMessage("Welcome to Taxonome.", 10000)
        
        self.gui_select_name = selectname.GuiNameSelector()
        self.gui_select_name.choice_required.connect(self.gui_select_name.present_dialog)
        self.silent_select_name = name_selector.NameSelector()
    
    def select_dataset(self, index):
        ds_item = self.datasets_model.itemFromIndex(index)
        self.active_dataset = ds_item
        if ds_item.search_results:
            self.ui.taxa_list.setModel(ds_item.search_results)
            self.ui.searchbox.setText(ds_item.search_term)
            self.ui.taxa_list_label.setText("Search results:")
        else:
            self.ui.taxa_list.setModel(ds_item.preview)
            self.ui.searchbox.clear()
            self.ui.taxa_list_label.setText("Example taxa:")
    
    def select_taxon(self, index):
        tax_item = self.ui.taxa_list.model().itemFromIndex(index)
        self.ui.tax_preview.setHtml(tax_item.taxon.html())
    
    def add_dataset(self, name, ts, filename=None):
        ds_item = DatasetItem(name, ts, filename=filename)
        self.datasets_model.appendRow(ds_item)
        
        ds_item.preview = TaxaItemModel(self)
        its = iter(ts)
        for _ in range(10):
            try:
                tax = next(its)
            except StopIteration:
                break
            name = TaxonItem(tax.name.plain, taxon=tax)
            auth = TaxonItem(str(tax.name.authority), taxon=tax)
            ds_item.preview.appendRow([name, auth])
    
    def empty_ds(self):
        ts = TaxonSet()
        self.add_dataset("unnamed", ts)
    
    def load_jsonlines(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, "Open file",
                    self.lastdir, "JSONlines (*.jsonlines);;All files (*.*)")
        if not filename:
            return
        self.lastdir = os.path.dirname(filename)
        
        ds_name = os.path.splitext(os.path.basename(filename))[0].replace("_"," ")
        
        iothread.load_jsonlines(self, ds_name, filename)
    
    def save_jsonlines(self):
        seln = self.ui.datasets.selectedIndexes()
        if not seln:
            return
        ds_item = self.datasets_model.itemFromIndex(seln[0])
        filename = os.path.splitext(ds_item.autofilename)[0] + ".jsonlines"
        filename = QtGui.QFileDialog.getSaveFileName(self, "Save file", filename,
                                "JSONlines (*.jsonlines);;All files (*.*)")
        if not filename:
            return
        if not os.path.splitext(filename)[1]:
            filename += ".jsonlines"
        
        with open(filename,"w", encoding='utf-8') as f:
            file_jsonlines.save_taxa(f, ds_item.ds)
    
    def save_csv(self):
        ds_item = self.active_dataset
        if not ds_item:
            return
        filename = os.path.splitext(ds_item.autofilename)[0] + ".csv"
        filename = QtGui.QFileDialog.getSaveFileName(self, "Save file", filename,
                                                "CSV (*.csv);;All files (*.*)")
        if not filename:
            return
        if not os.path.splitext(filename)[1]:
            filename += ".csv"
        
        with open(filename,"w",encoding='utf-8', newline='') as f:
            file_csv.save_taxa(f, ds_item.ds, info_fields=True, write_distribution=None)
    
    def save_csv_synonyms(self):
        ds_item = self.active_dataset
        if not ds_item:
            return
        filename = os.path.splitext(ds_item.autofilename)[0] + ".csv"
        filename = QtGui.QFileDialog.getSaveFileName(self, "Save file", filename,
                                                "CSV (*.csv);;All files (*.*)")
        if not filename:
            return
        if not os.path.splitext(filename)[1]:
            filename += ".csv"
        
        with open(filename,"w",encoding='utf-8', newline='') as f:
            file_csv.save_synonyms(f, ds_item.ds)
    
    def save_csv_individuals(self):
        ds_item = self.active_dataset
        if not ds_item:
            return
        filename = os.path.splitext(ds_item.autofilename)[0] + ".csv"
        filename = QtGui.QFileDialog.getSaveFileName(self, "Save file", filename,
                                                "CSV (*.csv);;All files (*.*)")
        if not filename:
            return
        if not os.path.splitext(filename)[1]:
            filename += ".csv"
        
        with open(filename,"w",encoding='utf-8', newline='') as f:
            file_csv.save_individuals(f, ds_item.ds)
    
    load_csv = csvdialogs.load_csv
    load_csv_synonyms = csvdialogs.load_csv_synonyms
    load_csv_individuals = csvdialogs.load_csv_individuals
    
    def do_search(self):
        """Search for a taxon name in the active dataset."""
        term = self.ui.searchbox.text()
        wildcard = "*" in term
        try:
            results = self.active_dataset.ds.resolve(term, wildcard=wildcard)
        except NotImplementedError:
            self.ui.statusbar.showMessage("This data source doesn't support "
                                          "wildcard searches.")
            return
        results_model = TaxaItemModel(self)
        for tax in results:
            name = TaxonItem(tax.name.plain, taxon=tax)
            auth = TaxonItem(str(tax.name.authority), taxon=tax)
            results_model.appendRow([name, auth])
        
        # Display the results
        self.ui.taxa_list.setModel(results_model)
        self.ui.taxa_list_label.setText("Search results:")
        
        # Store results with the dataset for later use.
        self.active_dataset.search_results = results_model
        self.active_dataset.search_term = term
    
    def clear_search(self):
        """Clear search results. The input field is cleared separately by
        a connection to its own slot."""
        self.ui.taxa_list.setModel(self.active_dataset.preview)
        self.ui.taxa_list_label.setText("Example taxa:")
        
        self.active_dataset.search_results = None
        self.active_dataset.search_term = None
    
    def show_error(self, e):
        self.excepthook(type(e), e, e.__traceback__)
    
    def excepthook(self, etype, value, tb):
        msgbox = QtGui.QMessageBox(self)
        err = "".join(traceback.format_exception(etype, value, tb))
        msgbox.setText("An exception occurred:\n" + err +\
                       "\n\nPlease report this at https://bitbucket.org/taxonome/taxonome/issues")
        msgbox.exec_()
    
    warning = QtCore.Signal(object, object, object, object, object, object)
    def thread_warn(self, message, category, filename, lineno, file=None, line=None):
        self.warning.emit(message, category, filename, lineno, file, line)
    
    def showwarning(self, message, category, filename, lineno, file=None, line=None):
        self.ui.statusbar.showMessage("Warning: " + str(message), 10000)
    
    map_names = mapnames.wizard_map_names
    combine_datasets = combine.gui_combine_datasets
    fetch_taxa = webservices.fetch_taxa
    find_taxon_web = webservices.find_taxon
    edit_prevchoices = prevchoices.edit_prevchoices
        
def main():
    app = QtGui.QApplication(sys.argv)
    window = Main()
    warnings.showwarning = window.thread_warn
    if sys.stderr is None:
        sys.excepthook = window.excepthook
    window.show()
    sys.exit(app.exec_())
