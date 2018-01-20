# Search and Sample Return Project

Dear reviewer,
This is the best I could do with the project in the time available. This was by far the largest Python project I had to work on (not much experience with Python). I am also working 4 days a week and in the mornings I am preparing for the drivers exam.
If any aspect of the project is insufficiently implemented please let me know. I will address as soon as I have time.

## Generating video with the Jupiter Notebook
I have managed to run all the function is the notebook. `process_image()` was completed using the functions in the notebook.

`color_thresh()` was modifie to take in ranges.
```sh
def color_thresh(img, rgb_thresh):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # whitin_thresh will now contain a boolean array with "True"
    # where threshold was met
    whitin_thresh = ( img[:, :, 0] >  rgb_thresh[0][0]) \
                   & (img[:, :, 0] <= rgb_thresh[0][1]) \
                   & (img[:, :, 1] >  rgb_thresh[1][0]) \
                   & (img[:, :, 1] <= rgb_thresh[1][1]) \
                   & (img[:, :, 2] >  rgb_thresh[2][0]) \
                   & (img[:, :, 2] <= rgb_thresh[2][1])
    # Index the array of zeros with the boolean array and set to 1
    color_select[whitin_thresh] = 1
    # Return the binary image
    return color_select
```
The color ranges where chosen using MS Paint-s color sampling tool.

```sh
rgb_thresh_navigable = ([160, 255], [160, 255], [160, 255])
rgb_thresh_obstacle = ([0, 160], [0, 160], [0, 160])
rgb_thresh_rock = ([132, 157], [109, 177], [0, 55])
```

Optional functionality was added for debuging that marks the position of the rover on the worldmap.

```sh
 if mark_rover_position:
        data.worldmap[y_pos,
                      x_pos,
                      :] = 255
```

## Autonomous Navigation and Mapping
The code was edited using the PyCharm IDE to be able to benefit from code folding and region definition. The code is syced to a Git repository [PocsGeza/Udacity_Rover_Challange](https://github.com/PocsGeza/Udacity_Rover_Challange). 

## Preception Step
The `perception_step()` is similar to `process_image()` from the Jupiter Notebook.
### 1) Define source and destination points for perspective transform

```sh
source = np.float32([[14, 140], [301, 140], [200, 96], [118, 96]])
    destination = np.float32([[image.shape[1] / 2 - dst_size, image.shape[0] - bottom_offset],
                              [image.shape[1] / 2 + dst_size, image.shape[0] - bottom_offset],
                              [image.shape[1] / 2 + dst_size, image.shape[0] - 2 * dst_size - bottom_offset],
                              [image.shape[1] / 2 - dst_size, image.shape[0] - 2 * dst_size - bottom_offset],
                              ])
```

### 2) Apply perspective transform to the image
```sh
warped = perspect_transform(image, source, destination)
```
### 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
```sh
rgb_thresh_navigable = ([160, 255], [160, 255], [160, 255])
rgb_thresh_obstacle = ([0, 160], [0, 160], [0, 160])
rgb_thresh_rock = ([132, 157], [109, 177], [0, 55])

threshed_navigable = color_thresh(warped, rgb_thresh_navigable)
threshed_obstacle = color_thresh(warped, rgb_thresh_obstacle)
threshed_rock = color_thresh(warped, rgb_thresh_rock)

```
### 4) Update Rover.vision_image
```sh
Rover.vision_image[:, :, 0] = threshed_obstacle*255
Rover.vision_image[:, :, 1] = threshed_rock*255
Rover.vision_image[:, :, 2] = threshed_navigable*255
```
I've saved some test data for you in the folder called `test_dataset`.  In that folder you'll find a csv file with the output data for steering, throttle position etc. and the pathnames to the images recorded in each run.  I've also saved a few images in the folder called `calibration_images` to do some of the initial calibration steps with.  

The first step of this project is to record data on your own.  To do this, you should first create a new folder to store the image data in.  Then launch the simulator and choose "Training Mode" then hit "r".  Navigate to the directory you want to store data in, select it, and then drive around collecting data.  Hit "r" again to stop data collection.

## Data Analysis
Included in the IPython notebook called `Rover_Project_Test_Notebook.ipynb` are the functions from the lesson for performing the various steps of this project.  The notebook should function as is without need for modification at this point.  To see what's in the notebook and execute the code there, start the jupyter notebook server at the command line like this:

```sh
jupyter notebook
```

This command will bring up a browser window in the current directory where you can navigate to wherever `Rover_Project_Test_Notebook.ipynb` is and select it.  Run the cells in the notebook from top to bottom to see the various data analysis steps.  

The last two cells in the notebook are for running the analysis on a folder of test images to create a map of the simulator environment and write the output to a video.  These cells should run as-is and save a video called `test_mapping.mp4` to the `output` folder.  This should give you an idea of how to go about modifying the `process_image()` function to perform mapping on your data.  

## Navigating Autonomously
The file called `drive_rover.py` is what you will use to navigate the environment in autonomous mode.  This script calls functions from within `perception.py` and `decision.py`.  The functions defined in the IPython notebook are all included in`perception.py` and it's your job to fill in the function called `perception_step()` with the appropriate processing steps and update the rover map. `decision.py` includes another function called `decision_step()`, which includes an example of a conditional statement you could use to navigate autonomously.  Here you should implement other conditionals to make driving decisions based on the rover's state and the results of the `perception_step()` analysis.

`drive_rover.py` should work as is if you have all the required Python packages installed. Call it at the command line like this: 

```sh
python drive_rover.py
```  

Then launch the simulator and choose "Autonomous Mode".  The rover should drive itself now!  It doesn't drive that well yet, but it's your job to make it better!  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results!  Make a note of your simulator settings in your writeup when you submit the project.**

### Project Walkthrough
If you're struggling to get started on this project, or just want some help getting your code up to the minimum standards for a passing submission, we've recorded a walkthrough of the basic implementation for you but **spoiler alert: this [Project Walkthrough Video](https://www.youtube.com/watch?v=oJA6QHDPdQw) contains a basic solution to the project!**.


