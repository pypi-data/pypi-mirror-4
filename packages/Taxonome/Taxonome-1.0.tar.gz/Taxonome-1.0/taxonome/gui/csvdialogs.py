"""GUI Dialogs for loading CSV files.
"""
import os.path
import csv
from .qt import QtGui, QtCore

from . import iothread
from .ui.csvimport import Ui_CsvImportDialog
from .ui.csvimport_synonyms import Ui_CsvSynonymsImportDialog

supported_encodings = ["UTF-8", "Windows-1252", "IBM850", "GB18030"]

class CsvImportDialog(QtGui.QDialog):
    encoding = 'utf-8'
    UiClass = Ui_CsvImportDialog
    
    def __init__(self, filename, parent=None):
        super().__init__(parent=parent)
        self.ui = self.UiClass()
        self.ui.setupUi(self)
        
        self.ui.csv_encoding.addItems(supported_encodings)
        
        QtCore.QObject.connect(self.ui.csv_encoding,
            QtCore.SIGNAL("currentIndexChanged(QString)"), self.encoding_changed)
        
        self.filename = filename
        self.preview_file()
        
        ds_name = os.path.splitext(os.path.basename(filename))[0].replace("_"," ")
        self.ui.ds_name.setText(ds_name)
    
    def fill_column_dropdowns(self, fields):
        """Prepare CSV field dropdowns"""
        self.ui.namefield.clear()
        self.ui.authfield.clear()
        self.ui.namefield.addItems(fields)
        self.ui.authfield.addItems(fields)
        self.ui.authfield.setCurrentIndex(1)

    def preview_file(self):
        """Open file, grab column names, and preview the first 10 rows.
        
        preview should be a QTableWidget to put the preview in.
        """
        # Fill in preview table from CSV file
        with open(self.filename, encoding=self.encoding, errors='replace') as f:
            csvin = csv.reader(f)
            fields = next(csvin)
            head = []
            i = 0
            for row in csvin:
                head.append(row)
                i += 1
                if i >= 10:
                    break
        
        # Clear the old preview
        self.ui.preview.setColumnCount(0)
        self.ui.preview.setRowCount(0)
        
        for i in range(len(fields)):
            self.ui.preview.insertColumn(i)
        self.ui.preview.setHorizontalHeaderLabels(fields)
        for i, row in enumerate(head):
            self.ui.preview.insertRow(i)
            for j, cell in enumerate(row):
                self.ui.preview.setItem(i, j, QtGui.QTableWidgetItem(cell))
        
        self.fill_column_dropdowns(fields)
    
    def encoding_changed(self, new_encoding):
        "Switch encoding and update preview."
        self.encoding = new_encoding
        self.preview_file()

    def get_auth_field(self, prefix=''):
        """Get the location of the authorities in the format that the file_csv
        functions expect."""
        if getattr(self.ui, prefix+'noauth').isChecked():
            return None
        elif getattr(self.ui, prefix+'auth_with_name').isChecked():
            return True
        else:
            return getattr(self.ui, prefix+'authfield').currentText()

class CsvSynonymsImportDialog(CsvImportDialog):
    UiClass = Ui_CsvSynonymsImportDialog
    
    def fill_column_dropdowns(self, fields):
        self.ui.accnamefield.clear()
        self.ui.accauthfield.clear()
        self.ui.synnamefield.clear()
        self.ui.synauthfield.clear()
        self.ui.accnamefield.addItems(fields)
        self.ui.accauthfield.addItems(fields)
        self.ui.accauthfield.setCurrentIndex(1)
        self.ui.synnamefield.addItems(fields)
        self.ui.synnamefield.setCurrentIndex(2)
        self.ui.synauthfield.addItems(fields)
        self.ui.synauthfield.setCurrentIndex(3)

def load_csv(app):
    """Load a user-selected CSV file into the application."""
    filename = QtGui.QFileDialog.getOpenFileName(app, "Open file",
                            app.lastdir, "CSV (*.csv);;All files (*.*)")
    if not filename:
        return
    app.lastdir = os.path.dirname(filename)
    
    dialog = CsvImportDialog(filename, parent=app)
    
    if not dialog.exec_():
        return

    namefield = dialog.ui.namefield.currentText()
    authfield = dialog.get_auth_field()
    encoding = dialog.ui.csv_encoding.currentText()
    
    iothread.load_csv(app, dialog.ui.ds_name.text(), filename, encoding=encoding,
                                namefield=namefield, authfield=authfield)

def load_csv_synonyms(app):
    """Load a user-selected CSV file of synonyms into the application."""
    filename = QtGui.QFileDialog.getOpenFileName(app, "Open file",
                            app.lastdir, "CSV (*.csv);;All files (*.*)")
    if not filename:
        return
    app.lastdir = os.path.dirname(filename)
    
    dialog = CsvSynonymsImportDialog(filename, parent=app)
    
    if not dialog.exec_():
        return

    accnamefield = dialog.ui.accnamefield.currentText()
    synnamefield = dialog.ui.synnamefield.currentText()
    accauthfield = dialog.get_auth_field('acc')
    synauthfield = dialog.get_auth_field('syn')
    encoding = dialog.ui.csv_encoding.currentText()
    
    iothread.load_csv_synonyms(app, dialog.ui.ds_name.text(), filename, encoding,
                        accnamefield=accnamefield, accauthfield=accauthfield,
                        synnamefield=synnamefield, synauthfield=synauthfield)

def load_csv_individuals(app):
    """Load a user-selected CSV file of individual records into the application."""
    filename = QtGui.QFileDialog.getOpenFileName(app, "Open file",
                            app.lastdir, "CSV (*.csv);;All files (*.*)")
    if not filename:
        return
    app.lastdir = os.path.dirname(filename)
    
    dialog = CsvImportDialog(filename, parent=app)
    
    if not dialog.exec_():
        return

    namefield = dialog.ui.namefield.currentText()
    authfield = dialog.get_auth_field()
    encoding = dialog.ui.csv_encoding.currentText()
    
    iothread.load_csv_individuals(app, dialog.ui.ds_name.text(), filename, encoding=encoding,
                                namefield=namefield, authfield=authfield)
