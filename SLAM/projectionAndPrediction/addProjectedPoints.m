function projectedPointSet = addProjectedPoints(projectedPointSet, pointIndices)
if ~isempty(pointIndices)
    nbOfNewPoints = length(pointIndices);
    projectedPointSet.BarycentricCoordinates(pointIndices, :) = zeros(nbOfNewPoints,3);
    projectedPointSet.TrianglePointIdx(pointIndices, :) = zeros(nbOfNewPoints,3);
    projectedPointSet.IsProjected(pointIndices) = zeros(nbOfNewPoints,1);
    projectedPointSet.ViewId(pointIndices) = zeros(nbOfNewPoints,1);
    projectedPointSet.ViewsTried(pointIndices) = zeros(nbOfNewPoints,1);
    projectedPointSet.ProjectionAngle(pointIndices) = zeros(nbOfNewPoints,1);
    projectedPointSet.NumberOfPointsConsidered = projectedPointSet.NumberOfPointsConsidered + nbOfNewPoints;
%     projectedPointSet.NumberOfPointsConsidered = pointIndices(end);
end
end