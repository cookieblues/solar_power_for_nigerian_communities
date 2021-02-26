import os
import datetime

from tqdm import tqdm
from pandas import date_range

from ._base import fetch_url, dataset_is_fetched, get_data_directory
#from ..utils import day_range, hour_range


def load_infrared(country, start_date='2019-01-01', end_date='2019-02-01'):
    """Description

    Parameters
    ----------
    country : string
        The country from which to load infrared dataset.
    date_range : tuple
        The dates from which to load infrared dataset (start, end) where dates
        are formatted strings as 'YYYY-MM-DD'.
    
    Returns
    -------

    Examples
    --------
    >>> nga_infrared = load_infrared('nigeria')

    """

    # If statement to check if the dataset is already downloaded.
    if not dataset_is_fetched(country, 'infrared'):
        _fetch_infrared(country, start_date, end_date)
        _prepare_infrared(country)
    
    raise NotImplementedError()
    path = f'{get_data_directory()}/interim/{country}/infrared/{band}/alos_aw3d30.tif'
    infrared = rio.open(path)
    return infrared


def _fetch_infrared(country, start_date, end_date):
    print('Fetching dataset. This can take a while.')

    # Setup folders to prepare for the dataset.
    raw_data_path = f'{get_data_directory()}/raw/{country}/infrared'
    os.makedirs(raw_data_path)
    
    # McFetch link for raw Meteosat-11 data.
    api_key = '240f281c-4692-11ea-b63b-a0369f818cc4'
    mcfetch_url = f'https://mcfetch.ssec.wisc.edu/cgi-bin/mcfetch?dkey={api_key}&satellite=MET11&output=GEOTIFF&lat=9+-8.5&size=380+450&mag=-1+-1'
    
    
    # &satellite=MET11&band=1&output=GEOTIFF&date=2020-01-02&time=12:00&lat=9+-8.5&size=380+450&mag=-1+-1'

    # Fetch raw data of Meteosat-11 from SSEC.
    for date in tqdm(date_range(start_date, end_date, freq='15min')):
        # The 11 full disk (FD) bands.
        for band in range(1, 12):
            # Construct the url.
            url = '&'.join([
                mcfetch_url,
                f'band={band}',
                'date=' + date.strftime('%Y-%m-%d'),
                'time=' + date.strftime('%H:%M')
            ])

            # Fetch the url.
            name = date.strftime('%Y%m%d%H%M') + '_' + str(band) + '.tif'
            fetch_url(url, os.path.join(raw_data_path, name))


def _prepare_infrared(country, band):
    raise NotImplementedError()



