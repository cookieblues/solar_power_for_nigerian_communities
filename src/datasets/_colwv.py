import numpy as np
import pygrib
import rasterio as rio
from ecmwfapi import ECMWFDataServer
from tqdm import tqdm

from config import RAW_DATA_DIRECTORY, PREP_DATA_DIRECTORY
from ._base import dataset_is_fetched, dataset_is_preprocessed,\
    _crop_raster_to_shapefile
from ..utils import *


def load_colwv(year, month, hour):
    """TBA

    Parameters
    ----------
    
    Returns
    -------
    colwv : 

    Examples
    --------
    >>> nga_colwv = load_colwv()
    """

    # If statement to check if the dataset is already downloaded.
    if not dataset_is_fetched('cams_reanalysis/all_years.grb'):
        _fetch_colwv()
    
    if not dataset_is_preprocessed('colwv'):
        _preprocess_colwv()
    
    colwv_filename = month_to_string(month) + '_' + hour_to_string(closest_third_hour(hour)) + '.tif'
    colwv_directory = PREP_DATA_DIRECTORY / 'colwv' / str(year)
    # colwv_dict = {str(i)[1:]: dict() for i in range(101, 113)}
    # for year_dir in colwv_directory.iterdir():
    #     if year_dir.stem == str(year):
    #         for colwv_file in year_dir.iterdir():
    #             if colwv_file.suffix == '.tif':
    #                 month, time = colwv_file.stem.split('_')
    #                 colwv_dict[month][time] = rio.open(colwv_file)
    return rio.open(colwv_directory / colwv_filename)


def _fetch_colwv():
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


def _preprocess_colwv():
    print('Preprocessing dataset. This can take a while.')

    # Setup folders to prepare for the dataset.
    output_directory = PREP_DATA_DIRECTORY / 'colwv'
    output_directory.mkdir(parents=True, exist_ok=True)
    raw_dataset_path = RAW_DATA_DIRECTORY / 'cams_reanalysis/all_years.grb'
    cams_reanalysis = pygrib.open(str(raw_dataset_path))
    colwvs = cams_reanalysis.select(name='Total column water vapour')

    for colwv in tqdm(colwvs):
        date = str(colwv.dataDate)
        time = str(colwv.dataTime)

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

        colwv_data = colwv.values
        height, width = colwv_data.shape

        # Adjust grid.
        first_lon = colwv['longitudeOfFirstGridPointInDegrees']
        last_lon = colwv['longitudeOfLastGridPointInDegrees']
        first_lat = colwv['latitudeOfFirstGridPointInDegrees']
        last_lat = colwv['latitudeOfLastGridPointInDegrees']
        # need to shift data grid longitudes from (0..360) to (-180..180)
        lons = np.linspace(float(first_lon), float(last_lon), width) - 180
        lats = np.linspace(float(first_lat), float(last_lat), height)
        colwv_data = np.roll(colwv_data, 256, axis=1)

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
            dtype=colwv_data.dtype,
            crs='EPSG:4326',
            transform=transform,
        )
        new_dataset.write(colwv_data, 1)
        new_dataset.close()

        _crop_raster_to_shapefile(year_directory / filename)
