#!/usr/bin/env python3

import numpy as np
import time
import math
import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import *
from PyQt5.QtOpenGL import *

from utils import *
from _GLWidget import *

class mainWindow(QMainWindow):

    def __init__(self, *args):
        super(mainWindow, self).__init__(*args)
        self.scaling = self.devicePixelRatioF()

        loadUi('Tsugite.ui', self)
        self.setupUi()

        self.title = "Tsugite"
        self.filename = get_untitled_filename("Untitled","tsu","_")
        self.setWindowTitle(self.filename.split(os.sep)[-1]+" - "+self.title)
        self.setWindowIcon(QIcon("tsugite_icon.png"))

        self.glWidget = GLWidget(self)

        self.H_layout.addWidget(self.glWidget)
        # self.setCentralWidget(self.glWidget)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("To open and close the joint: PRESS 'Open/close joint' button or DOUBLE-CLICK anywhere inside the window.")

        timer = QTimer(self)
        timer.setInterval(20)   # period, in milliseconds
        timer.timeout.connect(self.glWidget.updateGL)
        timer.start()


    def setupUi(self):
        #get opengl window size
        self.x_range = [10,500]
        self.y_range = [10,500]

        #---Design
        self.findChild(QPushButton, "buttonOPEN").clicked.connect(self.open_close_joint)
        self.findChild(QCheckBox, "checkFEED").stateChanged.connect(self.set_feedback_view)
        #suggestions
        self.findChild(QComboBox, "comboSLIDE").currentTextChanged.connect(self.change_sliding_axis)
        self.findChild(QSpinBox, "spinBoxNUM").valueChanged.connect(self.change_number_of_timbers)
        self.findChild(QSpinBox, "spinBoxRES").valueChanged.connect(self.change_resolution)
        self.findChild(QDoubleSpinBox, "spinANG").valueChanged.connect(self.set_angle_of_intersection)
        self.findChild(QCheckBox, "checkCUBE").stateChanged.connect(self.set_all_timber_same)
        self.findChild(QDoubleSpinBox, "spinDX").valueChanged.connect(self.set_timber_X)
        self.findChild(QDoubleSpinBox, "spinDY").valueChanged.connect(self.set_timber_Y)
        self.findChild(QDoubleSpinBox, "spinDZ").valueChanged.connect(self.set_timber_Z)
        self.findChild(QPushButton, "buttonR").clicked.connect(self.randomize_geometry)
        self.findChild(QPushButton, "buttonC").clicked.connect(self.clear_geometry)
        #gallery
        #---Fabrication
        self.findChild(QDoubleSpinBox, "spinDIA").valueChanged.connect(self.set_milling_bit_diameter)
        self.findChild(QDoubleSpinBox, "spinTOL").valueChanged.connect(self.set_fab_tolerance)
        self.findChild(QSpinBox, "spinSPEED").valueChanged.connect(self.set_fab_speed)
        self.findChild(QSpinBox, "spinSPINDLE").valueChanged.connect(self.set_fab_spindlespeed)
        self.findChild(QComboBox, "comboALIGN").currentTextChanged.connect(self.set_milling_path_axis_alginement)
        self.findChild(QCheckBox, "checkINC").stateChanged.connect(self.set_incremental)
        self.findChild(QCheckBox, "checkFIN").stateChanged.connect(self.set_interpolation)
        self.findChild(QPushButton, "buttonPATH").clicked.connect(self.set_millingpath_view)
        self.findChild(QPushButton, "buttonGCODE").clicked.connect(self.export_gcode)
        self.findChild(QRadioButton, "radioGCODE").toggled.connect(self.set_gcode_as_standard)
        self.findChild(QRadioButton, "radioNC").toggled.connect(self.set_nccode_as_standard)
        self.findChild(QRadioButton, "radioSBP").toggled.connect(self.set_sbp_as_standard)
        #---MENU
        #---File
        self.findChild(QAction, "actionNew").triggered.connect(self.new_file)
        self.findChild(QAction, "actionOpen").triggered.connect(self.open_file)
        self.findChild(QAction, "actionSave").triggered.connect(self.save_file)
        self.findChild(QAction, "actionSaveas").triggered.connect(self.save_file_as)
        #---View
        self.findChild(QAction, "actionHIDDEN").triggered.connect(self.show_hide_hidden_lines)
        self.findChild(QAction, "actionA").triggered.connect(self.show_hide_timbers)
        self.findChild(QAction, "actionB").triggered.connect(self.show_hide_timbers)
        self.findChild(QAction, "actionC").triggered.connect(self.show_hide_timbers)
        self.findChild(QAction, "actionD").triggered.connect(self.show_hide_timbers)
        self.findChild(QAction, "actionALL").triggered.connect(self.show_all_timbers)
        self.findChild(QAction, "actionAXO").triggered.connect(self.set_standard_rotation)
        self.findChild(QAction, "actionPLN").triggered.connect(self.set_closest_plane_rotation)

    @pyqtSlot()
    def open_close_joint(self):
        self.glWidget.show.view.open_joint = not self.glWidget.show.view.open_joint

    @pyqtSlot()
    def set_feedback_view(self):
        bool = self.findChild(QCheckBox, "checkFEED").checkState()
        self.glWidget.show.view.show_feedback = bool

    @pyqtSlot()
    def change_sliding_axis(self):
        ax = self.findChild(QComboBox, "comboSLIDE").currentIndex()
        bool, msg = self.glWidget.type.update_sliding_direction(ax)
        print("msg")
        #QMessageBox = ...

    @pyqtSlot()
    def change_number_of_timbers(self):
        val = self.findChild(QSpinBox, "spinBoxNUM").value()
        self.glWidget.type.update_number_of_components(val)

    @pyqtSlot()
    def change_resolution(self):
        val = self.findChild(QSpinBox, "spinBoxRES").value()
        add = val-self.glWidget.type.dim
        self.glWidget.type.update_dimension(add)

    @pyqtSlot()
    def set_angle_of_intersection(self):
        val = self.findChild(QDoubleSpinBox, "spinANG").value()
        self.glWidget.type.update_angle(val)

    @pyqtSlot()
    def set_timber_X(self):
        val = self.findChild(QDoubleSpinBox, "spinDX").value()
        mp = self.glWidget.show.view.show_milling_path
        if mp: self.glWidget.type.create_and_buffer_vertices(milling_path=True)
        if self.findChild(QCheckBox, "checkCUBE").isChecked():
            self.glWidget.type.update_timber_width_and_height([0,1,2],val,milling_path=mp)
            self.findChild(QDoubleSpinBox, "spinDY").setValue(val)
            self.findChild(QDoubleSpinBox, "spinDZ").setValue(val)
        else:
            self.glWidget.type.update_timber_width_and_height([0],val,milling_path=mp)

    @pyqtSlot()
    def set_timber_Y(self):
        val = self.findChild(QDoubleSpinBox, "spinDY").value()
        mp = self.glWidget.show.view.show_milling_path
        if self.findChild(QCheckBox, "checkCUBE").isChecked():
            self.glWidget.type.update_timber_width_and_height([0,1,2],val,milling_path=mp)
            self.findChild(QDoubleSpinBox, "spinDX").setValue(val)
            self.findChild(QDoubleSpinBox, "spinDZ").setValue(val)
        else:
            self.glWidget.type.update_timber_width_and_height([1],val,milling_path=mp)

    @pyqtSlot()
    def set_timber_Z(self):
        val = self.findChild(QDoubleSpinBox, "spinDZ").value()
        mp = self.glWidget.show.view.show_milling_path
        if self.findChild(QCheckBox, "checkCUBE").isChecked():
            self.glWidget.type.update_timber_width_and_height([0,1,2],val,milling_path=mp)
            self.findChild(QDoubleSpinBox, "spinDX").setValue(val)
            self.findChild(QDoubleSpinBox, "spinDY").setValue(val)
        else:
            self.glWidget.type.update_timber_width_and_height([2],val,milling_path=mp)

    @pyqtSlot()
    def set_all_timber_same(self):
        mp = self.glWidget.show.view.show_milling_path
        if self.findChild(QCheckBox, "checkCUBE").isChecked():
            val = self.glWidget.type.real_tim_dims[0]
            self.glWidget.type.update_timber_width_and_height([0,1,2],val,milling_path=mp)
            self.findChild(QDoubleSpinBox, "spinDY").setValue(val)
            self.findChild(QDoubleSpinBox, "spinDZ").setValue(val)

    @pyqtSlot()
    def randomize_geometry(self):
        self.glWidget.type.mesh.randomize_height_fields()

    @pyqtSlot()
    def clear_geometry(self):
        self.glWidget.type.mesh.clear_height_fields()

    @pyqtSlot()
    def set_milling_bit_diameter(self):
        val = self.findChild(QDoubleSpinBox, "spinDIA").value()
        self.glWidget.type.fab.real_dia = val
        self.glWidget.type.fab.radius = 0.5 * self.glWidget.type.fab.real_dia - self.glWidget.type.fab.tolerances
        self.glWidget.type.fab.diameter = 2 * self.glWidget.type.fab.radius
        self.glWidget.type.fab.vdia = self.glWidget.type.fab.diameter / self.glWidget.type.ratio
        self.glWidget.type.fab.vrad = self.glWidget.type.fab.radius / self.glWidget.type.ratio
        if self.glWidget.show.view.show_milling_path:
            self.glWidget.type.create_and_buffer_vertices(milling_path=True)
            self.glWidget.type.combine_and_buffer_indices(milling_path=True)

    @pyqtSlot()
    def set_fab_tolerance(self):
        val = self.findChild(QDoubleSpinBox, "spinTOL").value()
        self.glWidget.type.fab.tolerances = val
        self.glWidget.type.fab.radius = 0.5 * self.glWidget.type.fab.real_dia - self.glWidget.type.fab.tolerances
        self.glWidget.type.fab.diameter = 2 * self.glWidget.type.fab.radius
        self.glWidget.type.fab.vdia = self.glWidget.type.fab.diameter / self.glWidget.type.ratio
        self.glWidget.type.fab.vrad = self.glWidget.type.fab.radius / self.glWidget.type.ratio
        self.glWidget.type.fab.vtol = self.glWidget.type.fab.tolerances / self.glWidget.type.ratio
        if self.glWidget.show.view.show_milling_path:
            self.glWidget.type.create_and_buffer_vertices(milling_path=True)
            self.glWidget.type.combine_and_buffer_indices(milling_path=True)

    @pyqtSlot()
    def set_fab_speed(self):
        val = self.findChild(QSpinBox, "spinSPEED").value()
        self.glWidget.type.fab.fab_speed = val


    @pyqtSlot()
    def set_fab_spindlespeed(self):
        val = self.findChild(QSpinBox, "spinSPINDLE").value()
        self.glWidget.type.fab.spindle_speed = val

    @pyqtSlot()
    def set_milling_path_axis_alginement(self):
        val = self.findChild(QComboBox, "comboALIGN").currentIndex()
        self.glWidget.type.fab.align_ax = val

    @pyqtSlot()
    def set_incremental(self):
        val = self.findChild(QCheckBox, "checkINC").isChecked()
        self.glWidget.type.incremental = val

    @pyqtSlot()
    def set_interpolation(self):
        val = self.findChild(QCheckBox, "checkFIN").isChecked()
        self.glWidget.type.fab.arc_interp = val

    @pyqtSlot()
    def set_millingpath_view(self):
        self.glWidget.show.view.show_milling_path = not self.glWidget.show.view.show_milling_path
        bool = self.glWidget.show.view.show_milling_path
        self.glWidget.type.create_and_buffer_vertices(milling_path=bool)
        self.glWidget.type.combine_and_buffer_indices(milling_path=bool)

    @pyqtSlot()
    def export_gcode(self):
        if not self.glWidget.show.view.show_milling_path:
            self.glWidget.show.view.show_milling_path = True
            self.glWidget.type.create_and_buffer_vertices(milling_path=True)
            self.glWidget.type.combine_and_buffer_indices(milling_path=True)
        self.glWidget.type.fab.export_gcode(filename_tsu=self.filename)

    @pyqtSlot()
    def set_gcode_as_standard(self):
        bool = self.findChild(QRadioButton, "radioGCODE").isChecked()
        if bool: self.glWidget.type.fab.fab_ext = "gcode"

    @pyqtSlot()
    def set_nccode_as_standard(self):
        bool = self.findChild(QRadioButton, "radioNC").isChecked()
        if bool: self.glWidget.type.fab.fab_ext = "nc"

    @pyqtSlot()
    def set_sbp_as_standard(self):
        bool = self.findChild(QRadioButton, "radioSBP").isChecked()
        if bool: self.glWidget.type.fab.fab_ext = "sbp"

    @pyqtSlot()
    def new_file(self):
        self.filename = get_untitled_filename("Untitled","tsu","_")
        self.setWindowTitle(self.filename.split("/")[-1]+" - "+self.title)
        self.glWidget.show.view.show_milling_path=False
        self.glWidget.type.reset()
        self.set_ui_values()
        self.show_all_timbers()

    @pyqtSlot()
    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(filter="Tsugite files (*.tsu)")
        if filename!='':
            self.filename = filename
            self.setWindowTitle(self.filename.split("/")[-1]+" - "+self.title)
            self.findChild(QCheckBox, "checkCUBE").setChecked(False)
            self.glWidget.type.open(self.filename)
            self.set_ui_values()

    @pyqtSlot()
    def save_file(self):
        self.glWidget.type.save(self.filename)

    @pyqtSlot()
    def save_file_as(self):
        filename, _ = QFileDialog.getSaveFileName(filter="Tsugite files (*.tsu)")
        if filename!='':
            self.filename = filename
            self.setWindowTitle(self.filename.split("/")[-1]+" - "+self.title)
            self.glWidget.type.save(self.filename)

    @pyqtSlot()
    def show_hide_hidden_lines(self):
        self.glWidget.show.view.show_hidden_lines = self.findChild(QAction, "actionHIDDEN").isChecked()

    @pyqtSlot()
    def show_hide_timbers(self):
        names = ["A","B","C","D"]
        for i,item in enumerate(names):
            bool = self.findChild(QAction, "action"+names[i]).isChecked()
            self.glWidget.show.view.hidden[i] = not bool

    @pyqtSlot()
    def show_all_timbers(self):
        names = ["A","B","C","D"]
        for i,item in enumerate(names):
            self.findChild(QAction, "action"+names[i]).setChecked(True)
            self.glWidget.show.view.hidden[i] = False

    @pyqtSlot()
    def set_standard_rotation(self):
        self.glWidget.show.view.xrot = 0.8
        self.glWidget.show.view.yrot = 0.4

    @pyqtSlot()
    def set_closest_plane_rotation(self):
        xrot = self.glWidget.show.view.xrot
        yrot = self.glWidget.show.view.yrot
        nang = 0.5*math.pi
        xrot = round(xrot/nang,0)*nang
        yrot = round(yrot/nang,0)*nang
        self.glWidget.show.view.xrot = xrot
        self.glWidget.show.view.yrot = yrot

    def set_ui_values(self):
        self.findChild(QComboBox, "comboSLIDE").setCurrentIndex(self.glWidget.type.sax)
        self.findChild(QSpinBox, "spinBoxNUM").setValue(self.glWidget.type.noc)
        self.findChild(QSpinBox, "spinBoxRES").setValue(self.glWidget.type.dim)
        self.findChild(QDoubleSpinBox, "spinANG").setValue(self.glWidget.type.ang)
        self.findChild(QDoubleSpinBox, "spinDX").setValue(self.glWidget.type.real_tim_dims[0])
        self.findChild(QDoubleSpinBox, "spinDY").setValue(self.glWidget.type.real_tim_dims[1])
        self.findChild(QDoubleSpinBox, "spinDZ").setValue(self.glWidget.type.real_tim_dims[2])
        if np.max(self.glWidget.type.real_tim_dims)==np.min(self.glWidget.type.real_tim_dims):
            self.findChild(QCheckBox, "checkCUBE").setChecked(True)
        else: self.findChild(QCheckBox, "checkCUBE").setChecked(False)
        self.findChild(QDoubleSpinBox, "spinDIA").setValue(self.glWidget.type.fab.real_dia)
        self.findChild(QDoubleSpinBox, "spinTOL").setValue(self.glWidget.type.fab.tolerances)
        self.findChild(QSpinBox, "spinSPEED").setValue(self.glWidget.type.fab.fab_speed)
        self.findChild(QSpinBox, "spinSPINDLE").setValue(self.glWidget.type.fab.spindle_speed)
        self.findChild(QCheckBox, "checkINC").setChecked(self.glWidget.type.incremental)
        self.findChild(QCheckBox, "checkFIN").setChecked(self.glWidget.type.fab.arc_interp)
        self.findChild(QComboBox, "comboALIGN").setCurrentIndex(self.glWidget.type.fab.align_ax)
        if self.glWidget.type.fab.fab_ext== "gcode":
            self.findChild(QRadioButton, "radioGCODE").setChecked(True)
        elif self.glWidget.type.fab.fab_ext== "sbp":
            self.findChild(QRadioButton, "radioSBP").setChecked(True)
        elif self.glWidget.type.fab.fab_ext== "nc":
            self.findChild(QRadioButton, "radioNC").setChecked(True)

    def keyPressEvent(self, e):
        if e.key()==Qt.Key_Shift:
            self.glWidget.type.mesh.select.shift = True
            self.glWidget.type.mesh.select.refresh = True

    def keyReleaseEvent(self, e):
        if e.key()==Qt.Key_Shift:
            self.glWidget.type.mesh.select.shift = False
            self.glWidget.type.mesh.select.refresh = True

class MovieSplashScreen(QSplashScreen):

    def __init__(self, movie, parent = None):


        movie.jumpToFrame(0)
        pixmap = QPixmap(movie.frameRect().size())

        QSplashScreen.__init__(self, pixmap)
        self.movie = movie
        self.movie.frameChanged.connect(self.repaint)

    def showEvent(self, event):
        self.movie.start()

    def hideEvent(self, event):
        self.movie.stop()

    def paintEvent(self, event):

        painter = QPainter(self)
        pixmap = self.movie.currentPixmap()
        self.setMask(pixmap.mask())
        painter.drawPixmap(0, 0, pixmap)

    def sizeHint(self):
        return self.movie.scaledSize()