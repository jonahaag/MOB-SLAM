function projectedPointSet = removeProjectedPoints(projectedPointSet, pointIndices)
if ~isempty(pointIndices)
    projectedPointSet.BarycentricCoordinates(pointIndices, :) = [];
    projectedPointSet.TrianglePointIdx(pointIndices, :) = [];
    projectedPointSet.IsProjected(pointIndices) = [];
    projectedPointSet.ViewId(pointIndices) = [];
    projectedPointSet.ViewsTried(pointIndices) = [];
    projectedPointSet.ProjectionAngle(pointIndices) = [];
    projectedPointSet.NumberOfPointsConsidered = projectedPointSet.NumberOfPointsConsidered - numel(pointIndices);
end
end