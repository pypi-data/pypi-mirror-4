#import sys, os
from PyQt4.QtGui import QPlainTextEdit, QGridLayout, QWidget, QTabWidget, QFont, QPlainTextEdit, QAction, QIcon
from PyQt4.Qt import QSize, Qt
from coopr.age import PyomoSyntax

class ProblemEditor(QWidget):
    def __init__(self, ownerWidget):
        QWidget.__init__(self, ownerWidget)
        self.ownerProblemWindow = ownerWidget
        self.layout = QGridLayout(self)
        self.tabWidget = QTabWidget(self)
#        self.tabWidget.runAction = QAction(QIcon('images/remove.png'), \
#                                 "Close", self, \
#                                 statusTip="Close Document", triggered=self.closeActiveDocument)
#        self.tabWidget.addAction(self.tabWidget.runAction)
#        self.tabWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.closeTab)
        self.layout.addWidget(self.tabWidget)
        self.setLayout(self.layout)
        self.textEdits = list()
        if self.ownerProblemWindow.ownerCooprApplication.fontSize is not None:
            self.font = QFont("Courier", int(self.ownerProblemWindow.ownerCooprApplication.fontSize))
        else:
            self.font = QFont('Courier', 10)
        self.font.setFixedPitch(True)
        self.font.setStyleHint(QFont.Courier, QFont.PreferAntialias)

    def updateFont(self):
        if self.ownerProblemWindow.ownerCooprApplication.fontSize is not None:
            self.font = QFont("Courier", self.ownerProblemWindow.ownerCooprApplication.fontSize)
        else:
            self.font = QFont('Courier', 10)
        self.update()

    def sizeHint(self):
        return QSize(500,200)

    def closeTab(self, idx):
        name = self.tabWidget.tabText(idx)
        self.ownerProblemWindow.pushEditorData(name)
        self.tabWidget.removeTab(idx)

    def addDocument(self, name, initialText):
        # check if the document is already open
        tabidx = self.getTabIdx(name)
        textEdit = None
        if tabidx is None:
            textEdit = QPlainTextEdit()
            self.textEdits.append(textEdit)
            textEdit.document().setPlainText(initialText)
            textEdit.setFont(self.font)
            textEdit.syntaxHighlighter = PyomoSyntax.Python(textEdit.document())
            textEdit.document().modificationChanged.connect(self._modificationChanged)
            self.tabWidget.addTab(textEdit, name)
            textEdit.document().setModified(False)
            self.tabWidget.setCurrentIndex(self.tabWidget.count()-1)
        else:
            textEdit = self.tabWidget.widget(tabidx)
            self.tabWidget.setCurrentIndex(tabidx)

        return textEdit

    def closeDocument(self, name):
        tabidx = self.getTabIdx(name)
        if tabidx is not None:
            self.tabWidget.removeTab(tabidx)

    def changeName(self, oldname, newname):
        tabidx = self.getTabIdx(oldname)
        if tabidx is not None:
            self.tabWidget.setTabText(newname)
            self.update()

    def addText(self, name, text):
        tabidx = self.getTabIdx(name)
        if tabidx is not None:
            textEdit = self.tabWidget.widget(tabidx)
            textEdit.appendPlainText(text)

    def setText(self, name, text):
        tabidx = self.getTabIdx(name)
        if tabidx is not None:
            textEdit = self.tabWidget.widget(i)
            textEdit.document().setPlainText(text)

    def getTextEdit(self, name):
        tabidx = self.getTabIdx(name)
        if tabidx is not None:
            return self.tabWidget.widget(tabidx)
        return None

    def getTabIdx(self, name):
        # find the page that corresponds to the document and close
        N = self.tabWidget.count()
        tabWidget = self.tabWidget
        tabidx = None
        for i in range(0,N):
            tabtext = tabWidget.tabText(i)
            if tabtext == name or tabtext == name + '*':
                # found it
                tabidx = i
                break

        return tabidx

    def getDocumentNames(self):
        names = list()
        N = self.tabWidget.count()
        tabWidget = self.tabWidget
        for i in range(0,N):
            tabText = tabWidget.tabText(i)
            # to do: remove '*' if necessary
            names.append(tabText)

        return names

    def update(self):
        N = self.tabWidget.count()
        tabsToRemove = list()
        for i in range(0,N):
            widget = self.tabWidget.widget(i)
            widget.setFont(self.font)
            tabname = self.tabWidget.tabText(i)
            if self.ownerProblemWindow.problem.getDocument(tabname) is None:
                tabsToRemove.append(i)

        for i in tabsToRemove:
            self.tabWidget.removeTab(i)

        return
        N = self.tabWidget.count()
        for i in range(0,N):
            textEdit = self.tabWidget.widget(i)
            tabname = self.tabWidget.tabText(i)
            if textEdit.document().isModified() == True and not str(tabname).endswith('*'):
                self.tabWidget.setTabText(i, tabname + '*')
            elif textEdit.document().isModified() == False and str(tabname).endswith('*'):
                # to do: fix when we get internet
                self.tabWidget.setTabText(tabname + 'x')

    def getText(self, name):
        tabidx = self.getTabIdx(name)
        if tabidx is not None:
            textEdit = self.tabWidget.widget(i)
            return textEdit.document().toPlainText()
        return None

    def _modificationChanged(self):
        self.update()
