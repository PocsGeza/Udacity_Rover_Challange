# Search and Sample Return Project

Dear reviewer,
This is the best I could do with the project in the time available. This was by far the largest Python project I had to work on (not much experience with Python). I am also working 4 days a week and in the mornings I am preparing for the drivers exam.
If any aspect of the project is insufficiently implemented please let me know. I will address as soon as I have time.

## Generating video with the Jupiter Notebook
I have managed to run all the function is the notebook. `process_image()` was completed using the functions in the notebook.

`color_thresh()` was modified to take in ranges.
```
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

```
rgb_thresh_navigable = ([160, 255], [160, 255], [160, 255])
rgb_thresh_obstacle = ([0, 160], [0, 160], [0, 160])
rgb_thresh_rock = ([132, 157], [109, 177], [0, 55])
```

Optional functionality was added for debugging that marks the position of the rover on the world map.

```
 if mark_rover_position:
        data.worldmap[y_pos,
                      x_pos,
                      :] = 255
```

## Autonomous Navigation and Mapping
The code was edited using the PyCharm IDE to be able to benefit from code folding and region definition. The code is synced to a Git repository [PocsGeza/Udacity_Rover_Challange](https://github.com/PocsGeza/Udacity_Rover_Challange). 

## Preception Step
The `perception_step()` is similar to `process_image()` from the Jupiter Notebook.
### 1) Define source and destination points for perspective transform

```
source = np.float32([[14, 140], [301, 140], [200, 96], [118, 96]])
    destination = np.float32([[image.shape[1] / 2 - dst_size, image.shape[0] - bottom_offset],
                              [image.shape[1] / 2 + dst_size, image.shape[0] - bottom_offset],
                              [image.shape[1] / 2 + dst_size, image.shape[0] - 2 * dst_size - bottom_offset],
                              [image.shape[1] / 2 - dst_size, image.shape[0] - 2 * dst_size - bottom_offset],
                              ])
```

### 2) Apply perspective transform to the image
```
warped = perspect_transform(image, source, destination)
```
### 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
```
rgb_thresh_navigable = ([160, 255], [160, 255], [160, 255])
rgb_thresh_obstacle = ([0, 160], [0, 160], [0, 160])
rgb_thresh_rock = ([132, 157], [109, 177], [0, 55])

threshed_navigable = color_thresh(warped, rgb_thresh_navigable)
threshed_obstacle = color_thresh(warped, rgb_thresh_obstacle)
threshed_rock = color_thresh(warped, rgb_thresh_rock)
```
### 4) Update Rover.vision_image
```
Rover.vision_image[:, :, 0] = threshed_obstacle*255
Rover.vision_image[:, :, 1] = threshed_rock*255
Rover.vision_image[:, :, 2] = threshed_navigable*255
```

### 5) Convert map image pixel values to rover-centric coords
```
xpix_rc_nav, ypix_rn_nav = rover_coords(threshed_navigable)
xpix_rc_obs, ypix_rn_obs = rover_coords(threshed_obstacle)
xpix_rc_rock, ypix_rn_rock = rover_coords(threshed_rock)
```
### 6) Convert rover-centric pixel values to world coordinates
 Rotate navigable, obstacles and rock threshold images
 
  ```
    yaw = Rover.yaw

    xpix_rotated_nav, ypix_rotated_nav = rotate_pix(xpix_rc_nav,
                                                    ypix_rn_nav,
                                                    yaw)
    xpix_rotated_obs, ypix_rotated_obs = rotate_pix(xpix_rc_obs,
                                                    ypix_rn_obs,
                                                    yaw)
    xpix_rotated_rock, ypix_rotated_rock = rotate_pix(xpix_rc_rock,
                                                      ypix_rn_rock,
                                                      yaw)
