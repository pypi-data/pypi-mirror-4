import sys, os, time, datetime
import time
from PyQt4.QtGui import QSplitter, QListView, QPlainTextEdit, QDockWidget, \
     QGridLayout, QLabel, QWidget, QPushButton, QToolBar, QAction, QIcon, QKeySequence, \
     QMainWindow, QTreeView, QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator, \
     QFileDialog, QStackedWidget, QFont, QMessageBox, QDialog, QCheckBox, QLineEdit, \
     QGroupBox, QRadioButton, QVBoxLayout, QInputDialog
from PyQt4.QtCore import Qt, QFileInfo, QFile, QTextStream, QProcess, QString, QSize

from coopr.age.Editor import ProblemEditor


class ProblemWindow(QMainWindow):
    def __init__(self, ownerWindow, ownerCooprApplication, problem):
        QMainWindow.__init__(self)
        self.ownerCooprApplication = ownerCooprApplication
        self.ownerMainWindow = ownerWindow
        self.problem = problem
        self.setWindowTitle(problem.name)
        self.setWindowIcon(QIcon('images/small_coopr_logo.png'))

        self.skipUpdate = True
        self.datapane = DataPane(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.datapane)
        self.resultspane = ResultsPane(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.resultspane)
        self.editor = ProblemEditor(self)

        self.setCentralWidget(self.editor)
        # open at least one document - first one should be the model
        for doc in self.problem.getInputDocuments():
            self.editDocument(doc)
            break

        self.skipUpdate = False
        self.update()

    def closeEvent(self, event):
        if self.ownerMainWindow.maybeSave(self, self.problem, True) == QMessageBox.Cancel:
            event.ignore()
        else:
            self.ownerMainWindow.ownerCooprApplication.closeProblem(self.problem)
            event.accept()

    def pushEditorData(self, name=None):
        if name is not None:
            textEdit = self.editor.getTextEdit(name)
            doc = self.problem.getDocument(name)
            if textEdit is not None and doc is not None:
                doc.text = textEdit.document().toPlainText()
                textEdit.document().setModified(False)
        else:
            names = self.editor.getDocumentNames()
            for name in names:
                textEdit = self.editor.getTextEdit(name)
                doc = self.problem.getDocument(name)
                if textEdit is not None and doc is not None:
                    doc.text = textEdit.document().toPlainText()
                    textEdit.document().setModified(False)

    def runProblem(self):
        if self.ownerCooprApplication.pyomoExe is None:
            text = self.ownerMainWindow.browsePyomoExe()
            if text is None:
                return
            else:
                self.ownerCooprApplication.pyomoExe = text

        pyomo_exe = self.ownerCooprApplication.pyomoExe
        if not os.path.isfile(pyomo_exe):
            raise AssertionError("The specified pyomo executable: " + str(pyomo_exe) + " does not exist.")

        self.stored_cursor = self.ownerMainWindow.cursor()
        self.ownerMainWindow.setCursor(Qt.WaitCursor)
        self.pushEditorData()
        (cmd, files) = self.problem.prepareForRun()
        console = self.problem.newOutputDocument()
        self.update()
        self.activeConsoleDocumentName = console.GetName()
        self.activeConsoleTempFiles = files
        console.text = datetime.datetime.now().strftime("###\n# Pyomo Run: %A %B %d %I:%M:%S %p %Y\n# Commands:\npyomo ")

        console.text = console.text + cmd + '\n###\n\n'
        self.editDocument(console)

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.readOutput)
        self.process.readyReadStandardError.connect(self.readError)
        self.process.finished.connect(self.processFinished)
        args = str(cmd).split()
        self.process.start(pyomo_exe, args)

    def readOutput(self):
        bytes = self.process.readAllStandardOutput()
        string = unicode( QString.fromLocal8Bit(bytes.data()) )
        self.editor.addText(self.activeConsoleDocumentName, string)
        self.ownerMainWindow.ownerApplication.processEvents()

    def readError(self):
        bytes = self.process.readAllStandardError()
        string = unicode( QString.fromLocal8Bit(bytes.data()) )
        self.editor.addText(self.activeConsoleDocumentName, string)
        self.ownerMainWindow.ownerApplication.processEvents()

    def processFinished(self):
        if self.problem.run_options["__UserCmd__"] is None or str(self.problem.run_options["__UserCmd__"]).find('--keepfiles') == -1:
            # delete the files we created...
            for file in self.activeConsoleTempFiles:
                QFile(file).remove()
                if str(file).endswith('.py'):
                    QFile(file + 'c').remove()

        self.activeConsoleTempFiles = None
        self.activeConsoleEditWidget = None
        self.ownerMainWindow.setCursor(self.stored_cursor)
        self.update()

    def update(self):
        if self.skipUpdate:
            return
        self.setWindowTitle(self.problem.name)

        self.datapane.update()
        self.resultspane.update()
        self.editor.update()

    def editDocument(self, cooprdoc):
        text = cooprdoc.text
        return self.editor.addDocument(cooprdoc.GetName(), text)

    def runOptionsDialog(self):
        dialog = RunOptionsDialog(self, self.problem)
        dialog.show()

