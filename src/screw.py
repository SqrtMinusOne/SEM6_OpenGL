import threading
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QOpenGLShaderProgram, QOpenGLShader, QMatrix4x4, \
    QVector3D, QVector4D
from OpenGL import GL

from ui.screw import Ui_ShadersWindow
from main import pol2cart, cart2pol


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
        self.camera_pos = QVector3D(0, 0, 4)
        self.scale_vec = QVector3D(1, 1, 1)
        self.ambient = 0.2
        self.diffuse = 0.8

        self.precision = 20
        self.draw_lines = True
        self.invisible = True

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
        if self.invisible:
            GL.glEnable(GL.GL_DEPTH_TEST)
            GL.glDepthFunc(GL.GL_LEQUAL)
        else:
            GL.glDisable(GL.GL_DEPTH_TEST)
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
        self.drawCoordSystem()
        self.drawObject()
        self.drawLightSource()

    def getCubeCoords(self):
        polygons = np.array([
            ((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)),
            ((0, 0, 1), (0, 1, 1), (1, 1, 1), (1, 0, 1)),
            ((0, 0, 0), (0, 0, 1), (1, 0, 1), (1, 0, 0)),
            ((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)),
            ((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)),
            ((1, 0, 0), (1, 0, 1), (1, 1, 1), (1, 1, 0))
        ])
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
        center = np.array((self.light_pos.x(), self.light_pos.y(), self.light_pos.z()))
        polygons = [[p * 0.1 + center for p in side] for side in polygons]
        return polygons, new_normals, center

    def getCircleApprox(self, r, y, h, precision,
                        map_proc=None, map_norm=None):
        map_proc = map_proc if map_proc is not None else lambda v: v
        map_norm = map_norm if map_norm is not None else map_proc
        polygons = []
        normals = []
        for i1, i2 in zip(range(precision+1), range(1, precision+1)):
            angle_1 = 2 * np.pi / precision * i1
            angle_2 = 2 * np.pi / precision * i2
            x1, z1 = pol2cart(r, angle_1)
            x2, z2 = pol2cart(r, angle_2)
            p1 = map_proc(QVector3D(x1, y, z1))
            p2 = map_proc(QVector3D(x1, y + h, z1))
            p3 = map_proc(QVector3D(x2, y + h, z2))
            p4 = map_proc(QVector3D(x2, y, z2))
            polygons.append([(p.x(), p.y(), p.z()) for p in (p1, p2, p3, p4)])

            xn, zn = pol2cart(1, (angle_1 + angle_2) / 2)
            normal = map_norm(QVector3D(xn, 0, zn))
            [normals.append((normal.x(), normal.y(), normal.z()))
             for _ in range(4)]
        return polygons, normals

    def getFlatCircleApprox(self, r1, r2, y, y_dir, precision,
                            map_proc=None, map_norm=None):
        map_proc = map_proc if map_proc is not None else lambda v: v
        map_norm = map_norm if map_norm is not None else map_proc
        polygons = []
        normals = []
        for i1, i2 in zip(range(precision+1), range(1, precision+1)):
            angle_1 = 2 * np.pi / precision * i1
            angle_2 = 2 * np.pi / precision * i2
            x1, z1 = pol2cart(r1, angle_1)
            x2, z2 = pol2cart(r2, angle_1)
            x3, z3 = pol2cart(r2, angle_2)
            x4, z4 = pol2cart(r1, angle_2)
            p1, p2, p3, p4 = [map_proc(QVector3D(x, y, z))
                            for x, z in ((x1, z1), (x2, z2), (x3,z3), (x4,z4))]

            polygons.append([(p.x(), p.y(), p.z()) for p in (p1, p2, p3, p4)])
            normal = map_norm(QVector3D(0, y_dir, 0))
            [normals.append((normal.x(), normal.y(), normal.z()))
             for _ in range(4)]
        return polygons, normals

    def getObjectCoords(self, precision=20):
        center = QVector3D(0.5, 0.5, 0.5)
        map_proc = lambda vec: vec + center
        map_norm = lambda vec: vec
        screw_vertical = [(1, 0, 1, 6),
                          (0.5, 0, 1, 6)]
        screw_flat = [(0.5, 1, 0, -1, 6),
                      (0.5, 1, 1, 1, 6)]

        coords, normals = [], []
        for obj in screw_vertical:
            coords_, normals_ = self.getCircleApprox(*obj, map_proc, map_norm)
            coords += coords_
            normals += normals_

        for obj in screw_flat:
            coords_, normals_ = self.getFlatCircleApprox(*obj, map_proc, map_norm)
            coords += coords_
            normals += normals_

        return coords, normals, center

    def drawObject(self):
        coords, normals, center = self.getObjectCoords(self.precision)
        screw_colors, line_colors = [], []
        [screw_colors.append(QVector4D(*self.screw_color)) for _ in range(len(normals))]
        [line_colors.append(QVector4D(1, 1, 1, 1)) for _ in range(len(normals))]

        self.shaders.setAttributeArray("v_color", screw_colors)
        self.shaders.enableAttributeArray("v_color")
        self.shaders.setAttributeArray("v_normal", normals)
        self.shaders.enableAttributeArray("v_normal")

        self.shaders.setUniformValue("Center", center)
        self.shaders.setUniformValue("ambientStrength", self.ambient)
        self.shaders.setUniformValue("diffuseStrength", self.diffuse)
        self.shaders.setUniformValue("phongModel", True)

        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)

        coords_array = []
        [[coords_array.append(p) for p in polygon] for polygon in coords]
        len_array = [len(polygon) for polygon in coords]
        GL.glVertexPointer(3, GL.GL_FLOAT, 0, coords_array)
        for i in range(len(coords)):
            start_index = sum(len_array[:i])
            GL.glDrawArrays(GL.GL_POLYGON, start_index, len_array[i])

        if self.draw_lines:
            self.shaders.setAttributeArray("v_color", line_colors)
            for i in range(len(coords)):
                start_index = sum(len_array[:i])
                GL.glDrawArrays(GL.GL_LINE_LOOP, start_index, len_array[i])
        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)

    def drawLightSource(self):
        coords, normals, center = self.getCubeCoords()
        source_colors = []
        [source_colors.append(QVector4D(1, 153 / 255, 0, 1) * self.diffuse) for _ in range(len(normals))]

        self.shaders.setAttributeArray("v_color", source_colors)
        self.shaders.enableAttributeArray("v_color")

        self.shaders.setUniformValue("phongModel", False)

        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)

        coords_array = []
        [[coords_array.append(list(p)) for p in polygon] for polygon in coords]
        len_array = [len(polygon) for polygon in coords]
        GL.glVertexPointer(3, GL.GL_FLOAT, 0, coords_array)
        for i in range(len(coords)):
            start_index = sum(len_array[:i])
            GL.glDrawArrays(GL.GL_POLYGON, start_index, len_array[i])

        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)

    def drawCoordSystem(self):
        coords = (
            ((0, 0, -100), (0, 0, 100)),
            ((-100, 0, 0), (100, 0, 0)),
            ((0, -100, 0), (0, 100, 0))
        )
        coords_array = []
        line_colors = []
        [line_colors.append(QVector4D(1, 1, 1, 1)) for _ in range(len(coords) * 2)]
        [[coords_array.append(p) for p in line] for line in coords]

        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        self.shaders.setAttributeArray("v_color", line_colors)
        self.shaders.setUniformValue("phongModel", False)
        GL.glVertexPointer(3, GL.GL_FLOAT, 0, coords_array)
        for i in range(len(coords)):
            start_index = i * 2
            GL.glDrawArrays(GL.GL_LINES, start_index, 2)

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
        self.ambientSlider.valueChanged.connect(lambda v: setattr(self, 'ambient', v / 100))
        self.diffuseSlider.valueChanged.connect(lambda v: setattr(self, 'diffuse', v / 100))
        self.alphaSlider.valueChanged.connect(lambda a: setattr(self,
            'screw_color',
            (self.screw_color[0], self.screw_color[1], self.screw_color[2],
             a / 100)))

        self.drawLinesCheckBox.stateChanged.connect(lambda s: setattr(self, 'draw_lines', s))
        self.invisibleCheckBox.stateChanged.connect(lambda s: setattr(self, 'invisible', s))


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
