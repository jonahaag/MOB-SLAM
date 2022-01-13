import math

def plot_slam_results(
    worldpoint_plot,
    cam_pos_plot,
    worldpoints,
    camera_positions,
    slam_results_plot,
    follow_camera,
):
    """Function to plot the SLAM results (camera tracking and environment mapping) using pyqtgraph

    Args:
        worldpoint_plot (GLScatterPlotItem): A pyqtgraph.opengl item to scatter plot the detected world points
        cam_pos_plot (GLLinePlotItem): A pyqtgraph.opengl item to line plot the estimated camera positions
        worldpoints (np.array): Set of estimated world points
        camera_positions (np.array): Set of estimated camera positions
        slam_results_plot (GLViewWidget): Parent widget that contains the plot items
        follow_camera (bool): Indicating whether the view of the plot should update automatically to reflect the estimated camera position, not working properly
    """
    worldpoint_plot.setData(
        pos=worldpoints, color=(0.5, 0.7, 1.0, 1.0), size=5, pxMode=True
    )
    cam_pos_plot.setData(
        pos=camera_positions,
        color="#66cdaa",
        width=10.0,
        antialias=True,
        mode="line_strip",
    )
    if follow_camera:
        x = camera_positions[-1][0]
        y = camera_positions[-1][1]
        z = camera_positions[-1][2]
        r = math.sqrt(x ** 2 + y ** 2 + z ** 2)
        # slam_results_plot.setCameraPosition(pos=pg.Vector(camera_positions[-1][0],camera_positions[-1][1],camera_positions[-1][2]))
        azimuth = math.atan(x / y) * 180 / math.pi
        elevation = math.atan(y / z) * 180 / math.pi
        slam_results_plot.opts["distance"] = r  ## distance of camera from center
        slam_results_plot.opts["fov"] = 60  ## horizontal field of view in degrees
        slam_results_plot.opts[
            "elevation"
        ] = elevation  ## camera's angle of elevation in degrees
        slam_results_plot.opts[
            "azimuth"
        ] = azimuth  ## camera's azimuthal angle in degrees
    else:
        slam_results_plot.opts["distance"] = 3.5  ## distance of camera from center
        slam_results_plot.opts["fov"] = 60  ## horizontal field of view in degrees
        slam_results_plot.opts[
            "elevation"
        ] = -65  ## camera's angle of elevation in degrees
        slam_results_plot.opts["azimuth"] = 30  ## camera's azimuthal angle in degrees

def plot_ground_truth(ground_truth_plot, camera_positions):
    """Function to plot the ground truth after stopping the SLAM

    Args:
        ground_truth_plot (GLLinePlotItem): A pyqtgraph.opengl item to line plot the actual camera positions
        camera_positions (np.array): Set of actual camera positions
    """
    ground_truth_plot.setData(
        pos=camera_positions,
        color="#cb9b1d",
        width=10.0,
        antialias=True,
        mode="line_strip",
    )
