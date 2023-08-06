from PySide import QtCore, QtGui
from .unable import Ui_Dialog as unable_Ui_Dialog
from .nomovie import Ui_Dialog as nomovie_Ui_Dialog
from .noentryselected import Ui_Dialog as noentryselected_Ui_Dialog
from .nointernet import Ui_Dialog as nointernet_Ui_Dialog
import mainWindow, sys

class unable(QtGui.QDialog, mainWindow.Ui_MainWindow):
    def __init__(self, parent=None):
        super(unable, self).__init__(parent)
        self.ui = unable_Ui_Dialog()
        self.ui.setupUi(self)

class noMovie(QtGui.QDialog, mainWindow.Ui_MainWindow):
    def __init__(self, parent=None):
        super(noMovie, self).__init__(parent)
        self.ui = nomovie_Ui_Dialog()
        self.ui.setupUi(self)

class noEntrySelected(QtGui.QDialog, mainWindow.Ui_MainWindow):
    def __init__(self, parent=None):
        super(noEntrySelected, self).__init__(parent)
        self.ui = noentryselected_Ui_Dialog()
        self.ui.setupUi(self)

class noInternet(QtGui.QDialog, mainWindow.Ui_MainWindow):
    def __init__(self, parent=None):
        super(noInternet, self).__init__(parent)
        self.ui = nointernet_Ui_Dialog()
        self.ui.setupUi(self)