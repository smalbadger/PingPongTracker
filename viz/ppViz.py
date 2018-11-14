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
SHIFT = False   # toggle showing all previous ball positions or just the current
CTRL  = False

TABLE_Z_OFFSET = 0.07

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

CAM_FRAME_RATE = 119.88

# parametric approximations of ball flight
X_POLY = None
Y_POLY = None
Z_POLY = None
HIT_DETECTED = 0


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
 
#############################################################################
#                            Globals End                                    #
#############################################################################

#############################################################################
#                           Utility Functions Begin                         #
############################################################################# 
def updateSequence(seqNum):
    global BALL_3D_COORDS_DIR
    global VIDEO_DIR
    global CUR_SEQUENCE 
    global CUR_FRAME
    global NUMBER_OF_FRAMES
    global CUR_3D_FILE
    global READER_3D
    global X_POLY
    global Y_POLY
    global Z_POLY
    global CAM_FRAME_RATE
    global HIT_DETECTED
    
    CUR_SEQUENCE = seqNum
    videoFiles = sorted([VIDEO_DIR+name for name in os.listdir(VIDEO_DIR)])[:10]
    vid = imageio.get_reader(videoFiles[CUR_SEQUENCE],'mp4')
    NUMBER_OF_FRAMES = vid._meta['nframes']
    print("Switched to sequence: {}".format(CUR_SEQUENCE))
    print("# of frames: {}".format(NUMBER_OF_FRAMES))
    
    dir3D = BALL_3D_COORDS_DIR
    curSeq = CUR_SEQUENCE
    _3DCoordFiles = sorted([dir3D+name for name in os.listdir(dir3D)])
    try:
        CUR_3D_FILE = open(_3DCoordFiles[curSeq])
        READER_3D = csv.DictReader(CUR_3D_FILE)
        print("Reading 3D coordinates from {}".format(_3DCoordFiles[curSeq]))
    except:
        print("Couldn't find a file of 3D coordinates for this sequence")
        
    # split all data into x, y, z, and t
    t_data = []
    x_data = []
    y_data = []
    z_data = []
    if READER_3D != None:
        CUR_3D_FILE.seek(0)
        for row in READER_3D:
            try:
                frame = int(row['frame'])
                x = float(row['x'])
                y = float(row['y'])
                z = float(row['z'])
                z += TABLE_Z_OFFSET
                
                if np.isnan(x) or np.isnan(y) or np.isnan(z):
                    continue
                
                time = frame / CAM_FRAME_RATE
                
                t_data.append(time)
                x_data.append(x)
                y_data.append(y)
                z_data.append(z)
            except:
                continue
                
    # get all data points before the ball hits somthing
    HIT_DETECTED = 0
    for t, x, y, z, in zip(t_data, x_data, y_data, z_data):
        HIT_DETECTED += 1
        if z < -TABLE_Z_OFFSET:
            break
        
    HIT_DETECTED = 40
    print("Ball hit went below table at frame: {}".format(HIT_DETECTED))
        
    t_data = t_data[:HIT_DETECTED]
    x_data = x_data[:HIT_DETECTED]
    y_data = y_data[:HIT_DETECTED]
    z_data = z_data[:HIT_DETECTED]
    
    x_coff = np.polyfit(t_data, x_data, 2)
    y_coff = np.polyfit(t_data, y_data, 2)
    z_coff = np.polyfit(t_data, z_data, 2)
    
    X_POLY = np.poly1d(x_coff)
    Y_POLY = np.poly1d(y_coff)
    Z_POLY = np.poly1d(z_coff)
            
    
def updateFrame(frameNum):
    global CUR_FRAME    
    CUR_FRAME = frameNum % NUMBER_OF_FRAMES
    #print("CUR_FRAME: {}".format(CUR_FRAME))

def getPointOneAway(p1, p2):
    return (p2-p1) / (np.linalg.norm(p2-p1)) + p1
#############################################################################
#                           Utility Functions End                           #
#############################################################################

