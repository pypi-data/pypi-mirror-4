"""Commonly used Job widgets."""

import plow.client
import plow.gui.constants as constants

from plow.gui.manifest import QtCore, QtGui
from plow.gui.form import FormWidget, FormWidgetFactory

class JobProgressFormWidget(FormWidget):
    def __init__(self, value, parent=None):
        FormWidget.__init__(self, parent)
        self.setWidget(JobProgressBar(value, parent))

class JobStateFormWidget(FormWidget):
    def __init__(self, value, parent=None):
        FormWidget.__init__(self, parent)
        self.setWidget(JobStateWidget(value, False, parent))
        self._widget.setMinimumWidth(100)

FormWidgetFactory.register("jobProgressBar", JobProgressFormWidget)
FormWidgetFactory.register("jobState", JobStateFormWidget)

class JobProgressBar(QtGui.QWidget):
    # Left, top, right, bottom
    __PEN = QtGui.QColor(33, 33, 33)

    Margins = [5, 2, 10, 4]

    def __init__(self, totals, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setTotals(totals)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Preferred)

        ## Missing ability to detect size
    
    def setTotals(self, totals):
        self.__totals = totals
        self.__values =  [
            totals.waiting,
            totals.running,
            totals.dead, 
            totals.eaten,
            totals.depend,
            totals.succeeded
        ]

    def paintEvent(self, event):

        total_width = self.width() - self.Margins[2]
        total_height = self.height() - self.Margins[3]
        total_tasks = float(self.__totals.total)

        bar = []
        for i, v in enumerate(self.__values):
            if v == 0:
                continue
            bar.append((total_width * (v / total_tasks), constants.COLOR_TASK_STATE[i + 1]))

        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHints(
            painter.HighQualityAntialiasing |
            painter.SmoothPixmapTransform |
            painter.Antialiasing)
        painter.setPen(self.__PEN)

        move = 0
        for width, color in bar:
            painter.setBrush(color)
            rect = QtCore.QRectF(
                self.Margins[0],
                self.Margins[1],
                total_width,
                total_height)
            if move:
                rect.setLeft(move)
            move+=width
            painter.drawRoundedRect(rect, 3, 3)
        painter.end()
        event.accept()


class JobSelectionDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.__jobs = plow.client.get_active_jobs()

        self.__txt_filter = QtGui.QLineEdit(self)
        self.__txt_filter.textChanged.connect(self.__filterChanged)
        self.__list_jobs = QtGui.QListWidget(self)
        self.__list_jobs.setSelectionMode(self.__list_jobs.ExtendedSelection)
        self.__list_jobs.addItems([job.name for job in self.__jobs])
        self.__list_jobs.sortItems()
        self.__list_jobs.itemDoubleClicked.connect(self.__itemDoubleClicked)

        self.__btns = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | 
            QtGui.QDialogButtonBox.Cancel)

        self.__btns.accepted.connect(self.accept)
        self.__btns.rejected.connect(self.reject)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.__txt_filter)
        layout.addWidget(self.__list_jobs)
        layout.addWidget(self.__btns)
        self.setLayout(layout)

    def __itemDoubleClicked(self, item):
        self.accept()

    def __filterChanged(self, value):
        if not value:
            self.__list_jobs.clear()
            self.__list_jobs.addItems([job.name for job in self.__jobs])
        else:
            new_items = [i.text() for i in self.__list_jobs.findItems(value, QtCore.Qt.MatchContains)]
            self.__list_jobs.clear()
            self.__list_jobs.addItems(new_items)
        self.__list_jobs.sortItems()

    def getSelectedJobs(self):
        jobNames = [str(item.text()) for item in self.__list_jobs.selectedItems()]
        if not jobNames:
            return []
        else:
            return plow.client.get_jobs(matchingOnly=True, name=jobNames, states=[plow.JobState.RUNNING])

class JobStateWidget(QtGui.QWidget):
    """
    A widget for displaying the job state.
    """
    def __init__(self, state, hasErrors=False, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.__state = state
        self.__hasErrors = hasErrors
        self.setSizePolicy(QtGui.QSizePolicy.Minimum,
            QtGui.QSizePolicy.Preferred)

    def getState(self):
        return self.__state

    def hasErrors(self):
        return self.__hasErrors

    def setState(self, state, hasErrors):
        self.__state = state
        self.__hasErrors = hasErrors

    def paintEvent(self, event):

        total_width = self.width()
        total_height = self.height()

        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHints(
            painter.HighQualityAntialiasing |
            painter.SmoothPixmapTransform |
            painter.Antialiasing)
        
        if self.__hasErrors:
            painter.setBrush(constants.RED)
        else:
            painter.setBrush(constants.COLOR_JOB_STATE[self.__state])
        
        painter.setPen(painter.brush().color().darker())

        rect = QtCore.QRect(0, 0, total_width, total_height)
        painter.drawRoundedRect(rect, 5, 5)
        painter.setPen(QtCore.Qt.black)
        painter.drawText(rect, QtCore.Qt.AlignCenter, constants.JOB_STATES[self.__state])
        painter.end()
