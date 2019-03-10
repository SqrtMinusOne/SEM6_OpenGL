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
    color = [random.random() for _ in range(4)]
    if sum(color[:3]) / 3 < 0.5:
        return random_rgb()
    else:
        return color


def cart2pol(x, y):
    r = np.sqrt(x ** 2 + y ** 2)
    φ = np.arctan2(y, x)
    return r, φ


def pol2cart(r, φ):
    x = r * np.cos(φ)
    y = r * np.sin(φ)
    return x, y


# noinspection PyPep8Naming
class MainWindow(QMainWindow, Ui_MainWindow):
    generated_points = []
    generated_colors = []

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.primitiveComboBox.activated.connect(self.resetRandomAndUpdate)
        self.AlphaSlider.valueChanged.connect(self.openGLWidget.update)
        self.AlphaComboBox.activated.connect(self.openGLWidget.update)
        self.blendSFactor.activated.connect(self.openGLWidget.update)
        self.blendDFactor.activated.connect(self.openGLWidget.update)
        self.updateButton.clicked.connect(self.resetRandomAndUpdate)
        self.XScissorSlider.valueChanged.connect(self.openGLWidget.update)
        self.YScissorSlider.valueChanged.connect(self.openGLWidget.update)
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
            "GL_POLYGON": self.paintGL_polygon,
            "Фрактал": self.paintGL_fractal,
            "Кривая Безье 3": self.paintGL_spline
        }

    def resetRandomAndUpdate(self):
        self.fractalLevelSpinBox.setEnabled(False)
        self.generated_points = []
        self.generated_colors = []
        self.openGLWidget.update()

    def glScissorTest(self):
        GL.glEnable(GL.GL_SCISSOR_TEST)
        # print(self.x_scissor, self.y_scissor)
        x_scissor = self.XScissorSlider.value() / 100
        y_scissor = self.YScissorSlider.value() / 100
        GL.glScissor(int(x_scissor * self.openGLWidget.width()), int(y_scissor * self.openGLWidget.height()),
                     self.openGLWidget.width(), self.openGLWidget.height())

    def glAlphaTest(self):
        GL.glEnable(GL.GL_ALPHA_TEST)
        alpha_method = self.AlphaComboBox.currentText()
        alpha_value = self.AlphaSlider.value() / 100
        GL.glAlphaFunc(getattr(GL, alpha_method), alpha_value)

    def glBlendTest(self):
        GL.glEnable(GL.GL_BLEND)
        sFactor = self.blendSFactor.currentText()
        dFactor = self.blendDFactor.currentText()
        GL.glBlendFunc(getattr(GL, sFactor), getattr(GL, dFactor))

    def loadScene(self):
        width, height = self.openGLWidget.width(), self.openGLWidget.height()
        GL.glViewport(0, 0, width, height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, 1, 0, 1, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

    def paintGL(self):
        # print('Paint')
        self.loadScene()
        try:
            self.glScissorTest()
            self.glAlphaTest()
            self.glBlendTest()
            self.actionsDict[self.primitiveComboBox.currentText()]()
        except Exception as exp:
            print(exp)
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
        if len(self.generated_points) == 0:
            self.generated_points = [(np.random.random(), np.random.random()) for _ in range(number)]
            self.generated_colors = [random_rgb() for _ in range(number)]
        self.placeGeneratedPoints()

    def placeGeneratedPoints(self):
        for point, color in zip(self.generated_points, self.generated_colors):
            GL.glColor4d(*color)
            GL.glVertex2d(*point)

    def paint(self, X1, Y1, X2, Y2):

        line11 = []
        line12 = []
        line13 = []

        start = (0.1, 0.1)
        finish = (0.9, 0.1)
        draggable1= (X1, Y1)
        draggable2 = (X2, Y2)

        GL.glBegin(GL.GL_POINTS)
        GL.glVertex2d(*draggable2)
        GL.glVertex2d(*draggable1)
        GL.glEnd()

        GL.glBegin(GL.GL_LINE_STRIP)

        for i in range(100):
            line11.append(((draggable1[0] - start[0])/100*i + start[0],
                          (draggable1[1] - start[1])/100*i + start[1]))
            line12.append(((draggable2[0] - draggable1[0]) / 100 * i + draggable1[0],
                          (draggable2[1] - draggable1[1]) / 100 * i + draggable1[1]))
            line13.append(((finish[0] - draggable2[0]) / 100 * i + draggable2[0],
                          (finish[1] - draggable2[1]) / 100 * i + draggable2[1]))

        line21 = []
        line22 = []

        for i in range(100):
            dot1 = line11[i]
            dot2 = line12[i]
            dot3 = line13[i]
            line21.append(((dot2[0] - dot1[0]) / 100 * i + dot1[0],
                           (dot2[1] - dot1[1]) / 100 * i + dot1[1]))
            line22.append(((dot3[0] - dot2[0]) / 100 * i + dot2[0],
                           (dot3[1] - dot2[1]) / 100 * i + dot2[1]))

        for i in range(100):
            dot21 = line21[i]
            dot22 = line22[i]
            GL.glVertex2d((dot22[0] - dot21[0]) / 100 * i + dot21[0],
                          (dot22[1] - dot21[1]) / 100 * i + dot21[1])

        GL.glEnd()
        GL.glFinish()

    def paintGL_spline(self):
        self.paint(0.25, 0.75, 0.75, 0.75)

    def paintGL_circular_random(self):
        random_dict = {
            "GL_TRIANGLE_STRIP": GL.GL_TRIANGLE_STRIP,
            "GL_TRIANGLE_FAN": GL.GL_TRIANGLE_FAN,
        }
        acc_angle = 0
        N = 5
        if len(self.generated_points) == 0:
            self.generated_colors.append(random_rgb())
            self.generated_points.append((0.5, 0.5))
            max_rad = 0.5
            self.generated_colors.extend([random_rgb() for _ in range(N)])
            for _ in range(N):
                r = np.random.random() * max_rad
                acc_angle += random.random() * 360 / N
                x, y = pol2cart(r, acc_angle / 180 * np.pi)
                x += 0.5
                y += 0.5
                self.generated_points.append((x, y))
        GL.glPointSize(2)
        GL.glBegin(random_dict[self.primitiveComboBox.currentText()])
        self.placeGeneratedPoints()
        GL.glEnd()
        GL.glFinish()

    def paintGL_quads(self):
        N = 4
        if len(self.generated_points) == 0:
            for _ in range(N):
                c_x, c_y = np.random.random() * 0.98 + 0.01, np.random.random() * 0.98 + 0.01
                max_rad = min(c_x, 1 - c_x, c_y, 1 - c_y)
                acc_angle = 0
                r = np.random.random() * max_rad
                self.generated_colors.extend([random_rgb() for _ in range(4)])
                for _ in range(4):
                    acc_angle += random.random() * 360 / 4
                    x, y = pol2cart(r, acc_angle / 180 * np.pi)
                    x += c_x
                    y += c_y
                    self.generated_points.append((x, y))
        GL.glPointSize(2)
        GL.glBegin(GL.GL_QUADS)
        self.placeGeneratedPoints()
        GL.glEnd()
        GL.glFinish()

    def paintGL_quad_strip(self):
        N = 4
        if len(self.generated_points) == 0:
            y_s = [np.random.random() for _ in range(N)]
            y_s.sort()
            x_s = [[np.random.random() for _ in range(2)] for _ in range(N)]
            [l.sort() for l in x_s]
            self.generated_colors = [random_rgb() for _ in range(N * 2)]
            for i in range(N):
                self.generated_points.append((x_s[i][0], y_s[i]))
                self.generated_points.append((x_s[i][1], y_s[i]))
        GL.glPointSize(2)
        GL.glBegin(GL.GL_QUAD_STRIP)
        self.placeGeneratedPoints()
        GL.glEnd()
        GL.glFinish()

    def paintGL_polygon(self):
        N = 8
        if len(self.generated_points) == 0:
            acc_angle = 0
            r = np.random.random() * 0.5
            self.generated_colors = [random_rgb() for _ in range(N)]
            for _ in range(N):
                acc_angle += random.random() * 360 / N
                x, y = pol2cart(r, acc_angle / 180 * np.pi)
                x += 0.5
                y += 0.5
                self.generated_points.append((x, y))
        GL.glPointSize(2)
        GL.glBegin(GL.GL_POLYGON)
        self.placeGeneratedPoints()
        GL.glEnd()
        GL.glFinish()

    def paintGL_fractal(self):
        self.fractalLevelSpinBox.setEnabled(True)
        GL.glBegin(GL.GL_LINE_STRIP)
        start = (0.05, 0.3)
        end = (0.95, 0.3)

        GL.glVertex2d(*start)
        self.drawFractal(*start, *end, level=self.fractalLevelSpinBox.value())
        GL.glEnd()

    def drawFractal(self, x1, y1, x2, y2, level=1):
        p1, p2 = np.array((x1, y1)), np.array((x2, y2))
        vec = p2 - p1
        coef = np.linalg.norm(vec)
        center = p1 + vec / 2
        angle = cart2pol(*vec)[1]
        rotate_matr = np.array([  # Матрица поворота
            [np.cos(angle), np.sin(angle)],
            [-np.sin(angle), np.cos(angle)]
        ])
        points = np.array([  # Точки
            (0, 0),
            (0.25, 0.19 * 0.51),
            (0.33, 0.69 * 0.51),
            (0.33, 0.19 * 0.51),
            (0.57, 0.19 * 0.51),
            (0.67, 1.00 * 0.51),
            (0.75, 0.19 * 0.51),
            (1, 0)
        ])

        # Повернуть
        points = np.array([p.dot(rotate_matr) for p in points])

        # Установить начало
        points = np.array([p + p1 for p in points])

        # Масштабировать
        points = np.array([p1 + (p - p1) * coef for p in points])

        for i in range(1, len(points)):
            if level > 1:
                self.drawFractal(*points[i - 1], *points[i], level - 1)
            GL.glVertex2d(*points[i])


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
