import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

from config import DATAVIZ_DIRECTORY, PREP_DATA_DIRECTORY
from src.utils import month_to_string, hour_to_string
from src.datasets import load_aod, load_coloz, load_colwv

plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams.update({'font.size': 13})
mpl.rcParams['mathtext.fontset'] = 'stix'


dgr = mpl.colors.to_rgb("darkgreen")
fg = mpl.colors.to_rgb("forestgreen")
gold = mpl.colors.to_rgb("goldenrod")
yel = mpl.colors.to_rgb('yellow')
turq = mpl.colors.to_rgb("darkturquoise")
orc = mpl.colors.to_rgb("orchid")
fire = mpl.colors.to_rgb("firebrick")
ored = mpl.colors.to_rgb("darkorange")

cdict3 = {"red":  ((0.0, dgr[0], dgr[0]),
                   (0.25, fg[0], fg[0]),
                   (0.75, gold[0], gold[0]),
                   (1.0, yel[0], yel[0])),

         "green": ((0.0, dgr[1], dgr[1]),
                   (0.25, fg[1], fg[1]),
                   (0.75, gold[1], gold[1]),
                   (1.0, yel[1], yel[1])),

         "blue":  ((0.0, dgr[2], dgr[2]),
                   (0.25, fg[2], fg[2]),
                   (0.75, gold[2], gold[2]),
                   (1.0, yel[2], yel[2])),
         #"alpha": ((0.0, 0.5, 0.5), (1.0, 0.5, 0.5))
        }
mycmp = mpl.colors.LinearSegmentedColormap("mycmp", cdict3)


atmos_comps = ['AOD', 'COLOZ', 'COLWV']

year = 2010
month = 1
hours = [i for i in range(0, 24, 3)]

# comps


# figure setup
n_rows = len(hours)
n_columns = len(atmos_comps)
fig = plt.figure(figsize=(4, n_rows))
subplot_counter = 1

for hour in hours:
    aod = load_aod(year, month, hour)
    coloz = load_coloz(year, month, hour)
    colwv = load_colwv(year, month, hour)
    for i in range(n_columns):
        ax = fig.add_subplot(n_rows, n_columns, subplot_counter)
        if i == 0:
            cur_data = aod.read(1)
            ax.set_ylabel(f'{hour}:00', rotation=0, verticalalignment='center', horizontalalignment='right')
            ax.yaxis.set_label_coords(-0.075,0.5)
        elif i == 1:
            cur_data = coloz.read(1)
            idxs = np.nonzero(cur_data != -32768)
            cur_data[idxs] = cur_data[idxs] * 1000
        elif i == 2:
            cur_data = colwv.read(1)

        cur_data[cur_data == -32768] = np.nan
        min_ = np.nanmin(cur_data)
        max_ = np.nanmax(cur_data)
        if i % 3 == 0:
            mi = 0.1
            ma = 0.8
        elif i % 3 == 1:
            mi = 5.2
            ma = 5.4
        else:
            mi = 8
            ma = 47
        im = ax.imshow(cur_data, cmap=mycmp, vmin=mi, vmax=ma)

        ax.set_xticks([])
        ax.set_yticks([])
        if subplot_counter == len(hours)*n_columns-2:
            ax.set_xlabel('(a)', fontsize=13)
            cbar_x = 0.1625
            x_spacing = 0.2625
            cbar_y = 0.89
            cbar_w = 0.175
            cbar_h = 0.01
            cbaxes = fig.add_axes([cbar_x, cbar_y, cbar_w, cbar_h])
            
            cbar = plt.colorbar(
                im,
                cax=cbaxes,
                orientation='horizontal',
                ticks=[min_, max_]
            )
            cbaxes.xaxis.set_label_position('top')
            cbaxes.xaxis.set_ticks_position('top')
            cbar.ax.set_xticklabels([f'{min_:.1f}', f'{max_:.1f}'])
            #cbar.ax.set_yticklabels(['< -1', '0', '> 1'])
        elif subplot_counter == len(hours)*n_columns-1:
            ax.set_xlabel('(b)', fontsize=13)
            cbaxes = fig.add_axes([cbar_x+x_spacing, cbar_y, cbar_w, cbar_h])
            cbar = plt.colorbar(
                im,
                cax=cbaxes,
                orientation='horizontal',
                ticks=[min_, max_]
            )
            cbaxes.xaxis.set_label_position('top')
            cbaxes.xaxis.set_ticks_position('top')
            #cbaxes.xaxis.set_major_formatter(mpl.ticker.ScalarFormatter(useMathText=True, useOffset=True))
            cbar.ax.set_xticklabels([f'{min_:.1f}', f'{max_:.1f}'])
            #cbar.ax.set_xticklabels([min_, max_])
            #plt.colorbar(im, ax=ax, orientation='horizontal')
        elif subplot_counter == len(hours)*n_columns:
            ax.set_xlabel('(c)', fontsize=13)
            cbaxes = fig.add_axes([cbar_x+2*x_spacing, cbar_y, cbar_w, cbar_h])
            cbar = plt.colorbar(
                im,
                cax=cbaxes,
                orientation='horizontal',
                ticks=[min_, max_]
            )
            cbaxes.xaxis.set_label_position('top')
            cbaxes.xaxis.set_ticks_position('top')
            cbar.ax.set_xticklabels([f'{min_:.0f}', f'{max_:.0f}'])
        #ax.xaxis.set_label_coords(0.5, -0.5)

        subplot_counter += 1


#plt.tight_layout()
plt.subplots_adjust(wspace=0.05, hspace=0.1)
#plt.suptitle('Atmospheric composition monthly\n means (January, 2010)', y=1)
plt.savefig(DATAVIZ_DIRECTORY / 'atmos_comps.pdf', bbox_inches='tight')

plt.show()
