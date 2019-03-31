import threading
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QOpenGLShaderProgram, QOpenGLShader, QMatrix4x4, \
    QVector3D
from OpenGL import GL

from ui.shaders import Ui_ShadersWindow
from main import pol2cart


def load_shader(shader_type, filename):
    with open(filename, 'r') as file:
        content = file.read()
        return create_shader(shader_type, content)


def create_shader(shader_type, source):
    shader = GL.glCreateShader(shader_type)
    GL.glShaderSource(shader, source)
    GL.glCompileShader(shader)
    return shader


def star_coords(point, rad, angle=0):
    pts1 = []
    pts2 = []
    angle -= np.pi / 2
    coef = 0.382
    for a in range(5):
        delta = np.array(pol2cart(rad, a * np.pi * 2 / 5 + angle))
        delta2 = np.array(
            pol2cart(
                rad *
                coef,
                a *
                np.pi *
                2 /
                5 +
                angle -
                np.pi))
        pts1.append(point - delta)
        pts2.append(point - delta2)
    res = [point]
    for i1, i2 in zip(range(5), [3, 4, 0, 1, 2]):
        res.extend([pts1[i1], pts2[i2]])
    res.append(pts1[0])
    return [list(p) for p in res]
    # return [list(p) for p in [pts[0], pts[2], pts[4], pts[1], pts[3]]]


# noinspection PyPep8Naming
class MainWindow(QMainWindow, Ui_ShadersWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.star_color = (255 / 255, 223 / 255, 0 / 255)
        self.flag_color = (223 / 255, 37 / 255, 0 / 255)
        self.star_coords = []
        self.setupUi(self)
        self.openGLWidget.initializeGL = self.initializeGL
        self.openGLWidget.paintGL = self.paintGL
        self.keyPressEvent = self.onKeyPressed
        self.angleX = 0
        self.angleY = 0
        self.mutex = threading.Lock()
        self.shaders = QOpenGLShaderProgram()

    def loadScene(self):
        width, height = self.openGLWidget.width(), self.openGLWidget.height()
        GL.glViewport(0, 0, width, height)
        # Why the heck this does not work...
        # GL.glMatrixMode(GL.GL_PROJECTION)
        # GL.glLoadIdentity()
        # GL.glFrustum(-1, 1, -1, 1, 1, 20)
        # GL.glMatrixMode(GL.GL_MODELVIEW)
        # GL.glLoadIdentity()

    def initializeGL(self):
        GL.glClearColor(1.0, 1.0, 1.0, 1.0)
        self.setUpShaders()

    def paintGL(self):
        self.loadScene()
        try:
            with self.mutex:
                self.updateMatrices()
                self.drawStuff()
        except Exception as exp:
            print(exp)
            pass

    def setUpShaders(self):
        self.shaders.addShaderFromSourceFile(QOpenGLShader.Vertex,
                                             'shader.vert')
        self.shaders.addShaderFromSourceFile(QOpenGLShader.Fragment,
                                             'shader.frag')
        self.shaders.link()
        self.shaders.bind()

        self.updateMatrices()

    def updateMatrices(self):
        proj = QMatrix4x4()
        proj.frustum(-1, 1, -1, 1, 2, 20)
        modelview = QMatrix4x4()
        modelview.lookAt(
            QVector3D(0, 0, 3),
            QVector3D(0, 0, 0),
            QVector3D(0, 1, 0)
        )
        modelview.rotate(self.angleX, 1, 0, 0)
        modelview.rotate(self.angleY, 0, 1, 0)

        self.shaders.setUniformValue("ModelViewMatrix", modelview)
        self.shaders.setUniformValue("MVP", proj * modelview)

    def putStar(self, color, point, radius, angle):
        self.star_coords.extend(star_coords(np.array(point), radius, angle))

    def drawStars(self):
        self.shaders.setUniformValue("FlagColor", QVector3D(*self.star_color))
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEnableClientState(GL.GL_COLOR_ARRAY)
        GL.glVertexPointer(2, GL.GL_FLOAT, 0, self.star_coords)
        GL.glColorPointer(3, GL.GL_FLOAT, 0, [
                          self.star_color] * len(self.star_coords))
        [GL.glDrawArrays(GL.GL_POLYGON, i, 12) for i in range(0, 12 * 5, 12)]
        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        GL.glDisableClientState(GL.GL_COLOR_ARRAY)

    def drawFlag(self, flag_coords):
        self.shaders.setUniformValue("FlagColor", QVector3D(*self.flag_color))
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEnableClientState(GL.GL_COLOR_ARRAY)
        GL.glVertexPointer(2, GL.GL_FLOAT, 0, flag_coords)
        color = []
        [color.extend(self.flag_color) for _ in range(len(flag_coords))]
        GL.glColorPointer(3, GL.GL_FLOAT, 0, color)
        GL.glDrawArrays(GL.GL_POLYGON, 0, 4)
        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        GL.glDisableClientState(GL.GL_COLOR_ARRAY)

    def drawStuff(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        star_params = (
            ((1 / 3, 1 / 2), 0.2, 0),
            ((2 / 3, 0.8), 1 / 15, np.arcsin(3 / 5) + np.pi / 2),
            ((0.8, 0.6), 1 / 15, np.arcsin(1 / 6) + np.pi / 2),
            ((0.8, 0.3), 1 / 15, 0),
            ((2 / 3, 0.1), 1 / 15, np.arcsin(4 / 5))
        )
        star_params = [(np.array(coords), rad, angle)
                       for coords, rad, angle in star_params]
        flag_coords = np.array((
            (0.05, 0.2),
            (0.95, 0.2),
            (0.95, 0.8),
            (0.05, 0.8)
        ))
        stars_start = (flag_coords[3] - flag_coords[0]) / 2 + flag_coords[0]
        flag_size_x = (flag_coords[1][0] - flag_coords[0][0]) / 2
        flag_size_y = (flag_coords[3][1] - flag_coords[0][1]) / 2
        star_params = [
            ((
                 coords[0] * flag_size_x + stars_start[0],
                 coords[1] * flag_size_y + stars_start[1]
             ), rad * flag_size_x, angle)
            for coords, rad, angle in star_params
        ]
        [self.putStar(self.star_color, *param) for param in star_params]
        self.drawFlag(flag_coords)
        self.drawStars()

    def onKeyPressed(self, event):
        key = event.key()
        if key == Qt.Key_A:
            self.angleY = (self.angleY - 5) % 360
        elif key == Qt.Key_D:
            self.angleY = (self.angleY + 5) % 360
        elif key == Qt.Key_W:
            self.angleX = (self.angleX + 5) % 360
        elif key == Qt.Key_S:
            self.angleX = (self.angleX - 5) % 360
        self.openGLWidget.update()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
