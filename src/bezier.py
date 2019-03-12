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
        self.paintBezierCommon((p1, p2, p3, p4))

    def paintBezierCommon(self, points):
        lines = np.array([[(p2 - p1) / 100 * i + p1 for i in range(100)]
                          for p1, p2 in zip(points, points[1:])])
        while len(lines) > 1:
            lines = np.array([[
                    (p2 - p1) / 100 * i + p1 for i, p1, p2 in zip(range(100), line1, line2)
                ]
                for line1, line2 in zip(lines, lines[1:])
            ])
        GL.glBegin(GL.GL_LINE_STRIP)
        [GL.glVertex2d(*p) for p in lines[0]]
        GL.glEnd()
        GL.glFinish()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
