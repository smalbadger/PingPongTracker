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
from threading import Thread
from threading import Event

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from PySide2.QtOpenGL import *
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QMainWindow
from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QPushButton
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QGridLayout
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QLineEdit
from PySide2.QtWidgets import QSpinBox
from PySide2.QtWidgets import QGroupBox
from PySide2.QtWidgets import QSlider
from PySide2.QtGui import QPixmap
from PySide2.QtGui import QImage
from PySide2.QtGui import QPalette
from PySide2.QtCore import Qt
from PySide2.QtCore import Signal
import PySide2.QtGui as QtGui
import PySide2.QtCore as QtCore

import imageio
import numpy as np
import csv
import traceback

#############################################################################
#                            Globals Begin                                  #
#############################################################################
SHIFT = False   # toggle showing all previous ball positions or just the current one.
CTRL  = False

MOUSE_BUTTON = None
MOVING = None
START_X = None
START_Y = None
ANGLE = 0
ANGLE2 = 0

PLAYING = False
CUR_SEQUENCE = 0
CUR_FRAME = 0
FRAME_RATE = 5
NUMBER_OF_FRAMES = 1
PLAYING = False
VIDEO_DIR = "../TestVideos/"

BALL_2D_COORDS_DIR = "../Annotation/"
CUR_2D_FILE = None
READER_2D = None


BALL_3D_COORDS_DIR = "../triangulation_output/"
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
    #print("CUR_FRAME: {}".format(CUR_FRAME))
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
        self.pos = np.array([0.0,0.0,6.0])
        self.front = np.array([0.0,0.0,-1.0])
        self.up = np.array([0.0,1.0, 0.0])
        self.fovy        = 60.0 
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
        
    def changeView(self, option):
        self.center = np.array([0.0,0.0,0.0])
        if option == 'x':
            self.pos = np.array([-7.0,0.0,1.0])
            self.front = np.array([1.0,0.0,0.0])
            self.up = np.array([0.0,0.0, 1.0])
            
        elif option == 'y':
            self.pos = np.array([0.0,-7.0,1.0])
            self.front = np.array([0.0,1.0,0.0])
            self.up = np.array([0.0,0.0, 1.0])
        
        elif option == 'z':
            self.pos = np.array([0.0,0.0,7.0])
            self.front = np.array([0.0,0.0,-1.0])
            self.up = np.array([0.0,1.0, 0.0])
            
        elif option == '1':
            self.pos = c1.reshape((1, 3))[0]
            self.front = self.center - self.pos
            t = np.array([self.front[0], self.front[1], 0])
            self.up = np.cross(np.cross(self.front, t), self.front)
            
        elif option == '2':
            self.pos = c2.reshape((1, 3))[0]
            self.front = self.center - self.pos
            t = np.array([self.front[0], self.front[1], 0])
            self.up = np.cross(np.cross(self.front, t), self.front)
            
        elif option == '3':
            self.pos = c3.reshape((1, 3))[0]
            self.front = self.center - self.pos
            t = np.array([self.front[0], self.front[1], 0])
            self.up = np.cross(np.cross(self.front, t), self.front)

