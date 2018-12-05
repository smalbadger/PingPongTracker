%diary on
close all
clear all

% ================== Parameters ================== %
% Specify where the filelist is stored
file_list = '..\FileList.csv';
% Specify directory where videos are stored
vid_dir = '..\TestVideos\';
% Specify directory where annotation results are stored
res_dir = '.\results\';

% ==================== Script ==================== %
% Read video names from filelist
fid = fopen(file_list,'r');
while ~feof(fid)
    % Read in each line of the file
    tline = fgetl(fid);
    % Obtain the names of videos for each camera for each footage set
    footage_set = textscan(tline,'%s','delimiter',',');
    videos = footage_set{1}
    % Iterate through each video, executing ball tracking algorithm upon it
    for idx = 1: size(videos,1)
        %{
        Step 1: Read in the test video
        %}
        disp('Reading in the current test video')
        % Retrieve the name of the current video
        vid_name = strcat(vid_dir,videos{idx})
        vid = VideoReader(vid_name);
        disp('Video read!')

        %{
        Step 2: Obtain common video attributes for subsequent use
        %}
        disp('Obtaining common video attributes for subsequent use')
        duration = vid.duration;
        pixel_height = vid.height;
        pixel_width = vid.width;
        framerate = vid.FrameRate;
        disp('Video attributes obtained!')

        %{
        Step 3: Get the background by averaging away the foreground (i.e. moving) objects.
        %}
        k = 1;
        avg = zeros(pixel_height, pixel_width);
        framecount = floor(duration*framerate)
        frames = cell(1,framecount);
        originals = frames;
        while hasFrame(vid)
            % Obtain the current frame of the video
            curr_frame = double(readFrame(vid));
            % Calculate the running average of the video
            avg = ((k-1)/k)*avg +(1/k)*curr_frame;
            % Save the frame for subsequent use
            frames{k} = curr_frame;
            % Increment proportion counter
            k = k + 1;
        end
        disp('Static Background is obtained!')

        %{
        Step 4: Subtract background from each frame of the video
        %}
        disp('Subtracting background from frame');
        % Convert frame to grayscale (i.e. black-to-white gradient)
        colormap('gray');
        [f_rows, f_cols] = size(frames);
        % Track the maximum difference per frame
        max_diffs = zeros(1,f_cols);
        for f_idx = 1: f_cols
            curr_frame = frames{f_idx};
            % Obtain the subtracted version of the current frame
            subtracted_frame = curr_frame - avg;
            % Store maximum difference detected for each frame
            max_diffs(f_idx) = max(subtracted_frame(:));
            % Replace frame with its corresponding difference matrix
            frames{f_idx} = subtracted_frame;
        end
        disp('Background removed!')
        
        %{
        SANITY CHECK! (Uncomment to run)
        Observe the distribution of noise after background subtraction
        %}
        %{
        for f_idx = 1: f_cols
            curr_frame = frames{f_idx};
            curr_frame(curr_frame < 0) = 0;
            % Retrieving scaled difference histograms
            diff_count = zeros(1,257);
            for row = 1 : pixel_height
                for col = 1 : pixel_width
                    diff = round(curr_frame(row,col));
                    diff_count(diff + 1) = diff_count(diff + 1) + 1;
                end
            end
            figD = figure('Visible','off');
            plot(diff_count);
            mkdir('./results/b_histograms/');
            baseName = strcat('./results/b_histograms/',num2str(f_idx));
            figName = strcat(baseName, '_diff_histogram.jpg');
            print(figD, '-djpeg', figName);
        end
        %}
        
        %{
        Step 5: Scale and reassign colour values according to extent of difference
        %}
        disp('Scaling and reassigning colour values according to extent of difference')
        % Compute the median maximum difference across all frames
        m_max_diff = max(max_diffs);
        for f_idx = 1: f_cols
            curr_frame = frames{f_idx};
            % Scale differences with respect to median max difference
            curr_frame = curr_frame./m_max_diff;
            % If difference ratio in the current frame exceed 1, reassign as 1
            curr_frame(curr_frame > 1) = 1;
            curr_frame = floor(curr_frame.*256);
            % Replace all values below threshold with colour value 0
            threshold = max(curr_frame(:))*0.80;
            curr_frame(curr_frame < threshold) = 0;
            % Replace frame with new difference scaled frame
            frames{f_idx} = curr_frame;
        end
        disp('Scaling and reassignment completed!')

        %{
        SANITY CHECK! (Uncomment to run)
        Observe the distribution of the colour values in the scaled frames.
        Since grayscale is used, and each difference is scaled to 256, hence,
        the higher the value/closer to 256, the more deviation from background
        the pixel was, implying that it is highly likely it makes up the ball!
        %}
        %{
        for f_idx = 1: f_cols
            curr_frame = frames{f_idx}; 
            % Retrieving scaled difference histograms
            colour_count = zeros(1,257);
            for row = 1 : pixel_height
                for col = 1 : pixel_width
                    colour_value = curr_frame(row,col);
                    colour_count(colour_value + 1) = colour_count(colour_value + 1) + 1;
                end
            end
            figH = figure('Visible','off');
            plot(colour_count);
            mkdir('./results/a_histograms/');
            baseName = strcat('./results/a_histograms/',num2str(f_idx));
            figName = strcat(baseName, '_scaled_histogram.jpg');
            print(figH, '-djpeg', figName);
        end
        %}

        %{
        Step 6: Extract the coordinates of non-zero pixels & perform clustering
        %}
        disp('Detecting the centroid of ball cluster...')
        coords = zeros(framecount,3);
        for f_idx = 1: f_cols
            curr_frame = frames{f_idx};
            % Find dimensions of current frame
            [y,x,rgb] = size(curr_frame);
            % Extract coordinates for non-zero values from current frame
            [nz_y, nz_x, nz_val] = find(curr_frame);
            % Account for RGB dimension for x-coordinates
            nz_x = mod(nz_x,x);
            % Create cluster data using coordinates(indexes) of non-zero pixels
            nz_coords = [nz_x nz_y];
            % Find optimal number of clusters for k-means clustering
            eva = evalclusters(nz_coords,'kmeans','silhouette','KList',1:5);
            opt_K = eva.OptimalK;
            % Error Catching
            if isnan(opt_K)
                opt_K = 1;
            end
            % Perform K-means clustering
            [index, C, sumd] = kmeans(nz_coords,opt_K);
            % Find sorted (via percentage) composition (i.e. how many datapoints) of each cluster
            sorted_composition = sortrows(tabulate(index),3,'descend');
            % Find the largest cluster (i.e. most likely to be from ball)
            ball_cluster = sorted_composition(1,1);
            % Retrieve centroid that represents the cluster
            ball_centroid = C(ball_cluster,:);
            % Save the coordinates of centroid
            coords(f_idx,1) = f_idx - 1;
            coords(f_idx,2) = ball_centroid(1);
            coords(f_idx,3) = ball_centroid(2);
        end
        disp('Centroid coordinates have been obtained!')

        %{
        Step 7: Export coordinates to file (.csv)
        %}
        disp('Exporting coordinates to CSV file')
        dirName = './results/';
        output_name = videos{idx}(1:end-4);
        baseName = strcat(dirName,output_name);
        outputFilePath = strcat(baseName,'.csv');
        fid = fopen(outputFilePath, 'w');
        colHeader = {'frame','x','y'};
        fprintf(fid, '%s,', colHeader{1:2});
        fprintf(fid, '%s\n', colHeader{3});
        fclose(fid);
        dlmwrite(outputFilePath, coords, '-append');
        disp('Export Completed!')
        
        %{
        Alternative algorithm that incorporates colour but is less precise
        %{
        Step 3: 
        Read and store each frame of the video for further processing
        %}
        framecount = floor(duration*framerate)
        f = 1;
        frames = cell(1,framecount);
        while hasFrame(vid)
            % Obtain the current frame of the video
            curr_frame = double(rgb2gray(readFrame(vid)));
            % Save the frame for subsequent use
            frames{f} = curr_frame;
            % Increment counter
            f = f + 1;
        end
        disp('Video frames obtained!')

        % Stating dimensions for subsequent reference
        [f_rows, f_cols] = size(frames)

        %{
        % Sanity Checking
        for f_idx = 1: f_cols
            curr_frame = frames{f_idx};
            imshow(uint8(curr_frame))
        end
        break
        %}    

        %{
        Step 4: 
        Keep only "white enough" colour values (since ball is white)
        %}
        disp('Selecting pixels with "white enough" colour values...');
        % Define colour threshold
        c_thres_low = 190;
        c_thres_high = 230;
        for f_idx = 1: f_cols
            % Obtain the current frame of the video
            curr_frame = frames{f_idx};
            % Remove all colours that are not "white enough"
            curr_frame(curr_frame < c_thres_low) = 0;
            % Remove all colours that "too white"
            curr_frame(curr_frame > c_thres_high) = 0;
            % Replace original frame with the colour filtered frame
            frames{f_idx} = curr_frame;
        end
        disp('Colour filtering complete!');

        %{
        % Sanity Checking
        for f_idx = 1: f_cols
            curr_frame = frames{f_idx};
            imshow(uint8(curr_frame))
        end
        break
        %}

        %{
        Step 5: 
        Removing unneccessary noise by iterating through background subtraction
        %}
        for i_count = 1: 10
            disp(strcat('Iteration no.: ', num2str(i_count)))

            %{
            Step 5a: 
            Get the background by averaging away the foreground (i.e. moving)
            objects.
            %}
            disp('Averaging away foreground to obtain background...')
            k = 1;
            avg = zeros(pixel_height, pixel_width);
            for f_idx = 1: f_cols
                % Obtain the current frame of the video
                curr_frame = frames{f_idx};
                % Calculate the running average of the video
                avg = ((k-1)/k)*avg +(1/k)*curr_frame;
                % Increment proportion counter
                k = k + 1;
            end
            disp('Static Background is obtained!')

            %{
            % Sanity Checking
            imshow(uint8(avg));
            break
            %}

            %{
            Step 5b: 
            Subtract background from each frame of the video
            %}
            disp('Subtracting background from frame...');
            % Track the maximum difference per frame
            max_diffs = zeros(1,f_cols);
            for f_idx = 1: f_cols
                curr_frame = frames{f_idx};
                % Obtain the subtracted version of the current frame
                subtracted_frame = curr_frame - avg;
                % Store maximum difference detected for each frame
                max_diff = max(subtracted_frame(:));
                max_diffs(f_idx) = max_diff;
                % Remove pixels that have differences below threshold
                threshold = max_diff*0.80;
                subtracted_frame(subtracted_frame < threshold) = 0;
                %{
                % For visualising the subtractions
                subtracted_frame = logical(subtracted_frame);
                frames{f_idx} = subtracted_frame.*curr_frame;
                %}
                % Replace frame with its corresponding subtracted frame
                frames{f_idx} = subtracted_frame;
            end
            disp('Background removed!')
        end

        %{
        % Sanity Checking
        for f_idx = 1: f_cols
            curr_frame = frames{f_idx};
            imshow(uint8(curr_frame))
        end
        break
        %}

        %{
        Step 6: 
        Scale and reassign colour values according to extent of difference
        %}
        disp('Scaling and reassigning colour values according to extent of difference')
        % Compute the maximum difference across all frames
        m_max_diff = max(max_diffs);
        for f_idx = 1: f_cols
            curr_frame = frames{f_idx};
            % Scale differences with respect to median max difference
            curr_frame = curr_frame./m_max_diff;
            curr_frame = floor(curr_frame.*256);

            % Replace all values below threshold with colour value 0
            threshold = max(curr_frame(:))*0.50;
            curr_frame(curr_frame < threshold) = 0;

            % Replace frame with new difference scaled frame
            frames{f_idx} = curr_frame;
        end
        disp('Scaling and reassignment completed!')

        %{
        % Sanity Checking
        for f_idx = 1: f_cols
            curr_frame = frames{f_idx};
            imshow(uint8(curr_frame))
        end
        break
        %}

        %{
        Step 7: Extract the coordinates of non-zero pixels & perform clustering
        %}
        disp('Detecting the centroid of ball cluster...')
        coords = zeros(framecount,3);
        %coords = table('frame','x','y'); % For formatting issues
        for f_idx = 1: f_cols
            curr_frame = frames{f_idx};
            % Find dimensions of current frame
            [y,x,rgb] = size(curr_frame);
            % Extract coordinates for non-zero values from current frame
            [nz_y, nz_x, nz_val] = find(curr_frame);
            % Account for RGB dimension for x-coordinates
            nz_x = mod(nz_x,x);
            % Create cluster data using coordinates(indexes) of non-zero pixels
            nz_coords = [nz_x nz_y];
            % Find optimal number of clusters for k-means clustering
            eva = evalclusters(nz_coords,'kmeans','silhouette','KList',1:5)
            opt_K = eva.OptimalK;
            if isnan(opt_K)
                opt_K = 1;
            end
            % Perform K-means clustering
            [index, C, sumd] = kmeans(nz_coords,opt_K);
            % Find sorted (via percentage) composition (i.e. how many datapoints) of each cluster
            sorted_composition = sortrows(tabulate(index),3,'descend');
            % Find the largest cluster (i.e. most likely to be from ball)
            ball_cluster = sorted_composition(1,1);
            % Retrieve centroid that represents the cluster
            ball_centroid = C(ball_cluster,:);
            % Save the coordinates of centroid
            coords(f_idx,1) = f_idx - 1;
            coords(f_idx,2) = ball_centroid(1);
            coords(f_idx,3) = ball_centroid(2);
        end
        disp('Centroid coordinates have been obtained!')
        %}
    end
end
%fclose(fid);

%diary off