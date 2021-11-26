function [mapPointSet, vSetKeyFrames] = scaleMap(mapPointSet, vSetKeyFrames, scale, currKeyFrameId) 
    indices = 1:mapPointSet.Count;
    newPositions = mapPointSet.WorldPoints * scale;
    mapPointSet = updateWorldPoints(mapPointSet, indices, newPositions);
%     for i = 1:mapPointSet.Count
%        mapPointSet = updateWorldPoints(mapPointSet, i, newPositions(i,:)); 
%     end

    newPoses = poses(vSetKeyFrames);
    newTranslations = vertcat(newPoses.AbsolutePose.Translation) * scale;
    for i = 1:currKeyFrameId
        newPose = rigid3d(newPoses.AbsolutePose(i,1).Rotation,newTranslations(i,:));
        vSetKeyFrames = updateView(vSetKeyFrames, i, newPose);
    end
    
    % ind = (1:mapPointSet.Count)';
    % directionAndDepth = update(directionAndDepth, mapPointSet, vSetKeyFrames.Views, ind, true);

    % % Local bundle adjustment
    % [mapPointSet, directionAndDepth, vSetKeyFrames, newPointIdx] = helperLocalBundleAdjustment(mapPointSet, directionAndDepth, vSetKeyFrames, ...
    %     currKeyFrameId, intrinsics, newPointIdx); 
end

