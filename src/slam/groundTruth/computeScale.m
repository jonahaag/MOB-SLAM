function [scale] = computeScale(vSetKeyFrames,groundTruthPosition) 
    estimatedCams = vertcat(poses(vSetKeyFrames).AbsolutePose.Translation);
    scale = median(vecnorm(groundTruthPosition, 2, 2))/ median(vecnorm(estimatedCams, 2, 2));
end