class ResultsPane(QDockWidget):
    def __init__(self, ownerProblemWindow):
        QDockWidget.__init__(self)
        self.ownerProblemWindow = ownerProblemWindow
        self.problem = ownerProblemWindow.problem
        self.setWindowTitle('Solve Panel')
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.NoDockWidgetFeatures)

        self.listpane = QWidget()
        self.listlayout = QGridLayout(self.listpane)

        self.runAction = QAction(QIcon('images/arrow-right-3.png'), \
                                  "Run", self, \
                                  statusTip="Run Coopr", triggered=self.ownerProblemWindow.runProblem)
        self.runOptionsAction = QAction(QIcon('images/run-build-configure.png'), \
                                  "Run Options", self, \
                                  statusTip="Set Run Options", triggered=self.ownerProblemWindow.runOptionsDialog)
        self.openResultsAction = QAction(QIcon('images/document-edit.png'), "View Run Results", \
                                  self, statusTip="Open Run Results", triggered=self.openResults)
        self.renameResultsAction = QAction(QIcon('images/edit-rename.png'), \
                                  "Rename Run Results...", self, statusTip="Rename Run Results", \
                                  triggered=self.renameResults)
        self.importResultsAction = QAction(QIcon('images/document-import-2.png'), \
                                  "Import Run Results...", self, statusTip="Import Run Results", \
                                  triggered=self.importResults)
        self.exportResultsAction = QAction(QIcon('images/document-export-4.png'), "Export Run Results...", self, \
                                  statusTip="Export the selected set of run results to a file", \
                                  triggered=self.exportResults)
        self.removeResultsAction = QAction(QIcon('images/archive-remove.png'), "Remove Run Results", self, \
                                  statusTip="Remove the selected set of run results from the problem", \
                                  triggered=self.removeResults)


        toolbar = QToolBar()
