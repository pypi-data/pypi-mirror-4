"""
<name>Model File</name>
<description>Load a Model Map</description>
<contact>Miha Stajdohar (miha.stajdohar(@at@)gmail.com)</contact>
<icon>icons/DistanceFile.png</icon>
<priority>6510</priority>
"""
import os.path
import cPickle as pickle
import bz2

import OWGUI
import orngMisc

from OWWidget import *
from Orange import data, misc

class OWModelFile(OWWidget):
    settingsList = ["files", "file_index"]

    def __init__(self, parent=None, signalManager=None):
        OWWidget.__init__(self, parent, signalManager, name='Model File', wantMainArea=0, resizingEnabled=1)

        self.outputs = [("Distances", misc.SymMatrix),
                        ("Model Meta-data", data.Table),
                        ("Original Data", data.Table)]

        #self.dataFileBox.setTitle("Model File")
        self.files = []
        self.file_index = 0

        self.matrix = None
        self.matrices = None
        self.model_data = None
        self.original_data = None
        self.selected_matrix = None

        self.loadSettings()

        self.fileBox = OWGUI.widgetBox(self.controlArea, "Model File", addSpace=True)
        hbox = OWGUI.widgetBox(self.fileBox, orientation=0)
        self.filecombo = OWGUI.comboBox(hbox, self, "file_index", callback=self.loadFile)
        self.filecombo.setMinimumWidth(250)
        button = OWGUI.button(hbox, self, '...', callback=self.browseFile)
        button.setIcon(self.style().standardIcon(QStyle.SP_DirOpenIcon))
        button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)

        self.propertiesBox = OWGUI.widgetBox(self.controlArea, "Properties", addSpace=True)
        self.select_matrix_combo = OWGUI.comboBox(self.propertiesBox, self, "selected_matrix", label='Select matrix:', orientation='horizontal', callback=self.select_matrix)
        self.select_matrix_combo.setEnabled(False)

#        Moved to SymMatrixTransform widget
#
#        ribg = OWGUI.radioButtonsInBox(self.controlArea, self, "normalizeMethod", [], "Normalize method", callback = self.setNormalizeMode)
#        OWGUI.appendRadioButton(ribg, self, "normalizeMethod", "None", callback = self.setNormalizeMode)
#        OWGUI.appendRadioButton(ribg, self, "normalizeMethod", "To interval [0,1]", callback = self.setNormalizeMode)
#        OWGUI.appendRadioButton(ribg, self, "normalizeMethod", "Sigmoid function: 1 / (1 + e^x)", callback = self.setNormalizeMode)
#        
#        ribg = OWGUI.radioButtonsInBox(self.controlArea, self, "invertMethod", [], "Invert method", callback = self.setInvertMode)
#        OWGUI.appendRadioButton(ribg, self, "invertMethod", "None", callback = self.setInvertMode)
#        OWGUI.appendRadioButton(ribg, self, "invertMethod", "-X", callback = self.setInvertMode)
#        OWGUI.appendRadioButton(ribg, self, "invertMethod", "1 - X", callback = self.setInvertMode)
#        OWGUI.appendRadioButton(ribg, self, "invertMethod", "Max - X", callback = self.setInvertMode)
#        OWGUI.appendRadioButton(ribg, self, "invertMethod", "1 / X", callback = self.setInvertMode)

        OWGUI.rubber(self.controlArea)

        self.adjustSize()

        for i in range(len(self.files) - 1, -1, -1):
            if not (os.path.exists(self.files[i]) and os.path.isfile(self.files[i])):
                del self.files[i]

        if self.files:
            self.loadFile()

    def select_matrix(self):
        self.matrix = self.matrices[str(self.select_matrix_combo.currentText())]
        self.relabel()

    def browseFile(self):
        if self.files:
            lastPath = os.path.split(self.files[0])[0]
        else:
            lastPath = "."
        fn = unicode(QFileDialog.getOpenFileName(self, "Open Model Map File",
                                             lastPath, "Model Map (*.bz2)"))
        fn = os.path.abspath(fn)
        if fn in self.files: # if already in list, remove it
            self.files.remove(fn)
        self.files.insert(0, fn)
        self.file_index = 0
        self.loadFile()

    def loadFile(self):
        if self.file_index:
            fn = self.files[self.file_index]
            self.files.remove(fn)
            self.files.insert(0, fn)
            self.file_index = 0
        else:
            fn = self.files[0]

        self.filecombo.clear()
        self.select_matrix_combo.clear()
        self.select_matrix_combo.setEnabled(False)

        for file in self.files:
            self.filecombo.addItem(os.path.split(file)[1])
        #self.filecombo.updateGeometry()

        self.matrix = None
        self.matrices = None
        self.model_data = None
        self.original_data = None
        pb = OWGUI.ProgressBar(self, 100)
        pb.advance()
        self.error()
        try:
            matrix, self.model_data, self.original_data = pickle.load(bz2.BZ2File('%s' % fn, "r"))
            if type(matrix) == type({}):
                for name in matrix.iterkeys():
                    self.select_matrix_combo.addItem(name)

                self.matrices = matrix
                self.matrix = matrix[str(self.select_matrix_combo.currentText())]
                self.select_matrix_combo.setEnabled(True)

            elif type(matrix) == type(misc.SymMatrix(1)):
                self.matrix = matrix
                self.select_matrix_combo.addItem("Single matrix found")
            else:
                try:
                    self.matrix = misc.SymMatrix(matrix)
                    self.select_matrix_combo.addItem("Single matrix found")
                except TypeError:
                    self.matrix = misc.SymMatrix(matrix + matrix.T)
                    self.select_matrix_combo.addItem("Single matrix found")

        except Exception, ex:
            self.error("Error while reading the file: '%s'" % str(ex))
            return

        pb.finish()
        self.relabel()

    def relabel(self):
        self.error()
        if self.matrix is not None:
            if self.model_data is not None and self.matrix.dim == len(self.model_data):
                self.matrix.setattr("items", self.model_data)
            else:
                self.error("The number of model doesn't match the matrix dimension. Invalid Model Map file.")

            if self.original_data is not None:
                self.matrix.setattr("original_data", self.original_data)

            self.send("Distances", self.matrix)

        if self.model_data is not None:
            self.send("Model Meta-data", self.model_data)

        if self.original_data is not None:
            self.send("Original Data", self.original_data)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWModelFile()
    ow.show()
    a.exec_()
    ow.saveSettings()
