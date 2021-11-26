function groundTruthTransformed = transformSofa2Slam(groundTruthPosition, transformation) 
    groundTruthTransformed = transformation *...
                [groundTruthPosition'; ones(1,length(groundTruthPosition))];
    groundTruthTransformed = groundTruthTransformed(1:3,:)';
end

