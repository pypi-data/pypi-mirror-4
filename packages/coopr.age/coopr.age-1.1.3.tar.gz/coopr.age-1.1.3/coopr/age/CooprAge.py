import sys, os
try:
    import PyQt4
except ImportError:
    print("Aborting CooprAge.  Failed to import the PyQt4 package.")
    sys.exit(0)

from PyQt4.QtGui import QMainWindow, QMdiArea, QKeySequence, QAction, QIcon, QDialog,\
     QToolBar, QStatusBar, QMdiSubWindow, QApplication, QFileDialog, QMessageBox, QLabel, \
     QTextEdit, QPushButton, QGridLayout, QLineEdit, QWidget
from PyQt4.QtCore import Qt, QFileInfo
from UIProblem import ProblemWindow
import cPickle as pickle

from coopr.age import CooprAgeCore

class CooprAgeMainWindow(QMainWindow):
    def __init__(self, ownerApplication, ownerCooprApplication):
        self.ownerCooprApplication = ownerCooprApplication
        self.ownerApplication = ownerApplication
        QMainWindow.__init__(self)
        self.mdiarea = QMdiArea()
        self.setCentralWidget(self.mdiarea)
        self.setObjectName("CooprAge Main Window")
        self.setWindowIcon(QIcon('images/small_coopr_logo.png'))
        self.initUI()
        self.read_preferences()


