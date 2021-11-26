%% Load image
load currI.mat
currI = uint8(currI);

%% forward prediction
% forward predict projected points at each slam step, not just at key
% frames
if currKeyFrameId == minNumberOfKeyframesBeforeScaling-1
    % comp~ute the transformation between sofa and slam coordinates
    load('groundTruth/groundTruth.mat');
    H_sofa2slam = computeTransformation(sofaGroundTruth_pos);
    sofaGroundTruth_pos_slam = transformSofa2Slam(sofaGroundTruth_pos, H_sofa2slam);
    stlData = readAndTransformSTL(H_sofa2slam,'../mesh/blender_ellipsoid.stl', scale);
    previousNodePositions = stlData.Points;
end
if  doProjections && currKeyFrameId >= minNumberOfKeyframesBeforeProjection-1
    % load and transform the current ground truth (TODO just at every
    % keyframe, not needed at all once H_sofa2slam is initialized)
    load('groundTruth/groundTruth.mat');
    sofaGroundTruth_pos_slam = transformSofa2Slam(sofaGroundTruth_pos, H_sofa2slam);
    % load and transform the current position of the simulation nodes,
    % scale down
    load('currentNodePositions.mat')
    currentNodePositions = transformSofa2Slam(currentNodePositions, H_sofa2slam);
    currentNodePositions = currentNodePositions/scale;
    diffNodePositions = sum(vecnorm(currentNodePositions-previousNodePositions,2,2));
    if  projectionInitialized && diffNodePositions > 1e-15
        predictionIndices = find(projectedPointSet.IsProjected);
        mapPointSet = forwardPrediction(mapPointSet, projectedPointSet, currentNodePositions, predictionIndices);
        previousNodePositions = currentNodePositions;
%         vSetKeyFrames = updateFeaturePosition(mapPointSet, vSetKeyFrames,...
%             currKeyFrameId, intrinsics, currKeyImage);
    end
end

%% Tracking
[currFeatures, currPoints] = helperDetectAndExtractFeatures(currI, scaleFactor, numLevels, intrinsics);

% Track the last key frame
% mapPointsIdx:   Indices of the map points observed in the current frame
% featureIdx:     Indices of the corresponding feature points in the 
%                 current frame
[currPose, mapPointsIdx, featureIdx] = helperTrackLastKeyFrame(mapPointSet, ...
    vSetKeyFrames.Views, currFeatures, currPoints, lastKeyFrameId, intrinsics, scaleFactor);

% Track the local map
% refKeyFrameId:      ViewId of the reference key frame that has the most 
%                     co-visible map points with the current frame
% localKeyFrameIds:   ViewId of the connected key frames of the current frame
[refKeyFrameId, localKeyFrameIds, currPose, mapPointsIdx, featureIdx] = ...
    helperTrackLocalMap(mapPointSet, directionAndDepth, vSetKeyFrames, mapPointsIdx, ...
    featureIdx, currPose, currFeatures, currPoints, intrinsics, scaleFactor, numLevels);

% Check if the current frame is a key frame. 
% A frame is a key frame if both of the following conditions are satisfied:
%
% 1. At least 20 frames have passed since the last key frame or the 
%    current frame tracks fewer than 80 map points
% 2. The map points tracked by the current frame are fewer than 90% of 
%    points tracked by the reference key frame
isKeyFrame = helperIsKeyFrame(mapPointSet, refKeyFrameId, lastKeyFrameIdx, ...
    currFrameIdx, mapPointsIdx);
% Visualize matched features
% updatePlot(featurePlot, currI, currPoints(featureIdx));

if ~isKeyFrame
    currFrameIdx = currFrameIdx + 1;
    return
end

% Update current key frame ID
currKeyFrameId  = currKeyFrameId + 1;

