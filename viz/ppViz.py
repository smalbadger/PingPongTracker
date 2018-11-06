'''
file:       ppViz.py
Author:     Sam Badger
Date:       November 3, 2018
Description:
            This is the graphical visualization software for CS4243 (COMPUTER 
            VISION & PATTERN RECOGNITION).
'''

import os

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtOpenGL import *

from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QLineEdit
from PySide2.QtWidgets import QSpinBox
from PySide2.QtWidgets import QGroupBox
from PySide2.QtGui import QPixmap
from PySide2.QtGui import QImage
from PySide2.QtCore import Qt

import imageio
import numpy as np
import csv
import traceback

#############################################################################
#                            Globals Begin                                  #
#############################################################################
MOUSE_BUTTON = None
MOVING = None
START_X = None
START_Y = None
ANGLE = 0
ANGLE2 = 0


CUR_SEQUENCE = 0
CUR_FRAME = 0
FRAME_RATE = .25
NUMBER_OF_FRAMES = 1
PLAYING = False
VIDEO_DIR = "../TestVideos/"

BALL_2D_COORDS_DIR = ""
CUR_2D_FILE = None
READER_2D = None


BALL_3D_COORDS_DIR = "../Test3DCoords/"
CUR_3D_FILE = None
READER_3D = None


R1 = np.array([[ .96428, -.26485, -.0024166],
               [-.089795, -.31832, -.94372],
               [ .24917,  .91023, -.33074]])
               
t1 = np.array([[ .13305],
               [-.25319],
               [ 2.2444]])
               
R2 = np.array([[ .94962,  .31338, -.0026554],
               [ .11546, -.35774, -.92665],
               [-.29134,  .87966, -.37591]])

t2 = np.array([[-.042633],
               [-.35442],
               [ 2.2750]])
               
R3 = np.array([[-.99541,  .038473, -.087527],
               [ .091201,  .65687, -.74846],
               [ .028698, -.75301, -.65737]])

t3 = np.array([[-.060452],
               [-.39533],
               [ 2.2980]])
               
c1 = np.matmul(-1 * np.linalg.inv(R1), t1)
c2 = np.matmul(-1 * np.linalg.inv(R2), t2)
c3 = np.matmul(-1 * np.linalg.inv(R3), t3)

 
def updateSequence(seqNum):
    global BALL_3D_COORDS_DIR
    global VIDEO_DIR
    global CUR_SEQUENCE 
    global CUR_FRAME
    global NUMBER_OF_FRAMES
    global CUR_3D_FILE
    global READER_3D
    
    CUR_SEQUENCE = seqNum
    videoFiles = sorted([VIDEO_DIR+name for name in os.listdir(VIDEO_DIR)])[:10]
    vid = imageio.get_reader(videoFiles[CUR_SEQUENCE],'mp4')
    NUMBER_OF_FRAMES = vid._meta['nframes']
    print("Switched to sequence: {}".format(CUR_SEQUENCE))
    print("# of frames: {}".format(NUMBER_OF_FRAMES))
    
    _3DCoordFiles = sorted([BALL_3D_COORDS_DIR+name for name in os.listdir(BALL_3D_COORDS_DIR)])
    try:
        CUR_3D_FILE = open(_3DCoordFiles[CUR_SEQUENCE])
        READER_3D = csv.DictReader(CUR_3D_FILE)
        print("Reading 3D coordinates from {}".format(_3DCoordFiles[CUR_SEQUENCE]))
    except:
        print("Couldn't find a file of 3D coordinates for this sequence")
    
    
    
def updateFrame(frameNum):
    global CUR_FRAME    
    CUR_FRAME = frameNum % NUMBER_OF_FRAMES
    print("CUR_FRAME: {}".format(CUR_FRAME))
#############################################################################
#                            Globals End                                    #
#############################################################################

#############################################################################
#                           Utility Functions Begin                         #
#############################################################################
def getPointOneAway(p1, p2):
    return (p2-p1) / (np.linalg.norm(p2-p1)) + p1
#############################################################################
#                           Utility Functions End                           #
#############################################################################

