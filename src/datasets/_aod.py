import numpy as np
import pygrib
import rasterio as rio
from ecmwfapi import ECMWFDataServer
from tqdm import tqdm

from config import RAW_DATA_DIRECTORY, PREP_DATA_DIRECTORY
from ._base import dataset_is_fetched, dataset_is_preprocessed,\
    _crop_raster_to_shapefile
from ..utils import *


def load_aod(year, month, hour):
    """TBA

    Parameters
    ----------
    
    Returns
    -------
    aod : 

    Examples
    --------
    >>> nga_aod = load_aod()
    """

    # If statement to check if the dataset is already downloaded.
    if not dataset_is_fetched('cams_reanalysis/all_years.grb'):
        _fetch_aod()
    
    if not dataset_is_preprocessed('aod'):
        _preprocess_aod()
    
    aod_filename = month_to_string(month) + '_' + hour_to_string(closest_third_hour(hour)) + '.tif'
    aod_directory = PREP_DATA_DIRECTORY / 'aod' / str(year)
    # aod_dict = {str(i)[1:]: dict() for i in range(101, 113)}
    # for year_dir in aod_directory.iterdir():
    #     if year_dir.stem == str(year):
    #         for aod_file in year_dir.iterdir():
    #             if aod_file.suffix == '.tif':
    #                 month, time = aod_file.stem.split('_')
    #                 aod_dict[month][time] = rio.open(aod_file)
    return rio.open(aod_directory / aod_filename)


def _fetch_aod():
    print('Fetching dataset. This can take a while.')

    # Setup folders to prepare for the dataset.
    output_directory = RAW_DATA_DIRECTORY / 'cams_reanalysis'
    output_directory.mkdir(parents=True, exist_ok=True)

    # Create all dates.
    dates = list()
    for year in range(2003, 2019):
        for month in range(1, 13):
            if month < 10:
                month = '0' + str(month)
            date = str(year) + str(month) + '01'
            dates.append(date)

    dates_string = '/'.join([date for date in dates])

    # Fetch files from ECMWF.
    server = ECMWFDataServer()
    server.retrieve({
        'class': 'mc',
        'dataset': 'cams_reanalysis',
        'date': dates_string,
        'expver': 'eac4',
        'levtype': 'sfc',
        'param': '137.128/206.210/207.210', # Total aerosol optical depth at 550 nm, water vapour total column
        'stream': 'mnth',
        'time': '00:00:00/03:00:00/06:00:00/09:00:00/12:00:00/15:00:00/18:00:00/21:00:00',
        'type': 'an',
        'target': str(output_directory / 'all_years.grb')
    })


def _preprocess_aod():
    print('Preprocessing dataset. This can take a while.')

    # Setup folders to prepare for the dataset.
    output_directory = PREP_DATA_DIRECTORY / 'aod'
    output_directory.mkdir(parents=True, exist_ok=True)
    raw_dataset_path = RAW_DATA_DIRECTORY / 'cams_reanalysis/all_years.grb'
    cams_reanalysis = pygrib.open(str(raw_dataset_path))
    aods = cams_reanalysis.select(name='Total Aerosol Optical Depth at 550nm')

    for aod in tqdm(aods):
        date = str(aod.dataDate)
        time = str(aod.dataTime)

        # Create year folder.
        year = date[:4]
        year_directory = output_directory / year
        year_directory.mkdir(parents=True, exist_ok=True)

        # Create filename.
        month = date[4:6]
        if len(time) == 1:
            time = '00'
        elif len(time) == 3:
            time = '0' + time[0]
        elif len(time) == 4:
            time = time[:2]
        filename = month + '_' + time + '.tif'

        aod_data = aod.values
        height, width = aod_data.shape

        # Adjust grid.
        first_lon = aod['longitudeOfFirstGridPointInDegrees']
        last_lon = aod['longitudeOfLastGridPointInDegrees']
        first_lat = aod['latitudeOfFirstGridPointInDegrees']
        last_lat = aod['latitudeOfLastGridPointInDegrees']
        # need to shift data grid longitudes from (0..360) to (-180..180)
        lons = np.linspace(float(first_lon), float(last_lon), width) - 180
        lats = np.linspace(float(first_lat), float(last_lat), height)
        aod_data = np.roll(aod_data, 256, axis=1)

        # Create transformation.
        res = (lons[-1] - lons[0]) / width
        transform = rio.transform.from_bounds(min(lons), min(lats), max(lons) + res, max(lats), width, height)

        # Save as raster.
        new_dataset = rio.open(
            year_directory / filename,
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=1,
            dtype=aod_data.dtype,
            crs='EPSG:4326',
            transform=transform,
        )
        new_dataset.write(aod_data, 1)
        new_dataset.close()

        _crop_raster_to_shapefile(year_directory / filename)