#        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        toolbar.addAction(self.runAction)
        toolbar.addAction(self.runOptionsAction)
        toolbar.addAction(self.openResultsAction)
        toolbar.addAction(self.renameResultsAction)
        toolbar.addAction(self.importResultsAction)
        toolbar.addAction(self.exportResultsAction)
        toolbar.addAction(self.removeResultsAction)
        self.listlayout.addWidget(toolbar)
        self.resultsTreeWidget = ResultsTreeWidget(self.ownerProblemWindow, self.problem)
        self.resultsTreeWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.resultsTreeWidget.addAction(self.runAction)
        self.resultsTreeWidget.addAction(self.runOptionsAction)
        self.resultsTreeWidget.addAction(self.openResultsAction)
        self.resultsTreeWidget.addAction(self.renameResultsAction)
        self.resultsTreeWidget.addAction(self.importResultsAction)
        self.resultsTreeWidget.addAction(self.exportResultsAction)
        self.resultsTreeWidget.addAction(self.removeResultsAction)
        self.resultsTreeWidget.itemDoubleClicked.connect(self.openResults)

        self.listlayout.addWidget(self.resultsTreeWidget)
        self.setWidget(self.listpane)

        self.update()

    def openResults(self):
        selectedItem = self.resultsTreeWidget.selectedItem()
        if selectedItem is not None:
            self.ownerProblemWindow.editDocument(selectedItem.cooprDocument)

    def renameResults(self):
        selectedItem = self.resultsTreeWidget.selectedItem()
        if selectedItem is not None:
            default_txt = selectedItem.cooprDocument.GetName()
            text, ok = QInputDialog.getText(self.ownerProblemWindow, 'New Results Name', 'Provide new name for results:', QLineEdit.Normal, default_txt)
            if ok == True and text is not None:
                self.ownerProblemWindow.pushEditorData(default_txt)
                selectedItem.cooprDocument.SetName(text)
                self.ownerProblemWindow.update()
                self.ownerProblemWindow.editDocument(selectedItem.cooprDocument)

    def update(self):
        self.resultsTreeWidget.update()

    def importResults(self):
        filePath = QFileDialog.getOpenFileName(self, "Open", "", \
            filter="All Files [*] (*)")
        if filePath != "":
            file = QFile(filePath)
            if not file.open(QFile.ReadOnly | QFile.Text):
                QMessageBox.warning(self.ownerProblemWindow.ownerMainWindow, "File Error", \
                                    "Cannot read file %s:\n%s." % (fileName, file.errorString()))
                file.close()
                return

            outstr = QTextStream(file)
            newdoc = self.problem.newOutputDocument(str(QFileInfo(filePath).fileName()))
            newdoc.text = outstr.readAll()

            file.close()

        self.update()


    def exportResults(self):
        cooprdoc = None
        selectedItem = self.resultsTreeWidget.selectedItem()
        if isinstance(selectedItem, ResultsTreeItem):
            cooprdoc = selectedItem.cooprDocument

            filePath = QFileDialog.getSaveFileName(self, "Save As", cooprdoc.GetName(), \
                filter="All Files [*] (*)")
            if filePath != "":
                name = str(QFileInfo(filePath).fileName())
                file = QFile(filePath)
                if not file.open(QFile.WriteOnly | QFile.Text):
                    QMessageBox.warning(self.ownerProblemWindow.ownerMainWindow, "File Error", \
                                        "Cannot write file %s:\n%s." % (fileName, file.errorString()))
                    file.close()
                    return

                self.ownerProblemWindow.pushEditorData(cooprdoc.GetName())
                outstr = QTextStream(file)
                outstr << cooprdoc.text
                file.close()

        self.update()

    def removeResults(self):
        selectedItem = self.resultsTreeWidget.selectedItem()
        if isinstance(selectedItem, ResultsTreeItem):
            cooprdoc = selectedItem.cooprDocument

            # ask the user...
            response = QMessageBox.warning(self, "Confirm Delete?",
                                           "Are you sure you want to remove '%s' from the problem?" % str(cooprdoc.GetName()),
                                           QMessageBox.Yes | QMessageBox.Cancel)

            if response == QMessageBox.Yes:
                self.problem.removeOutputDocument(cooprdoc)
                self.ownerProblemWindow.editor.closeDocument(cooprdoc.GetName())

        self.ownerProblemWindow.update()

