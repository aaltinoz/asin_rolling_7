import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
from datetime import datetime
from google.colab import files

#Global variable
STORE_NAME = 'Lemon&Co'


def run_app():
    print("Please upload Sponsored Products Campaign data as a csv file")
    uploaded = files.upload()

    for fn in uploaded.keys():

        print('User uploaded file "{name}" with length {length} bytes'.format(name=fn, length=len(uploaded[fn])))

    # #Get data
    filename = list(uploaded.keys())[0]
    data = pd.read_csv(filename)

    ## Styles
    # Define the color formatting function
    def color_scale(val, min_val, val_25, val_75, max_val):
        if min_val <= val <= val_25:
            return 'background-color: red'
        elif val_25 < val <= val_75:
            return 'background-color: orange'
        elif val_75 < val <= max_val:
            return 'background-color: green'
        else:
            return ''  # No formatting

    # Apply conditional formatting to each column separately
    def apply_color_scale(column):
        min_val = column.min()
        val_25 = column.quantile(0.25)
        val_75 = column.quantile(0.75)
        max_val = column.max()
        return column.apply(color_scale, args=(min_val, val_25, val_75, max_val))

    data = pd.read_csv('lemonco.csv', parse_dates=['formatted_date'])


    # Add organic data
    def add_organic_data(data):
        data = (data
                    .fillna(0)
                    .rename(columns={'quantity':'total_order',
                                    'sales_amount': 'total_sales'})
                    .assign(organic_order=data['quantity']-data['ad_units_ordered'],
                            organic_sales=data['sales_amount']-data['ad_sales'],
                            cvr=data['ad_units_ordered']/data['ad_clicks'])
                    .set_index('formatted_date')
                    .sort_index(ascending=True) # Ensure the data is in descending order
                    
                    )
        return data

    data = add_organic_data(data)

    data.index = data.index.strftime('%m-%d-%Y')
    # Add 7 day rolling
    def add_7_day_rolling(data):
            return (data.assign(rolling7adRoas=data['ad_sales'].rolling(window=7).sum()/data['ad_spend'].rolling(window=7).sum(),
                rolling7grossRoas=data['total_sales'].rolling(window=7).sum()/data['ad_spend'].rolling(window=7).sum(),
                rolling7adUnits=data['ad_units_ordered'].rolling(window=7).sum(),
                rolling7organicUnits=data['total_order'].rolling(window=7).sum()-data['ad_units_ordered'].rolling(window=7).sum(),
                rolling7adSpend=data['ad_spend'].rolling(window=7).sum(),
                rolling7dayCvr=data['ad_units_ordered'].rolling(window=7).sum()/data['ad_clicks'].rolling(window=7).sum())
    )

    data = add_7_day_rolling(data)

    # 7 day heatmap
    def heatmap_7(data):
        return data.fillna(0).iloc[::-1].iloc[:45,-6:].fillna(0).style.apply(apply_color_scale)
    heatmap_7(data)


    # plot data function
    def plot_metrics(data):
        fig, axs = plt.subplots(3, 1, figsize=(25, 30), sharex=False)

        # Plot 1: Stacked Bar Chart with Organic Sales and Ad Sales, Line Chart with CVR
        ax1 = axs[0]
        data[['organic_sales', 'ad_sales']].plot(kind='bar', stacked=True, ax=ax1, color=['blue', 'orange'])
        ax2 = ax1.twinx()
        data['rolling7dayCvr'].plot(ax=ax2, color='green', marker='o', linestyle='-', linewidth=2)

        ax1.set_ylabel('Sales')
        ax2.set_ylabel('CVR')
        ax1.set_title('Organic Sales and Ad Sales with CVR')
        ax1.legend(loc='upper left')
        ax2.legend(['CVR'], loc='upper right')
        ax1.tick_params(axis='x', rotation=90)

        # Plot 2: 7-day Ad Spend as Line, 7-day Organic Units and 7-day Ad Units as Bar Chart
        ax3 = axs[1]
        data[['rolling7adUnits', 'rolling7organicUnits']].plot(kind='bar', stacked=True, ax=ax3, color=['purple', 'red'])
        ax4 = ax3.twinx()
        data['rolling7adSpend'].plot(ax=ax4, color='magenta', marker='o', linestyle='-', linewidth=2)

        ax3.set_ylabel('Units')
        ax4.set_ylabel('Ad Spend')
        ax3.set_title('7-Day Ad Spend, Organic Units, and Ad Units')
        ax3.legend(loc='upper left')
        ax4.legend(['Ad Spend'], loc='upper right')
        ax3.tick_params(axis='x', rotation=90)

        # Plot 3: 7-day Gross ROAS and 7-day Ad ROAS as Line Graph, 7-day Organic Units and 7-day Ad Units as Bar Chart
        ax5 = axs[2]
        data[['rolling7adUnits', 'rolling7organicUnits']].plot(kind='bar', stacked=True, ax=ax5, color=['cyan', 'magenta'])
        ax6 = ax5.twinx()
        data[['rolling7grossRoas', 'rolling7adRoas']].plot(ax=ax6, linestyle='-', marker='o', color=['blue', 'orange'])

        ax5.set_ylabel('Units')
        ax6.set_ylabel('ROAS')
        ax5.set_title('7-Day Gross ROAS and Ad ROAS with Organic Units and Ad Units')
        ax5.legend(loc='upper left')
        ax6.legend(['Gross ROAS', 'Ad ROAS'], loc='upper right')
        ax5.tick_params(axis='x', rotation=90)

        # Adjust layout to prevent overlapping
        plt.tight_layout()
        plt.show()

    # Example usage:
    #plot_metrics(data)

