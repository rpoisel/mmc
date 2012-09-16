import datetime
import logging

from PySide import QtCore

from jobs import Jobs


class CThreadWorker(QtCore.QThread):
    sBegin = QtCore.Signal(int, long, int, str)
    sProgress = QtCore.Signal(int)
    # job, jobs, error
    sFinished = QtCore.Signal(int, int, int)
    sError = QtCore.Signal(str)

    def __init__(self, pOptions, pFileCarver, pJobs):
        super(CThreadWorker, self).__init__()
        self.mOptions = pOptions
        self.mFileCarver = pFileCarver
        self.mJobs = pJobs
        self.mRunningJob = Jobs.NONE
        self.mLastTs = datetime.datetime.now()

    def beginCallback(self, pSize, pOffset, pFsType):
        self.sBegin.emit(self.mRunningJob, pSize, pOffset, pFsType)

    def progressCallback(self, pProgress):
        if self.mJobs & Jobs.CLASSIFY == Jobs.CLASSIFY \
                and \
                self.mJobs & Jobs.REASSEMBLE == Jobs.REASSEMBLE:
                    if self.mRunningJob & Jobs.REASSEMBLE == Jobs.REASSEMBLE:
                        self.sProgress.emit(85 + pProgress * 0.15)
                    else:
                        self.sProgress.emit(pProgress * 0.85)
        else:
            self.sProgress.emit(pProgress)

    def finishedCallback(self):
        self.sFinished.emit(self.mRunningJob, self.mJobs, False)

    def run(self):
        if self.mJobs & Jobs.CLASSIFY == Jobs.CLASSIFY:
            self.mRunningJob = Jobs.CLASSIFY
            try:
                self.mFileCarver.runClassify(self.mOptions, self)
            except OSError, pExc:
                logging.error(str(pExc) + ". Please make sure the "
                        "classifier binaries are compiled. ")
                self.sError.emit(str(pExc) + ". Please make sure the "
                        "classifier binaries are compiled. ")
                self.sFinished.emit(self.mRunningJob, self.mJobs, True)
#            except Exception, pExc:
#                logging.error(str(pExc))
#                self.sError.emit(str(pExc))

        if self.mJobs & Jobs.REASSEMBLE == Jobs.REASSEMBLE:
            self.mRunningJob = Jobs.REASSEMBLE
            try:
                self.mFileCarver.runReassembly(self.mOptions, self)
            except TypeError, pExc:
                self.sFinished.emit(self.mRunningJob, self.mJobs, True)
#            except Exception, pExc:
#                logging.error(str(pExc))
#                self.sFinished.emit(self.mRunningJob, self.mJobs, True)
