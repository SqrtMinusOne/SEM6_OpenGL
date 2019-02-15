from PyQt5.QtWidgets import QMainWindow, QApplication
from OpenGL import GL, GLU, GLUT

from mainwindow import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.openGLWidget.initializeGL()
        self.openGLWidget.paintGL = self.paintGL

    def loadScene(self):
        width, height = self.openGLWidget.width(), self.openGLWidget.height()
        GL.glViewport(0, 0, width, height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, width, 0, height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

    def paintGL(self):
        self.loadScene()
        width, height = self.openGLWidget.width(), self.openGLWidget.height()
        cube_size = 200
        left = (width - cube_size) / 2
        right = left + cube_size
        bottom = (height - cube_size) / 2
        top = bottom + cube_size
        GL.glClearColor(0, 0, 0, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glColor3ub(255, 0, 0)
        GL.glBegin(GL.GL_QUADS)
        GL.glVertex2f(left, bottom)
        GL.glVertex2f(left, top)
        GL.glVertex2f(right, top)
        GL.glVertex2f(right, bottom)
        GL.glEnd()
        GL.glFinish()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
