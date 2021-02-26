import numpy as np
from numba import jit

from ..spa import solar_position


def shadows(elevation_map, azimuth_angle, elevation_angle, nodata=-32768):
    shadows = np.full(elevation_map.shape, nodata, dtype=np.int16)

    # Change azimuth and elevation angles to radians.
    azimuth_angle = _deg_to_rad(azimuth_angle)
    elevation_angle = _deg_to_rad(elevation_angle)
    
    elevation_map = _orient_map(elevation_map, azimuth_angle)


def _orient_map(elevation_map, azimuth_angle):
    if 0 <= azimuth_angle < 90:
        return np.rot90(elevation_map, axes=(1, 0))
    else:
        NotImplementedError()


def _deg_to_rad(angle):
    return (angle % 360) * np.pi / 180


@jit(nopython=True)
def calc_shadow_mask(dem, elevs, azis):
    """TBA.
    """
    # Calculate stepsize.
    stepsize = np.round(dem.shape[0] / elevs.shape[0])

    # Initiate shadow mask.
    n_rows, n_cols = dem.shape
    shadow_mask = np.full(dem.shape, 0, dtype=np.bool_)
    
    for y in range(n_cols):
        if y % (n_cols // 10) == 0:
            print(int(100*y/n_cols), 'percent done.')
        for x in range(n_rows):
            cur_altitude = dem[x, y]
            x_ = int(x/stepsize)
            y_ = int(y/stepsize)
            cur_elevation = elevs[x_, y_]
            cur_azimuth = azis[x_, y_]

            # Change altitude and azimuth to radians.
            #cur_elevation = (cur_elevation % 360) * np.pi / 180
            #cur_azimuth = (cur_azimuth % 360) * np.pi / 180 # Minus 90 to fit the map's coordinate system.

            # Calculate the distance of the shadow cast by the current square.
            shadow_dist = cur_altitude / np.tan(cur_elevation)

            # Find the square where the shadow ends.
            if 0 <= cur_azimuth < np.pi/2:
                delta_x = int(np.floor(shadow_dist * np.cos(cur_azimuth) / 30))
                delta_y = int(np.floor(shadow_dist * np.sin(cur_azimuth) / 30))
                x_end = x + delta_x
                y_end = y - delta_y
            elif np.pi/2 <= cur_azimuth < np.pi:
                delta_x = int(np.floor(shadow_dist * np.sin(cur_azimuth-np.pi/2) / 30))
                delta_y = int(np.floor(shadow_dist * np.cos(cur_azimuth-np.pi/2) / 30))
                x_end = x - delta_x
                y_end = y - delta_y
            elif np.pi <= cur_azimuth < 3*np.pi/2:
                delta_x = int(np.floor(shadow_dist * np.cos(cur_azimuth-np.pi) / 30))
                delta_y = int(np.floor(shadow_dist * np.sin(cur_azimuth-np.pi) / 30))
                x_end = x - delta_x
                y_end = y + delta_y
            else:
                delta_x = int(np.floor(shadow_dist * np.sin(cur_azimuth-(3*np.pi/2)) / 30))
                delta_y = int(np.floor(shadow_dist * np.cos(cur_azimuth-(3*np.pi/2)) / 30))
                x_end = x + delta_x
                y_end = y + delta_y

            # Adjust if the end square is out of bounds.
            if x_end >= n_rows:
                x_end = int(n_rows-1)
            elif x_end < 0:
                x_end = 0
            
            if y_end >= n_cols:
                y_end = int(n_cols-1)
            elif y_end < 0:
                y_end = 0
            
            # Use Bresenham's algorithm to find all squares between current and end square.
            shadow_squares = get_line((x, y), (x_end, y_end))

            # Skip the first square as it's the current square.
            for shadow_square in shadow_squares[1:]: 
                # Calculate distance from shadow square to start square.
                dist_to_cur_square = np.sqrt((x-shadow_square[0])**2 + (y-shadow_square[1])**2)

                # Calculate if the shadow square is low enough to be covered by the shadow,
                # and remember to multiply by 30 to accomodate the resolution of the map.
                if dem[shadow_square] <= cur_altitude - 30 * dist_to_cur_square * np.tan(cur_elevation):
                    shadow_mask[shadow_square] = 1
                else:
                    # Since the shadow squares are ordered, we skip the rest,
                    # if we run into a shadow square that isnt covered.
                    break
    return shadow_mask


@jit(nopython=True)
def shadow_mask(altitude, azimuth, elevation_map, nodata=-32768):
    # Intitiate shadow mask.
    shadow_map = np.full(elevation_map.shape, nodata, dtype=np.int16)

    # Change altitude and azimuth to radians.
    altitude = (altitude % 360) * np.pi / 180
    azimuth = (azimuth % 360) * np.pi / 180 # Minus 90 to fit the map's coordinate system.
    
    M, N = elevation_map.shape
    count = 0 # to see how far along we are
    for y in range(M):
        for x in range(N):
            count = count + 1
            if count % (N*M // 100) == 0: # print how far along we are
                print(int(100*count/(N*M)), 'percent done.')

            current_height = elevation_map[x, y]

            # Skip the square if it has no data.
            if current_height == nodata: 
                continue

            # Calculate the distance of the shadow cast by the current square.
            shadow_dist = current_height / np.tan(altitude)

            # Find the square where the shadow ends.
            if 0 <= azimuth < np.pi/2:
                delta_x = int(np.floor(shadow_dist * np.cos(azimuth) / 30))
                delta_y = int(np.floor(shadow_dist * np.sin(azimuth) / 30))
                x_end = x + delta_x
                y_end = y - delta_y
            elif np.pi/2 <= azimuth < np.pi:
                delta_x = int(np.floor(shadow_dist * np.sin(azimuth-np.pi/2) / 30))
                delta_y = int(np.floor(shadow_dist * np.cos(azimuth-np.pi/2) / 30))
                x_end = x - delta_x
                y_end = y - delta_y
            elif np.pi <= azimuth < 3*np.pi/2:
                delta_x = int(np.floor(shadow_dist * np.cos(azimuth-np.pi) / 30))
                delta_y = int(np.floor(shadow_dist * np.sin(azimuth-np.pi) / 30))
                x_end = x - delta_x
                y_end = y + delta_y
            else:
                delta_x = int(np.floor(shadow_dist * np.sin(azimuth-(3*np.pi/2)) / 30))
                delta_y = int(np.floor(shadow_dist * np.cos(azimuth-(3*np.pi/2)) / 30))
                x_end = x + delta_x
                y_end = y + delta_y

            # Adjust if the end square is out of bounds.
            if x_end >= N:
                x_end = int(N-1)
            elif x_end < 0:
                x_end = 0
            
            if y_end >= M:
                y_end = int(M-1)
            elif y_end < 0:
                y_end = 0
            
            # Use Bresenham's algorithm to find all squares between current and end square.
            shadow_squares = get_line((x, y), (x_end, y_end))

            # Skip the first square as it's the current square.
            for shadow_square in shadow_squares[1:]: 
                # Calculate distance from shadow square to start square.
                dist_to_cur_square = np.sqrt((x-shadow_square[0])**2 + (y-shadow_square[1])**2)

                # Calculate if the shadow square is low enough to be covered by the shadow,
                # and remember to multiply by 30 to accomodate the resolution of the map.
                if elevation_map[shadow_square] <= current_height - 30 * dist_to_cur_square * np.tan(altitude):
                    shadow_map[shadow_square] = 1
                else:
                    # Since the shadow squares are ordered, we skip the rest,
                    # if we run into a shadow square that isnt covered.
                    break
    return shadow_map


@jit(nopython=True)
def get_line(start, end):
    """
    Accustomed from: http://www.roguebasin.com/index.php?title=Bresenham%27s_Line_Algorithm#Python
    """
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
 
    # Determine how steep the line is.
    is_steep = abs(dy) > abs(dx)
 
    # Rotate line.
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
 
    # Swap start and end points if necessary and store swap state.
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True
 
    # Recalculate differentials.
    dx = x2 - x1
    dy = y2 - y1
 
    # Calculate error.
    error = int(dx / 2.0)
    if y1 < y2:
        ystep = 1
    else:
        ystep = -1
 
    # Iterate over bounding box generating points between start and end.
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        if is_steep:
            coord = (y, x)
        else:
            coord = (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y = y + ystep
            error = error + dx
 
    # Reverse the list if the coordinates were swapped.
    if swapped:
        points.reverse()
    return points