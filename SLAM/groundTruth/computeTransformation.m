function H_sofa2slam = computeTransformation(groundTruthPosition) 
    translation = -groundTruthPosition(1,:)';
    rotation = [1 0 0; 0 -1 0; 0 0 -1]; % in sofa the initial view is rotated with pi around the x axis 
    H_sofa2slam = [rotation zeros(3,1); 0 0 0 1] * [eye(3) translation; 0 0 0 1];
end

