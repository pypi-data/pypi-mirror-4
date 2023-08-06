from .qt import QtGui

from taxonome.services import grin, tropicos, col
from .ui.fetch_taxa import Ui_FetchOptsDialog
from .ui.find_taxon import Ui_FindSpDialog

from . import iothread


class WrappedWoRMS:
    """Lazy loading so we don't import suds at startup."""
    __worms_resource = None
    
    @property
    def worms_resource(self):
        from taxonome.services.worms import WoRMSTaxaResource
        self.__worms_resource = WoRMSTaxaResource()
        return self.__worms_resource
    
    def select(self, *args, **kwargs):
        return self.worms_resource.select(*args, **kwargs)

fetch_taxa_services = {"USDA GRIN database": grin}
find_taxon_services = {"USDA GRIN database": grin,
                       "MBG Tropicos": tropicos,
                       "Catalogue of Life": col,
                       "World Register of Marine Species (WoRMS)": WrappedWoRMS(),
                      }

def fetch_taxa(app):
    optsdialog = Ui_FetchOptsDialog()
    dialog = QtGui.QDialog()
    optsdialog.setupUi(dialog)
    
    optsdialog.service.addItems(list(fetch_taxa_services.keys()))
    
    if not dialog.exec_():
        return False
    
    service_name = optsdialog.service.currentText()
    service = fetch_taxa_services[service_name]
    name = optsdialog.groupname.text()
    
    ds_name = "{} from {}".format(name, service_name)
    app.ui.statusbar.showMessage("Fetching {}...".format(ds_name))
    iothread.makeloader(app, lambda: service.fetch(name), ds_name)
    #ts = service.fetch(name)
    #app.add_dataset(, ts)

def find_taxon(app):
    tax = None
    finddialog = Ui_FindSpDialog()
    dialog = QtGui.QDialog()
    finddialog.setupUi(dialog)
    
    finddialog.service.addItems(list(find_taxon_services.keys()))
    finddialog.destination_ds.setModel(app.datasets_model)
    
    def dosearch():
        nonlocal tax
        service_name = finddialog.service.currentText()
        service = find_taxon_services[service_name]
        name = finddialog.taxname.text()
        
        tax = service.select(name)
        
        finddialog.result_view.setHtml(tax.html())
        finddialog.result_block.setEnabled(True)
    
    def add_to_ds():
        seln = finddialog.destination_ds.currentIndex()
        target = app.datasets_model.item(seln)
        
        target.ds.add(tax)
        target.emitDataChanged()
    
    finddialog.search.clicked.connect(dosearch)
    finddialog.ds_add.clicked.connect(add_to_ds)
    
    dialog.exec_()
    