class Camera:
    def __init__(self):
        self.speed = 0.01
        self.angularSpeed = 1
        self.distance = 3
        self.fovy        = 100.0 
        self.aspectRatio = 1.0
        self.zNear       = .1 
        self.zFar        = 100
        self.center = np.array([0.0,0.0,0.0])
        self.pos = np.array([-self.distance,0.0,1.0])
        self.updateFrontVector()
        self.updateUpVector()
        self.updateDistance()
    
    def moveUp(self):
        self.updatePos(up=True)
        
    def moveDown(self):
        self.updatePos(down=True)
        
    def moveLeft(self):
        self.updatePos(left=True)
        
    def moveRight(self):
        self.updatePos(right=True)
    
    def moveForward(self):
        if self.distance < 2 * self.speed:
            return
        self.pos += self.speed * self.front
        self.updateDistance()
        
    def moveBackward(self):
        if self.distance >10:
            return
        self.pos -= self.speed * self.front
        self.updateDistance()
        
    def updatePos(self, up=False, down=False, right=False, left=False):
        if up and down:
            print("can't move camera up and down at the same time")
            return
        if right and left:
            print("can't move camera right and left at the same time")
            return
            
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        
        transformation = np.zeros(16).reshape((4,4))
        rV = self.getRightVector()
        toZAxis = np.array([-self.pos[0], self.pos[1], 0])
        homogenized = np.ones(4)
        homogenized[0:3] = self.pos
        
        #rotate up or down
        if up or down:
            if self.pos[2] > 0:
                angleFromPZ= np.rad2deg(self.angle(self.pos,np.array([0,0,1])))
                angleFromNZ= 180 - angleFromPZ
            else:
                angleFromNZ= np.rad2deg(self.angle(self.pos,np.array([0,0,-1])))
                angleFromPZ= 180 - angleFromNZ
                
            if angleFromPZ > 10 and up or angleFromNZ > 10 and down:
                if up:
                    v = rV
                if down:
                    v = -rV
                
                # move to origin
                glTranslatef(0, 0, self.distance)
                # turn back to look at the current point from origin
                glRotatef(180, self.up[0], self.up[1], self.up[2])
                # turn 1 click either up or down
                glRotatef(self.angularSpeed, v[0], v[1], v[2])
                # go travel the same distance away from the origin
                glTranslatef(0, 0, self.distance)
                
                glGetDoublev(GL_MODELVIEW_MATRIX, transformation)
                newPt = np.matmul(transformation, homogenized)
                self.pos = newPt[0:3]/newPt[3]
                self.pos *= (-self.distance/np.linalg.norm(self.pos))
                self.updateFrontVector()
                self.updateUpVector()
                
            else:
                if up:
                    print("Can't go up any more.")
                if down:
                    print("Can't go down any more.")
                    
        # rotate left or right
        if left or right:
            if left:
                speed = -self.angularSpeed
            elif right:
                speed = self.angularSpeed
                
            # use x and y to get distance from z axis.
            _2d = np.array([self.pos[0], self.pos[1]])
            x = np.array([1, 0])
            y = np.array([0, 1])
            zDist = np.linalg.norm(_2d)
            
            if _2d[1]>0:
                xAngle = self.angle(_2d, x, acute=True)
            else:
                xAngle = self.angle(_2d, x, acute=False)
            
            xAngle += np.deg2rad(speed)
            newX = np.cos(xAngle) * zDist
            newY = np.sin(xAngle) * zDist
            self.pos[0] = newX
            self.pos[1] = newY
            self.updateFrontVector()
            self.updateUpVector()
            
        glPopMatrix()
        
    def updateUpVector(self):
        right = self.getRightVector()
        self.up = np.cross(right, self.front)
    
    def updateFrontVector(self):
        self.front = self.center - self.pos
        
    def getRightVector(self):
        toZAxis = np.array([-self.pos[0], -self.pos[1], 0])
        if self.pos[2] < 0:
            right = np.cross(toZAxis, self.front)
        elif self.pos[2] > 0:
            right = np.cross(self.front, toZAxis)
        else:
            toZAxis[2] = 1
            right = np.cross(self.front, toZAxis)
        return right
        
    def angle(self, v1, v2, acute=True):
        angle= np.arccos(np.dot(v1,v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)))
        if (acute == True):
            return angle
        else:
            return 2 * np.pi - angle
            
        
    def updateDistance(self):
        self.distance= np.sqrt(self.pos[0]**2 + self.pos[1]**2 + self.pos[2]**2)
     
    def changeView(self, option):
        if option == 'x':
            self.pos = np.array([-self.distance,0.0,0.0])
            
        elif option == 'y':
            self.pos = np.array([0.0,-self.distance,0.0])
            
        elif option == '1':
            self.pos = np.copy(c1.reshape((1, 3))[:][0])
            
        elif option == '2':
            self.pos = np.copy(c2.reshape((1, 3))[:][0])
            
        elif option == '3':
            self.pos = np.copy(c3.reshape((1, 3))[:][0])
            
        self.updateFrontVector()
        self.updateUpVector()
        self.updateDistance()
    
    

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
            self.drawEnvironment()
            #self.drawAxes()
            self.drawTable()
            self.drawCameras()
            self.drawFlightApproximation()
            
            
        self.drawBalls()
        
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        
        glFlush()
       
    def resizeGL(self, w, h):
        '''
        Resize the GL window 
        '''
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.cam.fovy, 
                       self.cam.aspectRatio, 
                       self.cam.zNear, 
                       self.cam.zFar)
    
    def initializeGL(self):
        '''
        Initialize GL
        '''
        glutInit()
        glEnable(GL_BLEND);
        glEnable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        glClearColor(.2,.3,.0, 1.0)
        glClearDepth(1.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        glMatrixMode(GL_MODELVIEW)
        self.lookAt()
        
    def lookAt(self):
        c = self.cam
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.cam.fovy, 
                       self.cam.aspectRatio, 
                       self.cam.zNear, 
                       self.cam.zFar)
        gluLookAt(   c.pos[0],    c.pos[1],    c.pos[2], 
                  c.center[0], c.center[1], c.center[2],
                      c.up[0],     c.up[1],     c.up[2])
        glMatrixMode(GL_MODELVIEW)
        
    def drawFlightApproximation(self):
        global CUR_3D_FILE
        global READER_3D
        global X_POLY
        global Y_POLY
        global Z_POLY
        global CAM_FRAME_RATE
        global HIT_DETECTED
    
        glColor3f(0,1,1)    
        glLineWidth(5)
        glBegin(GL_LINE_STRIP)
        for i in range(0, HIT_DETECTED+1):
            if i > CUR_FRAME:
                break
            time = i/CAM_FRAME_RATE
            x = X_POLY(time)
            y = Y_POLY(time)
            z = Z_POLY(time)
            #print("x: {}\ty:{}\tz:{}".format(x, y, z))
            glVertex3f(x, y, z)
        glEnd()
        glLineWidth(1)   
                
                
        
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
                    z += TABLE_Z_OFFSET
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
        height = 0.76
        offset = .0001
        
        # draw shadow
        glBegin(GL_POLYGON)
        glColor4f(0,0,0,.8); glVertex3f( 0,        0,      -height+offset)
        glColor4f(0,0,0,.1); glVertex3f( length/2, 0,      -height+offset)
        glColor4f(0,0,0, 0); glVertex3f( length/2, width/2,-height+offset)
        glColor4f(0,0,0,.1); glVertex3f( 0,        width/2,-height+offset)
        glEnd()
        
        glBegin(GL_POLYGON)
        glColor4f(0,0,0,.8); glVertex3f( 0,        0,      -height+offset)
        glColor4f(0,0,0,.1); glVertex3f( 0,       -width/2,-height+offset)
        glColor4f(0,0,0, 0); glVertex3f( length/2,-width/2,-height+offset)
        glColor4f(0,0,0,.1); glVertex3f( length/2, 0,      -height+offset)
        glEnd()
        
        glBegin(GL_POLYGON)
        glColor4f(0,0,0,.8); glVertex3f( 0,        0,      -height+offset)
        glColor4f(0,0,0,.1); glVertex3f(-length/2, 0,      -height+offset)
        glColor4f(0,0,0, 0); glVertex3f(-length/2,-width/2,-height+offset)
        glColor4f(0,0,0,.1); glVertex3f( 0,       -width/2,-height+offset)
        glEnd()
        
        glBegin(GL_POLYGON)
        glColor4f(0,0,0,.8); glVertex3f( 0,        0,      -height+offset)
        glColor4f(0,0,0,.1); glVertex3f( 0,        width/2,-height+offset)
        glColor4f(0,0,0, 0); glVertex3f(-length/2, width/2,-height+offset)
        glColor4f(0,0,0,.1); glVertex3f(-length/2, 0,      -height+offset)
        glEnd()
            
        
        #draw legs
        xDist = 1
        yDist = .65
        glColor4f(0,0,0,1)
        tList = [(xDist,yDist),(xDist,-yDist),(-xDist,yDist),(-xDist,-yDist)]
        for x,y in tList:
            for i in (1, 4):
                glPushMatrix()
                glTranslatef(x/i, y, -.00001)
                glScalef(.01, .01, -.38)
                self.drawUnitCube()
                glPopMatrix()
        
        # draw table top
        glColor4f(.1,.1,.8,1)
        glBegin(GL_POLYGON)
        glVertex3f(-length/2, -width/2, 0)
        glVertex3f( length/2, -width/2, 0)
        glVertex3f( length/2,  width/2, 0)
        glVertex3f(-length/2,  width/2, 0)
        glEnd()
        
        # draw lines on table
        lWidth = 0.025
        glColor4f(1, 1, 1, 1)
        glBegin(GL_POLYGON)
        glVertex(-length/2, lWidth/2, offset)
        glVertex( length/2, lWidth/2, offset)
        glVertex( length/2,-lWidth/2, offset)
        glVertex(-length/2,-lWidth/2, offset)
        glEnd()
        
        glBegin(GL_POLYGON)
        glVertex(-length/2, width/2, offset)
        glVertex( length/2, width/2, offset)
        glVertex( length/2, width/2-lWidth, offset)
        glVertex(-length/2, width/2-lWidth, offset)
        glEnd()
        
        glBegin(GL_POLYGON)
        glVertex(-length/2, -width/2, offset)
        glVertex( length/2, -width/2, offset)
        glVertex( length/2, -width/2+lWidth, offset)
        glVertex(-length/2, -width/2+lWidth, offset)
        glEnd()
        
        glBegin(GL_POLYGON)
        glVertex(-length/2, -width/2, offset)
        glVertex(-length/2,  width/2, offset)
        glVertex(-length/2+lWidth, width/2, offset)
        glVertex(-length/2+lWidth, -width/2, offset)
        glEnd()
        
        glBegin(GL_POLYGON)
        glVertex(length/2, -width/2, offset)
        glVertex(length/2,  width/2, offset)
        glVertex(length/2-lWidth, width/2, offset)
        glVertex(length/2-lWidth, -width/2, offset)
        glEnd()
        
        # draw net 
        glColor4f(1, 1, 1, 1)
        glBegin(GL_POLYGON)
        glVertex(0, -width/2, .1525)
        glVertex(0,  width/2, .1525)
        glVertex(0,  width/2, .1425)
        glVertex(0, -width/2, .1425)
        glEnd()
        
        glColor4f(0,0,0,.5)
        glBegin(GL_LINES)
        for i in np.arange(.01, .1425, .005):
            glVertex3f(0, -width/2, i)
            glVertex3f(0,  width/2, i)
            
        for i in np.arange(-width/2, width/2, .005):
            glVertex3f(0, i, .1425)
            glVertex3f(0, i, .01)
            
        glEnd()
        
       
        
        # draw net posts
        for i in (0,1):
            glPushMatrix()
            glLoadIdentity()
            if i==0:
                glRotate(180, 0,0,1)
            glTranslatef(0,width/2,0)
            glScalef(.01, .01, -.02)
            glRotatef(90, -1, 0, 0)
            glColor4f(.1,.1,.7,1)
            self.drawUnitCube()
            glRotatef(90, -1, 0, 0)
            glScalef(.4, .4, 4)
            self.drawUnitCube()
            glPopMatrix()
       
        
        
        
    def drawAxes(self):
        #draw x, y, and z lines
        glColor4f(0,0,0,1)
        glBegin(GL_LINES)
        glVertex3f(0, 0,  100)
        glVertex3f(0, 0, -100)
        glVertex3f(0,  100, 0)
        glVertex3f(0, -100, 0)
        glVertex3f( 100, 0, 0)
        glVertex3f(-100, 0, 0)
        glEnd()
        
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
        
    def drawEnvironment(self):
        # draw ground
        ground = -0.76
        glColor4f(.87, .72, .53, 1)
        glBegin(GL_POLYGON)
        glVertex3f( 10, 10, ground)
        glVertex3f(-10, 10, ground)
        glVertex3f(-10,-10, ground)
        glVertex3f( 10,-10, ground)
        glEnd()
        
        # draw stage
        height = .69
        y_coord = 1.5
        glColor4f(.54, .27, .07, 1)
        glBegin(GL_POLYGON)
        glVertex3f(5, y_coord, ground)
        glVertex3f(5, y_coord, ground+height)
        glVertex3f(-5, y_coord, ground+height)
        glVertex3f(-5, y_coord, ground)
        glEnd()
        
        glBegin(GL_POLYGON)
        glVertex3f(5, y_coord, ground+height)
        glVertex3f(-5, y_coord, ground+height)
        glVertex3f(-5, y_coord+3, ground+height)
        glVertex3f(5, y_coord+3, ground+height)
        glEnd()
        
        # draw barriers
        glColor4f(.2, .2, .2, 1)
        glPushMatrix()
        glTranslatef(2, 1.5, -.74)
        glRotatef(180, 0, 0, 1)
        self.drawBarrier()
        glTranslatef(0,1.26,0)
        glRotatef(1, 0,0,-1)
        self.drawBarrier()
        glTranslatef(0,1.26,0)
        glRotatef(15, 0,0,-1)
        self.drawBarrier()
        glTranslatef(0,1.26,0)
        glRotatef(50, 0,0,-1)
        self.drawBarrier()
        glTranslatef(0,1.26,0)
        glRotatef(14, 0,0,-1)
        self.drawBarrier()
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(3, 1.5, -.74)
        glRotatef(180, 0, 0, 1)
        self.drawBarrier()
        glTranslatef(1,5,0)
        glRotatef(80, 0, 0, -1)
        self.drawBarrier()
        glTranslatef(0, 1.5, 0)
        glRotatef(4, 0, 0, 1)
        self.drawBarrier()
        glPopMatrix()
        
        
        
        
        
    def drawBarrier(self):
        length = 1.25
        height = .5
        glBegin(GL_POLYGON)
        glVertex3f(0,0,0)
        glVertex3f(0,length,0)
        glVertex(0,length,height)
        glVertex(0,0,height)
        glEnd()
        
        
    def drawUnitCube(self):
        pts = [[ 1, 1, 1],
               [ 1, 1,-1],
               [ 1,-1, 1],
               [ 1,-1,-1],
               [-1, 1, 1],
               [-1, 1,-1],
               [-1,-1, 1],
               [-1,-1,-1]]
        
        for i in (-1, 1):
            for j in (0, 1, 2):
                c = [k for k in pts if k[j] == i]
                glBegin(GL_POLYGON)
                for k in (0, 1, 3, 2):
                    cpy = c[k][:]
                    cpy[2]+=1
                    glVertex3f(cpy[0], cpy[1], cpy[2]);
                    glVertex3f(cpy[0], cpy[1], cpy[2]);
                    glVertex3f(cpy[0], cpy[1], cpy[2]);
                    glVertex3f(cpy[0], cpy[1], cpy[2]);
                glEnd()
        
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
            self.cam.moveUp()
        if key == 83:
            self.cam.moveDown()
        if key == 65:
            self.cam.moveLeft()
        if key == 68:
            self.cam.moveRight()
            
        if key == 16777235:
            self.cam.moveForward()
        if key == 16777237:
            self.cam.moveBackward()
            
        if key == 88:
            self.cam.changeView('x')
        if key == 89:
            self.cam.changeView('y')
        if key == 49:
            self.cam.changeView('1')
        if key == 50:
            self.cam.changeView('2')
        if key == 51:
            self.cam.changeView('3')
        
        self.updateGL()
        
