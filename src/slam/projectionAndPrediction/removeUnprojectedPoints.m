function [projectedPointSet, mapPointSet, directionAndDepth, newPointIdx] = removeUnprojectedPoints(projectedPointSet, mapPointSet, directionAndDepth, pointIndices, newPointIdx)
if ~isempty(pointIndices)
    projectedPointSet.BarycentricCoordinates(pointIndices, :) = [];
    projectedPointSet.TrianglePointIdx(pointIndices, :) = [];
    projectedPointSet.IsProjected(pointIndices) = [];
    projectedPointSet.ViewId(pointIndices) = [];
    projectedPointSet.ViewsTried(pointIndices) = [];
    projectedPointSet.ProjectionAngle(pointIndices) = [];
    projectedPointSet.NumberOfPointsConsidered = projectedPointSet.NumberOfPointsConsidered - numel(pointIndices);
    mapPointSet = removeWorldPoints(mapPointSet, pointIndices);
    directionAndDepth = remove(directionAndDepth, pointIndices);
    % pointIndices have to be >= newPointIdx
%     save test1.mat newPointIdx pointIndices
    largeEnough = pointIndices > newPointIdx(1); %logical indexing
    pointIndices = pointIndices(largeEnough);
    newPointIdx = newPointIdx - arrayfun(@(x) nnz(x>pointIndices), newPointIdx);
%     save test2.mat newPointIdx pointIndices
end
end