#!/usr/bin/env python3

import sys
import time
import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import *
from PyQt5.QtOpenGL import *

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from _mainWindow import *

# deal with dpi
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # enable highdpi scaling
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  # use highdpi icons
app = QApplication(sys.argv)
movie = QMovie("tsugite_loading_3d.gif")

splash = MovieSplashScreen(movie)

splash.show()

start = time.time()

while movie.state() == QMovie.Running and time.time() < start + 1:
    app.processEvents()
# screen = app.screens()[0]
# dpi = screen.physicalDotsPerInch()

window = mainWindow()
window.show()
splash.finish(window)
sys.exit(app.exec_())