class GL3DPlot(QGLWidget):
    def __init__(self, parent):
        QGLWidget.__init__(self, parent)
        self.setFocusPolicy(Qt.TabFocus)
        self.grabKeyboard()
        self.cam = Camera()
        
    def paintGL(self):
        ''' Drawing routine '''
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        self.lookAt()
        
        if not CTRL:
            self.drawAxes()
            self.drawTable()
            self.drawCameras()
            
        self.drawBalls()
        
        glEnableClientState(GL_VERTEX_ARRAY)
        
        glFlush()
       
    def resizeGL(self, w, h):
        '''
        Resize the GL window 
        '''
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.cam.fovy, self.cam.aspectRatio, self.cam.zNear, self.cam.zFar)
    
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
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.cam.fovy, self.cam.aspectRatio, self.cam.zNear, self.cam.zFar)
        gluLookAt(   c.pos[0],    c.pos[1],    c.pos[2], 
                  c.center[0], c.center[1], c.center[2],
                      c.up[0],     c.up[1],     c.up[2])
        glMatrixMode(GL_MODELVIEW)
        
    def drawBalls(self):
        global READER_3D
        global CUR_3D_FILE
        global SHIFT
        if READER_3D != None:
            CUR_3D_FILE.seek(0)
            for row in READER_3D:
                try:
                    frame = int(row['frame'])
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
                    if SHIFT:
                        continue
                    glColor3f(1,.5, 0)
                
                glPushMatrix();
                glTranslatef(x, y, z)
                glutSolidSphere(.02, 20, 10)
                glPopMatrix();
       
    def drawTable(self):
        length = 2.74
        width = 1.525
        height = 0
        glColor4f(.1,.1,1,1)
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
        #glVertex3f(0, 0,  100)
        #glVertex3f(0, 0, -100)
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

    
        
    def keyPressEvent(self, event):
        global SHIFT
        global CTRL
        key = event.key()
        #print(key)
              
        if key == 16777248:
            SHIFT = not SHIFT
        if key == 16777249:
            CTRL = not CTRL
              
        if key == 87:
            self.cam.moveForward()
            #self.cam.moveUp()
        if key == 83:
            self.cam.moveBackward()
            #self.cam.moveDown()
        if key == 65:
            self.cam.moveLeft()
        if key == 68:
            self.cam.moveRight()
            
        if key == 16777235:
            self.cam.lookUp()
            #self.cam.moveForward()
        if key == 16777237:
            self.cam.lookDown()
            #self.cam.moveBackward()
        if key == 16777236:
            self.cam.lookRight()
        if key == 16777234:
            self.cam.lookLeft()
            
        if key == 88:
            self.cam.changeView('x')
        if key == 89:
            self.cam.changeView('y')
        if key == 90:
            self.cam.changeView('z')
        if key == 49:
            self.cam.changeView('1')
        if key == 50:
            self.cam.changeView('2')
        if key == 51:
            self.cam.changeView('3')
        
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
        self.cName = cName
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
        global BALL_2D_COORDS_DIR
        global CUR_SEQUENCE
        
        cs = CUR_SEQUENCE
        cDir = BALL_2D_COORDS_DIR
        self.vid = imageio.get_reader(VIDEO_DIR + self.videoFiles[CUR_SEQUENCE],'mp4')
        self.pathLabel.setText(self.videoFiles[CUR_SEQUENCE])
        try:
            self.coordFiles = sorted([cDir+name for name in os.listdir(cDir) if self.cName in name])
            self.coordFile = self.coordFiles[cs]
            self.coordFile = open(self.coordFile)
            self.coordFileReader = csv.DictReader(self.coordFile)
            print("{} is reading 2D Coordinates from {}".format(self.cName, self.coordFiles[cs]))
        except Exception as e:
            print(e)
        
    def updateImg(self):
        img = np.asarray(self.vid.get_data(CUR_FRAME))
        h, w, d = img.shape
        
        if CTRL:
            img.fill(255)
            
        self.coordFile.seek(0)
        for row in self.coordFileReader:
            try:
                frame = int(row["frame"])
                x = int(row['x'])
                y = int(row['y'])
            except:
                continue
                    
            if frame > CUR_FRAME:
                break
                
            elif frame < CUR_FRAME and not SHIFT:
                self.markImage(img, x, y, False)
            elif frame == CUR_FRAME:
                self.markImage(img, x, y, True)
                    
        qImg = QImage(img, w, h, d*w, QImage.Format_RGB888)
        pMap = QPixmap(qImg)
        pMap = pMap.scaledToWidth(450)
        self.imgBox.setPixmap(pMap)
        
    def markImage(self, pxlImg, x, y, curLocation):
        color = np.array([0,0,0])
        h, w, d = pxlImg.shape
        if curLocation:
            color = np.array([255, 0, 0])
        else:
            color = np.array([255, 140, 0])
            
        size = 5
        for i in range(y-size, y+size+1):
            for j in range(x-size, x+size+1):
                if i>=0 and j>=0 and i<h and j<w:
                    pxlImg[i, j, :] = color
            
        


