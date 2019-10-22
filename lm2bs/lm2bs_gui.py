# Simple PyQt-based GUI for converting Leica Matrix Screener output-folder/file 
# structures into Big Stitcher projects (Big Data Vieweer .xml/.h5 format)
#
# No warranties, use at your own risk
#
# Volker dot Hilsenstein at Monash dot edu
# Sep/Oct 2019
# License BSD-3

from PyQt5 import QtWidgets, QtCore, QtGui
from process_matrix_screener_data import Matrix_Mosaic_Processor
from background_worker import Worker, WorkerSignals
import pathlib


class MatrixScreenerToBigStitcherGUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(MatrixScreenerToBigStitcherGUI, self).__init__(parent)
        self.processor = None
        self.rootfolder = ""
        self.outfolder = ""
        self.threadpool = QtCore.QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.layout = QtWidgets.QVBoxLayout()

        # input root folder
        self.inputFolderButton = QtWidgets.QPushButton("Select root folder")
        self.selectedroot = QtWidgets.QLabel(self.rootfolder)
        # output folder
        self.outputFolderButton = QtWidgets.QPushButton("Select output folder")
        self.selectedoutput = QtWidgets.QLabel(self.outfolder)
        self.checkbox_2D = QtWidgets.QCheckBox("create 2D BDV file (max-projected Z)")
        self.checkbox_2D.setChecked(True)
        self.checkbox_3D = QtWidgets.QCheckBox("create 3D BDV file")
        self.checkbox_3D.setChecked(False)
        self.lineedit_zspacing = QtWidgets.QLineEdit()
        self.lineedit_zspacing.setText("1.00")
        self.lineedit_zspacing.setValidator(QtGui.QDoubleValidator(0.0, 1000.0, 2))
        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.listWidget.setGeometry(QtCore.QRect(10, 10, 211, 291))
        self.startProcessingButton = QtWidgets.QPushButton("Process selected folders")
        self.startProcessingButton.setEnabled(False)
        # Make connections
        self.listWidget.itemSelectionChanged.connect(self._checkProcessingButton)
        self.inputFolderButton.clicked.connect(self.get_root_folder)
        self.outputFolderButton.clicked.connect(self.get_output_folder)
        self.startProcessingButton.clicked.connect(self.process_selected)
        # Assemble GUI elements into final layout

        self.layout.addWidget(self.inputFolderButton)
        self.layout.addWidget(QtWidgets.QLabel("Root folder:"))
        self.layout.addWidget(self.selectedroot)
        self.layout.addWidget(self.outputFolderButton)
        self.layout.addWidget(QtWidgets.QLabel("Output folder:"))
        self.layout.addWidget(self.selectedoutput)
        self.layout.addWidget(self.checkbox_2D)
        self.layout.addWidget(self.checkbox_3D)
        self.layout.addWidget(QtWidgets.QLabel("Enter Z-Stack spacing in um:"))
        self.layout.addWidget(self.lineedit_zspacing)
        self.layout.addWidget(QtWidgets.QLabel("Select the wells to process:"))
        self.layout.addWidget(self.listWidget)
        self.layout.addWidget(self.startProcessingButton)

        self.setLayout(self.layout)

    def get_root_folder(self):
        self.rootfolder = str(
            QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        )
        # self.update_wells()
        self._trigger_update()

    def get_output_folder(self):
        self.outfolder = str(
            QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Folder")
        )
        self.selectedoutput.setText(self.outfolder)
        self._checkProcessingButton()

    def process_selected(self):
        self.startProcessingButton.setEnabled(False)

        worker = Worker(self._process_selected)
        worker.signals.finished.connect(self._checkProcessingButton)
        self.threadpool.start(worker)

    def _process_selected(self, *args, **kwargs):
        self.processor.process_wells(
            self._get_selected_indices(),
            outfolder_base=pathlib.Path(self.outfolder),
            projected=self.checkbox_2D.isChecked(),
            volume=self.checkbox_3D.isChecked(),
            zspacing=float(self.lineedit_zspacing.text()),
        )

    def _get_selected_indices(self):
        selectedindices = []
        for i in range(self.listWidget.count()):
            if self.listWidget.item(i).isSelected():
                selectedindices.append(i)
        return selectedindices

    def _checkProcessingButton(self):
        if (
            self.listWidget.count() > 0
            and self.outfolder != ""
            and len(self._get_selected_indices()) > 0
        ):
            self.startProcessingButton.setEnabled(True)
        else:
            self.startProcessingButton.setEnabled(False)

    def _trigger_update(self):
        worker = Worker(self.update_wells)
        # worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self._checkProcessingButton)
        # worker.signals.progress.connect(self.progress_fn)
        print("starting worker")
        self.threadpool.start(worker)

    def update_wells(self, *args, **kwargs):
        print("in update wells")
        self.selectedroot.setText(self.rootfolder)
        self.listWidget.clear()
        print("initializing Matrix processor")
        self.processor = Matrix_Mosaic_Processor(self.rootfolder)
        if self.processor.uvwells == []:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle("No files")
            msg.setText("No matrix screener datasets found. Correct folder selected?")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
            return
        items = [f"({w[0]},{w[1]})" for w in self.processor.uvwells]
        self.listWidget.addItems(items)
        # self._checkProcessingButton()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    form = MatrixScreenerToBigStitcherGUI()
    form.show()
    app.exec_()
