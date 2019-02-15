import random
import numpy as np

from PyQt5.QtWidgets import QMainWindow, QApplication
from OpenGL import GL, GLU, GLUT
import logging

from mainwindow import Ui_MainWindow


def random_rgb():
    """
        Get random bright enough color
    """
    color = [random.random() for _ in range(3)]
    if sum(color) / len(color) < 0.5:
        return random_rgb()
    else:
        return color


# noinspection PyPep8Naming
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.primitiveComboBox.activated.connect(self.openGLWidget.update)
        self.openGLWidget.initializeGL()
        self.openGLWidget.paintGL = self.paintGL
        self.actionsDict = {
            "GL_POINTS": self.paintGL_points,
            "GL_LINES": self.paintGL_lines,
            "GL_LINE_STRIP": self.paintGL_line_loop,
            "GL_TRIANGLES": self.paintGL_triangles,
            "GL_TRIANGLE_STRIP": self.paintGL_triangle_strip,
            "GL_TRIANGLE_FAN": self.paintGL_triangle_fan,
            "GL_QUADS": self.paintGL_quads,
            "GL_QUAD_STRIP": self.paintGL_quad_strip,
            "GL_POLYGON": self.paintGL_polygon
        }

    def loadScene(self):
        width, height = self.openGLWidget.width(), self.openGLWidget.height()
        GL.glViewport(0, 0, width, height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, width, 0, height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

    def paintGL(self):
        print('Paint')
        self.loadScene()
        self.actionsDict[self.primitiveComboBox.currentText()]()

    def paintGL_points(self):
        GL.glPointSize(2)
        GL.glBegin(GL.GL_POINTS)
        w, h = self.openGLWidget.width(), self.openGLWidget.height()
        for _ in range(5):
            GL.glColor3d(*random_rgb())
            GL.glVertex2d(np.random.randint(0, w), np.random.randint(0, h))
            pass
        GL.glEnd()
        GL.glFinish()
        pass

    def paintGL_lines(self):
        print('Lines')
        pass

    def paintGL_line_strip(self):
        pass

    def paintGL_line_loop(self):
        pass

    def paintGL_triangles(self):
        pass

    def paintGL_triangle_strip(self):
        pass

    def paintGL_triangle_fan(self):
        pass

    def paintGL_quads(self):
        pass

    def paintGL_quad_strip(self):
        pass

    def paintGL_polygon(self):
        pass


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
