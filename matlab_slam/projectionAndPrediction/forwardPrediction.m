function mapPointSet = forwardPrediction(mapPointSet, projectedPointSet, nodePositions, indices)
% use barycentric coordinates of current projection to forward predict each
% map point
% indices = find(projectedPointSet.IsProjected);
triangles = projectedPointSet.TrianglePointIdx(indices,:);
bary = projectedPointSet.BarycentricCoordinates(indices,:);
n = length(bary);
baryMatrix = zeros(n, 3*n);
for i = 1:n
baryMatrix(i,3*i-2:3*i) = bary(i,:); % create some sort of diagonal matrix
end
% for n points, bary matrix is nx3*n and nodePositions is 3n*3, so
% newPositions is nx3
positionsNew = baryMatrix*nodePositions(triangles',:);

% for i = 1:length(indices)
%     index = indices(i);
%     triangles = projectedPointSet.TrianglePointIdx(index,:);
%     positionsNew(i,:) = projectedPointSet.BarycentricCoordinates(index,:)*nodePositions(triangles,:);
% end
mapPointSet = updateWorldPoints(mapPointSet, indices, positionsNew);
end


