import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

from config import PLOT_DATA_DIRECTORY, DATAVIZ_DIRECTORY

plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams.update({'font.size': 16})
mpl.rcParams['mathtext.fontset'] = 'stix'

df = pd.read_csv(PLOT_DATA_DIRECTORY / 'WDIData.csv')

years = [str(i) for i in range(1990, 2018)]
df = df.loc[df['Country Name'] == 'Nigeria', ['Indicator Name'] + years].copy()

cols = [
    'Population, total',
    'Rural population',
    'Urban population',
    'Access to electricity (% of population)',
    'Access to electricity, rural (% of rural population)',
    'Access to electricity, urban (% of urban population)'
]
nga_df = pd.DataFrame(columns=cols)

for col in cols:
    nga_df[col] = df.loc[df['Indicator Name'] == col, years].T.values.squeeze()

years = list(map(int, years))

fig = plt.figure(figsize=(11, 4))
n_subplots = 2
for i in range(n_subplots):
    # if i == 0:
    #     # Electrification
    #     ax = fig.add_subplot(n_subplots, int(i+1), 1)

    #     total_with = nga_df['Access to electricity (% of population)']

    #     l1 = ax.plot(years, total_with,
    #         label='% with access to electricity',
    #         color='dimgrey',
    #         marker='o',
    #         markerfacecolor='dimgrey',
    #         markersize=9.5,
    #         markeredgecolor='none',
    #         alpha=1
    #     )
    #     ax.set_ylim(0, 100)
    #     ax.set_yticks([0, 25, 50, 75, 100])
    #     ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
    #     ax.set_xticks([])
    #     ax.grid(axis='y', alpha=0.375)

        

    #     # Population
    #     ax2 = ax.twinx()

    #     total_pop = nga_df['Population, total']
    #     total_pop_with = total_pop * (nga_df['Access to electricity (% of population)'] / 100)
    #     total_pop_without = total_pop * (1-(nga_df['Access to electricity (% of population)'] / 100))

    #     p1 = ax2.bar(years, total_pop_with,
    #         label='Population with access',
    #         width=0.5,
    #         color='goldenrod',
    #         alpha=0.5
    #     )
    #     p2 = ax2.bar(years, total_pop_without,
    #         label='Population without access',
    #         width=0.5,
    #         bottom=total_pop_with,
    #         color='forestgreen',
    #         alpha=0.5
    #     )
    #     ax2.set_ylim(0, 200_000_000)
    #     ax2.set_yticks([0, 5e7, 1e8, 1.5e8, 2e8])
    #     ax2.set_yticklabels(['0', '50', '100', '150', '200'])


    #     ax.set_zorder(ax2.get_zorder()+1)
    #     ax.patch.set_visible(False)

    #     ax.set_ylabel('Electrification rate', fontsize=18)
    #     ax2.set_ylabel('Population (millions)', fontsize=18)

    #     axs = [l1[0], p2, p1]
    #     labels = [ax.get_label() for ax in axs]
    #     ax.legend(
    #         axs,
    #         labels,
    #         loc=4,
    #         ncol=1,
    #         framealpha=0,
    #         fontsize=14,
    #         bbox_to_anchor=(0.85, 0.71)
    #     )
    #     ax.set_title('(a) Total population',
    #         x=0.98,
    #         y=-0.01,
    #         horizontalalignment='right',
    #         verticalalignment='bottom',
    #         fontsize=20
    #     )
    if i == 0:
        # Electrification
        ax = fig.add_subplot(1, 2, int(i+1))

        total_with = nga_df['Access to electricity, urban (% of urban population)']

        l1 = ax.plot(years, total_with,
            label='% with access to electricity',
            color='dimgrey',
            marker='o',
            markerfacecolor='dimgrey',
            markersize=9.5,
            markeredgecolor='none',
            alpha=1
        )
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
        ax.set_xticks([])
        ax.grid(axis='y', alpha=0.375)


        # Population
        ax2 = ax.twinx()

        total_pop = nga_df['Urban population']
        total_pop_with = total_pop * (nga_df['Access to electricity, urban (% of urban population)'] / 100)
        total_pop_without = total_pop * (1-(nga_df['Access to electricity, urban (% of urban population)'] / 100))

        p1 = ax2.bar(years, total_pop_with,
            label='Population with access',
            width=0.5,
            color='thistle',
            alpha=1
        )
        p2 = ax2.bar(years, total_pop_without,
            label='Population without access',
            width=0.5,
            bottom=total_pop_with,
            color='midnightblue',
            alpha=0.7
        )
        ax2.set_ylim(0, 100_000_000)
        ax2.set_yticks([0, 25e6, 50e6, 75e6, 100e6])
        ax2.set_yticklabels(['0', '25', '50', '75', '100'])

        ax.set_xticks([i for i in range(1990, 2018, 3)])
        ax.set_xticklabels([str(i) for i in range(1990, 2018, 3)], rotation=45)
        ax.set_zorder(ax2.get_zorder()+1)
        ax.patch.set_visible(False)

        ax.set_ylabel('Electrification rate', fontsize=18)
        ax2.set_ylabel('Population (millions)', fontsize=18)

        axs = [l1[0], p1, p2]
        labels = [ax.get_label() for ax in axs]
        leg = ax.legend(
            axs,
            labels,
            #loc=4,
            ncol=3,
            framealpha=0,
            fontsize=16,
            bbox_to_anchor=(2.65, 1.2)
        )
        leg.set_in_layout(False)
        ax.set_title('(a) Urban population',
            x=0.98,
            y=-0.01,
            horizontalalignment='right',
            verticalalignment='bottom',
            fontsize=20
        )
    elif i == 1:
        # Electrification
        ax = fig.add_subplot(1, 2, int(i+1))

        total_with = nga_df['Access to electricity, rural (% of rural population)']

        l1 = ax.plot(years, total_with,
            label='% with access to electricity',
            color='dimgrey',
            marker='o',
            markerfacecolor='dimgrey',
            markersize=9.5,
            markeredgecolor='none',
            alpha=1
        )
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.set_yticklabels(['0%', '25%', '50%', '75%', '100%'])
        ax.grid(axis='y', alpha=0.375)


        # Population
        ax2 = ax.twinx()

        total_pop = nga_df['Rural population']
        total_pop_with = total_pop * (nga_df['Access to electricity, rural (% of rural population)'] / 100)
        total_pop_without = total_pop * (1-(nga_df['Access to electricity, rural (% of rural population)'] / 100))

        p1 = ax2.bar(years, total_pop_with,
            label='Population with access',
            width=0.5,
            color='thistle',
            alpha=1
        )
        p2 = ax2.bar(years, total_pop_without,
            label='Population without access',
            width=0.5,
            bottom=total_pop_with,
            color='midnightblue',
            alpha=0.7
        )
        ax2.set_ylim(0, 100_000_000)
        ax2.set_yticks([0, 25e6, 50e6, 75e6, 100e6])
        ax2.set_yticklabels(['0', '25', '50', '75', '100'])


        ax.set_xticks([i for i in range(1990, 2018, 3)])
        ax.set_xticklabels([str(i) for i in range(1990, 2018, 3)], rotation=45)
        ax.set_zorder(ax2.get_zorder()+1)
        ax.patch.set_visible(False)

        ax.set_ylabel('Electrification rate', fontsize=18)
        ax2.set_ylabel('Population (millions)', fontsize=18)

        axs = [l1[0], p1, p2]
        labels = [ax.get_label() for ax in axs]
        # ax.legend(
        #     axs,
        #     labels,
        #     loc=4,
        #     ncol=1,
        #     framealpha=0,
        #     fontsize=11,
        #     bbox_to_anchor=(0.65, 0.7)
        # )
        ax.set_title('(b) Rural population',
            x=0.98,
            y=-0.01,
            horizontalalignment='right',
            verticalalignment='bottom',
            fontsize=20
        )

    ax.set_xlabel('Years')
    ax.set_xlim(1989.5, 2017.5)

#plt.suptitle('Access to electricity', x=0.5, y=1, horizontalalignment='center', verticalalignment='center')
plt.tight_layout(pad=1.5)
#plt.savefig(DATAVIZ_DIRECTORY / 'electrification_rate_v2.pdf'
plt.show()



