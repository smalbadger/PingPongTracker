% Import external function
addpath('./lineIntersect3D');

% Set output FOLDER
OUTPUT_PATH = './triangulation_output/';

% Read File List
FILE_LIST_NAME = 'FileList.csv';
[num, FILE_VIDEO_LIST] = xlsread(FILE_LIST_NAME);
FILE_ANNOTATION_LIST = getFileAnnotationList(FILE_VIDEO_LIST);

% Camera Properties
N_TRAJECTORIES = size(FILE_ANNOTATION_LIST, 1);
N_CAMERAS = size(FILE_ANNOTATION_LIST, 2);
INTRINSIC_MATRICES = getInstrinsicMatrices();
Rs = getRs();
ts = getTs();

% Constants for reading from file
COL_NUM_FRAME = 1;
COL_NUM_U = 2;
COL_NUM_V = 3;
COL_NUM_UNDISTORT_U = 4;
COL_NUM_UNDISTORT_V = 5;

% Constants for writing to file
COL_NUM_FRAME = 1;
COL_NUM_X = 2;
COL_NUM_Y = 3;
COL_NUM_Z = 4;

figure
drawCamAxis();

for trajectoryIdx = 1:N_TRAJECTORIES
    % for trajectoryIdx = 1 : 1
    % Read 2D data from file
    camFile1 = FILE_ANNOTATION_LIST{trajectoryIdx, 1};
    camFile2 = FILE_ANNOTATION_LIST{trajectoryIdx, 2};
    camFile3 = FILE_ANNOTATION_LIST{trajectoryIdx, 3};
    [data1, text] = xlsread(camFile1);
    [data2, text] = xlsread(camFile2);
    [data3, text] = xlsread(camFile3);

    nRows = size(data1, 1);
    result = zeros(nRows, 4);
    colHeader = {'frame', 'x', 'y', 'z'};

    for rowIdx = 1:nRows
        frameData1 = data1(rowIdx, :);
        frameData2 = data2(rowIdx, :);
        frameData3 = data3(rowIdx, :);
        frame = data1(rowIdx);

        % Don't process if any coord pt is not defined
        if (any(isnan(frameData1), 2) || any(isnan(frameData2), 2) || any(isnan(frameData3), 2))
            result(rowIdx, :) = [frame, NaN, NaN, NaN];
            continue
        end

        dirToImg1 = getDirectionToImagePt(frameData1(COL_NUM_U), frameData1(COL_NUM_V), INTRINSIC_MATRICES{1});
        imgCoord1 = getImageCoord(Rs{1}, ts{1}, dirToImg1);

        dirToImg2 = getDirectionToImagePt(frameData2(COL_NUM_U), frameData2(COL_NUM_V), INTRINSIC_MATRICES{2});
        imgCoord2 = getImageCoord(Rs{2}, ts{2}, dirToImg2);

        dirToImg3 = getDirectionToImagePt(frameData3(COL_NUM_U), frameData3(COL_NUM_V), INTRINSIC_MATRICES{3});
        imgCoord3 = getImageCoord(Rs{3}, ts{3}, dirToImg3);

        startPoints = [ts{1}.'; ts{2}.'; ts{3}.'; ];
        endPoints = [imgCoord1.'; imgCoord2.'; imgCoord3.'; ];
        vectors = endPoints - startPoints;

        intersectionPt = lineIntersect(startPoints, vectors);

        result(rowIdx, :) = [frame, intersectionPt];
    end

    comet3(result(:, 2), result(:, 3), result(:, 4));
    output = [colHeader; num2cell(result)];
    outputFilePath = strcat(OUTPUT_PATH, extractAfter(camFile1, '/'));

    fid = fopen(outputFilePath, 'w');
    fprintf(fid, '%s,', colHeader{1:3});
    fprintf(fid, '%s\n', colHeader{4});
    fclose(fid);
    dlmwrite(outputFilePath, result, '-append');

    % Write 3D data to file
end

function intersectionPt = lineIntersect(startPoints, vectors)
    M = zeros(6, 3);
    D = zeros(6, 1);
    for idx = 1 : 3
        vector = vectors(idx, :);
        startPt = startPoints(idx, :);
        a = vector(1);
        b = vector(2);
        c = vector(3);
        d = startPt(1);
        e = startPt(2);
        f = startPt(3);
        M(idx, :) = [b, -a, 0];
        M(2 * idx, :) = [c, 0, -a];
        D(idx) = b * d - a * e;
        D(idx * 2) = c * d - a * f;
    end
    intersectionPt = inv(M.' * M) * M.' * D;
    intersectionPt = intersectionPt.';
end

% ================================================ Helper Functions ================================================

% Returns corresponding 2D data file locations from File List
function FILE_ANNOTATION_LIST = getFileAnnotationList(FILE_VIDEO_LIST)
    FILE_ANNOTATION_LIST = cell(size(FILE_VIDEO_LIST));

    for fileIdx = 1:numel(FILE_VIDEO_LIST)
        baseName = FILE_VIDEO_LIST{fileIdx}(1:find(FILE_VIDEO_LIST{fileIdx} == '.') - 1);
        prefix = 'Annotation/';
        fileType = '.csv';

        FILE_ANNOTATION_LIST{fileIdx} = strcat(prefix, baseName, fileType);
    end

end

function INTRINSIC_MATRICES = getInstrinsicMatrices()
    INTRINSIC_MATRIX_CAMERA_1 = [
                                870.14531487461625, 0, 949.42001822880479;
                                0, 870.14531487461625, 487.20049852775117;
                                0, 0, 1;
                                ];
    INTRINSIC_MATRIX_CAMERA_2 = [
                                870.14531487461625, 0, 949.42001822880479;
                                0, 870.14531487461625, 487.20049852775117;
                                0, 0, 1;
                                ];
    INTRINSIC_MATRIX_CAMERA_3 = [
                                870.14531487461625, 0, 949.42001822880479;
                                0, 870.14531487461625, 487.20049852775117;
                                0, 0, 1;
                                ];
    INTRINSIC_MATRICES = {INTRINSIC_MATRIX_CAMERA_1, INTRINSIC_MATRIX_CAMERA_2, INTRINSIC_MATRIX_CAMERA_3};
end

function Rs = getRs()
    R1 = [

        .96428667991264605, -.26484969138677328, -.0024165916859785336;
        -.089795446022112396, -.31832382771611223, -.94371961862719200;
        .24917459103354755, .91023325674273947, -.33073772313234923;
        ];
    R2 = [
        .94962278945631540, .31338395965783683, -.0026554800661627576;
        .115468564899954271, -.35774736713426591, -.92665194751235791;
        -.29134784753821596, .87966318277945221, -.37591104878304971;
        ];
    R3 = [
        -.99541881789113029, .038473906154401757, -.087527912881817604;
        .091201836523849486, .65687400820094410, -.74846426926387233;
        .028698466908561492, -.75301812454631367, -.65737363964632056;
        ];
    Rs = {R1, R2, R3};
end

% TODO: CORRECT TRANSLATION VECTORS
function ts = getTs()
    t1 = [
        .13305621037591506;
        -.25319578738559911;
        2.2444637695699150;
        ];

    t2 = [
        -.042633372670025989;
        -.35441906393933242;
        2.2750378317324982;
        ];

    t3 = [
        -.060451734755080713;
        -.39533167111966377;
        2.2979640654841407;
        ];

    % As stated in the email, need to change to correct translation matrix
    Rs = getRs();
    t1 = -inv(Rs{1}) * t1;
    t2 = -inv(Rs{2}) * t2;
    t3 = -inv(Rs{3}) * t3;
    ts = {t1, t2, t3};
end

% Returns direction vector to image point relative to camera coord
function dirToImg = getDirectionToImagePt(u, v, intrinsicMatrix)
    dirToImg = inv(intrinsicMatrix) * [u; v; 1];
end

% Returns coordinates of image point relative to real world coordinates
function imgCoord = getImageCoord(R, t, dirToImg)
    imgCoord = t + inv(R) * dirToImg;
end

function drawCamAxis()
    ts = getTs();
    Rs = getRs();

    for idx = 1:3
        R = Rs{idx};
        t = ts{idx};
        point1 = R(1, :) + t.';
        point2 = R(2, :) + t.';
        point3 = R(3, :) + t.';
        origin = t.';
        hold on;
        plot3([origin(1) point1(1)], [origin(2) point1(2)], [origin(3) point1(3)], 'LineWidth', 5, 'Color', 'red');
        plot3([origin(1) point2(1)], [origin(2) point2(2)], [origin(3) point2(3)], 'LineWidth', 5, 'Color', 'green');
        plot3([origin(1) point3(1)], [origin(2) point3(2)], [origin(3) point3(3)], 'LineWidth', 5, 'Color', 'blue');
        grid on;
        xlabel('X');
        ylabel('Y');
        zlabel('Z');
        set(gca, 'CameraPosition', [2 2 2]);
        text(t(1), t(2), t(3), strcat('CAM ', num2str(idx)));
        hold on
    end

end
