import sys, os
#from PyQt4.QtGui import QTextDocument, QPlainTextDocumentLayout
#from PyQt4.QtCore import QFileInfo, QTextStream, QFile
import pickle
import tempfile

if sys.version_info < (3,):
    xrange = range


class CooprAgeApplication(object):
    def __init__(self):
        self.problems = list()
        self.pyomoExe = None
        self.fontSize = 12

    def addNewProblem(self):
        problem = CooprAgeProblem(self)
        self.problems.append(problem)
        return problem

    def closeProblem(self, problem):
        if problem in self.problems:
            self.problems.remove(problem)

    def pickleProblem(self, problem, filename, name):
        file = open(filename,'w+')
        problem.filename = filename
        problem.name = name
        pickle.dump(problem, file)
        file.close()

    def addPickledProblem(self, filename, name):
        file = open(filename,'r')
        problem = pickle.load(file)
        problem.filename = filename
        problem.name = name
        self.problems.append(problem)
        file.close()
        return problem

class CooprAgeRunOptions(object):
    def __init__(self):
        self.disableGC = False
        self.timeLimit = 3000
        self.streamOutput = False
        self.verboseOutput = False
        self.quietOutput = False
        self.summaryOutput = False
        self.printSolverLog = False
        self.saveLogFile = False
        self.logFileName = ''
        self.solver = 'glpk'
        self.solverOptions = ''
        #self.solverMipGap = 0
        self.keepTempFiles = False

class CooprAgeProblem(object):
    sequenceNumber = 1

    def __init__(self, ownerApplication):
        self.ownerApplication_ = ownerApplication

        self.name = 'Problem-'+str(CooprAgeProblem.sequenceNumber)
        self.filename = None

        self.inputDocuments = list()
        self.inputDocumentStates = list()
        self.outputDocuments = list()

        CooprAgeProblem.sequenceNumber = CooprAgeProblem.sequenceNumber + 1
        self.newInputDocument('model', 'model')
        self.newInputDocument('data', 'data')
        self.newInputDocument('inactive','notes')

        # specify the run options
        self.run_options = dict()
        self.run_options["help"] = None
        self.run_options["solver"] = None
        self.run_options["solver-options"] = None
        #self.run_options["solver-mipgap"] = None
        self.run_options["timelimit"] = None
        self.run_options["log"] = None
        self.run_options["logfile"] = None
        self.run_options["quiet"] = None
        self.run_options["summary"] = None
        self.run_options["stream-output"] = None
        self.run_options["verbose"] = None
        self.run_options["warning"] = None

        self.run_options["__UserCmd__"] = None

    def getDocumentState(self, cooprdoc):
        if cooprdoc in self.inputDocuments:
            docidx = self.inputDocuments.index(cooprdoc)
            return self.inputDocumentStates[docidx]
        return None

    def setDocumentState(self, cooprdoc, state):
        if cooprdoc in self.inputDocuments:
            assert(state == 'model' or state == 'data' or state == 'inactive')
            docidx = self.inputDocuments.index(cooprdoc)
            self.inputDocumentStates[docidx] = state

    def NameUnique(self, name):
        docs = list()
        docs.extend(self.inputDocuments)
        docs.extend(self.outputDocuments)
        for doc in docs:
            if doc.GetName() == name:
                return False
        return True

    def getUniqueName(self, prefix):
        for i in xrange(1,32767):
            name = prefix + str(i)
            if self.NameUnique(name):
                return name
        return None

    def newInputDocument(self, state, name=None):
        if name is None:
            name = 'Doc'
        cooprdoc = CooprAgeDocument(self,name)
        self.inputDocuments.append(cooprdoc)
        self.inputDocumentStates.append(state)
        return cooprdoc

    def newOutputDocument(self, name=None):
        if name is None:
            name = 'Run'
        cooprdoc = CooprAgeDocument(self,name)
        self.outputDocuments.append(cooprdoc)
        return cooprdoc

    def removeInputDocument(self, cooprdoc):
        if cooprdoc in self.inputDocuments:
            self.inputDocuments.remove(cooprdoc)

    def removeOutputDocument(self, cooprdoc):
        if cooprdoc in self.outputDocuments:
            self.outputDocuments.remove(cooprdoc)

    def getInputDocuments(self):
        return self.inputDocuments

    def getOutputDocuments(self):
        return self.outputDocuments

    def getDocument(self, name):
        for doc in self.inputDocuments:
            if doc.GetName() == name:
                return doc

        for doc in self.outputDocuments:
            if doc.GetName() == name:
                return doc

    def prepareForRun(self):
        # build up the command line...
        cmd = ""
        for (key,value) in self.run_options.items():
            if value is not None and key != "__UserCmd__":
                if value == True:
                    cmd += "--" + key + " "
                elif key == "solver-options":
                    cmd += "--" + key + "=\"" + value + "\" "
                else:
                    cmd += "--" + key + "=" + value + " "

        usercmd = self.run_options["__UserCmd__"]
        if usercmd is not None:
            cmd += usercmd + " "

        files = list()
        # need to save temp file for the model
        foundmodel = False
        for modelfile in self.inputDocuments:
            if self.getDocumentState(modelfile) == 'model':
                (mfile, mfilename) = tempfile.mkstemp(suffix='.py', prefix='coopr_model', dir='./workspace', text=True)
                os.write(mfile,str(modelfile.text))
                os.close(mfile)
                cmd = cmd + mfilename + " ";
                files.append(mfilename)
                break

        for datfile in self.inputDocuments:
            if self.getDocumentState(datfile) == 'data':
                (dfile, dfilename) = tempfile.mkstemp(suffix='.dat', prefix='coopr_dat', dir='./workspace', text=True)
                cmd = cmd + dfilename + " ";
                os.write(dfile,str(datfile.text))
                os.close(dfile)
                files.append(dfilename)
                cmd += dfilename + " "

        return (cmd, files)

    def cleanupAfterRun(self, files):
        for file in files:
            os.remove(file)

class CooprAgeDocument(object):
    sequenceNumber = 1

    def __init__(self, ownerProblem, name=None):
        self.ownerProblem = ownerProblem
        self.SetName(name)
        self.text = str()

    def SetName(self, name):
        if name is not None and self.ownerProblem.NameUnique(name) and name is not 'Run' and name is not 'Doc':
            self.name = name
        elif name is None:
            self.name = self.ownerProblem.getUniqueName('Doc-')
        else:
            self.name = self.ownerProblem.getUniqueName(name + '-')

    def GetName(self):
        return self.name
