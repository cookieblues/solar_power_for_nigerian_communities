import numpy as np
from tqdm import tqdm

from ..utils import haversine_dist, find_corners


def _minmax(val, min_val, max_val):
    return min(max(min_val, val), max_val)


def _extract_circle(lon, lat, buffer, raster, x_max, y_max):
    # Calcuate corners of circumscribed square.
    xlon, xlat, ylon, ylat = find_corners(lon, lat, buffer)

    # Find indices of corners in raster file.
    upper_left_row, upper_left_col = raster.index(xlon, xlat)
    upper_left_row = _minmax(upper_left_row, 0, x_max)
    upper_left_col = _minmax(upper_left_col, 0, y_max)
    lower_right_row, lower_right_col = raster.index(ylon, ylat)
    lower_right_row = _minmax(lower_right_row, 0, x_max)
    lower_right_col = _minmax(lower_right_col, 0, y_max)
    
    # Get longitude and latitude of all points in circumscribed square.
    xs = np.arange(upper_left_row, lower_right_row+1)
    ys = np.arange(upper_left_col, lower_right_col+1)
    xs, ys = np.meshgrid(xs, ys)
    lons, lats = raster.xy(xs.ravel(), ys.ravel())

    # Return points that are within buffer.
    square_idxs = np.column_stack([xs.ravel(), ys.ravel()])
    lon = [lon]*len(lons)
    lat = [lat]*len(lats)
    idxs_to_keep = np.flatnonzero(haversine_dist(lon, lat, lons, lats) <= buffer)
    return square_idxs[idxs_to_keep]


def extract_circle(lons, lats, buffer, raster, statistic=None):
    """TBA
    """
    statistics = list()
    raster_array = raster.read(1)
    x_max, y_max = raster_array.shape
    for lon, lat in list(zip(lons, lats)):
        circle_points = _extract_circle(lon, lat, buffer, raster, x_max-1, y_max-1)
        # Calculate statistic for points in circle if given.
        if statistic:
            rows = circle_points[:, 0]
            cols = circle_points[:, 1]
            values = raster_array[rows, cols]
            values = values[np.flatnonzero(values != raster.nodata)]
            statistics.append(statistic(values))
    if statistic:
        return statistics
    else:
        return circle_points
