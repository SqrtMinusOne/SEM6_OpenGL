import random
import numpy as np

from PyQt5.QtWidgets import QMainWindow, QApplication
from OpenGL import GL, GLU, GLUT
import logging

from ui.mainwindow import Ui_MainWindow


def random_rgb():
    """
        Get random bright enough color
    """
    color = [random.random() for _ in range(3)]
    if sum(color) / len(color) < 0.5:
        return random_rgb()
    else:
        return color


def cart2pol(x, y):
    r = np.sqrt(x**2 + y**2)
    φ = np.arctan2(y, x)
    return r, φ


def pol2cart(r, φ):
    x = r * np.cos(φ)
    y = r * np.sin(φ)
    return x, y


# noinspection PyPep8Naming
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.primitiveComboBox.activated.connect(self.openGLWidget.update)
        self.openGLWidget.initializeGL()
        self.openGLWidget.paintGL = self.paintGL
        self.actionsDict = {
            "GL_POINTS": self.paintGL_random,
            "GL_LINES": self.paintGL_random,
            "GL_LINE_STRIP": self.paintGL_random,
            "GL_LINE_LOOP": self.paintGL_random,
            "GL_TRIANGLES": self.paintGL_random,
            "GL_TRIANGLE_STRIP": self.paintGL_circular_random,
            "GL_TRIANGLE_FAN": self.paintGL_circular_random,
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
        # print('Paint')
        self.loadScene()
        try:
            self.actionsDict[self.primitiveComboBox.currentText()]()
        except:
            pass

    def paintGL_random(self):
        GL.glPointSize(2)
        random_dict = {
            "GL_POINTS": {
                "GL_MODE": GL.GL_POINTS,
                "POINTS_NUM": 50
            },
            "GL_LINES": {
                "GL_MODE": GL.GL_LINES,
                "POINTS_NUM": 5 * 2
            },
            "GL_LINE_STRIP": {
                "GL_MODE": GL.GL_LINE_STRIP,
                "POINTS_NUM": 5
            },
            "GL_LINE_LOOP": {
                "GL_MODE": GL.GL_LINE_LOOP,
                "POINTS_NUM": 5
            },
            "GL_TRIANGLES": {
                "GL_MODE": GL.GL_TRIANGLES,
                "POINTS_NUM": 3 * 3
            }
        }
        GL.glBegin(random_dict[self.primitiveComboBox.currentText()]['GL_MODE'])
        self.drawRandomPoints(random_dict[self.primitiveComboBox.currentText()]['POINTS_NUM'])
        GL.glEnd()
        GL.glFinish()

    def drawRandomPoints(self, number):
        w, h = self.openGLWidget.width(), self.openGLWidget.height()
        for _ in range(number):
            GL.glColor3d(*random_rgb())
            GL.glVertex2d(np.random.randint(0, w), np.random.randint(0, h))

    def paintGL_circular_random(self):
        random_dict = {
            "GL_TRIANGLE_STRIP": GL.GL_TRIANGLE_STRIP,
            "GL_TRIANGLE_FAN": GL.GL_TRIANGLE_FAN,
        }
        GL.glPointSize(2)
        GL.glBegin(random_dict[self.primitiveComboBox.currentText()])
        w, h = self.openGLWidget.width(), self.openGLWidget.height()
        acc_angle = 0
        N = 5
        GL.glColor3d(*random_rgb())
        GL.glVertex2d(w / 2, h / 2)
        max_rad = min(w / 2, h / 2)
        for _ in range(N):
            GL.glColor3d(*random_rgb())
            r = np.random.randint(0, max_rad)
            acc_angle += random.random() * 360 / N
            x, y = pol2cart(r, acc_angle / 180 * np.pi)
            x += w / 2
            y += h / 2
            GL.glVertex2d(x, y)
        GL.glEnd()
        GL.glFinish()

    def paintGL_quads(self):
        GL.glPointSize(2)
        GL.glBegin(GL.GL_QUADS)
        w, h = self.openGLWidget.width(), self.openGLWidget.height()
        N = 4
        for _ in range(N):
            c_x, c_y = np.random.randint(10, w), np.random.randint(10, h)
            max_rad = min(c_x, w - c_x, c_y, h - c_y)
            acc_angle = 0
            r = np.random.randint(0, max_rad)
            for _ in range(4):
                GL.glColor3d(*random_rgb())
                acc_angle += random.random() * 360 / 4
                x, y = pol2cart(r, acc_angle / 180 * np.pi)
                x += c_x
                y += c_y
                GL.glVertex2d(x, y)
        GL.glEnd()
        GL.glFinish()

    def paintGL_quad_strip(self):
        GL.glPointSize(2)
        GL.glBegin(GL.GL_QUAD_STRIP)
        w, h = self.openGLWidget.width(), self.openGLWidget.height()
        N = 4
        y_s = [np.random.randint(0, h) for _ in range(N)]
        y_s.sort()
        x_s = [[np.random.randint(0, w) for _ in range(2)] for _ in range(N)]
        for i in range(N):
            x_s[i].sort()
            GL.glColor3d(*random_rgb())
            GL.glVertex2d(x_s[i][0], y_s[i])
            GL.glColor3d(*random_rgb())
            GL.glVertex2d(x_s[i][1], y_s[i])
        GL.glEnd()
        GL.glFinish()

    def paintGL_polygon(self):
        GL.glPointSize(2)
        GL.glBegin(GL.GL_POLYGON)
        w, h = self.openGLWidget.width(), self.openGLWidget.height()
        acc_angle = 0
        N = 4
        print('-----')
        max_rad = min(w / 2, h / 2)
        r = np.random.randint(max_rad / 2, max_rad)
        for _ in range(N):
            GL.glColor3d(*random_rgb())
            acc_angle += random.random() * 360 / N
            x, y = pol2cart(r, acc_angle / 180 * np.pi)
            print(r, acc_angle)
            print(x, y)
            x += w / 2
            y += h / 2
            GL.glVertex2d(x, y)
        GL.glEnd()
        GL.glFinish()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
