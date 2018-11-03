'''
file:       ppViz.py
Author:     Sam Badger
Date:       November 3, 2018
Description:
            This is the graphical visualization software for CS4243 (COMPUTER 
            VISION & PATTERN RECOGNITION).
'''

import os
import time
import threading

from OpenGL.GL import *
from OpenGL.GLU import *
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
from PySide2.QtCore import QThread

import imageio
import numpy as np

#############################################################################
#                            Globals Begin                                  #
#############################################################################
CUR_SEQUENCE = 0
CUR_FRAME = 0
FRAME_RATE = .25
NUMBER_OF_FRAMES = 1
PLAYING = False
VIDEO_DIR = "../TestVideos/"
BALL_2D_COORDS_DIR = ""
BALL_3D_COORDS_DIR = ""


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
'''
print(R1)
print(R1[0])
print(R1[0][0])
print(R1[0,:])
print(R1[0,0])
'''              
def updateSequence(seqNum):
    global CUR_SEQUENCE 
    global CUR_FRAME
    global NUMBER_OF_FRAMES
    CUR_SEQUENCE = seqNum
    videoFiles = sorted([name for name in os.listdir(VIDEO_DIR)])[:10]
    vid = imageio.get_reader(VIDEO_DIR + videoFiles[CUR_SEQUENCE],'mp4')
    NUMBER_OF_FRAMES = vid._meta['nframes']
    print("Switched to sequence: {}".format(CUR_SEQUENCE))
    print("# of frames: {}".format(NUMBER_OF_FRAMES))
    
def updateFrame(frameNum):
    global CUR_FRAME    
    CUR_FRAME = frameNum % NUMBER_OF_FRAMES
    print("CUR_FRAME: {}".format(CUR_FRAME))
#############################################################################
#                            Globals End                                    #
#############################################################################


#############################################################################
#                           Utility function begin
#############################################################################
def getRotation(a, b):
    a = a.reshape((1,3))
    b = b.reshape((1,3))
        
    print("A: {}".format(a))
    print("B: {}".format(b))
    
    v = np.cross(a,b)       # a X b
    s = np.linalg.norm(v)   # magnitude of v
    c = np.dot(a,b)
    
    skew = np.array([[    0, -v[2],  v[1]],
                     [ v[2],     0, -v[0]],
                     [-v[1],  v[0],    0]])
                     
    R = np.identity(3) + skew + np.matmul(np.square(skew),1/(1+c))
    return R

#############################################################################
#                           Utility function end
#############################################################################



class GL3DPlot(QGLWidget):
    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        #self.setMinimumSize(500, 500)
        
    def paintGL(self):
        ''' Drawing routine '''
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        glBegin(GL_LINES)
        glColor4f(1, 0, 0,.3)
        for i in (c1, R1[0,:], c2, R2[0,:], c3, R3[0,:]):
            glVertex3f(i[0], i[1], i[2])
            
        glColor4f(0, 1, 0, .3)
        for i in (c1, R1[1,:], c2, R2[1,:], c3, R3[1,:]):
            glVertex3f(i[0], i[1], i[2])
            
        glColor4f(0, 0, 1, .3)
        for i in (c1, R1[2,:], c2, R2[2,:], c3, R3[2,:]):
            glVertex3f(i[0], i[1], i[2])
        glEnd()
        '''
        glColor3f(0.5,1,1)
        for i1, i2 in ((c1, R1[0,:]), (c2, R2[0,:]), (c3, R3[0,:])):
            glPushMatrix()
            glTranslatef(i1[0], i1[1], i1[2])
            alpha = np.dot(i2, np.array([0,0,1]))/(np.linalg.norm(i2))
            about = np.cross(i2, np.array([0,0,1]))
            
            glRotatef(np.arccos(alpha), about[0], about[1], about[2])
            glBegin(GL_LINES)
            glVertex3f(0,0,0)
            glVertex3f(0,1,0)
            glEnd()
            glPopMatrix
        '''
        glEnableClientState(GL_VERTEX_ARRAY)
        
        glFlush()

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
        # set viewing projection
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClearDepth(1.0)
        glLoadIdentity()
        glOrtho(-3, 3, -3, 3, -3, 3);
        
        
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
        self.totFrame = QLabel()
        self.backward = QPushButton('prev')
        self.forward = QPushButton('next')
        self.pause = QPushButton('pause')
        self.play = QPushButton('play')
        
    def createLayout(self):
        self.mainBox     = QHBoxLayout()
        self._3dPlotBox  = QVBoxLayout()
        self.vidBox      = QVBoxLayout()
        self.buttonBox   = QHBoxLayout()
        
        self.mainBox.addLayout(self._3dPlotBox)
        self.mainBox.addLayout(self.vidBox)
        
        self._3dPlotBox.addWidget(self.gl3dPlot)
        self._3dPlotBox.addLayout(self.buttonBox)
        
        self.vidBox.addWidget(self.vidFrame1)
        self.vidBox.addWidget(self.vidFrame2)
        self.vidBox.addWidget(self.vidFrame3)
        
        self.buttonBox.addWidget(self.curFrame)
        self.buttonBox.addWidget(self.curSequence)
        self.buttonBox.addWidget(self.totFrame)
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
        self.onFrameChange()
    
    def onCurFrameSpinBoxChange(self):
        updateFrame(self.curFrame.value())
        self.onFrameChange()
    
    def onBackward(self):
        if CUR_FRAME == 0:
            updateFrame(NUMBER_OF_FRAMES-1)
        else:
            updateFrame(CUR_FRAME + 1)
        self.onFrameChange()
        
        
    def onForward(self):
        updateFrame(CUR_FRAME + 1)
        self.onFrameChange()
    
    def onFrameChange(self):
        self.curFrame.setValue(CUR_FRAME)
        self.vidFrame1.updateImg()
        self.vidFrame2.updateImg()
        self.vidFrame3.updateImg()
            

class PPApplication(QMainWindow):
    ''' main window for the Ping Pong Application '''
    def __init__(self):
        super(PPApplication, self).__init__()
        updateSequence(0)
        widget = PPDashBoard(self)
        self.setCentralWidget(widget)
        self.showMaximized()
        self.setWindowTitle("Ping Pong Flight Visualization")


if __name__ == "__main__":
    app = QApplication(['Ping Pong Flight Visualization'])
    window = PPApplication()
    window.show()
    app.exec_()