class DataPane(QDockWidget):
    def __init__(self, ownerProblemWindow):
        QDockWidget.__init__(self)
        self.ownerProblemWindow = ownerProblemWindow
        self.problem = ownerProblemWindow.problem
        self.setWindowTitle('Problem Specification')
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.NoDockWidgetFeatures)

        self.listpane = QWidget()
        self.listlayout = QGridLayout(self.listpane)
        self.newDocAction = QAction(QIcon('images/document-new-7.png'), "New Document", \
                                  self, statusTip="Create a new document", triggered=self.newDocument)
        self.editDocAction = QAction(QIcon('images/document-edit.png'), "Edit Document", \
                                  self, statusTip="Open document in editor", triggered=self.editDocument)
        self.renameDocAction = QAction(QIcon('images/edit-rename.png'), \
                                  "Rename Document...", self, statusTip="Rename the document", \
                                  triggered=self.renameDocument)
        self.importDocAction = QAction(QIcon('images/document-import-2.png'), \
                                  "Import Document...", self, statusTip="Import a document", \
                                  triggered=self.importDocument)
        self.exportDocAction = QAction(QIcon('images/document-export-4.png'), "Export Document...", self, \
                                  statusTip="Export the selected document to a file", \
                                  triggered=self.exportDocument)
        self.removeDocAction = QAction(QIcon('images/archive-remove.png'), "Remove Document", self, \
                                  statusTip="Remove the selected document from the problem", \
                                  triggered=self.removeDocument)
        toolbar = QToolBar()
        toolbar.addAction(self.newDocAction)
        toolbar.addAction(self.editDocAction)
        toolbar.addAction(self.renameDocAction)
        toolbar.addAction(self.importDocAction)
        toolbar.addAction(self.exportDocAction)
        toolbar.addAction(self.removeDocAction)

        self.listlayout.addWidget(toolbar)
        self.dataTreeWidget = DataTreeWidget(ownerProblemWindow,self.problem)
        self.dataTreeWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.dataTreeWidget.addAction(self.newDocAction)
        self.dataTreeWidget.addAction(self.editDocAction)
        self.dataTreeWidget.addAction(self.renameDocAction)
        self.dataTreeWidget.addAction(self.importDocAction)
        self.dataTreeWidget.addAction(self.exportDocAction)
        self.dataTreeWidget.addAction(self.removeDocAction)
        self.dataTreeWidget.itemDoubleClicked.connect(self.editDocument)
        self.dataTreeWidget.itemClicked.connect(self.clickedItem)
        self.listlayout.addWidget(self.dataTreeWidget)
        self.setWidget(self.listpane)

        self.update()

    def clickedItem(self, item, column):
        if item is not None:
            item.clickedItem(column)

    def renameDocument(self):
        selectedItem = self.dataTreeWidget.selectedItem()
        if selectedItem is not None:
            default_txt = selectedItem.cooprDocument.GetName()
            text, ok = QInputDialog.getText(self.ownerProblemWindow, 'New Document Name', 'Provide new document name:', QLineEdit.Normal, default_txt)
            if ok == True and text is not None:
                self.ownerProblemWindow.pushEditorData(default_txt)
                selectedItem.cooprDocument.SetName(text)
                self.ownerProblemWindow.update()
                self.ownerProblemWindow.editDocument(selectedItem.cooprDocument)

    def editDocument(self):
        selectedItem = self.dataTreeWidget.selectedItem()
        if selectedItem is not None:
            self.ownerProblemWindow.editDocument(selectedItem.cooprDocument)

    def newDocument(self):
        self.problem.newInputDocument('inactive')
        self.ownerProblemWindow.update()

    def importDocument(self):
        filePath = QFileDialog.getOpenFileName(self, "Open", "", \
            filter="Coopr Model File [*.py] (*.py);;Coopr Data File [*.dat] (*.dat);; All Files [*] (*)")
        if filePath != "":
            file = QFile(filePath)
            if not file.open(QFile.ReadOnly | QFile.Text):
                QMessageBox.warning(self.ownerProblemWindow.ownerMainWindow, "File Error", \
                                    "Cannot read file %s:\n%s." % (fileName, file.errorString()))
                file.close()
                return

            outstr = QTextStream(file)
            newdoc = self.problem.newInputDocument('inactive', str(QFileInfo(filePath).fileName()))
            newdoc.text = outstr.readAll()

            file.close()

        self.update()


    def exportDocument(self):
        cooprdoc = None
        selectedItem = self.dataTreeWidget.selectedItem()
        if isinstance(selectedItem, DataTreeItem):
            cooprdoc = selectedItem.cooprDocument

            filePath = QFileDialog.getSaveFileName(self, "Save As", cooprdoc.GetName(), \
                filter="Coopr Model File [*.py] (*.py);;Coopr Data File [*.dat] (*.dat);; All Files [*] (*)")
            if filePath != "":
                name = str(QFileInfo(filePath).fileName())
                file = QFile(filePath)
                if not file.open(QFile.WriteOnly | QFile.Text):
                    QMessageBox.warning(self.ownerProblemWindow.ownerMainWindow, "File Error", \
                                        "Cannot write file %s:\n%s." % (fileName, file.errorString()))
                    file.close()
                    return

                self.ownerProblemWindow.pushEditorData(cooprdoc.GetName())
                outstr = QTextStream(file)
                outstr << cooprdoc.text
                file.close()

        self.update()

    def removeDocument(self):
        selectedItem = self.dataTreeWidget.selectedItem()
        if isinstance(selectedItem, DataTreeItem):
            cooprdoc = selectedItem.cooprDocument

            # ask the user...
            response = QMessageBox.warning(self, "Confirm Delete?",
                                           "Are you sure you want to remove '%s' from the problem?" % str(cooprdoc.GetName()),
                                           QMessageBox.Yes | QMessageBox.Cancel)

            if response == QMessageBox.Yes:
                self.problem.removeInputDocument(cooprdoc)
                self.ownerProblemWindow.editor.closeDocument(cooprdoc.GetName())

        self.ownerProblemWindow.update()

    def update(self):
        self.dataTreeWidget.update()

