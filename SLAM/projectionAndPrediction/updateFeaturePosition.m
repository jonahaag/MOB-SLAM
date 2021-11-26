function vSetKeyFrames = updateFeaturePosition(mapPoints, vSetKeyFrames, currKeyFrameId, intrinsics, Irgb)
% get indices of map points and corresponding features of the current frame
[index3d, index2d] = findWorldPointsInView(mapPoints, currKeyFrameId);
% get updated position of the 3d world points and current camera pose 
xyzPoints = mapPoints.WorldPoints(index3d,:);
views = vSetKeyFrames.Views;
currPose = views.AbsolutePose(currKeyFrameId); % does this already exist in the workspace of main_loop2?
% get the initial orb feature points
currPoints = views.Points{currKeyFrameId};
newPoints = currPoints;
% features2 = getFeatures(directionAndDepth, views, mapPointsIdx);

% compute new 2d image points based on updated 3d position
[isInImage, newImagePoints] = helperFindProjectedPointsInImage(...
    xyzPoints, currPose, intrinsics, intrinsics.ImageSize);
isInImage = find(isInImage); % this might be unnecessary 
index2d = index2d(isInImage);
% update the location of the orb points
newPoints.Location(index2d,:) = newImagePoints(isInImage,:);
% scale, metric, orientation??
% vSetKeyFrames = updateView(vSetKeyFrames, currKeyFrameId, 'Points', newPoints);

% % convert the image to greyscale
Igray  = rgb2gray(Irgb);
% % Extract features descriptor based on new feature location
[newFeatures, validPoints] = extractFeatures(Igray, newPoints, 'Method', 'ORB');
newFeatures = newFeatures.Features;
% % update vSetKeyFrames 
if newPoints.Count == validPoints.Count
    vSetKeyFrames = updateView(vSetKeyFrames, currKeyFrameId, 'Features', newFeatures,...
        'Points', validPoints);
else
    id = find(~ismember(newPoints.Location,validPoints.Location,'rows'));
    newFeatures2 = uint8(zeros(1000,32));
    oldFeatures = views.Features(currKeyFrameId);
    oldFeatures = oldFeatures{1}(id,:);
%     oldDataInd = (1:size(newFeatures,1)) + cumsum([0, id(1:end-1)]);
    for i = 1:length(id)+1
        if i == 1
            a = 1;
            b = id(i)-1;
        elseif i == length(id)+1
            a = id(i-1)+1;
            b = length(newFeatures2);
        else
            a = id(i-1)+1;
            b = id(i)-1;
        end
        newFeatures2(a:b,:) = newFeatures(a-(i-1):b-(i-1),:);
        if i <= length(id)
            newFeatures2(id(i),:) = oldFeatures(i,:);
        end
    end

%     newFeatures = [newFeatures(1:id-1,:); oldFeatures{1}(id,:); newFeatures(id:end,:)];
%     newFeatures2 = zeros(1000,32);
%     addRows = ismember(1:size(newFeatures,1), id);
%     oldDataInd = (1:size(newFeatures,1)) + cumsum([0, addRows(1:end-1)]);
%     newFeatures2(oldDataInd,:) = newFeatures(:,:);
%     newDataInd = (1:length(id)) + id;
    
    vSetKeyFrames = updateView(vSetKeyFrames, currKeyFrameId, 'Features', newFeatures2,...
        'Points', newPoints);
%     a = 0;
% end
% updateConnection??

end
end


function features = getFeatures(directionAndDepth, views, mapPointIdx)

% Efficiently retrieve features and image points corresponding to map points
% denoted by mapPointIdx
allIndices = zeros(1, numel(mapPointIdx));

% ViewId and offset pair
count = []; % (ViewId, NumFeatures)
viewsFeatures = views.Features;
majorViewIds  = directionAndDepth.MajorViewId;
majorFeatureindices = directionAndDepth.MajorFeatureIndex;

for i = 1:numel(mapPointIdx)
    index3d  = mapPointIdx(i);
    
    viewId   = double(majorViewIds(index3d));
    
    if isempty(count)
        count = [viewId, size(viewsFeatures{viewId},1)];
    elseif ~any(count(:,1) == viewId)
        count = [count; viewId, size(viewsFeatures{viewId},1)];
    end
    
    idx = find(count(:,1)==viewId);
    
    if idx > 1
        offset = sum(count(1:idx-1,2));
    else
        offset = 0;
    end
    allIndices(i) = majorFeatureindices(index3d) + offset;
end

uIds = count(:,1);

% Concatenating features and indexing once is faster than accessing via a for loop
allFeatures = vertcat(viewsFeatures{uIds});
features    = allFeatures(allIndices, :);
end