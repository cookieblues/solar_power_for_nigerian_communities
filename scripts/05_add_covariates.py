import numpy as np
import matplotlib.pyplot as plt
import rasterio as rio
from scipy.stats import mode
from tqdm import tqdm

from config import PROC_DATA_DIRECTORY
from src.datasets import load_dhs, load_worldpop, load_landcover, load_viirs
from src.feature_engineering import extract_circle


def mode_(x):
    if len(mode(x)[0]) > 0:
        return mode(x)[0].item()
    else:
        return np.nan

dhs_df = load_dhs()
dhs_df['pia'] = np.nan
dhs_df['ntl'] = np.nan
dhs_df['landcover'] = np.nan
dhs_df['population'] = np.nan

for year in tqdm(range(2013, 2021)):
    cur_df = dhs_df.loc[dhs_df['DHSYEAR'] == year, ['LONGNUM', 'LATNUM', 'URBAN_RURA']]
    if len(cur_df) > 0:
        urban_df = cur_df.loc[cur_df['URBAN_RURA'] == 'U', ['LONGNUM', 'LATNUM']]
        rural_df = cur_df.loc[cur_df['URBAN_RURA'] == 'R', ['LONGNUM', 'LATNUM']]

        # Proximity to impervious area.
        try:
            filename = str(year) + '.tif'
            pia = rio.open(PROC_DATA_DIRECTORY / 'pia' / filename)
            dhs_df.loc[urban_df.index, 'pia'] = extract_circle(
                urban_df['LONGNUM'], urban_df['LATNUM'], 2000, pia, np.mean
            )
            dhs_df.loc[rural_df.index, 'pia'] = extract_circle(
                rural_df['LONGNUM'], rural_df['LATNUM'], 5000, pia, np.mean
            )
        except:
            pass
        
        # Nighttime lights.
        try:
            ntl = load_viirs(year)
            dhs_df.loc[urban_df.index, 'ntl'] = extract_circle(
                urban_df['LONGNUM'], urban_df['LATNUM'], 2000, ntl, np.mean
            )
            dhs_df.loc[rural_df.index, 'ntl'] = extract_circle(
                rural_df['LONGNUM'], rural_df['LATNUM'], 5000, ntl, np.mean
            )
        except:
            pass

        # Landcover.
        try:
            landcover = load_landcover(year)
            dhs_df.loc[urban_df.index, 'landcover'] = extract_circle(
                urban_df['LONGNUM'], urban_df['LATNUM'], 2000, landcover, mode_
            )
            dhs_df.loc[rural_df.index, 'landcover'] = extract_circle(
                rural_df['LONGNUM'], rural_df['LATNUM'], 5000, landcover, mode_
            )
        except:
            pass
        
        # Population.
        try:
            worldpop = load_worldpop(year)
            dhs_df.loc[urban_df.index, 'population'] = extract_circle(
                urban_df['LONGNUM'], urban_df['LATNUM'], 2000, worldpop, np.mean
            )
            dhs_df.loc[rural_df.index, 'population'] = extract_circle(
                rural_df['LONGNUM'], rural_df['LATNUM'], 5000, worldpop, np.mean
            )
        except:
            pass

# DROP NULLS
# DROP LAT LONG THAT ARE INSANE

dhs_df['pia'] = dhs_df['pia'] / 296

dhs_df = dhs_df.loc[dhs_df['DHSYEAR'] >= 2013]
dhs_df.to_csv(PROC_DATA_DIRECTORY / 'dhs/covariates.csv', index=False)
