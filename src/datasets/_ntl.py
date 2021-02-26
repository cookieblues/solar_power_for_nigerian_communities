import rasterio as rio
from tqdm import tqdm

from config import RAW_DATA_DIRECTORY
from ._base import fetch_url, dataset_is_fetched


def load_ntl(year):
    """TBA

    Parameters
    ----------
    year : int
        TBA.
    
    Returns
    -------
    ntl : DatasetReader object
        TBA.

    Examples
    --------
    >>> nga_ntl = load_ntl(2010)
    >>> nga_ntl.meta
    >>> nga_ntl.read(1)
    """

    # If statement to check if the dataset is already downloaded.
    if not dataset_is_fetched(f'ntl/{year}.tif'):
        _fetch_ntl(year)
    
    dataset_path = RAW_DATA_DIRECTORY / f'ntl/{year}.tif'
    ntl = rio.open(dataset_path)
    return ntl


def _fetch_ntl(year):
    print('Fetching dataset. This can take a while.')

    # Setup folders to prepare for the dataset.
    directory = RAW_DATA_DIRECTORY / 'ntl'
    directory.mkdir(parents=True, exist_ok=True)

    # ntl url.
    ntl_url = f'https://geodata.globalhealthapp.net/images/gp{year}africa.tif'

    # Fetch spatial distribution of population from ntl.
    path = directory / f'{year}.tif'
    fetch_url(ntl_url, path)


def _prepare_ntl(year):
    NotImplementedError()
