function [alpha, beta, gamma, P_proj, phi] = cameraViewProjection(A,B,C,P,cameraP)
    % Given a triangle consisting of three points in space A, B, and C
    % and an arbitrary point P compute the barycentric coordinates of the 
    % orthogonal projection of P onto the plane defined by A, B, and C. 
    % define some vectors
%     A = [1, 1, 0];
%     B = [1, 0, 0];
%     C = [0, 1, 0];
%     P = [1,1,1];
%     cameraP = [2,2,2];
    v0 = B-A;
    v1 = C-A;
    % compute the unit normal of the triangle
    n = cross(v0, v1);
    u = P-cameraP;
    % interscetion between line (cameraP and P) and plane (A,B,C)
    lambda = (A*n' - cameraP*n') / (u*n');
    P_proj = cameraP + lambda * u;
    % compute barycentric coordinates 
    % https://gamedev.stackexchange.com/questions/23743/whats-the-most-efficient-way-to-find-barycentric-coordinates
    v2 = P_proj-A;
    d00 = v0*v0';
    d01 = v0*v1';
    d11 = v1*v1';
    d20 = v2*v0';
    d21 = v2*v1';
    denom = d00 * d11 - d01 * d01;
    beta = (d11 * d20 - d01 * d21) / denom;
    gamma = (d00 * d21 - d01 * d20) / denom;
    alpha = 1.0 - beta - gamma;

    phi = acos(u*n'/(norm(u)*norm(n)));
    
end

