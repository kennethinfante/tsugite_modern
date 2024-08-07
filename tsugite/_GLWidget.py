#!/usr/bin/env python3

import numpy as np
import time
import math

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import *
from PyQt5.QtOpenGL import *

from OpenGL.GL import *  # imports start with gl
from OpenGL.GLUT import *  # imports start with glu
from OpenGL.GLU import *  # imports start with glut
from math import tan, pi

from JointTypes import JointType
from Geometries import Geometries
from Show import Show


# noinspection PyAttributeOutsideInit
class GLWidget(QGLWidget):
    def __init__(self, mainWindow=None, *__args):
        super().__init__(*__args)
        self.parent = mainWindow                        # cannot rename attribute because it extends QGLWidget class
        QGLWidget.__init__(self, mainWindow)
        # self.setMinimumSize(800, 800)
        self.setMouseTracking(True)
        self.click_time = time.time()
        self.x = 0
        self.y = 0

    def initializeGL(self):

        print(f"Opengl version: {glGetString(GL_VERSION)}")
        self.qglClearColor(QColor(255, 255, 255))
        glEnable(GL_DEPTH_TEST)  # enable depth testing
        sax = self.parent.findChild(QComboBox, "comboSLIDE").currentIndex()
        dim = self.parent.findChild(QSpinBox, "spinBoxRES").value()
        ang = self.parent.findChild(QDoubleSpinBox, "spinANG").value()
        dx = self.parent.findChild(QDoubleSpinBox, "spinDX").value()
        dy = self.parent.findChild(QDoubleSpinBox, "spinDY").value()
        dz = self.parent.findChild(QDoubleSpinBox, "spinDZ").value()
        dia = self.parent.findChild(QDoubleSpinBox, "spinDIA").value()
        tol = self.parent.findChild(QDoubleSpinBox, "spinTOL").value()
        spe = self.parent.findChild(QSpinBox, "spinSPEED").value()
        spi = self.parent.findChild(QSpinBox, "spinSPINDLE").value()
        aax = self.parent.findChild(QComboBox, "comboALIGN").currentIndex()
        inc = self.parent.findChild(QCheckBox, "checkINC").isChecked()
        fin = self.parent.findChild(QCheckBox, "checkFIN").isChecked()

        if self.parent.findChild(QRadioButton, "radioGCODE").isChecked():
            ext = "gcode"
        elif self.parent.findChild(QRadioButton, "radioNC").isChecked():
            ext = "nc"
        elif self.parent.findChild(QRadioButton, "radioSBP").isChecked():
            ext = "sbp"
        else:
            ext = "gcode"

        # these attributes have to be defined in this method, which overrides same method in base class
        self.joint_type = JointType(self, fs=[[[2, 0]], [[2, 1]]], sax=sax, dim=dim, angle=ang, td=[dx, dy, dz],
                                    tolerances=tol, bit_diameter=dia,
                                    fab_speed=spe, spindle_speed=spi, fab_ext=ext, align_ax=aax, incremental=inc,
                                    arc_interp=fin)

        self.show = Show(self, self.joint_type)

    def resizeGL(self, w, h):
        def perspective(fovY, aspect, zNear, zFar):
            fH = tan(fovY / 360. * pi) * zNear
            fW = fH * aspect
            glFrustum(-fW, fW, -fH, fH, zNear, zFar)

        # oratio = self.width() /self.height()
        ratio = 1.267

        if h * ratio > w:
            h = round(w / ratio)

        else:
            w = round(h * ratio)

        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        perspective(45.0, ratio, 1, 1000)
        glMatrixMode(GL_MODELVIEW)
        self.width = w
        self.height = h
        self.wstep = int(0.5 + w / 5)
        self.hstep = int(0.5 + h / 4)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
        # glViewport(0,0,self.width-self.wstep,self.height)
        glLoadIdentity()

        self.show.update()
        # ortho = np.multiply(np.array((-2, +2, -2, +2), dtype=float), self.zoomFactor)
        # glOrtho(ortho[0], ortho[1], ortho[2], ortho[3], 4.0, 15.0)

        glViewport(0, 0, self.width - self.wstep, self.height)
        # glLoadIdentity()
        # Color picking / editing
        # Pick faces -1: nothing, 0: hovered, 1: adding, 2: pulling

        # Draw back buffer colors
        if not self.joint_type.mesh.select.state == 2 and not self.joint_type.mesh.select.state == 12:
            self.show.pick(self.x, self.y, self.height)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
        elif self.joint_type.mesh.select.state == 2:  # Edit joint geometry
            self.joint_type.mesh.select.edit([self.x, self.y], self.show.view.xrot, self.show.view.yrot, w=self.width,
                                             h=self.height)
        elif self.joint_type.mesh.select.state == 12:  # Edit timber orientation/position
            self.joint_type.mesh.select.move([self.x, self.y], self.show.view.xrot, self.show.view.yrot)

        # Display main geometry
        self.show.end_grains()
        if self.show.view.show_feedback:
            self.show.unfabricatable()
            self.show.nondurable()
            self.show.unconnected()
            self.show.unbridged()
            self.show.checker()
            self.show.arrows()
            show_area = False  # <--replace by checkbox...
            if show_area:
                self.show.area()
        self.show.joint_geometry()

        if self.joint_type.mesh.select.suggestions_state >= 0:
            index = self.joint_type.mesh.select.suggestions_state
            if len(self.joint_type.suggestions) > index: self.show.difference_suggestion(index)

        # Display editing in action
        self.show.selected()
        self.show.moving_rotating()

        # Display milling paths
        self.show.milling_paths()

        # Suggestions
        if self.show.view.show_suggestions:
            for i in range(len(self.joint_type.suggestions)):
                # hquater = self.height / 4
                # wquater = self.width / 5
                glViewport(self.width - self.wstep, self.height - self.hstep * (i + 1), self.wstep, self.hstep)
                glLoadIdentity()
                if i == self.joint_type.mesh.select.suggestions_state:
                    glEnable(GL_SCISSOR_TEST)
                    glScissor(self.width - self.wstep, self.height - self.hstep * (i + 1), self.wstep, self.hstep)
                    glClearDepth(1.0)
                    glClearColor(0.9, 0.9, 0.9, 1.0)  # light grey
                    glClear(GL_COLOR_BUFFER_BIT)
                    glDisable(GL_SCISSOR_TEST)
                self.show.joint_geometry(mesh=self.joint_type.suggestions[i], lw=2, hidden=False)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if time.time() - self.click_time < 0.2:
                self.show.view.open_joint = not self.show.view.open_joint
            elif self.joint_type.mesh.select.state == 0:  # face hovered
                self.joint_type.mesh.select.start_pull([self.parent.scaling * e.x(), self.parent.scaling * e.y()])
            elif self.joint_type.mesh.select.state == 10:  # body hovered
                self.joint_type.mesh.select.start_move([self.parent.scaling * e.x(), self.parent.scaling * e.y()],
                                                       h=self.height)

            # SUGGESTION PICK
            elif self.joint_type.mesh.select.suggestions_state >= 0:
                index = self.joint_type.mesh.select.suggestions_state
                if len(self.joint_type.suggestions) > index:
                    self.joint_type.mesh = Geometries(self.joint_type,
                                                      hfs=self.joint_type.suggestions[index].height_fields)
                    self.joint_type.suggestions = []
                    self.joint_type.combine_and_buffer_indices()
                    self.joint_type.mesh.select.suggestions_state = -1
            # GALLERY PICK -- not implemented currently
            # elif joint_type.mesh.select.gallery_state>=0:
            #    index = joint_type.mesh.select.gallery_state
            #    if index<len(joint_type.gallery_figures):
            #        joint_type.mesh = Geometries(joint_type,hfs=joint_type.gallery_figures[index].height_fields)
            #        joint_type.gallery_figures = []
            #        view_opt.gallery=False
            #        joint_type.gallery_start_index = -20
            #        joint_type.combine_and_buffer_indices()
            else:
                self.click_time = time.time()
        elif e.button() == Qt.RightButton:
            self.show.view.start_rotation_xy(self.parent.scaling * e.x(), self.parent.scaling * e.y())

    def mouseMoveEvent(self, e):
        self.x = self.parent.scaling * e.x()
        self.y = self.parent.scaling * e.y()
        if self.show.view.dragged:
            self.show.view.update_rotation_xy(self.x, self.y)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self.joint_type.mesh.select.state == 2:  # face pulled
                self.joint_type.mesh.select.end_pull()
            elif self.joint_type.mesh.select.state == 12:  # body moved
                self.joint_type.mesh.select.end_move()
        elif e.button() == Qt.RightButton:
            self.show.view.end_rotation()

    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        # print("resize Hint!")
        return QSize(800, 800)