class PPDashBoard(QWidget):
    incrementFrame = Signal()
    ''' container for all application widgets '''
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.createElements()
        self.createLayout()
        self.createActions()
        
    def createElements(self):
        btnSize = 30
        self.gl3dPlot = GL3DPlot(self)
        
        self.vidFrame1 = VideoFrameDisplay('CAM1', self)
        self.vidFrame2 = VideoFrameDisplay('CAM2', self)
        self.vidFrame3 = VideoFrameDisplay('CAM3', self)
        
        self.frCtrlLabel = QLabel("- FRAME -")
        self.frPrev = QPushButton('<')
        self.frPrev.setFixedSize(btnSize,btnSize)
        self.frLabel = QLabel("{}/{}".format(CUR_FRAME+1, NUMBER_OF_FRAMES))
        self.frNext = QPushButton('>')
        self.frNext.setFixedSize(btnSize,btnSize)
        self.frReset = QPushButton('reset')
        self.frReset.setFixedHeight(btnSize*2)
        self.frPause = QPushButton('pause')
        self.frPause.setFixedHeight(btnSize*2)
        self.frPlay = QPushButton('play')
        self.frPlay.setFixedHeight(btnSize*2)
        
        self.seqCtrlLabel = QLabel("- SEQUENCE -")
        self.seqPrev = QPushButton('<')
        self.seqPrev.setFixedSize(btnSize,btnSize)
        self.seqLabel = QLabel("{}/10".format(CUR_SEQUENCE+1))
        self.seqNext = QPushButton('>')
        self.seqNext.setFixedSize(btnSize,btnSize)
        
        
    def createLayout(self):
        self.mainBox     = QHBoxLayout()
        self._3dPlotBox  = QVBoxLayout()
        self.vidBox      = QVBoxLayout()
        self.buttonBox   = QHBoxLayout()
        self.frCtrl      = QVBoxLayout()
        self.frBtnCtrl   = QHBoxLayout()
        self.seqCtrl     = QVBoxLayout()
        self.seqBtnCtrl  = QHBoxLayout()
        self.frSub       = QHBoxLayout()
        self.seqSub      = QHBoxLayout()
        
        self.mainBox.addLayout(self._3dPlotBox)
        self.mainBox.addLayout(self.vidBox)
        
        self._3dPlotBox.addLayout(self.buttonBox)
        self._3dPlotBox.addWidget(self.gl3dPlot)
        
        self.vidBox.addWidget(self.vidFrame1)
        self.vidBox.addWidget(self.vidFrame2)
        self.vidBox.addWidget(self.vidFrame3)
        
        self.frCtrl.addLayout(self.frSub)
        self.frSub.addStretch(1)
        self.frSub.addWidget(self.frCtrlLabel)
        self.frSub.addStretch(1)
        self.frCtrl.addLayout(self.frBtnCtrl)
        self.frBtnCtrl.addWidget(self.frPrev)
        self.frBtnCtrl.addWidget(self.frLabel)
        self.frBtnCtrl.addWidget(self.frNext)
        
        self.seqCtrl.addLayout(self.seqSub)
        self.seqSub.addStretch(1)
        self.seqSub.addWidget(self.seqCtrlLabel)
        self.seqSub.addStretch(1)
        self.seqCtrl.addLayout(self.seqBtnCtrl)
        self.seqBtnCtrl.addWidget(self.seqPrev)
        self.seqBtnCtrl.addWidget(self.seqLabel)
        self.seqBtnCtrl.addWidget(self.seqNext)
        
        self.buttonBox.addLayout(self.seqCtrl)
        self.buttonBox.addStretch(1)
        self.buttonBox.addLayout(self.frCtrl)
        self.buttonBox.addWidget(self.frReset)
        self.buttonBox.addStretch(1)
        self.buttonBox.addWidget(self.frPause)
        self.buttonBox.addWidget(self.frPlay)
        
        self.setLayout(self.mainBox)
       
    def createActions(self):
        self.frNext.clicked.connect(self.onFrameNext)
        self.frPrev.clicked.connect(self.onFramePrev)
        self.frReset.clicked.connect(self.onFrameReset)
        self.seqNext.clicked.connect(self.onSequenceNext)
        self.seqPrev.clicked.connect(self.onSequencePrev)
        self.frPlay.clicked.connect(self.onPlay)
        self.frPause.clicked.connect(self.onPause)
        self.incrementFrame.connect(self.onFrameNext)
    
    def onPause(self):
        global PLAYING
        try:
            PLAYING = False
            self.playThread.join()
        except Exception as e:
            pass
        
    def onPlay(self):
        self.playThread = PlayThread(self)
        self.playThread.start()
    
    def onFrameNext(self):
        updateFrame(CUR_FRAME + 1)
        self.onFrameChange()
        
    def onFramePrev(self):
        updateFrame(CUR_FRAME - 1)
        self.onFrameChange()
        
    def onFrameReset(self):
        updateFrame(0)
        self.onFrameChange()
        
    def onSequenceNext(self):
        if CUR_SEQUENCE < 9:
            updateSequence(CUR_SEQUENCE + 1)
            self.onSequenceChange()
            
    def onSequencePrev(self):
        if CUR_SEQUENCE > 0:
            updateSequence(CUR_SEQUENCE - 1)
            self.onSequenceChange()
    
    def onSequenceChange(self):
        self.seqLabel.setText('{}/10'.format(CUR_SEQUENCE+1))
        self.vidFrame1.updateSequence()
        self.vidFrame2.updateSequence()
        self.vidFrame3.updateSequence()
        updateFrame(0)
        self.onFrameChange()
        
    def onFrameChange(self):
        self.frLabel.setText('{}/{}'.format(CUR_FRAME+1, NUMBER_OF_FRAMES))
        self.vidFrame1.updateImg()
        self.vidFrame2.updateImg()
        self.vidFrame3.updateImg()
        self.gl3dPlot.updateGL()
        
        