```                                                  

 
Scale and translate to world coordinates
 
 ```
    scale = 10
    x_pos = Rover.pos[0]
    y_pos = Rover.pos[1]
    xpix_world_cord_nav, ypix_world_cord_nav = \
        translate_pix(xpix_rotated_nav,
                      ypix_rotated_nav,
                      x_pos,
                      y_pos,
                      scale)

    xpix_world_cord_obs, ypix_world_cord_obs = \
        translate_pix(xpix_rotated_obs,
                      ypix_rotated_obs,
                      x_pos,
                      y_pos,
                      scale)

    xpix_world_cord_rock, ypix_world_cord_rock = \
        translate_pix(xpix_rotated_rock,
                      ypix_rotated_rock,
                      x_pos, y_pos,
                      scale)
 ```
 
 Trim distant points from nav and obs
 This was in the hope of improving fidelity
 
```
  Select points closer than given distance
    good_proximity = 15
    close_enough_nav = ((xpix_world_cord_nav - x_pos) ** 2 + (ypix_world_cord_nav - y_pos) ** 2) ** 0.5 < good_proximity
    xpix_w_cor_nav_trim = xpix_world_cord_nav[close_enough_nav]
    ypix_w_cor_nav_trim = ypix_world_cord_nav[close_enough_nav]

    close_enough_obs = ((xpix_world_cord_obs - x_pos) ** 2 + (ypix_world_cord_obs - y_pos) ** 2) ** 0.5 < good_proximity-5
    xpix_w_cor_obs_trim = xpix_world_cord_obs[close_enough_obs]
    ypix_w_cor_obs_trim = ypix_world_cord_obs[close_enough_obs]
```
### 7) Update Rover worldmap (to be displayed on right side of screen)
 a) Update world map
 Filtering was added based pitch and roll avoid updating the world map when the perspective transform would produce incorrect mappings.
 I did not want to take time to figure what scenrio is causing the IndexError exception.
 
 ``` 
    pitch_range = [1, 359]
    roll_range = [1, 359]

    try:
        if  ((Rover.pitch < pitch_range[1]) | (Rover.pitch > pitch_range[0])) &\
        ((Rover.roll > roll_range[0]) | (Rover.roll > roll_range[0])):

            Rover.worldmap[ypix_w_cor_obs_trim.astype(np.int32), xpix_w_cor_obs_trim.astype(np.int32), 0] += 1
            Rover.worldmap[ypix_world_cord_rock.astype(np.int32), xpix_world_cord_rock.astype(np.int32), 1] += 1
            Rover.worldmap[ypix_w_cor_nav_trim.astype(np.int32), xpix_w_cor_nav_trim.astype(np.int32), 2] += 1
    except IndexError:
        pass
```
  b) Trim worldmap
  Low sum points on the world map where periodically reset to 0 in hope of increasing the fidelity of the mapping.
  
  ```sh
    Rover.counter += 1
    if Rover.counter == 400:
        to_low_nav = Rover.worldmap[:, :, 2] < 20
        Rover.worldmap[to_low_nav[1], to_low_nav[0], 2] = 0

        to_low_obs = Rover.worldmap[:, :, 0] < 20
        Rover.worldmap[to_low_obs[1], to_low_obs[0], 0] = 0
        Rover.counter = 0
```
### 8) Convert rover-centric pixel positions to polar coordinates

```
 dist_nav, angles_nav = to_polar_coords(xpix_rc_nav, ypix_rn_nav)
 Rover.nav_dists = dist_nav
 Rover.nav_angles = angles_nav
```

## Decision Step

I declared variables fine tuning the `decision()`.
`enough_space_on_both_sides` is used to indicate the there is enough navigable terrain on the front left and front right side of the rover. This avoids getting to close to walls.
`left_turn_bias` is added to invocations of Rover.steer and turns the rover into a wall crawler.

```
left_nav_ind = Rover.nav_angles[Rover.nav_angles > 0]
right_nav_ind = Rover.nav_angles[Rover.nav_angles <= 0]
enough_space_on_both_sides = (len(left_nav_ind) >= Rover.stop_forward/2) & (len(right_nav_ind) >= Rover.stop_forward/2)
                    
left_turn_bias = 11
```

## Possibilities for further improvements
Implement sample pickup

Implement the decision step with a finite state machine

Extract RoverState to separate .py file

Add type assertions to all methods

Creat RoverStateUdated class form RoverState and only do changes to the child class

Store Home coordinates in RoverStateUdated

Store color thresholds in RoverStateUdated

Add Going_Home state to the rover after all rocks are collected or a given time has passed
