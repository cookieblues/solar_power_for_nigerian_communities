import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from tqdm import tqdm

from src.datasets import load_dhs
from config import PREP_DATA_DIRECTORY, NIGERIA_SHAPEFILE


df = load_dhs()
nga = gpd.read_file(NIGERIA_SHAPEFILE)
fig = plt.figure(figsize=(21, 13))

for i, year in tqdm(enumerate(sorted(df['DHSYEAR'].unique()))):
    year_df = df.loc[df['DHSYEAR'] == year, ['DHSCLUST', 'has_electricity', 'LONGNUM', 'LATNUM']]

    ax = fig.add_subplot(2, 3, i+1)
    nga.plot(edgecolor='gray', facecolor='none', ax=ax)

    for cluster in year_df['DHSCLUST'].unique():
        cluster_df = year_df.loc[year_df['DHSCLUST'] == cluster, ['has_electricity', 'LONGNUM', 'LATNUM']]

        for j in range(2):
            cur_df = cluster_df.loc[cluster_df['has_electricity'] == j, ['LONGNUM', 'LATNUM']]

            cluster_gdf = gpd.GeoDataFrame(
                cur_df,
                geometry=gpd.points_from_xy(cur_df['LONGNUM'], cur_df['LATNUM'])
            )
            if j == 0:
                clr = 'turquoise'
            elif j == 1:
                clr = 'magenta'
            cluster_gdf.plot(edgecolor=clr, facecolor='none', markersize=1, ax=ax)


    # Text
    ax.set_title(f'Year {int(year)}')

plt.tight_layout()
plt.show()