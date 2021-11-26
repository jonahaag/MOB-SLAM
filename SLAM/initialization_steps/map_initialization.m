%% Map Initialization
load currI.mat
currI = uint8(currI);
% currI = initImages(currFrameIdx*viewerHeight+1:(currFrameIdx+1)*viewerHeight,:,:);

[currFeatures, currPoints] = helperDetectAndExtractFeatures(currI, scaleFactor, numLevels, intrinsics); 

currFrameIdx = currFrameIdx + 1;

% Find putative feature matches
indexPairs = matchFeatures(preFeatures, currFeatures, 'Unique', true, ...
    'MaxRatio', 0.9, 'MatchThreshold', 40);

preMatchedPoints  = prePoints(indexPairs(:,1),:);
currMatchedPoints = currPoints(indexPairs(:,2),:);

% If not enough matches are found, check the next frame
minMatches = 100;
if size(indexPairs, 1) < minMatches
    return
end

% Compute homography and evaluate reconstruction
[tformH, scoreH, inliersIdxH] = helperComputeHomography(preMatchedPoints, currMatchedPoints);

% Compute fundamental matrix and evaluate reconstruction
[tformF, scoreF, inliersIdxF] = helperComputeFundamentalMatrix(preMatchedPoints, currMatchedPoints);

% Select the model based on a heuristic
ratio = scoreH/(scoreH + scoreF);
ratioThreshold = 0.45;
if ratio > ratioThreshold
    inlierTformIdx = inliersIdxH;
    tform          = tformH;
else
    inlierTformIdx = inliersIdxF;
    tform          = tformF;
end

% Computes the camera location up to scale. Use half of the 
% points to reduce computation
inlierPrePoints  = preMatchedPoints(inlierTformIdx);
inlierCurrPoints = currMatchedPoints(inlierTformIdx);
[relOrient, relLoc, validFraction] = relativeCameraPose(tform, intrinsics, ...
    inlierPrePoints(1:2:end), inlierCurrPoints(1:2:end));

% If not enough inliers are found, move to the next frame
if validFraction < 0.9 || numel(size(relOrient))==3
    return
end

% Triangulate two views to obtain 3-D map points
relPose = rigid3d(relOrient, relLoc);
minParallax = 3; % In degrees
[isValid, xyzWorldPoints, inlierTriangulationIdx] = helperTriangulateTwoFrames(...
    rigid3d, relPose, inlierPrePoints, inlierCurrPoints, intrinsics, minParallax);

if ~isValid
    return
end

% Get the original index of features in the two key frames
indexPairs = indexPairs(inlierTformIdx(inlierTriangulationIdx),:);

isMapInitialized = true;