class PlayThread(Thread):
    def __init__(self, slave):
        Thread.__init__(self)
        self.slave = slave
        
    def run(self):
        global PLAYING
        global FRAME_RATE
        global CUR_FRAME
        self.done = False
        PLAYING = True
        while PLAYING:
            curVal = self.slave.incrementFrame.emit()
            time.sleep(1/FRAME_RATE)
        self.done = True
            
    def join(self):
        while not self.done:
            pass
        Thread.join(self, None)
            
            
class SettingsMenu(QMainWindow):
    '''popup window for user to change settings'''
    def __init__(self):
        QMainWindow.__init__(self)
        self.createElements()
        self.createLayout()
        self.createActions()
        
    def createElements(self):
        global VID_DIR
        global BALL_3D_COORDS_DIR
        global BALL_2D_COORDS_DIR
        global FRAME_RATE
        
        self.videoFileDirLabel = QLabel("Video Files Location: ")
        self.videoFileDirEdit  = QLineEdit()
        self.videoFileDirEdit.setText(VID_DIR)
        self.videofileDirBtn = QPushButton("change")
    
        self._3DFileDirLabel = QLabel("3D Files Location: ")
        self._3DFileDirEdit  = QLineEdit()
        self._3DFileDirEdit.setText(BALL_3D_COORDS_DIR)
        self._3DfileDirBtn = QPushButton("change")
        
        self._2DFileDirLabel = QLabel("2D Files Location: ")
        self._2DFileDirEdit  = QLineEdit()
        self._2DFileDirEdit.setText(BALL_2D_COORDS_DIR)
        self._2DfileDirBtn = QPushButton("change")
        
        self.frameRateLabel = QLabel("Frame Rate: ")
        self.frameRateLabel_2 = QLabel(str(FRAME_RATE))
        self.frameRateChanger = QSlider()
        self.frameRateChanger.setMinimum(1)
        self.frameRateChanger.setMaximum(10)
        self.frameRateChanger.setTickInterval(0.5)
        
        #add toggle buttons for x, y, and z axis grids here
        
        
    def createLayout(self):
        self.mainLayout = QGridLayout()
        
        self.mainLayout.addWidget(self.videoFileDirLabel)
        self.mainLayout.addWidget(self.videoFileDirEdit)
        self.mainLayout.addWidget(self.videoFileDirBtn)
        
        self.mainLayout.addWidget(self._3DFileDirLabel)
        self.mainLayout.addWidget(self._3DFileDirEdit)
        self.mainLayout.addWidget(self._3DFileDirBtn)
        
        self.mainLayout.addWidget(self._2DFileDirLabel)
        self.mainLayout.addWidget(self._2DFileDirEdit)
        self.mainLayout.addWidget(self._2DFileDirBtn)
        
        self.mainLayout.addWidget(self.frameRateLabel)
        self.mainLayout.addWidget(self.frameRateLabel2)
        self.mainLayout.addWidget(self.frameRateChanger)
        
    def createActions(self):
        self.videoFileDirBtn.clicked.connect(onVideoFileDirChanged)
        self._3DFileDirBtn.clicked.connect(on_3DFileDirChanged)
        self._2DFileDirBtn.clicked.connect(on_2DFileDirChanged)
        self.frameRateChanger.moved.connect(onFrameRateChanged)
        
    def onVideoFileDirChanged(self):
        global VID_DIR
        # TODO: check if path is valid. If not, highlight the lineEdit Widget and disable close
        VID_DIR = self.videoFileDirEdit.text()
        
    def on_3DFileDirChanged(self):
        global BALL_3D_COORDS_DIR
        # TODO: check if path is valid. If not, highlight the lineEdit Widget and disable close
        BALL_3D_COORDS_DIR = self._3DFileDirEdit.text()
        
    def on_2DFileDirChanged(self):
        global BALL_2D_COORDS_DIR
        # TODO: check if path is valid. If not, highlight the lineEdit Widget and disable close
        BALL_2D_COORDS_DIR = self._2DFileDirEdit.text()
        
    def checkPathValidity(self, path, expectedNumFiles):
        try:
            files = sys.listDir(path)
            if len(files) == expectedNumFiles:
                return True
            else:
                return False
        except:
            return False
        return False

class PPApplication(QMainWindow):
    ''' main window for the Ping Pong Application '''
    def __init__(self):
        super(PPApplication, self).__init__()
        updateSequence(0)
        self.dash = PPDashBoard(self)
        self.setCentralWidget(self.dash)
        self.showMaximized()
        self.setWindowTitle("Ping Pong Flight Visualization")

    def closeEvent(self, event):
        self.dash.onPause()
        sys.exit(0)


if __name__ == "__main__":
    app = QApplication(['Ping Pong Flight Visualization'])
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QtGui.QColor(53,53,53))
    palette.setColor(QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QPalette.Base, QtGui.QColor(15,15,15))
    palette.setColor(QPalette.AlternateBase, QtGui.QColor(53,53,53))
    palette.setColor(QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QPalette.Text, QtCore.Qt.white)
    palette.setColor(QPalette.Button, QtGui.QColor(53,53,53))
    palette.setColor(QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QPalette.Highlight, QtGui.QColor(142,45,197).lighter())
    palette.setColor(QPalette.HighlightedText, QtCore.Qt.black)
    app.setPalette(palette)
    
    window = PPApplication()
    window.show()
    app.exec_()
