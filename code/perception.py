import numpy as np
import cv2

# Identify pixels within a threshold
def color_thresh(img, rgb_thresh):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    whitin_thresh = (img[:, :, 0] > rgb_thresh[0][0]) \
                    & (img[:, :, 0] <= rgb_thresh[0][1]) \
                    & (img[:, :, 1] > rgb_thresh[1][0]) \
                    & (img[:, :, 1] <= rgb_thresh[1][1]) \
                    & (img[:, :, 2] > rgb_thresh[2][0]) \
                    & (img[:, :, 2] <= rgb_thresh[2][1])
    # Index the array of zeros with the boolean array and set to 1
    color_select[whitin_thresh] = 1
    # Return the binary image
    return color_select

# Define a function to convert from image coordinates to rover coordinates
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel

# Define a function to convert to radial coordinates in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to map rover space pixels to world space
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
                            
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated

def translate_pix(xpix_rot,
                  ypix_rot,
                  xpos,
                  ypos,
                  scale):
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result
    return xpix_translated, ypix_translated


# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    
    return warped


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # region Perform perception steps to update Rover()
    # TODO: 
    # endregion NOTE: camera image is coming to you in Rover.img

    # region 1) Define source and destination points for perspective transform
    image = Rover.img
    # Define calibration box in source (actual) and destination (desired) coordinates
    # These source and destination points are defined to warp the image
    # to a grid where each 10x10 pixel square represents 1 square meter
    # The destination box will be 2*dst_size on each side
    dst_size = 5
    # Set a bottom offset to account for the fact that the bottom of the image
    # is not the position of the rover but a bit in front of it
    bottom_offset = 6

    source = np.float32([[14, 140], [301, 140], [200, 96], [118, 96]])
    destination = np.float32([[image.shape[1] / 2 - dst_size, image.shape[0] - bottom_offset],
                              [image.shape[1] / 2 + dst_size, image.shape[0] - bottom_offset],
                              [image.shape[1] / 2 + dst_size, image.shape[0] - 2 * dst_size - bottom_offset],
                              [image.shape[1] / 2 - dst_size, image.shape[0] - 2 * dst_size - bottom_offset],
                              ])
    # endregion

    # region 2) Apply perspective transform to the image

    warped = perspect_transform(image, source, destination)
    # endregion

    # region 3) Apply color threshold to identify navigable terrain/obstacles/rock samples

    rgb_thresh_navigable = ([160, 255], [160, 255], [160, 255])
    rgb_thresh_obstacle = ([0, 160], [0, 160], [0, 160])
    rgb_thresh_rock = ([132, 157], [109, 177], [0, 55])

    threshed_navigable = color_thresh(warped, rgb_thresh_navigable)

    threshed_obstacle = color_thresh(warped, rgb_thresh_obstacle)

    threshed_rock = color_thresh(warped, rgb_thresh_rock)
    # endregion

    # region 4) Update Rover.vision_image (this will be displayed on left side of screen)
        # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
        #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
        #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image

    Rover.vision_image[:, :, 0] = threshed_obstacle*255
    Rover.vision_image[:, :, 1] = threshed_rock*255
    Rover.vision_image[:, :, 2] = threshed_navigable*255
    # endregion

    # region 5) Convert map image pixel values to rover-centric coords
    # Calculate pixel values in rover-centric coords and distance/angle to all pixels

    xpix_rc_nav, ypix_rn_nav = rover_coords(threshed_navigable)
    xpix_rc_obs, ypix_rn_obs = rover_coords(threshed_obstacle)
    xpix_rc_rock, ypix_rn_rock = rover_coords(threshed_rock)
    # endregion

    # region 6) Convert rover-centric pixel values to world coordinates

    # region a) Rotate navigable, obstacles and rock threshold images
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
    # endregion

    # region b) Scale and translate to world coordinates
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
    # endregion

    # region c) Trim distant points from nav and obs
    # Select points closer than given distance
    good_proximity = 15
    close_enough_nav = ((xpix_world_cord_nav - x_pos) ** 2 + (ypix_world_cord_nav - y_pos) ** 2) ** 0.5 < good_proximity
    xpix_w_cor_nav_trim = xpix_world_cord_nav[close_enough_nav]
    ypix_w_cor_nav_trim = ypix_world_cord_nav[close_enough_nav]

    close_enough_obs = ((xpix_world_cord_obs - x_pos) ** 2 + (ypix_world_cord_obs - y_pos) ** 2) ** 0.5 < good_proximity-5
    xpix_w_cor_obs_trim = xpix_world_cord_obs[close_enough_obs]
    ypix_w_cor_obs_trim = ypix_world_cord_obs[close_enough_obs]

    # endregion
    # endregion

    # region 7) Update Rover worldmap (to be displayed on right side of screen)
    # region a) Update worldmap
        # Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #          Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1
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
    # endregion

    # region b) Trim worldmap
    Rover.counter += 1
    if Rover.counter == 400:
        to_low_nav = Rover.worldmap[:, :, 2] < 20
        Rover.worldmap[to_low_nav[1], to_low_nav[0], 2] = 0

        to_low_obs = Rover.worldmap[:, :, 0] < 20
        Rover.worldmap[to_low_obs[1], to_low_obs[0], 0] = 0
        Rover.counter = 0


    # endregion
    # endregion

    # region 8) Convert rover-centric pixel positions to polar coordinates

    dist_nav, angles_nav = to_polar_coords(xpix_rc_nav, ypix_rn_nav)
    mean_dir_nav = np.mean(angles_nav)

    dist_obs, angles_obs = to_polar_coords(xpix_rc_obs, ypix_rn_obs)
    mean_dir_obs = np.mean(angles_obs)

    dist_rock, angles_rock = to_polar_coords(xpix_rc_rock, ypix_rn_rock)
    mean_dir_rock = np.mean(angles_rock)

    # Update Rover pixel distances and angles
        # Rover.nav_dists = rover_centric_pixel_distances
        # Rover.nav_angles = rover_centric_angles
    Rover.nav_dists = dist_nav
    Rover.nav_angles = angles_nav
    # endregion

    return Rover