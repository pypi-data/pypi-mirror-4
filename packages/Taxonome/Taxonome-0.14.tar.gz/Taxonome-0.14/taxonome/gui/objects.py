from .qt import QtCore, QtGui

class DatasetItem(QtGui.QStandardItem):
    search_term = None
    search_results = None
    
    def __init__(self, name, ds, filename=None, **kwargs):
        super().__init__()
        self.ds = ds
        self.filename = filename
        self.name = name
        self.setData(name, QtCore.Qt.EditRole)
    
    def data(self, role=QtCore.Qt.UserRole+1):
        if role == QtCore.Qt.DisplayRole:
            return "{} ({} taxa)".format(self.name, len(self.ds))
        return super().data(role)
    
    def update_name(self):
        self.name = self.data(QtCore.Qt.EditRole)
    
    @property
    def autofilename(self):
        return self.filename or self.name.replace(" ","_")
    
    def copy(self):
        return type(self)(self.name, self.ds, self.filename)

class TaxonItem(QtGui.QStandardItem):
    def __init__(self, text, taxon):
        super().__init__(text)
        self.taxon = taxon

class TaxaItemModel(QtGui.QStandardItemModel):
    def __init__(self, *args):
        super().__init__(*args)
        self.setColumnCount(2)
        self.setHeaderData(0, QtCore.Qt.Horizontal, "Name")
        self.setHeaderData(1, QtCore.Qt.Horizontal, "Authority")

class NamePairItem(QtGui.QStandardItem):
    def __init__(self, namepair):
        self.namepair = namepair
        name, accname = namepair
        if name == accname:
            text = str(name)
        else:
            text = "{an}\n   from {n}".format(n=name, an=accname)
        super().__init__(text)
