from queue import Queue
from .qt import QtGui, QtCore

from taxonome.taxa.name_selector import NameSelector, TryAnotherName
from taxonome import Name

from .ui.nameselector import Ui_NameSelector
from .objects import NamePairItem

class GuiNameSelector(NameSelector, QtCore.QObject):
    choice_required = QtCore.Signal(object, object)
    choice_results = Queue()
    
    def present_dialog(self, name_options, name):
        # This must run in the main GUI thread.
        dialog = QtGui.QDialog()
        selectdialog = Ui_NameSelector()
        selectdialog.setupUi(dialog)
        
        if isinstance(name, Name):
            selectdialog.subject_line.setText("Matches for <i>{n.plain}</i> {n.authority}:"\
                                                .format(n=name))
        elif name:
            selectdialog.subject_line.setText("Matches for {}:".format(name))
        else:
            selectdialog.subject_line.setText("Matches:")
        
        choices = QtGui.QStandardItemModel()
        for namepair in name_options:
            choices.appendRow(NamePairItem(namepair))
        selectdialog.choice_list.setModel(choices)
        
        exitstatus = dialog.exec_()
        seln = selectdialog.choice_list.selectedIndexes()
        if seln:
            choice = choices.itemFromIndex(seln[0])
        else:
            choice = None
        newname = selectdialog.new_name.text()
        
        self.choice_results.put((exitstatus, choice, newname))
    
    def user_select(self, name_options, name, allow_retype, tracker):
        """Allow the user to choose between the options interactively."""
        def cache_choice(choice):
            self.store_user_choice(name_options, name, choice)
        
        self.choice_required.emit(name_options, name)
        exitstatus, choice, newname = self.choice_results.get()
        
        if not (exitstatus and (choice or newname)):
            ke = KeyError(name)
            cache_choice(ke)
            raise ke
        
        if newname:
            tracker.name_transform(name, newname, "user input")
            retry = TryAnotherName(newname)
            cache_choice(retry)
            raise retry
        
        cache_choice(choice.namepair)
        self.choice_results.task_done()
        return choice.namepair
