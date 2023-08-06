from PySide import QtCore, QtGui
from .about import Ui_Dialog
import mainWindow, sys, os

class about(QtGui.QDialog, mainWindow.Ui_MainWindow):
    def __init__(self, parent=None):
        super(about, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.connect(self.ui.help, QtCore.SIGNAL("clicked()"), self.help)

    def help(self):
        try:
            os.startfile('README.txt')
        except WindowsError:
            pass