class DataTreeWidget(QTreeWidget):
    sequenceNumber = 1

    def __init__(self, ownerProblemWindow, problem):
        QTreeWidget.__init__(self)
        self.ownerProblemWindow = ownerProblemWindow
        self.problem = problem
        self.setObjectName(''.join(["DataTree-", str(DataTreeWidget.sequenceNumber)]))
        DataTreeWidget.sequenceNumber = DataTreeWidget.sequenceNumber + 1
        self.setColumnCount(2)
        self.setHeaderLabels(['Module','Status'])

    def selectedItem(self):
        selected = None
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            if iterator.value().isSelected():
                selected = iterator.value()
                break
            iterator += 1
        return selected

    def update(self):
        # cache the selected item if one exists
        selected = self.selectedItem()
        if selected is not None:
            selected = selected.cooprDocument.GetName()

        # Destroy the old tree
        self.clear()

        # Remake the tree
        for cooprdoc in self.problem.getInputDocuments():
            treeItem = DataTreeItem(self, cooprdoc, self.problem)
            self.addTopLevelItem(treeItem)
            treeItem.update()
            if cooprdoc.GetName() == selected:
                treeItem.setSelected(True)

class DataTreeItem(QTreeWidgetItem):
    def __init__(self, ownerDataTreeWidget, cooprDocument, cooprProblem):
        QTreeWidgetItem.__init__(self, ownerDataTreeWidget)
        self.ownerDataTreeWidget = ownerDataTreeWidget
        self.cooprDocument = cooprDocument
        self.cooprProblem = cooprProblem

        self.update()

    def update(self):
        self.setText(0, self.cooprDocument.GetName())

        state = self.cooprProblem.getDocumentState(self.cooprDocument)
        self.setText(1, state)

    def clickedItem(self, column):
        if column == 1:
            state = self.cooprProblem.getDocumentState(self.cooprDocument)
            if state == 'model':
                self.cooprProblem.setDocumentState(self.cooprDocument, 'data')
            elif state == 'data':
                self.cooprProblem.setDocumentState(self.cooprDocument, 'inactive')
            else:
                self.cooprProblem.setDocumentState(self.cooprDocument, 'model')

            self.update()
#        elif column == 0:
#            self.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)

    def editDocument(self):
        text = self.cooprDocument.text
        self.ownerDataTreeWidget.ownerProblemWindow.editDocument(self.cooprDocument)

    def modificationChanged(self, flag):
        self.update()

class ResultsTreeWidget(QTreeWidget):
    sequenceNumber = 1

    def __init__(self, ownerProblemPane, problem):
        QTreeWidget.__init__(self)
        self.ownerProblemPane = ownerProblemPane
        self.problem = problem
        self.setObjectName(''.join(["ResultsTree-", str(ResultsTreeWidget.sequenceNumber)]))
        ResultsTreeWidget.sequenceNumber = ResultsTreeWidget.sequenceNumber + 1
        self.setColumnCount(1)
        self.setHeaderLabels(['Results']);

    def update(self):
        # cache the selected item if one exists
        selected = self.selectedItem()
        if selected is not None:
            selected = selected.cooprDocument.GetName()

        # Destroy the old tree
        self.clear()

        # Remake the tree
        for cooprdoc in self.problem.getOutputDocuments():
            treeItem = ResultsTreeItem(self, cooprdoc, self.problem)
            treeItem.update()
            if cooprdoc.GetName() == selected:
                treeItem.setSelected(True)

    def selectedItem(self):
        selected = None
        iterator = QTreeWidgetItemIterator(self)
        while iterator.value():
            if iterator.value().isSelected():
                selected = iterator.value()
                break
            iterator += 1
        return selected

