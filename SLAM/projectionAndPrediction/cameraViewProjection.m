function [alpha, beta, gamma, P_proj, phi, k_triangle] = test_CameraViewProjection(A,B,C,P,cameraP)
    % Given a triangle consisting of three points in space A, B, and C
    % and an arbitrary point P compute the barycentric coordinates of the 
    % orthogonal projection of P onto the plane defined by A, B, and C. 
    % define some vectors
    v0 = B-A;
    v1 = C-A;
    % compute the unit normal of the triangle
    n = cross(v0, v1, 2);
    u = P-cameraP;
    % interscetion between line (cameraP and P) and plane (A,B,C)
    lambda = (diag(A*n')' - cameraP*n') ./ (u*n');
%     disp(size(cameraP))
%     disp(size(lambda))
%     disp(size(u))
    P_projs = cameraP + lambda' .* u;
    % compute barycentric coordinates 
    % https://gamedev.stackexchange.com/questions/23743/whats-the-most-efficient-way-to-find-barycentric-coordinates
    v2 = P_projs-A;
    d00 = diag(v0*v0');
    d01 = diag(v0*v1');
    d11 = diag(v1*v1');
    d20 = diag(v2*v0');
    d21 = diag(v2*v1');
    denom = d00 .* d11 - d01 .* d01;
    beta = (d11 .* d20 - d01 .* d21) ./ denom;
    gamma = (d00 .* d21 - d01 .* d20) ./ denom;
    alpha = 1.0 - beta - gamma;
    
    i = 0;
    foundTriangle = 0;
    while i < numel(alpha) && foundTriangle == 0
        i = i + 1;
        if alpha(i)>=0 && alpha(i)<=1 && beta(i)>=0 && beta(i)<=1 && gamma(i)>=0 && gamma(i)<=1
            foundTriangle = 1;
            alpha = alpha(i);
            beta = beta(i);
            gamma = gamma(i);
            P_proj = P_projs(i,:);
            phi = acos(u*n(i,:)'/(norm(u)*norm(n(i,:))));
            k_triangle = i;
        end
    end
    % in case there is no valid projection, just return some random values
    % and large phi, so that this point is just regarded as unprojected
    if foundTriangle == 0
        alpha = -1;
        beta = -1;
        gamma = -1;
        P_proj = [0 0 0];
        phi = 10000;
        k_triangle = 1;
    end
end

