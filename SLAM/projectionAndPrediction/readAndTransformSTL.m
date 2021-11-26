function stlData = readAndTransformSTL(transformationMatrix,filename, scale)
    %% Read and transform stl-data (model)
    % basis for projection / prediction
    stlData = stlread(filename);
    
    % transform directly for trimesh plot
    stlPoints = transformationMatrix *...
                [stlData.Points'; ones(1,length(stlData.Points))];
    stlPoints = stlPoints(1:3,:)';

    
    stlPoints = stlPoints/scale;
    
    stlData = triangulation(stlData.ConnectivityList, stlPoints);
%     trimesh(stlData,'FaceColor','k','EdgeColor','w')
end

