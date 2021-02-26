import os
import datetime

import numpy as np
import rasterio as rio
from pandas import date_range
from tqdm import tqdm

from config import RAW_DATA_DIRECTORY, PREP_DATA_DIRECTORY
from ._base import fetch_url, dataset_is_fetched, dataset_is_preprocessed,\
    _crop_raster_to_shapefile
from ..utils import *


def load_cloud_cover(year, month, day, hour):
    """Description

    Parameters
    ----------
    country : string
        The country from which to load cloud_cover dataset.
    date_range : tuple
        The dates from which to load cloud_cover dataset (start, end) where dates
        are formatted strings as 'YYYY-MM-DD'.
    
    Returns
    -------

    Examples
    --------
    >>> nga_cloud_cover = load_cloud_cover('nigeria')

    """

    # If statement to check if the dataset is already downloaded.
    if not dataset_is_fetched('meteosat'):
        _fetch_cloud_cover(start_date, end_date)
    
    if not dataset_is_preprocessed('cloud_cover'):
        _preprocess_cloud_cover()
    
    cloud_cover_filename = day_to_string(day) + '_' + hour_to_string(closest_third_hour(hour)) + '.tif'
    cloud_cover_directory = PREP_DATA_DIRECTORY / 'cloud_cover' / str(year) / month_to_string(month)
    return rio.open(cloud_cover_directory / cloud_cover_filename)


def _fetch_cloud_cover(start_date, end_date):
    print('Fetching dataset. This can take a while.')

    # Setup folders to prepare for the dataset.
    output_directory = RAW_DATA_DIRECTORY / 'meteosat'
    output_directory.mkdir(parents=True, exist_ok=True)
    
    # McFetch link for raw Meteosat-11 data.
    #api_key = '66eda7fc-8ef7-11ea-b010-a0369f818cc4'
    api_key = '240f281c-4692-11ea-b63b-a0369f818cc4'
                   #'https://mcfetch.ssec.wisc.edu/cgi-bin/mcfetch?dkey={api_key}&satellite=MET11&band=4&output=GEOTIFF&date=2019-09-11&time=01:30&lat=7.34+-7.09&size=4+4&mag=-1+-1'
    mcfetch_url = f'https://mcfetch.ssec.wisc.edu/cgi-bin/mcfetch?dkey={api_key}&satellite=MET10&output=GEOTIFF&lat=9+-8.5&size=380+450&mag=-1+-1'
    # &satellite=MET11&band=1&output=GEOTIFF&date=2020-01-02&time=12:00&lat=9+-8.5&size=380+450&mag=-1+-1'

    # Fetch raw data of Meteosat-10 from SSEC.
    tracker = 0
    for date in tqdm(date_range(start_date, end_date, freq='3H', closed='left')):
        # The 11 full disk (FD) bands.
        # First 3 are useless.
        for band in range(4, 12):
            if tracker == 1000:
                print('Reached daily quota.')
                exit()

            # Construct the url.
            url = '&'.join([
                mcfetch_url,
                f'band={band}',
                'date=' + date.strftime('%Y-%m-%d'),
                'time=' + date.strftime('%H:%M')
            ])

            # Fetch the url.
            name = date.strftime('%Y%m%d%H%M') + '_' + str(band) + '.tif'
            fetch_url(url, output_directory / name)

            # Increment tracker.
            tracker += 1


def _preprocess_cloud_cover(hours=[6, 9, 12, 15]):
    print('Preprocessing dataset. This can take a while.')

    # Setup folders to prepare for the dataset.
    cloud_cover_directory = PREP_DATA_DIRECTORY / 'cloud_cover'
    cloud_cover_directory.mkdir(parents=True, exist_ok=True)

    # Check which dates are found.
    missing_dates = _missing_dates()

    for idx, date in tqdm(enumerate(missing_dates)):
        cur_file = date + f'_2.tif'
        try:
            cur_raster = rio.open(RAW_DATA_DIRECTORY / 'meteosat' / cur_file)
            cur_array = cur_raster.read(1).astype(np.float32) / 255
        except:
            # If fails to load, save the previous cloud_cover raster as this one.
            prev_missing_date = missing_dates[idx-1]
            prev_year = prev_missing_date[:4]
            prev_month = prev_missing_date[4:6]
            prev_day = prev_missing_date[6:8] + '_' + prev_missing_date[8:10] + '.tif'
            prev_cloud_cover_path = cloud_cover_directory / prev_year / prev_month / prev_day
            prev_cloud_cover = rio.open(prev_cloud_cover_path)
            _save_cloud_cover(prev_cloud_cover.read(1), date, prev_cloud_cover.meta)
            continue
        # Load albedo for this day
        year = date[:4]
        month = date[4:6]
        day = date[6:8] + '.tif'
        albedo_path = PREP_DATA_DIRECTORY / 'albedo' / year / month / day
        albedo_array = rio.open(albedo_path).read(1)
        valid_idxs = np.nonzero(albedo_array != -32768)

        # Subtract albedo and save cloud cover
        _save_cloud_cover(cur_array, date, cur_raster.meta)

        # Crop
        filename = date[6:8] + '_' + date[8:10] + '.tif'
        _crop_raster_to_shapefile(
            PREP_DATA_DIRECTORY / 'cloud_cover' / year / month / filename
        )

        cur_raster = rio.open(
            PREP_DATA_DIRECTORY / 'cloud_cover' / year / month / filename
        )
        cur_array = cur_raster.read(1)
        cur_array[valid_idxs] -= albedo_array[valid_idxs]
        cur_array[valid_idxs] = cur_array[valid_idxs] / (1-albedo_array[valid_idxs])
        cur_array[cur_array < 0] = 0
        _save_cloud_cover(cur_array, date, cur_raster.meta)


def _save_cloud_cover(cloud_cover_array, date, meta):
    # Output directory
    year = date[:4]
    month = date[4:6]
    output_directory = PREP_DATA_DIRECTORY / 'cloud_cover' / year / month
    output_directory.mkdir(parents=True, exist_ok=True)

    # Filename
    day = date[6:8]
    hour = date[8:10]
    filename = day + '_' + hour + '.tif'

    # Save cloud_cover raster
    meta_dict = meta
    meta_dict.update({'dtype': np.float32, 'nodata': -32768})
    cloud_cover_array[cloud_cover_array == 0] = -32768
    cloud_cover = rio.open(
        output_directory / filename,
        'w',
        **meta_dict
    )
    cloud_cover.write(cloud_cover_array, 1)
    cloud_cover.close()


def _missing_dates():
    available_dates = set((RAW_DATA_DIRECTORY / 'meteosat').iterdir())
    available_dates = set([date.stem.split('_')[0] for date in available_dates])
    processed_dates = set()
    for year in (PREP_DATA_DIRECTORY / 'cloud_cover').iterdir():
        for month in year.iterdir():
            for day_hour in month.iterdir():
                day, hour = day_hour.stem.split('_')
                processed_date = year.stem + month.stem + day + hour + '00'
                if processed_date in available_dates:
                    processed_dates.add(processed_date)
    return sorted(available_dates-processed_dates)

