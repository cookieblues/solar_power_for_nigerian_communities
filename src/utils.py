import os
from datetime import datetime, timedelta
from warnings import warn
from itertools import product

import numpy as np
import rasterio as rio

from config import COUNTRIES


def add_dist_to_latitude(lat, dist, radius=6378000):
    lat = np.radians(lat)
    lat_rad = lat - dist/radius
    return np.degrees(lat_rad)


def add_dist_to_longitude(lon, lat, dist, radius=6378000):
    lat, lon = np.radians(lat), np.radians(lon)
    lon_rad = lon - 2*np.arcsin(1/np.cos(lat) * np.sin(dist/(2*radius)))
    return np.degrees(lon_rad)


def find_corners(lon, lat, buffer):
    upper_left_lon = add_dist_to_longitude(lon, lat, buffer)
    upper_left_lat = add_dist_to_latitude(lat, -buffer)
    lower_right_lon = add_dist_to_longitude(lon, lat, -buffer)
    lower_right_lat = add_dist_to_latitude(lat, buffer)
    return upper_left_lon, upper_left_lat, lower_right_lon, lower_right_lat


def haversine(theta):
    return (1-np.cos(theta))/2


def haversine_dist(xlon, xlat, ylon, ylat):
    """Calculate the great circle distance between two points on the earth.
    """
    # Radius of earth at equator in metres.
    radius = 6378000

    # Convert latitudes and longitudes to radians.
    xlon, xlat, ylon, ylat = map(np.radians, [xlon, xlat, ylon, ylat])
    dlat = ylat-xlat
    dlon = ylon-xlon

    # Calculate great circle distance.
    h = np.sqrt(haversine(dlat) + np.cos(xlat)*np.cos(ylat)*haversine(dlon))
    dist = 2 * radius * np.arcsin(h)
    return dist


def latitude_longitude_bounds(country):
    warn('Latitude and longitude calculations currently only work for north\
        and east positions.')
    return COUNTRIES[country]


def latitude_longitude_ranges(country, as_string):
    lat_bounds, lon_bounds = latitude_longitude_bounds(country)

    # Get integers of min and max latitude and longitude.
    min_lat, max_lat = map(lambda x: int(x[-3:]), lat_bounds)
    min_lon, max_lon = map(lambda x: int(x[-3:]), lon_bounds)

    # Get all latitude and longitude degrees from min to max.
    lats = [i for i in range(min_lat, max_lat+1)]
    lons = [i for i in range(min_lon, max_lon+1)]
    if as_string:
        lats = list(map(latitude_to_string, lats))
        lons = list(map(longitude_to_string, lons))
    return lats, lons


def latitude_longitude_grid(country, as_string):
    lats, lons = latitude_longitude_ranges(country, as_string)
    return list(product(lats, lons))


def latitude_to_string(latitude):
    # Convert value to string and puts zeros in front.
    return f'N{latitude:>3}'.replace(' ', '0')


def longitude_to_string(longitude):
    # Convert value to string and puts zeros in front.
    return f'E{longitude:>3}'.replace(' ', '0')


def day_range(start, end):
    # Helper function for generating dates in a range with a frequency of a day.
    start = datetime.strptime(start, '%Y-%m-%d')
    end = datetime.strptime(end, '%Y-%m-%d')
    return [start + timedelta(days=n) for n in range(0, (end-start).days)]


def hour_range(start, end):
    # Helper function for generating dates in a range with a frequency of an hour.
    start = datetime.strptime(start, '%Y-%m-%d')
    end = datetime.strptime(end, '%Y-%m-%d')
    n_hours = _timedelta_to_hours(end-start)
    return [start + timedelta(hours=n) for n in range(0, n_hours)]


def _timedelta_to_hours(td):
    hours = 0
    hours += td.days * 24
    hours += td.seconds // 3600
    return hours


def listfulldir(directory):
    # Helper function for listing absolute paths of files in directory.
    return [os.path.join(directory, f) for f in os.listdir(directory)]


def closest_third_hour(hour):
    if hour < 0 or hour > 24:
        ValueError('Invalid hour.')
    return int(np.round(hour/3)*3)


def hour_to_string(hour):
    if hour < 0 or hour > 24:
        ValueError('Invalid hour.')
    hour = str(hour)
    if len(hour) == 1:
        hour = '0' + hour
    return hour


def day_to_string(day):
    if day < 1 or day > 31:
        ValueError('Invalid day.')
    day = str(day)
    if len(day) == 1:
        day = '0' + day
    return day


def month_to_string(month):
    if month < 1 or month > 12:
        ValueError('Invalid month.')
    month = str(month)
    if len(month) == 1:
        month = '0' + month
    return month


def save_array_to_geotiff(array, path, meta):
    """TBA.

    Parameters
    ----------
    array : np.array
        The array of values to save.

    path : string
        Path and filename to save array.

    meta : dict
        The dictionary of metadata for the raster.
    """
    meta.update({'dtype': np.float32})
    raster = rio.open(
        path,
        'w',
        **meta
    )
    raster.write(array.astype(np.float32), 1)
    raster.close()