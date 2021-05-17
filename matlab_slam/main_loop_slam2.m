%% Local Mapping
% Add the new key frame
[mapPointSet, vSetKeyFrames] = helperAddNewKeyFrame(mapPointSet, vSetKeyFrames, ...
    currPose, currFeatures, currPoints, mapPointsIdx, featureIdx, localKeyFrameIds);

% Remove outlier map points that are observed in fewer than 3 key frames
[mapPointSet, directionAndDepth, mapPointsIdx, outlierIdx] = helperCullRecentMapPoints(mapPointSet, directionAndDepth, mapPointsIdx, newPointIdx);

% update projectedPointSet accordingly
if projectionInitialized
    projectedPointSet = removeProjectedPoints(projectedPointSet, outlierIdx);
end

%% Create new map points by triangulation
minNumMatches = 20;
minParallax = 3;
if projectionInitialized
    [mapPointSet, vSetKeyFrames, newPointIdx] = helperCreateNewMapPoints(mapPointSet, vSetKeyFrames, ...
    currKeyFrameId, intrinsics, scaleFactor, minNumMatches, minParallax);
    
    projectedPointSet = addProjectedPoints(projectedPointSet, newPointIdx);
    
        % Update view direction and depth
%     directionAndDepth = update(directionAndDepth, mapPointSet, vSetKeyFrames.Views, [mapPointsIdx; newPointIdx], true);

    % Local bundle adjustment
%     [mapPointSet, directionAndDepth, vSetKeyFrames, newPointIdx, projectedPointSet] = ProjectedHelperLocalBundleAdjustment(mapPointSet, directionAndDepth, vSetKeyFrames, ...
%         currKeyFrameId, intrinsics, newPointIdx, projectedPointSet);
else
    [mapPointSet, vSetKeyFrames, newPointIdx] = helperCreateNewMapPoints(mapPointSet, vSetKeyFrames, ...
    currKeyFrameId, intrinsics, scaleFactor, minNumMatches, minParallax);

    directionAndDepth = update(directionAndDepth, mapPointSet, vSetKeyFrames.Views, [mapPointsIdx; newPointIdx], true);
    
    [mapPointSet, directionAndDepth, vSetKeyFrames, newPointIdx] = helperLocalBundleAdjustment(mapPointSet, directionAndDepth, vSetKeyFrames, ...
        currKeyFrameId, intrinsics, newPointIdx);
end

%% Scale and rescale
% if currKeyFrameId >= minNumberOfKeyframesBeforeScaling
%     % get the scale and decide whether to rescale or not
%     scale_new = computeScale(vSetKeyFrames,sofaGroundTruth_pos_slam);
%     scale_ratio = scale/scale_new;
%     epsilon_scale = 1.25;
%     if scale_ratio >= epsilon_scale || scale_ratio <= 1/epsilon_scale
%         disp(['Rescale at key frame ',num2str(currKeyFrameId)])
%         scale = scale_new;
%         [mapPointSet, vSetKeyFrames] = scaleMap(mapPointSet, vSetKeyFrames, scale, currKeyFrameId);
%     end
% end

%% Projection and prediction
if  doProjections && currKeyFrameId >= minNumberOfKeyframesBeforeProjection
    % If enough key frames have passed project
    if ~projectionInitialized
        % project map points
        projectedPointSet = struct('BarycentricCoordinates', zeros(mapPointSet.Count,3), ...
                                   'IsProjected', zeros(mapPointSet.Count,1),...
                                   'TrianglePointIdx', zeros(mapPointSet.Count,3),...
                                   'ViewId', zeros(mapPointSet.Count,1),...
                                   'ViewsTried', zeros(mapPointSet.Count,1),...
                                   'ProjectionAngle', zeros(mapPointSet.Count,1),...
                                   'NumberOfPointsConsidered', mapPointSet.Count);
        projectionIndices = 1:mapPointSet.Count;
        tic
        [mapPointSet, projectedPointSet, unprojectedIndices] = projectMapPoints(projectedPointSet, mapPointSet, ...
            stlData, projectionIndices, vSetKeyFrames, currentNodePositions, directionAndDepth);
        toc