class ResultsTreeItem(QTreeWidgetItem):
    def __init__(self, ownerResultsTreeWidget, cooprDocument, problem):
        QTreeWidgetItem.__init__(self, ownerResultsTreeWidget)
        self.ownerResultsTreeWidget = ownerResultsTreeWidget
        self.cooprDocument = cooprDocument
        self.problem = problem
        self.update()

    def update(self):
        self.setText(0, self.cooprDocument.GetName())

    def modificationChanged(self, flag):
        self.update()

class RunOptionsDialog(QDialog):
    def __init__(self, ownerProblemWindow, problem):
        QDialog.__init__(self, ownerProblemWindow)
        self.ownerProblemWindow = ownerProblemWindow
        self.problem = problem
        self.setModal(True)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Run Options")

        self.layout = QGridLayout(self)
        self.layout.setVerticalSpacing(6)
#       self.layout.setColumnMinimumWidth(1,200)
        self.layout.setColumnStretch(1,2)

        self.solverButton = QCheckBox("Solver:", self)
        self.solverText = QLineEdit(self)
        self.layout.addWidget(self.solverButton,0,0)
        self.layout.addWidget(self.solverText,0,1)
        self.solverOptionsButton = QCheckBox("Solver options: ", self)
        self.solverOptionsText = QLineEdit(self)
        self.layout.addWidget(self.solverOptionsButton,1,0)
        self.layout.addWidget(self.solverOptionsText,1,1)
        self.timeLimitButton = QCheckBox("Time limit (seconds): ", self)
        self.timeLimitText = QLineEdit(self)
        self.layout.addWidget(self.timeLimitButton,2,0)
        self.layout.addWidget(self.timeLimitText,2,1)

        #self.solverMipGapButton = QCheckBox("Solver MIP gap:", self)
        #self.solverMipGapText = QLineEdit(self)
        #self.layout.addWidget(self.solverMipGapButton,3,0)
        #self.layout.addWidget(self.solverMipGapText,3,1)


        self.streamButton = QCheckBox("Stream Solver Output", self)
        self.layout.addWidget(self.streamButton,4,0)
        self.quietButton = QCheckBox("Quiet Solver Output", self)
        self.layout.addWidget(self.quietButton,5,0)
        self.verboseButton = QCheckBox("Verbose Solver Output", self)
        self.layout.addWidget(self.verboseButton,6,0)

        self.logButton = QCheckBox("Stream Solver Logfile", self)
        self.layout.addWidget(self.logButton,7,0)

        self.summaryButton = QCheckBox("Show Solution Summary", self)
        self.layout.addWidget(self.summaryButton,8,0)

        warningGroup = QGroupBox("Warning Level", self)
        self.warningGroup = warningGroup
        warningGroup.setCheckable(True)
        warningGroup.setChecked(False)
        grouplayout = QGridLayout(warningGroup)
        self.quietWarningButton = QRadioButton("Quiet", warningGroup)
        self.warningWarningButton = QRadioButton("Warning", warningGroup)
        self.warningWarningButton.setChecked(True)
        self.infoWarningButton = QRadioButton("Info", warningGroup)
        grouplayout.addWidget(self.quietWarningButton,0,0)
        grouplayout.addWidget(self.warningWarningButton,0,1)
        grouplayout.addWidget(self.infoWarningButton,0,2)
        warningGroup.setLayout(grouplayout)
        self.layout.addWidget(warningGroup,9,0)

        self.userCmdButton = QCheckBox("Additional Command Line Options", self)
        self.userCmdText = QLineEdit(self)
        self.layout.addWidget(self.userCmdButton, 10, 0)
        self.layout.addWidget(self.userCmdText, 11, 0, 1, 2)

        buttoncontainer = QWidget(self)
        buttonlayout = QGridLayout(buttoncontainer)
        self.acceptButton = QPushButton("OK", buttoncontainer)
        buttonlayout.addWidget(self.acceptButton,0,0)

        self.cancelButton = QPushButton("Cancel", buttoncontainer)
        buttonlayout.addWidget(self.cancelButton,0,1)
        buttoncontainer.setLayout(buttonlayout)
        self.layout.addWidget(buttoncontainer,12,0,1,2)

        self.setLayout(self.layout)


        self.acceptButton.clicked.connect(self.accept)
        self.acceptButton.setDefault(True)
        self.cancelButton.clicked.connect(self.closeDialog)

        self.update()

    def update(self):
        run_options = self.problem.run_options
        self.solverButton.setChecked(False)
        value = run_options["solver"]
        if value is not None:
            self.solverButton.setChecked(True)
            self.solverText.setText(value)

        self.solverOptionsButton.setChecked(False)
        value = run_options["solver-options"]
        if value is not None:
            self.solverOptionsButton.setChecked(True)
            self.solverOptionsText.setText(value)

        self.timeLimitButton.setChecked(False)
        value = run_options["timelimit"]
        if value is not None:
            self.timeLimitButton.setChecked(True)
            self.timeLimitText.setText(value)

        #self.solverMipGapButton.setChecked(False)
        #value = run_options["solver-mipgap"]
        #if value is not None:
            #self.solverMipGapButton.setChecked(True)
            #self.solverMipGapText.setText(value)

        self.streamButton.setChecked(False)
        value = run_options["stream-output"]
        if value is not None:
            self.streamButton.setChecked(True)

        self.verboseButton.setChecked(False)
        value = run_options["verbose"]
        if value is not None:
            self.verboseButton.setChecked(True)

        self.quietButton.setChecked(False)
        value = run_options["quiet"]
        if value is not None:
            self.quietButton.setChecked(True)

        self.logButton.setChecked(False)
        value = run_options["log"]
        if value is not None:
            self.logButton.setChecked(True)

        self.summaryButton.setChecked(False)
        value = run_options["summary"]
        if value is not None:
            self.summaryButton.setChecked(True)

        self.warningGroup.setChecked(False)
        value = run_options["warning"]
        if value is not None:
            self.warningGroup.setChecked(True)
            self.quietWarningButton.setChecked(False)
            self.warningWarningButton.setChecked(False)
            self.infoWarningButton.setChecked(False)
            if value == 'quiet':
                self.quietWarningButton.setChecked(True)
            elif value == 'warning':
                self.warningWarningButton.setChecked(True)
            elif value == 'info':
                self.infoWarningButton.setChecked(True)

        self.userCmdButton.setChecked(False)
        value = run_options["__UserCmd__"]
        if value is not None:
            self.userCmdButton.setChecked(True)
            self.userCmdText.setText(value)

    def pushToProblem(self):
        run_options = self.problem.run_options
        run_options["solver"] = None
        if self.solverButton.isChecked():
            run_options["solver"] = self.solverText.text()

        run_options["solver-options"] = None
        if self.solverOptionsButton.isChecked():
            run_options["solver-options"] = self.solverOptionsText.text()


        run_options["timelimit"] = None
        if self.timeLimitButton.isChecked():
            run_options["timelimit"] = self.timeLimitText.text()

        #run_options["solver-mipgap"] = None
        #if self.solverMipGapButton.isChecked():
            #run_options["solver-mipgap"] = self.solverMipGapText.text()

        run_options["stream-output"] = None
        if self.streamButton.isChecked():
            run_options["stream-output"] = True

        run_options["verbose"] = None
        if self.verboseButton.isChecked():
            run_options["verbose"] = True

        run_options["quiet"] = None
        if self.quietButton.isChecked():
            run_options["quiet"] = True

        run_options["log"] = None
        if self.logButton.isChecked():
            run_options["log"] = True

        run_options["summary"] = None
        if self.summaryButton.isChecked():
            run_options["summary"] = True

        run_options["warning"] = None
        if self.warningGroup.isChecked():
            if self.quietWarningButton.isChecked():
                run_options["warning"] = 'quiet'
            elif self.warningWarningButton.isChecked():
                run_options["warning"] = 'warning'
            elif self.infoWarningButton.isChecked():
                run_options["warning"] = 'info'

        run_options["__UserCmd__"] = None
        if self.userCmdButton.isChecked():
            run_options["__UserCmd__"] = self.userCmdText.text()

    def accept(self):
        self.pushToProblem()
        self.close()

    def closeDialog(self):
        self.close()