class Camera:
    def __init__(self):
        self.speed = 0.1
        self.pitch = 0
        self.yaw   = 0
        self.distance = 10
        self.theta = 0
        self.phi = 0
        self.center = np.array([0.0,0.0,0.0])
        self.pos = np.array([0.0,0.0,10.0])
        self.front = np.array([0.0,0.0,-1.0])
        self.up = np.array([0.0,1.0, 0.0])
        self.fovy        = 40.0 
        self.aspectRatio = 1.0
        self.zNear       = 0 
        self.zFar        = 10
    '''
    def moveUp(self):
        self.phi+=self.speed
        self.updatePos()
        
    def moveDown(self):
        self.phi-=self.speed
        self.updatePos()
      
    def moveForward(self):
        self.distance -= self.speed
        self.updatePos()
        
    def moveBackward(self):
        self.distance += self.speed
        self.updatePos()
        
    def moveLeft(self):
        self.theta -= self.speed
        self.updatePos()
        
    def moveRight(self):
        self.theta -= self.speed
        self.updatePos() 
    '''
    def moveForward(self):
        self.pos += self.speed * self.front
        
    def moveBackward(self):
        self.pos -= self.speed * self.front
        
    def moveLeft(self):
        self.pos -= np.cross(self.front, self.up) * self.speed
        
    def moveRight(self):
        self.pos += np.cross(self.front, self.up) * self.speed
    
    def lookUp(self):
        self.pitch += 1
        self.updateFront()
        
    def lookDown(self):
        self.pitch -= 1
        self.updateFront()
        
    def lookLeft(self):
        self.yaw -= 1
        self.updateFront()
        
    def lookRight(self):
        self.yaw += 1
        self.updateFront()
        
    '''
    def updatePos(self):
        self.pos[0] = self.distance * np.cos(self.theta) * np.sin(self.phi)
        self.pos[1] = self.distance * np.sin(self.theta) * np.sin(self.phi)
        self.pos[2] = self.distance * np.cos(self.phi)
        self.updateUp()
        
    def updateUp(self):
        perp = np.array([self.pos[1], self.pos[0], 0])
        self.up = np.cross(perp,(self.center - self.pos))
    '''    
    def updateFront(self):
        self.front[0] = np.cos(np.deg2rad(self.pitch)) * np.cos(np.deg2rad(self.yaw))
        self.front[1] = np.sin(np.deg2rad(self.pitch))
        self.front[0] = np.cos(np.deg2rad(self.pitch)) * np.sin(np.deg2rad(self.yaw))