#        self.ownerCooprApplication.addNewProblem()
        self.update()

    def closeEvent(self, event):
        for window in self.mdiarea.subWindowList():
            problemWindow = window.widget()
            self.maybeSave(problemWindow, problemWindow.problem, False)

        self.write_preferences()
        event.accept()

    def write_preferences(self):
        prefobj = dict()
        prefobj['uistate'] = self.saveState()
        if self.ownerCooprApplication.pyomoExe is not None:
            prefobj['pyomo_exe'] = self.ownerCooprApplication.pyomoExe
        if self.ownerCooprApplication.fontSize is not None:
            prefobj['font_size'] = self.ownerCooprApplication.fontSize

        preffile = open('UIPrefs.ini','w+')
        pickle.dump(prefobj, preffile)
        preffile.close()

    def read_preferences(self):
        if os.path.exists('UIPrefs.ini'):
            prefile = None
            try:
                preffile = open('UIPrefs.ini','r')
                prefobj = pickle.load(preffile)
                if 'uistate' in prefobj:
                    self.restoreState(prefobj['uistate'])
                if 'pyomo_exe' in prefobj:
                    self.ownerCooprApplication.pyomoExe = prefobj['pyomo_exe']
                if 'font_size' in prefobj:
                    self.ownerCooprApplication.fontSize = prefobj['font_size']

                preffile.close()

            except:
                if preffile is not None:
                    preffile.close()
                self.ownerCooprApplication.pyomoExe = None

    def initUI(self):
        """Initializes the GUI components (window title, menus, toolbars, etc)."""
        self.setWindowTitle('Coopr.AGE (Advanced Graphical Environment for Pyomo)')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setUnifiedTitleAndToolBarOnMac(True)

        toolbar = QToolBar()
        toolbar.setObjectName('MainToolBar')
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.addAction(QAction(QIcon('images/document-new-7.png'), \
                                  "&New", self,  \
                                  statusTip="Create a new Coopr problem", triggered=self.newCooprProblem))
        toolbar.addAction(QAction(QIcon('images/document-open-4.png'), \
                                  "&Open...", self, \
                                  statusTip="Open an existing Coopr problem", triggered=self.openCooprProblem))
        toolbar.addAction(QAction(QIcon('images/document-save-2.png'), \
                                  "&Save", self, shortcut=QKeySequence.Save, \
                                  statusTip="Save the Coopr problem to disk", triggered=self.saveActiveCooprProblem))
        toolbar.addAction(QAction(QIcon('images/document-save-as-2.png'), \
                                  "Save &As...", self, shortcut=QKeySequence.SaveAs, \
                                  statusTip="Save the Coopr problem under a new name", \
                                  triggered=self.saveAsActiveCooprProblem))
        toolbar.addAction(QAction(QIcon('images/configure.png'), \
                                  "Preferences...", self, shortcut=QKeySequence.SaveAs, \
                                  statusTip="Set preferences for Coopr.AGE", \
                                  triggered=self.openCooprPreferences))

        self.addToolBar(Qt.TopToolBarArea, toolbar)

    def browsePyomoExe(self):
        # we need to ask the user for the pyomo executable
        pyomoPath = QFileDialog.getOpenFileName(self, "Find the pyomo script", filter="pyomo executable (*)")
        if pyomoPath != "":
            canonicalFilePath = QFileInfo(pyomoPath).canonicalFilePath()
            return canonicalFilePath
        return None

    def newCooprProblem(self):
        self.ownerCooprApplication.addNewProblem()
        self.update()

    def openCooprProblem(self):
        filePath = QFileDialog.getOpenFileName(self, filter="Coopr Problem File [*.cpf] (*.cpf);;All files [*] (*)")
        if filePath != "":
            canonicalFilePath = QFileInfo(filePath).canonicalFilePath()
            name = QFileInfo(canonicalFilePath).fileName()
            self.ownerCooprApplication.addPickledProblem(canonicalFilePath, name)
            self.update()

    def maybeSave(self,problemWindow, problem, allow_cancel):
        if allow_cancel == True:
            choice = QMessageBox.warning(self, 'Save Document?', 'Do you wish to save ' + problem.name + '?', QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        else:
            choice = QMessageBox.warning(self, 'Save Document?', 'Do you wish to save ' + problem.name + '?', QMessageBox.Save | QMessageBox.Discard)

        if choice == QMessageBox.Save:
            return self.saveCooprProblem(problemWindow, problem)
        return choice

    def saveActiveCooprProblem(self):
        window = self.mdiarea.activeSubWindow()
        if not isinstance(window, ProblemWindow):
            window = window.widget()
        assert(isinstance(window, ProblemWindow))
        problem = window.problem
        return self.saveCooprProblem(window, problem)

    def saveCooprProblem(self, problemWindow, problem):
        if problem.filename is None:
            return self.saveAsCooprProblem(problemWindow, problem)

        filename = problem.filename
        name = QFileInfo(filename).fileName()
        problemWindow.pushEditorData()
        self.ownerCooprApplication.pickleProblem(problem, filename, name)
        self.update()
        return QMessageBox.Ok

    def saveAsActiveCooprProblem(self):
        window = self.mdiarea.activeSubWindow()
        if not isinstance(window, ProblemWindow):
            window = window.widget()
        assert(isinstance(window, ProblemWindow))
        problem = window.problem
        return self.saveAsCooprProblem(window, problem)

    def saveAsCooprProblem(self, problemWindow, problem):
        if problem.filename is None:
            filePath = QFileDialog.getSaveFileName(self, "Save As", "", filter="Coopr Problem File [*.cpf] (*.cpf)")
        else:
            filePath = QFileDialog.getSaveFileName(self, "Save As", problem.filename, filter="Coopr Problem File [*.cpf] (*.cpf)")

        if filePath != "":
            name = QFileInfo(filePath).fileName()
            problemWindow.pushEditorData()
            self.ownerCooprApplication.pickleProblem(problem, filePath, name)
            self.update()
            return QMessageBox.Ok
        else:
            return QMessageBox.Cancel

    def openCooprPreferences(self):
        dialog = CooprAgeSettingsDialog(self, self.ownerCooprApplication)
        dialog.show()

    def update(self):
        for problem in self.ownerCooprApplication.problems:
            found = False
            for window in self.mdiarea.subWindowList():
                if not isinstance(window, ProblemWindow):
                    window = window.widget()
                assert(isinstance(window, ProblemWindow))
                if window.problem == problem:
                    found = True
                    break

            if found == False:
                win = ProblemWindow(self, self.ownerCooprApplication, problem)
                self.mdiarea.addSubWindow(win)
                win.show()

        for window in self.mdiarea.subWindowList():
            if not isinstance(window, ProblemWindow):
                window = window.widget()
            assert(isinstance(window, ProblemWindow))
            window.update()

class CooprAgeSettingsDialog(QDialog):
    def __init__(self, ownerWindow, ownerCooprApplication):
        QDialog.__init__(self, ownerWindow)
        self.ownerWindow = ownerWindow
        self.ownerCooprApplication = ownerCooprApplication
        self.setModal(True)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Coopr.AGE Settings")

        self.layout = QGridLayout(self)
        self.layout.setVerticalSpacing(6)
        self.layout.setColumnMinimumWidth(1,300)
        self.layout.setColumnStretch(1,2)

        self.pyomoExeLabel = QLabel("Pyomo Executable:", self)
        self.pyomoExeEdit = QLineEdit(self)
        self.pyomoExeButton = QPushButton('Browse...', self)
        self.layout.addWidget(self.pyomoExeLabel,0,0)
        self.layout.addWidget(self.pyomoExeEdit,0,1)
        self.layout.addWidget(self.pyomoExeButton,0,2)
        self.fontSizeLabel = QLabel('Editor Font Size: ', self)
        self.fontSizeEdit = QLineEdit(self)
        self.layout.addWidget(self.fontSizeLabel,1,0)
        self.layout.addWidget(self.fontSizeEdit,1,1)

        buttoncontainer = QWidget(self)
        buttonlayout = QGridLayout(buttoncontainer)
        self.acceptButton = QPushButton("OK", buttoncontainer)
        buttonlayout.addWidget(self.acceptButton,0,0)

        self.cancelButton = QPushButton("Cancel", buttoncontainer)
        buttonlayout.addWidget(self.cancelButton,0,1)
        buttoncontainer.setLayout(buttonlayout)
        self.layout.addWidget(buttoncontainer,2,0,1,3)

        self.setLayout(self.layout)

        self.pyomoExeButton.clicked.connect(self.browsePyomoExeButton)
        self.acceptButton.clicked.connect(self.accept)
        self.acceptButton.setDefault(True)
        self.cancelButton.clicked.connect(self.closeDialog)

        self.update()

    def browsePyomoExeButton(self):
        text = self.ownerWindow.browsePyomoExe()
        if text is not None:
            self.pyomoExeEdit.setText(text)

    def update(self):
        if self.ownerCooprApplication.pyomoExe is not None:
            self.pyomoExeEdit.setText(str(self.ownerCooprApplication.pyomoExe))
        if self.ownerCooprApplication.fontSize is not None:
            self.fontSizeEdit.setText(str(self.ownerCooprApplication.fontSize))

    def accept(self):
        self.ownerCooprApplication.pyomoExe = None
        if self.pyomoExeEdit.text() != '':
            self.ownerCooprApplication.pyomoExe = str(self.pyomoExeEdit.text())

        if self.fontSizeEdit.text() != '':
            self.ownerCooprApplication.fontSize = int(self.fontSizeEdit.text())

        self.ownerWindow.update()
        self.close()

    def closeDialog(self):
        self.close()


def run():
    app = QApplication(sys.argv)
    cooprage_app = CooprAgeCore.CooprAgeApplication()
    mainWindow = CooprAgeMainWindow(app, cooprage_app)
    mainWindow.show()
    app.exec_()

if __name__ == "__main__":
    # when one "exectutes" a python program, it's __name__ is
    # __main__, otherwise it's name will be the module name
    run()
