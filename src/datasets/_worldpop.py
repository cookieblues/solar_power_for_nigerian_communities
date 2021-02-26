import rasterio as rio
from tqdm import tqdm

from config import RAW_DATA_DIRECTORY
from ._base import fetch_url, dataset_is_fetched


def load_worldpop(year):
    """TBA

    Parameters
    ----------
    year : int
        The year from which you want the spatial distribution of population
        from WorldPop.
    
    Returns
    -------
    worldpop : DatasetReader object
        The raster of the spatial distribution of population in Nigeria for a
        given year.

    Examples
    --------
    >>> nga_worldpop = load_worldpop(2010)
    >>> nga_worldpop.meta
    >>> nga_worldpop.read(1)
    """

    # If statement to check if the dataset is already downloaded.
    if not dataset_is_fetched(f'worldpop/{year}.tif'):
        _fetch_worldpop(year)
    
    dataset_path = RAW_DATA_DIRECTORY / f'worldpop/{year}.tif'
    worldpop = rio.open(dataset_path)
    return worldpop


def _fetch_worldpop(year):
    print('Fetching dataset. This can take a while.')

    # Setup folders to prepare for the dataset.
    directory = RAW_DATA_DIRECTORY / 'worldpop'
    directory.mkdir(parents=True, exist_ok=True)

    # WorldPop url.
    worldpop_url = f'ftp://ftp.worldpop.org.uk/GIS/Population/Global_2000_2020/{year}/NGA/nga_ppp_{year}.tif'

    # Fetch spatial distribution of population from WorldPop.
    path = directory / f'{year}.tif'
    fetch_url(worldpop_url, path)


def _prepare_worldpop(year):
    NotImplementedError()
