AXIS_LENGTH = 5;

figure
Rs = getRs();
ts = getTs()

for camIdx = 1:3
    R = Rs{camIdx};
    t = ts{camIdx};
    [X, Y, Z] = getAxes(R, t);

    plot3(X(1, :), X(2, :), X(3, :), 'Color', 'Red');
    hold on
    plot3(Y(1, :), Y(2, :), Y(3, :), 'Color', 'Green');
    hold on
    plot3(Z(1, :), Z(2, :), Z(3, :), 'Color', 'Blue');
    hold on
end

% ================================================ Helper Functions ================================================

function Rs = getRs()
    Rs = cell(3);
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
    Rs{1} = R1; Rs{2} = R2; Rs{3} = R3;
end

function ts = getTs()
    ts = cell(3);
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
    ts{1} = t1; ts{2} = t2; ts{3} = t3;
end

function [X, Y, Z] = getAxes(R, t)
    X = getXAxis(R, t);
    Y = getYAxis(R, t);
    Z = getZAxis(R, t);
end

function X = getXAxis(R, t)
    unitVectorInWorldCoord = [1; 0; 0];
    X = getAxis(R, t, unitVectorInWorldCoord);
end

function Y = getYAxis(R, t)
    unitVectorInWorldCoord = [0; 1; 0];
    Y = getAxis(R, t, unitVectorInWorldCoord);
end

function Z = getZAxis(R, t)
    unitVectorInWorldCoord = [0; 0; 1];
    Z = getAxis(R, t, unitVectorInWorldCoord);
end

function W = getAxis(R, t, unitVectorInWorldCoord)
    delta = R * unitVectorInWorldCoord;
    W = [t, delta + t]
end