class VideoFrameDisplay(QGroupBox):
    def __init__(self, cName, parent):
        QGroupBox.__init__(self, parent)
        self.cName = cName
        vidFiles = [name for name in os.listdir(VIDEO_DIR) if cName in name]
        self.videoFiles = sorted(vidFiles)
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
        self.vid = imageio.get_reader(VIDEO_DIR + self.videoFiles[cs],'mp4')
        self.pathLabel.setText(self.videoFiles[cs])
        try:
            cF = [cDir+name for name in os.listdir(cDir) if self.cName in name]
            self.coordFiles = sorted(cF)
            self.coordFile = self.coordFiles[cs]
            self.coordFile = open(self.coordFile)
            self.coordFileReader = csv.DictReader(self.coordFile)
            print("{} is reading 2D Coordinates from {}".format(self.cName, 
                                                           self.coordFiles[cs]))
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
        # TODO: check if path is valid. If not, highlight the lineEdit 
        # Widget and disable close
        VID_DIR = self.videoFileDirEdit.text()
        
    def on_3DFileDirChanged(self):
        global BALL_3D_COORDS_DIR
        # TODO: check if path is valid. If not, highlight the lineEdit 
        # Widget and disable close
        BALL_3D_COORDS_DIR = self._3DFileDirEdit.text()
        
    def on_2DFileDirChanged(self):
        global BALL_2D_COORDS_DIR
        # TODO: check if path is valid. If not, highlight the lineEdit 
        # Widget and disable close
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