%         [projectedPointSet, mapPointSet, directionAndDepth, newPointIdx] = removeUnprojectedPoints(projectedPointSet,...
%             mapPointSet, directionAndDepth, unprojectedIndices, newPointIdx);
        projectionInitialized = 1;
    else
        % find points in view
        % add projection for the new points (those should just have one
        % view, the current one - or three??)
        predictionIndices = find(projectedPointSet.IsProjected);
        [mapPointSet, projectedPointSet, unprojectedIndices] = projectMapPoints(projectedPointSet, mapPointSet, ...
            stlData, newPointIdx, vSetKeyFrames, currentNodePositions, directionAndDepth);
%         [projectedPointSet, mapPointSet, directionAndDepth, newPointIdx] = removeUnprojectedPoints(projectedPointSet,...
%             mapPointSet, directionAndDepth, unprojectedIndices, newPointIdx);
        mapPointSet = forwardPrediction(mapPointSet, projectedPointSet, currentNodePositions, predictionIndices);
    end
    a = numel(find(projectedPointSet.IsProjected));
    b = projectedPointSet.NumberOfPointsConsidered;
    c = mapPointSet.Count;
    disp(['Currently ',num2str(a),' out of ', num2str(c),' points are projected'])
    if b ~= c 
        disp(['Size mismatch between MapPointSet (',num2str(c),...
            ') and projectedPointSet (',num2str(b),')'])
    
    else
       disp(['Sizes fit, length: ', num2str(b)]) 
    end
    % update feature positions of all points visible in the current frame
    vSetKeyFrames = updateFeaturePosition(mapPointSet, vSetKeyFrames,...
        currKeyFrameId, intrinsics, currI);
    % Update view direction and depth
    directionAndDepth = update(directionAndDepth, mapPointSet, vSetKeyFrames.Views, [mapPointsIdx; newPointIdx], true);
end



%%  Visualize 3D world points and camera trajectory
updatePlot(mapPlot, vSetKeyFrames, mapPointSet);

%% Loop Closure
% % Initialize the loop closure database
% if currKeyFrameId == 3
%     % Load the bag of features data created offline
%     bofData         = load('bagOfFeaturesData.mat');
%     loopDatabase    = invertedImageIndex(bofData.bof);
%     loopCandidates  = [1; 2];
% 
% % Check loop closure after some key frames have been created    
% elseif currKeyFrameId > 20
% 
%     % Minimum number of feature matches of loop edges
%     loopEdgeNumMatches = 50;
% 
%     % Detect possible loop closure key frame candidates
%     [isDetected, validLoopCandidates] = helperCheckLoopClosure(vSetKeyFrames, currKeyFrameId, ...
%         loopDatabase, currI, loopCandidates, loopEdgeNumMatches);
% 
%     if isDetected 
%         % Add loop closure connections
%         [isLoopClosed, mapPointSet, vSetKeyFrames] = helperAddLoopConnections(...
%             mapPointSet, vSetKeyFrames, validLoopCandidates, currKeyFrameId, ...
%             currFeatures, currPoints, intrinsics, scaleFactor, loopEdgeNumMatches);
%     end
% end
% % If no loop closure is detected, add the image into the database
% path = ['keyframes/frame_',num2str(currKeyFrameId),'.jpg'];
% imwrite(currI,path);
% if ~isLoopClosed
%     currds = imageDatastore(path);
%     addImages(loopDatabase, currds, 'Verbose', false);
%     loopCandidates= [loopCandidates; currKeyFrameId]; 
% end

%% Update IDs and indices
lastKeyFrameId  = currKeyFrameId;
lastKeyFrameIdx = currFrameIdx;
addedFramesIdx  = [addedFramesIdx; currFrameIdx]; 
currFrameIdx  = currFrameIdx + 1;
currKeyImage = currI;

