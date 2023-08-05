# coding: utf-8

from .qt import QtCore, QtGui

from .ui.combine import Ui_CombineDialog
from taxonome.taxa import combine_datasets
from taxonome.taxa.combine import add_info_flat, add_info_nested

def _get_items(model):
    """Extract items from a single column QStandardItemModel"""
    return (model.item(r) for r in range(model.rowCount()))
    
_distrib_ds_all = "(Combine any distribution data)"

class CombineDialog(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_CombineDialog()
        self.ui.setupUi(self)
        self.parent = parent
        
        ds_model = parent.datasets_model
        
        # Set up the dataset lists
        self.ui.available_ds_list.setModel(ds_model)
        self.target_ds = QtGui.QStandardItemModel()
        self.bg_ds = QtGui.QStandardItemModel()
        self.ui.target_ds_list.setModel(self.target_ds)
        self.ui.bg_ds_list.setModel(self.bg_ds)
        
        # Set up combobox for distribution
        self.ui.distrib_ds.addItem(_distrib_ds_all)
        self.ui.distrib_ds.addItems([dsi.name for dsi in _get_items(ds_model)])
    
    def add_target_ds(self):
        dsi = self.get_selected_available_ds()
        self.target_ds.appendRow(dsi.copy())
        
    def add_bg_ds(self):
        dsi = self.get_selected_available_ds()
        self.bg_ds.appendRow(dsi.copy())
    
    def remove_target_ds(self):
        seln = self.ui.target_ds_list.selectedIndexes()
        if seln:
            self.target_ds.removeRow(seln[0].row())
    
    def remove_bg_ds(self):
        seln = self.ui.bg_ds_list.selectedIndexes()
        if seln:
            self.bg_ds.removeRow(seln[0].row())
    
    def get_selected_available_ds(self):
        """Get the selected DatasetItem from the list of available datasets"""
        seln = self.ui.available_ds_list.selectedIndexes()
        if not seln:
            return None
        return self.parent.datasets_model.itemFromIndex(seln[0])

def gui_combine_datasets(app):
    dialog = CombineDialog(app)
    if not dialog.exec_():
        return
    
    newname = dialog.ui.newname.text()
    target_ds = [(dsi.name, dsi.ds) for dsi in _get_items(dialog.target_ds)]
    bg_ds = [(dsi.name, dsi.ds) for dsi in _get_items(dialog.bg_ds)]
    distrib_ds = dialog.ui.distrib_ds.currentText()
    if distrib_ds == _distrib_ds_all:
        distrib_ds = "all"
    
    add_info = add_info_nested if dialog.ui.nest_info.isChecked() \
          else add_info_flat
    
    new_ds = combine_datasets(target_ds, bg_ds, distrib_ds, add_info=add_info)
    
    app.add_dataset(newname, new_ds)
