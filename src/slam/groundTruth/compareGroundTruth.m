%% Compare sofa ground truth with slam trajectory
% load ground truth
% transform ground truth into slam coordinates
% update plot based on trajectory (scale..)

load('groundTruth/groundTruth.mat');
% compute transformation if too few key frames 
if currKeyFrameId < 5
    H_sofa2slam = computeTransformation(sofaGroundTruth_pos);
end
sofaGroundTruth_pos_slam = transformSofa2Slam(sofaGroundTruth_pos, H_sofa2slam);


% [mapPointSet, vSetKeyFrames] = scaleMap(mapPointSet, vSetKeyFrames, scale, currKeyFrameId);
% % Visualize 3D world points and camera trajectory
% updatePlot(mapPlot, vSetKeyFrames, mapPointSet);

%% Evaluate tracking accuracy
% % compute scale factor 
scale1 = computeScale(vSetKeyFrames,sofaGroundTruth_pos_slam);
sofaGroundTruth_pos_slam1 = sofaGroundTruth_pos_slam/scale1;

% tweaked_helperEstsmateTrajectoryError(sofaGroundTruth_pos_slam, poses(vSetKeyFrames));
% tweaked_helperEstimateTrajectoryError(sofaGroundTruth_pos_slam, optimizedPoses);
cameraPoses = poses(vSetKeyFrames);
locations       = vertcat(cameraPoses.AbsolutePose.Translation);
rmse1 = sqrt(mean( sum((locations - sofaGroundTruth_pos_slam1).^2, 2) ));

sofaGroundTruth_pos_slam2 = sofaGroundTruth_pos_slam/scale;
rmse2 = sqrt(mean( sum((locations - sofaGroundTruth_pos_slam2).^2, 2) ));

if rmse1 < rmse2
    sofaGroundTruth_pos_slam = sofaGroundTruth_pos_slam1;
    %disp(['Absolute RMSE for key frame trajectory (m): ', num2str(rmse1)]);
else
    sofaGroundTruth_pos_slam = sofaGroundTruth_pos_slam2;
    %disp(['Absolute RMSE for key frame trajectory (m): ', num2str(rmse2)]);
end

%% Plot the actual camera trajectory
%plot3(mapPlot.Axes, sofaGroundTruth_pos_slam(:,1), sofaGroundTruth_pos_slam(:,2), sofaGroundTruth_pos_slam(:,3), ...
%                'g','LineWidth',2, 'DisplayName', 'Actual trajectory');
% Show legend
%showLegend(mapPlot);