class GL3DPlot(QGLWidget):
    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self.setFocusPolicy(Qt.TabFocus)
        self.grabKeyboard()
        self.cam = Camera()
        
    def paintGL(self):
        ''' Drawing routine '''
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluPerspective(self.cam.fovy, self.cam.aspectRatio, self.cam.zNear, self.cam.zFar)
        self.lookAt()
        
        self.drawAxes()
        self.drawCameras()
        self.drawTable()
        self.drawBalls()
        
        glEnableClientState(GL_VERTEX_ARRAY)
        
        glFlush()
        
    def drawBalls(self):
        global READER_3D
        global CUR_3D_FILE
        if READER_3D != None:
            CUR_3D_FILE.seek(0)
            for row in READER_3D:
                try:
                    frame = int(row['Frame'])
                    x = float(row['x'])
                    y = float(row['y'])
                    z = float(row['z'])
                except:
                    continue
                    
                if frame > CUR_FRAME:
                    break
                    
                if frame == CUR_FRAME:
                    glColor3f(1, 0, 0)
                else:
                    glColor3f(1,.5, 0)
                
                glPushMatrix();
                glTranslatef(x, y, z)
                glutSolidSphere(.02, 20, 10)
                glPopMatrix();
       
    def drawTable(self):
        length = 2.74
        width = 1.525
        height = .76
        glPushMatrix()
        glBegin(GL_POLYGON)
        glVertex3f(-length/2, -width/2, height)
        glVertex3f( length/2, -width/2, height)
        glVertex3f( length/2,  width/2, height)
        glVertex3f(-length/2,  width/2, height)
        glEnd()
        glPopMatrix()
        
    def drawAxes(self):
        #draw x, y, and z lines
        glPushMatrix()
        glColor4f(0,0,0,1)
        glBegin(GL_LINES)
        glVertex3f(0, 0,  100)
        glVertex3f(0, 0, -100)
        glVertex3f(0,  100, 0)
        glVertex3f(0, -100, 0)
        glVertex3f( 100, 0, 0)
        glVertex3f(-100, 0, 0)
        glEnd()
        glPopMatrix()
        
    def drawCameras(self):
        glPushMatrix()
        #draw camera i, j, and k vectors
        glBegin(GL_LINES)
        
        glColor3f(1, 0, 0)
        for p1, p2 in ((c1, R1[0,:]), (c2, R2[0,:]), (c3, R3[0,:])):
            p1 = p1.reshape((1,3))[0]
            glVertex3f(p1[0], p1[1], p1[2])
            drawP = getPointOneAway(p1, p2)
            glVertex3f(drawP[0], drawP[1], drawP[2])
        
        glColor3f(0, 1, 0)
        for p1, p2 in ((c1, R1[1,:]), (c2, R2[1,:]), (c3, R3[1,:])):
            p1 = p1.reshape((1,3))[0]
            glVertex3f(p1[0], p1[1], p1[2])
            drawP = getPointOneAway(p1, p2)
            glVertex3f(drawP[0], drawP[1], drawP[2])
            
        glColor3f(0, 0, 1)
        for p1, p2 in ((c1, R1[2,:]), (c2, R2[2,:]), (c3, R3[2,:])):
            p1 = p1.reshape((1,3))[0]
            glVertex3f(p1[0], p1[1], p1[2])
            drawP = getPointOneAway(p1, p2)
            glVertex3f(drawP[0], drawP[1], drawP[2])
        glEnd()
        glPopMatrix()
        
    def draw3DArrow(self, length=5):
        gluCylinder(gluNewQuadric(), 1, 1, length, 10, 10)
        glTranslatef(0, 0, length)
        gluCylinder(gluNewQuadric(), 3, 0, length/5, 100, 100)

    def resizeGL(self, w, h):
        '''
        Resize the GL window 
        '''
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(40.0, 1.0, 1.0, 30.0)
    
    def initializeGL(self):
        '''
        Initialize GL
        '''
        glutInit()
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClearDepth(1.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        glMatrixMode(GL_MODELVIEW)
        self.lookAt()
        
    def lookAt(self):
        c = self.cam
        center = c.pos + c.front
        gluLookAt(c.pos[0], c.pos[1], c.pos[2], 
                  center[0], center[1], center[2],
                  c.up[0],  c.up[1],  c.up[2])
        
    def keyPressEvent(self, event):        
        if event.key() == 87:
            self.cam.moveForward()
            #self.cam.moveUp()
        if event.key() == 83:
            self.cam.moveBackward()
            #self.cam.moveDown()
        if event.key() == 65:
            self.cam.moveLeft()
        if event.key() == 68:
            self.cam.moveRight()
            
        if event.key() == 16777235:
            self.cam.lookUp()
            #self.cam.moveForward()
        if event.key() == 16777237:
            self.cam.lookDown()
            #self.cam.moveBackward()
        if event.key() == 16777236:
            self.cam.lookRight()
        if event.key() == 16777234:
            self.cam.lookLeft()
        
        self.updateGL()
        
        
    def mouse(self, button, state, x, y):
        global MOUSE_BUTTON
        global MOVING
        global START_X
        global START_Y
        print("Mouse registered")
        if state == GLUT_DOWN:
            MOUSE_BUTTON = button
            MOVING = 1
            START_X = x
            START_Y = y
        
        if state == GLUT_UP:
            MOUSE_BUTTON = button
            MOVING = 0

    def motion(self, x, y):
        global MOVING
        global MOUSE_BUTTON
        global ANGLE
        global ANGLE2
        global START_X
        global START_Y
        print("Motion registered")
        if MOVING:
            if MOUSE_BUTTON == GLUT_LEFT_BUTTON:
                ANGLE += (x - START_X)
                angle2 += (y - START_Y)
            START_X = x
            START_Y = y
            self.updateGL()
            
        
class VideoFrameDisplay(QGroupBox):
    def __init__(self, cName, parent):
        QGroupBox.__init__(self, parent)
        self.videoFiles = sorted([name for name in os.listdir(VIDEO_DIR) if cName in name])
        self.createElements()
        self.createLayout()
        self.updateSequence()
        self.updateImg()
        
    def createElements(self):
        self.pathLabel = QLabel()
        self.imgBox = QLabel()
        
    def createLayout(self):
        
        self.mainBox = QVBoxLayout()
        self.mainBox.addWidget(self.pathLabel)
        self.mainBox.addWidget(self.imgBox)
        self.setLayout(self.mainBox)
        
    def updateSequence(self):
        self.vid = imageio.get_reader(VIDEO_DIR + self.videoFiles[CUR_SEQUENCE],'mp4')
        
    def updateImg(self):
        self.pathLabel.setText(self.videoFiles[CUR_SEQUENCE])
        img = np.asarray(self.vid.get_data(CUR_FRAME))
        h, w, d = img.shape
        qImg = QImage(img, w, h, d*w, QImage.Format_RGB888)
        pMap = QPixmap(qImg)
        pMap = pMap.scaledToWidth(450)
        self.imgBox.setPixmap(pMap)
        


class PPDashBoard(QWidget):
    ''' container for all application widgets '''
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.createElements()
        self.createLayout()
        self.createActions()
        
    def createElements(self):
        self.gl3dPlot = GL3DPlot(self)
        
        self.vidFrame1 = VideoFrameDisplay('CAM1', self)
        self.vidFrame2 = VideoFrameDisplay('CAM2', self)
        self.vidFrame3 = VideoFrameDisplay('CAM3', self)
        
        self.curFrame = QSpinBox()
        self.curFrame.setMinimum(0)
        self.curFrame.setMaximum(NUMBER_OF_FRAMES - 1)
        self.curSequence = QSpinBox()
        self.curSequence.setMinimum(0)
        self.curSequence.setMaximum(9)
        self.frTotLabel = QLabel("out of {}".format(NUMBER_OF_FRAMES))
        self.seqTotLabel = QLabel("out of 10")
        self.frLabel = QLabel("Frame:")
        self.seqLabel = QLabel("Sequence:")
        self.backward = QPushButton('prev')
        self.forward = QPushButton('next')
        self.pause = QPushButton('pause')
        self.play = QPushButton('play')
        
    def createLayout(self):
        self.mainBox     = QHBoxLayout()
        self._3dPlotBox  = QVBoxLayout()
        self.vidBox      = QVBoxLayout()
        self.buttonBox   = QHBoxLayout()
        self.frameSpin   = QVBoxLayout()
        self.seqSpin     = QVBoxLayout()
        
        self.mainBox.addLayout(self._3dPlotBox)
        self.mainBox.addLayout(self.vidBox)
        
        self._3dPlotBox.addLayout(self.buttonBox)
        self._3dPlotBox.addWidget(self.gl3dPlot)
        
        self.vidBox.addWidget(self.vidFrame1)
        self.vidBox.addWidget(self.vidFrame2)
        self.vidBox.addWidget(self.vidFrame3)
        
        self.seqSpin.addWidget(self.seqLabel)
        self.seqSpin.addWidget(self.curSequence)
        self.seqSpin.addWidget(self.seqTotLabel)
        self.buttonBox.addLayout(self.seqSpin)
        self.buttonBox.addStretch(1)
        
        self.frameSpin.addWidget(self.frLabel)
        self.frameSpin.addWidget(self.curFrame)
        self.frameSpin.addWidget(self.frTotLabel)
        self.buttonBox.addLayout(self.frameSpin)
        self.buttonBox.addStretch(1)
        
        self.buttonBox.addWidget(self.backward)
        self.buttonBox.addWidget(self.forward)
        self.buttonBox.addWidget(self.pause)
        self.buttonBox.addWidget(self.play)
        
        self.setLayout(self.mainBox)
       
    def createActions(self):
        self.forward.clicked.connect(self.onForward)
        self.backward.clicked.connect(self.onBackward)
        self.curFrame.valueChanged.connect(self.onCurFrameSpinBoxChange)
        self.curSequence.valueChanged.connect(self.onSequenceChange)
    
    def onSequenceChange(self):
        updateSequence(self.curSequence.value())
        self.curFrame.setMaximum(NUMBER_OF_FRAMES-1)
        self.curFrame.setValue(0)
        self.frTotLabel.setText('out of {}'.format(NUMBER_OF_FRAMES))
        self.vidFrame1.updateSequence()
        self.vidFrame2.updateSequence()
        self.vidFrame3.updateSequence()
        self.onFrameChange()
    
    def onCurFrameSpinBoxChange(self):
        updateFrame(self.curFrame.value())
        self.onFrameChange()
    
    def onBackward(self):
        if CUR_FRAME == 0:
            updateFrame(NUMBER_OF_FRAMES-1)
        else:
            updateFrame(CUR_FRAME - 1)
        self.onFrameChange()
        
        
    def onForward(self):
        updateFrame(CUR_FRAME + 1)
        self.onFrameChange()
    
    def onFrameChange(self):
        if self.curFrame.value() != CUR_FRAME:
            self.curFrame.setValue(CUR_FRAME)
        self.vidFrame1.updateImg()
        self.vidFrame2.updateImg()
        self.vidFrame3.updateImg()
        self.gl3dPlot.updateGL()
            

class PPApplication(QMainWindow):
    ''' main window for the Ping Pong Application '''
    def __init__(self):
        super(PPApplication, self).__init__()
        updateSequence(0)
        widget = PPDashBoard(self)
        self.setCentralWidget(widget)
        #self.showMaximized()
        self.setWindowTitle("Ping Pong Flight Visualization")


if __name__ == "__main__":
    app = QApplication(['Ping Pong Flight Visualization'])
    window = PPApplication()
    window.show()
    app.exec_()
