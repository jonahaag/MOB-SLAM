import math

def plot_slam_results(worldpoint_plot, cam_pos_plot, worldpoints, camera_positions, slam_results_plot, follow_camera):
    worldpoint_plot.setData(pos=worldpoints, color=(0.5,0.7,1.0,1.0), size=5, pxMode=True)
    cam_pos_plot.setData(pos=camera_positions, color='#66cdaa', width=10.0, antialias=True, mode='line_strip')
    if follow_camera:
        x = camera_positions[-1][0]
        y = camera_positions[-1][1]
        z = camera_positions[-1][2]
        r = math.sqrt(x**2 + y**2 + z**2)
        #slam_results_plot.setCameraPosition(pos=pg.Vector(camera_positions[-1][0],camera_positions[-1][1],camera_positions[-1][2]))
        azimuth = math.atan(x/y)*180/math.pi
        elevation = math.atan(y/z)*180/math.pi
        slam_results_plot.opts['distance'] = r        ## distance of camera from center
        slam_results_plot.opts['fov'] = 60                ## horizontal field of view in degrees
        slam_results_plot.opts['elevation'] = elevation          ## camera's angle of elevation in degrees
        slam_results_plot.opts['azimuth'] = azimuth           ## camera's azimuthal angle in degrees 
    else:
        slam_results_plot.opts['distance'] = 3.5         ## distance of camera from center
        slam_results_plot.opts['fov'] = 60                ## horizontal field of view in degrees
        slam_results_plot.opts['elevation'] = -65          ## camera's angle of elevation in degrees
        slam_results_plot.opts['azimuth'] = 30            ## camera's azimuthal angle in degrees 

def plot_ground_truth(ground_truth_plot, camera_positions):
    ground_truth_plot.setData(pos=camera_positions, color='#cb9b1d', width=10.0, antialias=True, mode='line_strip')
    
