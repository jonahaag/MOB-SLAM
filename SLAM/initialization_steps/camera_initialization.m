%% Camera intrinsics
% Create a cameraIntrinsics object to store the camera intrinsic parameters.
% The intrinsics for the dataset can be found at the following page:
% https://vision.in.tum.de/data/datasets/rgbd-dataset/file_formats
% Note that the images in the dataset are already undistorted, hence there
% is no need to specify the distortion coefficients.
% old calibration
% nRows = 1200;
% nCols = 1530;
% Cx =    734.8202;
% Cy =    640.9961;
% f =     2.1735;
% d =     0.0112;
% focalLength    = [f/d, f/d];    % in units of pixels
% principalPoint = [Cx, Cy];    % in units of pixels
focalLength = cameraParams.FocalLength;
principalPoint = cameraParams.PrincipalPoint;
imageSize      = size(currI,[1 2]);  % in units of pixels
intrinsics     = cameraIntrinsics(focalLength, principalPoint, imageSize);
