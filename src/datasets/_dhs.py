import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from tqdm import tqdm

from config import RAW_DATA_DIRECTORY, PREP_DATA_DIRECTORY, HR_COLS, GEO_COLS,\
    NIGERIA_SHAPEFILE
from ._base import fetch_url, dataset_is_fetched, dataset_is_preprocessed
from ..utils import find_corners, haversine_dist


def load_dhs():
    """TBA
    
    Returns
    -------
    dhs : pd.DataFrame
        DataFrame of DHS data.

    Examples
    --------
    >>> nga_dhs = load_dhs()
    """

    # If statement to check if the dataset is already downloaded.
    if not dataset_is_preprocessed('dhs'):
        _preprocess_dhs()
    
    dataset_path = PREP_DATA_DIRECTORY / 'dhs/all_years.csv'
    dhs = pd.read_csv(dataset_path)
    return dhs


def _preprocess_dhs():
    print('Preprocessing dataset. This can take a while.')

    # Setup folders to prepare for the dataset.
    output_directory = PREP_DATA_DIRECTORY / 'dhs'
    output_directory.mkdir(parents=True, exist_ok=True)

    # Prepare files.
    dhs_df = pd.DataFrame()
    raw_dhs_directory = RAW_DATA_DIRECTORY / 'dhs'
    nigeria_shape = gpd.read_file(NIGERIA_SHAPEFILE)

    # Preprocess DHS for each year.
    for year_dir in tqdm(list(raw_dhs_directory.iterdir())):
        if year_dir.is_dir():
            # Find HR and GE file for year.
            hr_df, ge_df = _find_household_and_geographic_recode(year_dir)
            # Aggregate households into clusters.
            cur_df = hr_df.groupby('hv001')['has_electricity'].agg(['sum', 'count']).reset_index()
            # Merge household and geo files.
            cur_df = cur_df.merge(ge_df, how='left', left_on='hv001', right_on='DHSCLUST')
            # Drop clusters with invalid lon/lats.
            cur_df = cur_df.loc[(cur_df['LONGNUM'] != 0) & (cur_df['LATNUM'] != 0)].copy()
            # Validly displace households.
            #cur_df = _displace_households(cur_df, valid_polygon=nigeria_shape['geometry'][0])
            dhs_df = pd.concat([dhs_df, cur_df])
    dhs_df = dhs_df.rename(columns={'sum': 'has_electricity', 'count': 'total'})
    dhs_df.to_csv(output_directory / 'all_years.csv', index=False)


def _displace_households(df, cluster_col='DHSCLUST', urban_rura_col='URBAN_RURA',
        lon_col='LONGNUM', lat_col='LATNUM', valid_polygon=None):
    clusters = df[cluster_col].unique()
    for cluster in clusters:
        df = _displace_households_in_cluster(
            df,
            cluster,
            cluster_col,
            urban_rura_col,
            lon_col,
            lat_col,
            valid_polygon
        )
    return df.copy()


def _displace_households_in_cluster(df, cluster, cluster_col, urban_rura_col,
        lon_col, lat_col, valid_polygon=None):
    # Find cluster.
    cluster_df = df.loc[df[cluster_col] == cluster, [lon_col, lat_col, urban_rura_col]]
    n_households = cluster_df.shape[0]
    lon = cluster_df[lon_col].unique()[0]
    lat = cluster_df[lat_col].unique()[0]
    urban_rura = cluster_df[urban_rura_col].unique()[0]

    # Specify buffer.
    if urban_rura == 'U':
        buffer = 2000
    elif urban_rura == 'R':
        buffer = 5000

    # Find new valid lons and lats for all households in cluster.
    xlon, xlat, ylon, ylat = find_corners(lon, lat, buffer)
    new_lons = np.random.uniform(xlon, ylon, size=n_households)
    new_lats = np.random.uniform(xlat, ylat, size=n_households)

    lons = [lon]*n_households
    lats = [lat]*n_households
    points_outside_buffer = np.flatnonzero(haversine_dist(lons, lats, new_lons, new_lats) > buffer)
    invalid_points = np.flatnonzero(list(map(
        valid_polygon.within,
        gpd.GeoSeries(map(Point, zip(new_lons, new_lats)))
    )))
    wrong_idxs = np.union1d(points_outside_buffer, invalid_points)
    while len(wrong_idxs) > 0:
        # Keep finding new points within circumscribed square.
        cur_lons = np.random.uniform(xlon, ylon, size=len(wrong_idxs))
        cur_lats = np.random.uniform(xlat, ylat, size=len(wrong_idxs))

        # Put new points into array.
        new_lons[wrong_idxs] = cur_lons
        new_lats[wrong_idxs] = cur_lats

        # Recalculate whether all points are inside buffer and valid.
        lons = [lon]*len(wrong_idxs) 
        lats = [lat]*len(wrong_idxs) 
        points_outside_buffer = np.flatnonzero(haversine_dist(lons, lats, cur_lons, cur_lats) > buffer)
        invalid_points = np.flatnonzero(list(map(
            valid_polygon.within,
            gpd.GeoSeries(map(Point, zip(cur_lons, cur_lats)))
        )))
        wrong_idxs = np.union1d(points_outside_buffer, invalid_points)
    
    # Insert the newly found points for households into original dataframe.
    df.loc[df[cluster_col] == cluster, lon_col] = new_lons
    df.loc[df[cluster_col] == cluster, lat_col] = new_lats

    # Add total number of houses with electricity in cluster.
    

    return df.copy()


def _find_household_and_geographic_recode(year_dir):
    for dataset_type_dir in year_dir.iterdir():
        dataset_type = dataset_type_dir.stem[2:4]
        if dataset_type == 'HR':
            for f in dataset_type_dir.iterdir():
                if f.suffix == '.DTA':
                    hr_df = pd.read_stata(f, columns=HR_COLS)
                    hr_df['hv206'] = hr_df['hv206'].str.lower()
                    hr_df['has_electricity'] = hr_df['hv206'].map({'yes': 1, 'no': 0})
        if dataset_type == 'GE':
            for f in dataset_type_dir.iterdir():
                if f.suffix == '.shp':
                    ge_df = gpd.read_file(f)[GEO_COLS]
    return hr_df, ge_df
