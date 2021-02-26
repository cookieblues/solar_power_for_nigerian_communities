from pathlib import Path

import numpy as np
import rasterio as rio
from numba import njit, jit, prange
from tqdm import tqdm

from config import DATA_DIRECTORY, PROC_DATA_DIRECTORY
from src.utils import *
from src import datasets
from src.spa import solar_position
from src.feature_engineering import calc_shadow_mask, clear_sky_irradiance


def _dem_array(stepsize):
    """TBA.
    """
    nga_elevation = datasets.load_elevation()
    n_rows, n_cols = nga_elevation.meta['height'], nga_elevation.meta['width']

    rows = np.arange(int((stepsize-1)/2), int(n_rows+1), step=stepsize, dtype=np.int32)
    cols = np.arange(int((stepsize-1)/2), int(n_cols+1), step=stepsize, dtype=np.int32)
    
    n_rows, n_cols = len(rows), len(cols)
    rows, cols = np.meshgrid(rows, cols, copy=False, indexing='ij')
    
    print('Creating DEM array, this might take a while.')
    
    lons, lats = nga_elevation.xy(cols.ravel(), rows.ravel())
    elevs = nga_elevation.read(1)[rows, cols]

    dem_array = np.zeros((n_rows, n_cols, 3))
    dem_array[:, :, 0] = np.array(lons).reshape((n_rows, n_cols))
    dem_array[:, :, 1] = np.array(lats).reshape((n_rows, n_cols))
    dem_array[:, :, 2] = elevs
    np.save(DATA_DIRECTORY / 'dem_array', dem_array, allow_pickle=False)


def solar_position_array(year, month, day, hour, create_solar_pos_array=False, create_dem_array=False, stepsize=1):
    """TBA.
    """
    if not (DATA_DIRECTORY / 'dem_array.npy').exists():
        print("DEM array doesn't exist.")
        _dem_array(stepsize)
    elif create_dem_array:
        print("DEM array exists, overwriting.")
        _dem_array(stepsize)
    if create_solar_pos_array:
        dem_array = np.load(DATA_DIRECTORY / 'dem_array.npy')
        rows, cols = dem_array.shape[0], dem_array.shape[1]
        solar_pos_array = np.zeros((rows, cols, 3))

        lons = dem_array[:, :, 0].ravel()
        lats = dem_array[:, :, 1].ravel()
        elevs = dem_array[:, :, 2].ravel()

        elevations, azimuths, aois = _solar_position_array(year, month, day, hour, lons, lats, elevs)
        solar_pos_array[:, :, 0] = elevations.reshape((rows, cols))
        solar_pos_array[:, :, 1] = azimuths.reshape((rows, cols))
        solar_pos_array[:, :, 2] = aois.reshape((rows, cols))

        np.save(DATA_DIRECTORY / 'solar_position_array', solar_pos_array, allow_pickle=False)
        return solar_pos_array
    elif (DATA_DIRECTORY / 'solar_position_array.npy').exists():
        return np.load(DATA_DIRECTORY / 'solar_position_array.npy')


@jit(nopython=True)
def angle_of_incidence(sol_elev, sol_a, arr_t=0.10471975511965978, arr_a=np.pi):
    """TBA.
    """
    sol_z = np.pi/2 - sol_elev
    aoi = np.arccos(np.cos(sol_z)*np.cos(arr_t)+np.sin(sol_z)*np.sin(arr_t)*np.cos(sol_a-arr_a))
    if 0 <= aoi <= np.pi/4:
        return aoi
    else:
        return np.pi/4


@njit(parallel=True)
def _solar_position_array(year, month, day, hour, lons, lats, elevs):
    """TBA.
    """
    elevations = np.zeros(lons.shape)
    azimuths = np.zeros(lons.shape)
    aois = np.zeros(lons.shape)

    for i in prange(len(lons)):        
        cur_lon, cur_lat, cur_elev = lons[i], lats[i], elevs[i]
        
        elev_angle, azimuth = solar_position(
            cur_lat,
            cur_lon,
            cur_elev,
            year,
            month,
            day,
            hour
        )
        elevations[i] = elev_angle
        azimuths[i] = azimuth
        aois[i] = angle_of_incidence(elev_angle, azimuth)
    return elevations, azimuths, aois


start_year = 2014
end_year = 2015

months = [i for i in range(1, 13)]
days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
hours = [9, 12]

nga_elevation = datasets.load_elevation()

pbar = tqdm(total=(end_year-start_year+1)*sum(days_per_month)*len(hours))
for year in range(start_year, end_year+1):
    for month in months:
        days = days_per_month[month-1]
        if year % 4 == 0 and month == 2:
            days += 1
        for day in range(1, days+1):
            for hour in hours:
                ### Calculate elevation angle and azimuth
                solar_pos = solar_position_array(year, month, day, hour, create_solar_pos_array=True)



                nga_coloz = datasets.load_coloz(year, month, hour)
                nga_colwv = datasets.load_colwv(year, month, hour)
                nga_aod = datasets.load_aod(year, month, hour)
                nga_albedo = datasets.load_albedo(year, month, day)
                nga_cloud_cover = datasets.load_cloud_cover(year, month, day, hour)

                clear_sky_irr = clear_sky_irradiance(
                    solar_pos[:, :, 0],
                    solar_pos[:, :, 2],
                    nga_elevation.read(1),
                    nga_coloz.read(1),
                    nga_colwv.read(1),
                    nga_aod.read(1),
                    nga_albedo.read(1),
                    nga_cloud_cover.read(1),
                    year,
                    month,
                    day
                )
                str_month = month_to_string(month)
                str_day = day_to_string(day)
                str_hour = hour_to_string(hour)
                path = Path(f'/media/hdd1/data/processed/{year}/{str_month}/')
                path.mkdir(parents=True, exist_ok=True)
                filename = f'{str_day}_{str_hour}.tif'
                save_array_to_geotiff(clear_sky_irr, path / filename, nga_elevation.meta)
                pbar.update(1)
pbar.close()


