import random
import numpy as np

from PyQt5.QtWidgets import QMainWindow, QApplication
from OpenGL import GL, GLU, GLUT
import logging

from ui.bezier import Ui_BezierWindow
from main import cart2pol, pol2cart, random_rgb


class ControlElement:
    p = 0.02

    def __init__(self, x, y, color=None):
        self.x, self.y = x, y
        self.color = random_rgb() if color is None else color

    def get_points(self):
        yield self.x - self.p / 2, self.y - self.p / 2
        yield self.x + self.p / 2, self.y - self.p / 2
        yield self.x + self.p / 2, self.y + self.p / 2
        yield self.x - self.p / 2, self.y + self.p / 2

    def set_center(self, x, y):
        self.x, self.y = x, y

    def center(self):
        return np.array((self.x, self.y))

    def has_point(self, x, y):
        p = np.array((x, y))
        p_s = np.array([p for p in self.get_points()])
        return np.all((
            np.all(p_s[0] <= p),
            np.all(p_s[2] >= p)
        ))

    def paint(self):
        GL.glBegin(GL.GL_LINE_LOOP)
        GL.glColor4d(*self.color)
        for point in self.get_points():
            GL.glVertex2d(*point)
        GL.glEnd()


# noinspection PyPep8Naming
class MainWindow(QMainWindow, Ui_BezierWindow):
    controls = []
    move_controls = []

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.openGLWidget.initializeGL()
        self.openGLWidget.paintGL = self.paintGL
        self.openGLWidget.mouseMoveEvent = self.onOpenGLWidgetMouseMoved
        self.openGLWidget.mousePressEvent = self.onOpenGLWidgetMousePressed
        self.openGLWidget.mouseReleaseEvent = self.onOpenGLWidgetMouseReleased
        self.updateButton.clicked.connect(self.generateControls)
        self.generateControls()

    def onOpenGLWidgetMousePressed(self, event):
        width, height = self.openGLWidget.width(), self.openGLWidget.height()
        point = np.array((event.x() / width, 1 - (event.y() / height)))
        for control in self.controls:
            if control.has_point(*point):
                self.move_controls.append((control, point - control.center()))

    def onOpenGLWidgetMouseReleased(self, event):
        self.move_controls.clear()

    def onOpenGLWidgetMouseMoved(self, event):
        if len(self.move_controls) == 0:
            return
        width, height = self.openGLWidget.width(), self.openGLWidget.height()
        point = (event.x() / width, 1 - (event.y() / height))
        for control, delta in self.move_controls:
            control.set_center(*(point - delta))
        self.openGLWidget.update()

    def loadScene(self):
        width, height = self.openGLWidget.width(), self.openGLWidget.height()
        GL.glViewport(0, 0, width, height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, 1, 0, 1, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

    def generateControls(self):
        color = random_rgb()
        self.controls = [ControlElement(np.random.random(), np.random.random(), color) for _ in range(4)]
        self.openGLWidget.update()

    def paintGL(self):
        self.loadScene()
        try:
            self.drawStuff()
        except Exception as exp:
            print(exp)
            pass

    def drawStuff(self):
        [c.paint() for c in self.controls]
        self.paintBezier(*[c.center() for c in self.controls[0:4]])
        self.paintControlLines()

    def paintControlLines(self):
        GL.glColor4d(1, 1, 1, 1)
        GL.glBegin(GL.GL_LINE_STRIP)
        [GL.glVertex2d(*c.center()) for c in self.controls]
        GL.glEnd()
        GL.glFinish()

    def paintBezier(self, p1, p2, p3, p4):
        line11, line12, line13 = [], [], []

        # GL.glBegin(GL.GL_POINTS)
        # GL.glVertex2d(*p4)
        # GL.glVertex2d(*p3)
        # GL.glEnd()

        GL.glBegin(GL.GL_LINE_STRIP)

        for i in range(100):
            line11.append((p2 - p1) / 100 * i + p1)
            line12.append((p3 - p2) / 100 * i + p2)
            line13.append((p4 - p3) / 100 * i + p3)

        line21, line22 = [], []

        for i in range(100):
            dot1 = line11[i]
            dot2 = line12[i]
            dot3 = line13[i]
            line21.append(((dot2 - dot1) / 100 * i + dot1))
            line22.append(((dot3 - dot2) / 100 * i + dot2))

        for i in range(100):
            dot21 = line21[i]
            dot22 = line22[i]
            GL.glVertex2d(*((dot22 - dot21) / 100 * i + dot21))

        GL.glEnd()
        GL.glFinish()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
