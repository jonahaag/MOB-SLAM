function [mapPointSet, projectedPointSet, notProjectedIndices] = projectMapPoints(projectedPointSet, mapPointSet, stlData, pointIndices, vSetKeyFrames, nodePositions, directionAndDepth)
notProjectedIndices = []; % contains map point indices that have not been updated
if ~isempty(pointIndices)
    positionsOld = mapPointSet.WorldPoints(pointIndices,:);
    positionsNew = zeros(length(pointIndices),3);
    poses = vSetKeyFrames.Views.AbsolutePose;
    updateIndices = []; % contains map point indices that have been updated
    updateIndices2 = []; % contains indices of positionsNew that have been updated
    for i = 1:length(pointIndices)
        ii = pointIndices(i); % ii corresponds with mapPointIdx
        viewIds = mapPointSet.Correspondences.ViewId{ii}(:);
%         viewIds = directionAndDepth.MajorViewId(ii);
        P = positionsOld(i,:);
        % find closest points
        P_distances = vecnorm(P-nodePositions,2,2);
%         [~, idx] = sort(P_distances);
%         k = idx(1);
%         k_2 = idx(2);
        k = find(P_distances == min(P_distances));        
        k_triangles = vertexAttachments(stlData,k);
        k_triangles = k_triangles{1}(:)';

        % get indices of triangle corners
        vertexIDs = stlData(k_triangles,:);
        % use indices to get triangle corner coordinates
        A = nodePositions(vertexIDs(:,1),:);
        B = nodePositions(vertexIDs(:,2),:);
        C = nodePositions(vertexIDs(:,3),:);
%         [alpha, beta, gamma, P_proj] = cameraViewProjection(A,B,C,P,viewCameraPositions);
        phi = pi/2;
        isProjected = false;
        for j = 1:numel(viewIds)
            viewCameraPosition = poses(viewIds(j)).Translation;
            [alpha_opt, beta_opt, gamma_opt, P_proj_opt, phi_opt, k_triangle] = cameraViewProjection(A,B,C,P,viewCameraPosition);
            if abs(phi_opt-pi) < abs(phi) % phi_opt is always \in [pi/2, pi]
                alpha = alpha_opt;
                beta = beta_opt;
                gamma = gamma_opt;
                P_proj = P_proj_opt;
                phi = abs(phi_opt-pi);
                viewId = viewIds(j);
                isProjected = true;
                trianglePointIdx = vertexIDs(k_triangle,:);
            end
        end
        if isProjected
%             positionsNew(ii,:) = [alpha beta gamma] * [A; B; C];
            positionsNew(i,:) = P_proj;
            projectedPointSet.IsProjected(ii) = 1;
            projectedPointSet.BarycentricCoordinates(ii,:) = [alpha beta gamma];
            projectedPointSet.TrianglePointIdx(ii,:) = trianglePointIdx;
            projectedPointSet.ViewId(ii) = viewId;
            projectedPointSet.ProjectionAngle(ii) = phi;
            updateIndices = [updateIndices; ii];
            updateIndices2 = [updateIndices2; i];
        else
            % try orthogonal projection
            notProjectedIndices = [notProjectedIndices; ii];
        end
    end
%     updateIndices = find(projectedPointSet.IsProjected);
    disp(['Projected ', num2str(length(updateIndices)), ' out of ',...
        num2str(length(pointIndices)), ' new points']);
    if ~isempty(updateIndices2)
        positionsNew = positionsNew(updateIndices2,:);
%     majorViewIds = directionAndDepth.MajorViewId(:);
%     save("results/testProjection.mat", 'mapPointSet', 'vSetKeyFrames', 'projectedPointSet', 'positionsNew', 'majorViewIds')
        mapPointSet = updateWorldPoints(mapPointSet, updateIndices, positionsNew);
    end
end
end




% function [alpha, beta, gamma, phi] = cameraViewProjection(A,B,C,P,cameraP)
%     % Given a triangle consisting of three points in space A, B, and C
%     % and an arbitrary point P compute the barycentric coordinates of the 
%     % orthogonal projection of P onto the plane defined by A, B, and C. 
%     % define some vectors
%     
%     v0 = B-A;
%     v1 = C-A;
%     % compute the unit normal of the triangle
%     n = cross(v0, v1);
%     % define the plane ABC and the line betwenn the camera and point of interest 
%     syms lambda
%     u = P-cameraP;
%     f(lambda) = cameraP + lambda * u;
%     lambda_sol = solve(dot(n,f(lambda)) - dot(A,n) == 0, lambda);
%     P_proj = double(f(lambda_sol));
%     
%     % compute barycentric coordinates 
%     % https://gamedev.stackexchange.com/questions/23743/whats-the-most-efficient-way-to-find-barycentric-coordinates
%     v2 = P_proj-A;
%     d00 = dot(v0, v0);
%     d01 = dot(v0, v1);
%     d11 = dot(v1, v1);
%     d20 = dot(v2, v0);
%     d21 = dot(v2, v1);
%     denom = d00 * d11 - d01 * d01;
%     beta = (d11 * d20 - d01 * d21) / denom;
%     gamma = (d00 * d21 - d01 * d20) / denom;
%     alpha = 1.0 - beta - gamma;
%     
%     phi = acos(dot(u,n)/(norm(u)*norm(n)));
%     
% end