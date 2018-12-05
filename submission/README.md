This zip file contains 3 visualisation software
Prerequisite:
    Before running the softwares, make sure there is a FileList.csv showing the names of the mp4 video files
    to be tracked in the root folder. Each row of the CSV represents a sequence and it must contain 3 names of the video
    files in the order of camera 1,2 and 3. A sample FileList.csv is already included in this zip file.
	The corresponding videos named in FileList.csv has to be put inside './TestVideos/' Folder

1. Ball Tracking Software
    Change directory to './BallTracker'. Run ballTracker.m on matlab. It will read the FileList.csv and read the corresponding
	videos in 'TestVideos/' folder and output the pixel coordinates of the balls in './BallTracker/results/' folder.
	
2. Triangulation Software
    Run Triangulation.m on matlab. It takes CSV input of pixel coordinates from './Annotation/'. It groups files
    of the same sequence together according to FileList.csv. The input CSVs have column headers 'frame', 'x', 'y', 'undistort_x', 'undistort_y', with each row representing the data from each frame.
    It outputs to './triangulation_output/', where each output file is named after the video taken at camera 1 position. The output CSV
	has column headers 'frame', 'x', 'y', 'z'.


3. Visualisation Software
	Change Directory to './viz'. Follow the instructions in the folder.


