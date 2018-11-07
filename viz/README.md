# Ping Pong Visualization Software (ppViz)
Welcome to the visualization software for the final project. This document describes how to install ppViz and its dependencies as well as general usage instructions and terminology used.

## Installation
1. clone this entire repository somewhere on your system. It was developed on Ubuntu 18.04, so something similar is your best bet. 
1. Make sure you have python3
1. run the following commands in the given order (there may be some others as well):
    - > pip3 install PySide2
    - > pip3 install numpy
    - > pip3 install imageio
    - > pip3 install PyOpenGL PyOpenGL_accelerate
    - > sudo apt-get install python-opengl
    * note: I use pip3, but if you don't have it, try just pip.

## Usage
The visualization tool can be used for visualizing the calculated 3D coordinates of the ball (and plot trajectoy), and show where the ping pong ball was found in each frame.

1. Run the program: python3 ppViz.py
1. Notice that there are 3 video frames on the right and a big 3D viewer box on the left with controls above it. 
    - Play and pause are for starting and stopping the video.
    - there are prev and next ('<' and '>' respectively) for both sequence and frame control.
1. The 3D viewer takes some keyboard controls:
    - W: move camera forward
    - S: move camera backward
    - A: move camera left
    - D: move camera right
    - ARROW KEYS: look up, down, left, and right. (There's a bug which doesn't allow the camera to rotate more than 180 degrees total.)
        - Note: moving is wonky right now. I'll try to fix it soon.
1. There are some keyboard controls that control both video and 3D viewer:
    - SHIFT: shows location of ball in all frames before and including the current frame. Toggling it will show only the current location of the ball.
    - CTRL: toggles background.
        - Note: if SHIFT and CTRL are both toggled on and the ball cannot be triangulated in the current frame, all video frames and 3D viewer will be blank.
1. Where do you need to put your files?
    - Store all of your files for 3D points in one directory and all files containing 2D points in another directory. Make sure you have a consistent naming convention for each of the files.
    - For 3D points, there should be 10 files in a directory and when they're sorted alphabetically, they should be in the same order as the video sequences. Look at the '../Test3DCoords/' directory as an example.
    - For 2D points, store your files exactly like the annotated files are stored that the professor gave us. Look at '../Test2DCoords/' as an example.
1. How does the program know where to look for your files?
    - right now, there's just 2 global variables: BALL_2D_COORDS_DIR and BALL_3D_COORDS_DIR. Change the value of these variable to be the relative or absolute file path to the directory you with to read from.
    - Coming soon, I'll make a file chooser widget so you don't have to mess with the code.
    
### Terminology
* Sequence - we have 10 'sequences' in total (couldn't think of a better name) a sequence is the group of 3 videos that show the SAME ball launch.
* Frame - the same frame number from all 3 cameras.


# :beetle: Bug Reporting :beetle:
If you run into a weird behavior, put your data set somewhere and message on the group chat. Don't try to save the day and fix the code. I'll admit, my coding standards aren't super great on this project.
