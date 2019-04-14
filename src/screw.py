import threading
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QOpenGLShaderProgram, QOpenGLShader, QMatrix4x4, \
    QVector3D, QVector4D
from OpenGL import GL

from ui.screw import Ui_ShadersWindow
from main import pol2cart


class MainWindow(QMainWindow, Ui_ShadersWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.screw_color = (223 / 255, 37 / 255, 0 / 255, 0.8)
        self.setupUi(self)
        self.getLightPos()
        self.mapControls()
        self.openGLWidget.initializeGL = self.initializeGL
        self.openGLWidget.paintGL = self.paintGL
        self.keyPressEvent = self.onKeyPressed
        self.objectAngleX, self.objectAngleY = 0, 0
        self.camera_pos = QVector3D(0, 0, 3)
        self.scale_vec = QVector3D(1, 1, 1)
        self.precision = 20
        self.borders = True

        self.mutex = threading.Lock()
        self.shaders = QOpenGLShaderProgram()

    def getLightPos(self):
        self.light_pos = QVector3D(
            self.xLightSpinBox.value(),
            self.yLightSpinBox.value(),
            self.zLightSpinBox.value()
        )

    def loadScene(self):
        width, height = self.openGLWidget.width(), self.openGLWidget.height()
        GL.glViewport(0, 0, width, height)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        self.getLightPos()

    def initializeGL(self):
        GL.glClearColor(0.1, 0.1, 0.1, 1.0)
        self.setUpShaders()

    def paintGL(self):
        self.loadScene()
        with self.mutex:
            self.updateMatrices()
            self.drawStuff()

    def setUpShaders(self):
        self.shaders.addShaderFromSourceFile(QOpenGLShader.Vertex,
                                             'screw_shader.vert')
        self.shaders.addShaderFromSourceFile(QOpenGLShader.Fragment,
                                             'screw_shader.frag')
        self.shaders.link()
        self.shaders.bind()

        self.updateMatrices()

    def updateMatrices(self):
        proj = QMatrix4x4()
        if self.projectionComboBox.currentIndex() == 0:
            proj.frustum(-0.3, 1, -0.3, 1, 2, 20)
        else:
            proj.ortho(-0.3, 1, -0.3, 1, 2, 20)
        modelview = QMatrix4x4()
        modelview.lookAt(
            self.camera_pos,
            QVector3D(0, 0, 0),
            QVector3D(0, 1, 0)
        )
        modelview.rotate(self.objectAngleX, 1, 0, 0)
        modelview.rotate(self.objectAngleY, 0, 1, 0)

        scale = QMatrix4x4()
        scale.scale(self.scale_vec)

        self.shaders.setUniformValue("ModelViewMatrix", modelview)
        self.shaders.setUniformValue("MVP", proj * modelview)
        self.shaders.setUniformValue("ScaleMatrix", scale)
        self.shaders.setUniformValue("LightPos", self.light_pos)

    def drawStuff(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        # self.star_coords.clear()
        # [self.putStar(self.star_color, *param) for param in self.star_params]
        # self.drawFlag(self.flag_coords)
        # self.drawStars()
        self.drawObject()

    def getObjectCoords(self, precision=20):
        polygons = [
            ((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)),
            ((0, 0, 1), (0, 1, 1), (1, 1, 1), (1, 0, 1)),
            ((0, 0, 0), (0, 0, 1), (1, 0, 1), (1, 0, 0)),
            ((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)),
            ((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)),
            ((1, 0, 0), (1, 0, 1), (1, 1, 1), (1, 1, 0))
        ]
        normals = [
            (0, 0, -1),
            (0, 0, 1),
            (0, -1, 0),
            (0, 1, 0),
            (-1, 0, 0),
            (1, 0, 0)
        ]
        new_normals = []
        [[new_normals.append(QVector3D(*normals[i])) for _ in range(len(polygons[i]))]
         for i in range(len(polygons))]
        center = (0.5, 0.5, 0.5)
        return polygons, new_normals, center

    def drawObject(self):
        coords, normals, center = self.getObjectCoords(self.precision)
        screw_colors, line_colors = [], []
        [screw_colors.append(QVector4D(*self.screw_color)) for _ in range(len(normals))]
        [line_colors.append(QVector4D(1, 1, 1, 1)) for _ in range(len(normals))]

        self.shaders.setAttributeArray("v_color", screw_colors)
        self.shaders.enableAttributeArray("v_color")
        self.shaders.setAttributeArray("v_normal", normals)
        self.shaders.enableAttributeArray("v_normal")

        self.shaders.setUniformValue("Center", QVector3D(*center))

        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)

        coords_array = []
        [[coords_array.append(p) for p in polygon] for polygon in coords]
        len_array = [len(polygon) for polygon in coords]
        GL.glVertexPointer(3, GL.GL_FLOAT, 0, coords_array)
        for i in range(len(coords)):
            start_index = sum(len_array[:i])
            GL.glDrawArrays(GL.GL_POLYGON, start_index, len_array[i])

        if self.borders:
            self.shaders.setAttributeArray("v_color", line_colors)
            for i in range(len(coords)):
                start_index = sum(len_array[:i])
                GL.glDrawArrays(GL.GL_LINE_LOOP, start_index, len_array[i])
        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)


    def onKeyPressed(self, event):
        key = event.key()
        if key == Qt.Key_A:
            self.moveCamera(x=-1)
        elif key == Qt.Key_D:
            self.moveCamera(x=1)
        elif key == Qt.Key_W:
            self.moveCamera(z=1)
        elif key == Qt.Key_S:
            self.moveCamera(z=-1)
        elif key == Qt.Key_Z:
            self.moveCamera(y=1)
        elif key == Qt.Key_X:
            self.moveCamera(y=-1)
        elif key == Qt.Key_8:
            self.rotateObject(1, 0)
        elif key == Qt.Key_2:
            self.rotateObject(-1, 0)
        elif key == Qt.Key_4:
            self.rotateObject(0, -1)
        elif key == Qt.Key_6:
            self.rotateObject(0, 1)
        self.openGLWidget.update()

    def mapControls(self):
        self.moveCameraUp.clicked.connect(lambda: self.moveCamera(y=1))
        self.moveCameraDown.clicked.connect(lambda: self.moveCamera(y=-1))
        self.moveCameraLeft.clicked.connect(lambda: self.moveCamera(x=-1))
        self.moveCameraRight.clicked.connect(lambda: self.moveCamera(x=1))
        self.moveCameraForward.clicked.connect(lambda: self.moveCamera(z=-1))
        self.moveCameraBackward.clicked.connect(lambda: self.moveCamera(z=1))

        self.rotateObjectUp.clicked.connect(lambda: self.rotateObject(1, 0))
        self.rotateObjectDown.clicked.connect(lambda: self.rotateObject(-1, 0))
        self.rotateObjectLeft.clicked.connect(lambda: self.rotateObject(0, -1))
        self.rotateObjectRight.clicked.connect(lambda: self.rotateObject(0, 1))

        self.xScaleSpinBox.valueChanged.connect(lambda x: self.scaleView(x=x))
        self.yScaleSpinBox.valueChanged.connect(lambda y: self.scaleView(y=y))
        self.zScaleSpinBox.valueChanged.connect(lambda z: self.scaleView(z=z))

        self.precisionSlider.valueChanged.connect(lambda p: setattr(self, 'precision', p))


    def rotateObject(self, x, y):
        angle_move = 5
        self.objectAngleX = (self.objectAngleX + angle_move * x) % 360
        self.objectAngleY = (self.objectAngleY + angle_move * y) % 360

    def moveCamera(self, x=0, y=0, z=0):
        camera_move = 0.2
        self.camera_pos.setX(self.camera_pos.x() + camera_move * x)
        self.camera_pos.setY(self.camera_pos.y() + camera_move * y)
        self.camera_pos.setZ(self.camera_pos.z() + camera_move * z)

    def scaleView(self, x=None, y=None, z=None):
        if x:
            self.scale_vec.setX(x)
        if y:
            self.scale_vec.setY(y)
        if z:
            self.scale_vec.setZ(z)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
