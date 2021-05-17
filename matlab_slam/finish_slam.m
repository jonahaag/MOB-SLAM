%% After main loop
% % Use ground truth so compare/optimize trajectory and calculate error
compareGroundTruth

saveResults = true;
if saveResults
    if projectionInitialized
        save("results/resultsProjection.mat", 'vSetKeyFrames', 'mapPointSet',...
            'sofaGroundTruth_pos_slam', 'projectedPointSet', 'currentNodePositions',...
            'scale','scale1','rmse1','rmse2')
    else
        % Optimize the poses
        vSetKeyFramesOptim = optimizePoses(vSetKeyFrames, minNumMatches, 'Tolerance', 1e-16, 'Verbose', true);

        % Update map points after optimizing the poses
        mapPointSet = helperUpdateGlobalMap(mapPointSet, directionAndDepth, ...
            vSetKeyFrames, vSetKeyFramesOptim);

        updatePlot(mapPlot, vSetKeyFrames, mapPointSet);

        % Plot the optimized camera trajectory
        optimizedPoses  = poses(vSetKeyFramesOptim);
        plotOptimizedTrajectory(mapPlot, optimizedPoses)

        % Update legend
        showLegend(mapPlot);
        
        save("results/results.mat", 'vSetKeyFrames', 'mapPointSet',...
            'sofaGroundTruth_pos_slam','scale','scale1','rmse1','rmse2',...
            'vSetKeyFramesOptim')
    end
end