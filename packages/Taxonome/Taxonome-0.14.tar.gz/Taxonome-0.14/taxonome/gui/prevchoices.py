import os.path
import shelve
from .qt import QtGui, QtCore

import taxonome
from taxonome.config import config
from taxonome.taxa.name_selector import TryAnotherName
from .ui.prevchoices import Ui_PrevChoicesDialog
from .objects import NamePairItem

class PrevChoiceItem(QtGui.QStandardItem):
    def __init__(self, name, shelf):
        super().__init__()
        self.name = name
        self.shelf = shelf
        self.setText(str(name))
    
    @property
    def choice(self):
        return self.shelf[repr(self.name)]
    
    def update_choice(self, newchoice):
        options, oldchoice = self.choice
        self.shelf[repr(self.name)] = options, newchoice
        try:
            self.shelf.sync()
        except AttributeError:
            pass
    
    def reject_all(self):
        self.update_choice(KeyError(self.name))

class PrevChoicesDialog(QtGui.QDialog):
    def __init__(self, user_choices=None):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_PrevChoicesDialog()
        self.ui.setupUi(self)
    
        if user_choices is not None:
            self.user_choices = user_choices
        else:
            user_choice_file = os.path.expanduser(config['cache']['user-choices'])
            self.user_choices = shelve.open(user_choice_file)
            self.destroyed.connect(self.user_choices.close)
        
        self.ambignames_model = QtGui.QStandardItemModel()
        self.ui.ambignames.setModel(self.ambignames_model)
        self.ui.ambignames.clicked.connect(self.select_ambigname)
        
        for ambigname in self.user_choices.keys():
            # Trivial bit of sanitisation - this is not secure against malicious
            # data in the user choices file.
            if not ambigname.startswith("taxonome.Name("):
                continue
            ambigname = eval(ambigname, {'taxonome':taxonome})
            self.ambignames_model.appendRow(PrevChoiceItem(ambigname, self.user_choices))
        
        # Connect action buttons
        self.ui.forget.clicked.connect(self.forget)
        self.ui.forget_all.clicked.connect(self.forget_all)
        self.ui.update_choice.clicked.connect(self.update_choice)
        self.ui.reject_all.clicked.connect(self.reject_all)
    
    @property
    def selected_choice(self):
        seln = self.ui.ambignames.selectedIndexes()
        return self.ambignames_model.itemFromIndex(seln[0])
    
    @property
    def selected_name(self):
        seln = self.ui.altmatches.selectedIndexes()
        return self.options_model.itemFromIndex(seln[0])
        
    def select_ambigname(self, index):
        prevchoice = self.ambignames_model.itemFromIndex(index)
        self.show_choices(prevchoice)
    
    def show_choices(self, prevchoice):
        options, chosen = prevchoice.choice
        
        if isinstance(chosen, KeyError):
            chosentxt = "(Reject all)"
        elif isinstance(chosen, TryAnotherName):
            chosentxt = "Retry with '{}'".format(chosen.newname)
        else:
            n, an = chosen
            if n==an:
                chosentxt = str(n)
            else:
                chosentxt = "{an}<br>&nbsp;&nbsp;from {n}".format(n=n, an=an)
        self.ui.chosenmatch.setText(chosentxt)
        
        self.options_model = QtGui.QStandardItemModel()
        for namepair in options:
            self.options_model.appendRow(NamePairItem(namepair))
        self.ui.altmatches.setModel(self.options_model)
    
    def forget(self):
        choice = self.selected_choice
        del self.user_choices[repr(choice.name)]
        row = choice.index().row()
        self.ambignames_model.removeRow(row)
    
    def forget_all(self):
        self.user_choices.clear()
        self.ambignames_model = QtGui.QStandardItemModel()
        self.ui.ambignames.setModel(self.ambignames_model)
    
    def update_choice(self):
        choice = self.selected_choice
        name = self.selected_name
        choice.update_choice(name.namepair)
        self.show_choices(choice)
    
    def reject_all(self):
        choice = self.selected_choice
        choice.reject_all()
        self.show_choices(choice)

def edit_prevchoices(app=None):
    user_choices = None
    if app is not None:
        user_choices = app.gui_select_name.previous_choices
    dialog = PrevChoicesDialog(user_choices)
    dialog.exec_()
