function indexPairs = helperMatchFeaturesInRadius(features1, features2, ...
    projectedPoints1, points2, radius, minScales, maxScales)
%helperMatchFeaturesInRadius Match features within a radius 
%   indexPairs = helperMatchFeaturesInRadius(feature1, feature2,
%   projectedPoints1, points2, radius, minScales, maxScales) returns a 
%   P-by-2 matrix, indexPairs, containing the indices to the features most
%   likely to correspond between the two input feature matrices satisfying
%   the distance and the scale constraints. 
%
%   This is an example helper function that is subject to change or removal 
%   in future releases.
%
%   Inputs
%   ------
%   features1              - Feature matrices in the first image
%   features2              - Feature matrices in the second image
%   projectedPoints1       - The projection of the world points in the 
%                            second image that correspond to features1
%   points2                - Feature points corresponding to features2
%   radius                 - Searching radius
%   minScales              - Minimum scales of feature points points1  
%   maxScales              - Maximum scales of feature points points1
%
%   Output
%   ------
%   indexPairs             - Indices of corresponding features 

%   Copyright 2019-2020 The MathWorks, Inc.

matchThreshold = 100;
maxRatio       = 0.8;

numPoints      = size(projectedPoints1, 1);
indexPairs     = zeros(numPoints, 2, 'uint32');
neighborScales = points2.Scale;
neighborPoints = points2.Location;

if isscalar(radius)
    radius = radius * ones(numPoints, 1);
end

for i = 1: numPoints
    % Find points within a radius subjected to the scale constraint
    pointIdx = findPointsInRadius(neighborPoints, projectedPoints1(i,:), ...
        radius(i), neighborScales, minScales(i), maxScales(i));
    
    if ~isempty(pointIdx)
        centerFeature   = features1(i,:);
        nearbyFeatures  = features2(pointIdx,:);
        
        if numel(pointIdx) == 1
            bestIndex = pointIdx;
        else
            scores = helperHammingDistance(centerFeature, nearbyFeatures);
            
            % Find the best two matches
            [minScore, index] = mink(scores, 2);
            if minScore(1) < matchThreshold
                % Ratio test when the best two matches have the same scale
                if  minScore(1) > maxRatio * minScore(2)
                    continue
                else
                    bestIndex  = pointIdx(index(1));
                end
            else
                continue
            end
        end
        
        indexPairs(i,:) = uint32([i, bestIndex]);
    end
end
isFound = indexPairs(:, 2) > 0;
indexPairs = indexPairs(isFound, :);
[~, ia] = unique(indexPairs(:, 2), 'stable');
indexPairs = indexPairs(ia, :);
end

function index = findPointsInRadius(neighborPoints, centerPoint, radius, ...
    neighborScales, minScalse, maxScales)

sqrDist   = sum((neighborPoints - centerPoint).^2 , 2);
index     = find(sqrDist < radius^2 & neighborScales >= minScalse & neighborScales <= maxScales);
end
