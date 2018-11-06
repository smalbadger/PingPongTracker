% Import external function
addpath('./lineIntersect3D');

% Set output FOLDER
OUTPUT_PATH = './triangulation_output/';

% Read File List
FILE_LIST_NAME = 'FileList.csv';
[num, FILE_VIDEO_LIST] = xlsread(FILE_LIST_NAME);
FILE_ANNOTATION_LIST = get_file_annotation_list(FILE_VIDEO_LIST);

% Set CAMERA constants
N_TRAJECTORIES = size(FILE_ANNOTATION_LIST, 1);
N_CAMERAS = size(FILE_ANNOTATION_LIST, 2);
INTRINSIC_MATRICES = get_intrinsic_matrices();
ROTATION_MATRICES = get_rotation_matrices();
TRANSLATION_VECTORS = get_translation_vectors();

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

% for trajectoryIdx = 1 : N_TRAJECTORIES
for trajectoryIdx = 1:1
    % Read 2D data from file
    cam_file_1 = FILE_ANNOTATION_LIST{trajectoryIdx, 1};
    cam_file_2 = FILE_ANNOTATION_LIST{trajectoryIdx, 2};
    cam_file_3 = FILE_ANNOTATION_LIST{trajectoryIdx, 3};
    [data_1, text] = xlsread(cam_file_1);
    [data_2, text] = xlsread(cam_file_2);
    [data_3, text] = xlsread(cam_file_3);

    nRows = size(data_1, 1)
    result = zeros(nRows, 4);

    for rowIdx = 1:nRows
        frameData1 = data_1(rowIdx, :);
        frameData2 = data_2(rowIdx, :);
        frameData3 = data_3(rowIdx, :);
        frame = data_1(rowIdx);

        % Don't process if any coord pt is not defined
        if (any(isnan(frameData1), 2) || any(isnan(frameData2), 2) || any(isnan(frameData3), 2))
            result(rowIdx, :) = [frame, NaN, NaN, NaN];
            continue
        end

        dirToImg1 = get_direction_to_image_pt(frameData1(COL_NUM_UNDISTORT_U), frameData1(COL_NUM_UNDISTORT_V), INTRINSIC_MATRICES{1})
        imgCoord1 = get_image_coord(ROTATION_MATRICES{1}, TRANSLATION_VECTORS{1}, dirToImg1);

        dirToImg2 = get_direction_to_image_pt(frameData2(COL_NUM_UNDISTORT_U), frameData2(COL_NUM_UNDISTORT_V), INTRINSIC_MATRICES{2})
        imgCoord2 = get_image_coord(ROTATION_MATRICES{2}, TRANSLATION_VECTORS{2}, dirToImg2);

        dirToImg3 = get_direction_to_image_pt(frameData3(COL_NUM_UNDISTORT_U), frameData3(COL_NUM_UNDISTORT_V), INTRINSIC_MATRICES{3})
        imgCoord3 = get_image_coord(ROTATION_MATRICES{3}, TRANSLATION_VECTORS{3}, dirToImg3);

        startPoints = [TRANSLATION_VECTORS{1}.'; TRANSLATION_VECTORS{2}.'; TRANSLATION_VECTORS{3}.'; ];
        endPoints = [imgCoord1.'; imgCoord2.'; imgCoord3.';];

        [P_intersect,distances] = lineIntersect3D(startPoints, endPoints);

        result(rowIdx, :) = [ frame , P_intersect];
    end
    result

    % Write 3D data to file
end

% ================================================ Helper Functions ================================================

% Returns corresponding 2D data file locations from File List
function FILE_ANNOTATION_LIST = get_file_annotation_list(FILE_VIDEO_LIST)
    FILE_ANNOTATION_LIST = cell(size(FILE_VIDEO_LIST));

    for fileIdx = 1:numel(FILE_VIDEO_LIST)
        baseName = FILE_VIDEO_LIST{fileIdx}(1:find(FILE_VIDEO_LIST{fileIdx} == '.') - 1);
        prefix = 'Annotation/';
        fileType = '.csv';

        FILE_ANNOTATION_LIST{fileIdx} = strcat(prefix, baseName, fileType);
    end

end

function INTRINSIC_MATRICES = get_intrinsic_matrices()
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

function ROTATION_MATRICES = get_rotation_matrices()
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
    ROTATION_MATRICES = {R1, R2, R3};
end

% TODO: CORRECT TRANSLATION VECTORS
function TRANSLATION_VECTORS = get_translation_vectors()
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
    TRANSLATION_VECTORS = {t1, t2, t3};
end

function focal_length = get_focal_length(intrinsic_matrix_camera)
    focal_length = intrinsic_matrix_camera(1, 1);
end

% Returns direction vector to image point relative to camera coord
function dirToImg = get_direction_to_image_pt(u, v, intrinsicMatrix)
    dirToImg = inv(intrinsicMatrix) * [u; v; 1];
end

% Returns coordinates of image point relative to real world coordinates
function imgCoord = get_image_coord(R, t, dirToImg)
    imgCoord = t + inv(R) * dirToImg;
end
