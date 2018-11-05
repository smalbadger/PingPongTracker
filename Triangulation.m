% Set constants
N_CAMERAS = 3;
INTRINSIC_MATRICES = get_intrinsic_matrices();
ROTATION_MATRICES = get_rotation_matrices();
TRANSLATION_VECTORS = get_translation_vectors();

% Read 2D data from file

% Process 2D to 3D

% Write 3D data to file

% ================================================ Helper Functions ================================================
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
