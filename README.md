# PingPongTracker
This was the final project for a class I took at the National University of Singapore - Computer Vision and Pattern Recognition (CS4243). We worked in groups of 4.

## Assignment
In this assignment, we were given 10 videos from 3 different cameras (30 videos in total). The cameras were set up around a ping pong table and each of them were facing directly at the center of the table. The 3 cameras are synchronized, so we can see 3 different views of the ball at each interval of time. We were also given the coordinates and orientation of each camera in the form of translation and rotation matricies relative to the center of the table. There were 3 main tasks in this assignment:

1. Write a program to track the ball in each frame of each video. 
1. Write a program to calculate where the ball lies in the 3D coordinate space.
1. Create software to visualize the flight of the ball and report the spin on the ball.

We were also given the desired output from task 1, so we could get a start on the other parts earlier and have good data in case we couldn't get part 1 to work.

### Team members
* [ChompsterZ](https://github.com/ChompsterZ) - Created software to track the ball in each frame.
* [MuhdNurKamal](https://github.com/MuhdNurKamal) - Created software to triangulate ball in 3D space given 2D coordinates from 3 cameras
* [smalbadger](https://github.com/smalbadger) - Created visualization software [ppViz](https://github.com/smalbadger/PingPongTracker/tree/master/viz)
* [VeryLazyBoy](https://github.com/VeryLazyBoy) - Didn't contribute to the team or project. At least his github name is honest.
