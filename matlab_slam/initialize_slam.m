clear all; close all;
addpath 'helperFunctions' 'initialization_steps' 'groundTruth' 'projectionAndPrediction'
load initI.mat
initIm = 1;
doProjections = 1;
projectionInitialized = 0;
minNumberOfKeyframesBeforeProjection = 5; % !> minNumberOfKeyframesBeforeScalings
minNumberOfKeyframesBeforeScaling = 5;
% scale = 0; % ensure rescale after minNumberOfKeyframesBeforeScaling at least once
scale = 4.15; % known scale factor
% Inspect the first image
currFrameIdx = initIm;
% currI = readimage(imds, currFrameIdx);
imageSize = double([viewerHeight, viewerWidth]);
currI = uint8(currI);
% himage = imshow(currI);
f = double(viewerHeight) / 1200 * 1.448882146816558e+03;
focalLength = [f f];
%% Load camera intrinsics
intrinsics = cameraIntrinsics(focalLength, principalPoint, imageSize);

%% Start of map initialization
% Set random seed for reproducibility
rng(0);

% Detect and extract ORB features
scaleFactor = 1.2;
numLevels   = 8;
[preFeatures, prePoints] = helperDetectAndExtractFeatures(currI, scaleFactor, numLevels, intrinsics); 

currFrameIdx = currFrameIdx + 1;
firstI       = currI; % Preserve the first frame 

isMapInitialized  = false;


