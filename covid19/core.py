# AUTOGENERATED! DO NOT EDIT! File to edit: 00_core.ipynb (unless otherwise specified).

__all__ = ['CONFIRMED_URI', 'DEATHS_URI', 'RECOVERED_URI', 'confirmed_df', 'deaths_df', 'recovered_df', 'get_data',
           'plot_seaborn', 'generate_plots']

# Cell
CONFIRMED_URI = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv"
DEATHS_URI = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv"
RECOVERED_URI = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv"

# Cell
import pandas as pd
confirmed_df = pd.read_csv(CONFIRMED_URI, skipinitialspace=True).fillna('')
deaths_df = pd.read_csv(DEATHS_URI, skipinitialspace=True).fillna('')
recovered_df = pd.read_csv(RECOVERED_URI, skipinitialspace=True).fillna('')

# Cell
def get_data(state, country, start_date):
    global confirmed_df, deaths_df, recovered_df

    if start_date == "":
        start_date = "1/23/20"

    def filter(df, state, country, start_date):
        if state == "":
            # Select rows by country and then sum over all rows that are returned
            tdf = df.loc[df["Country/Region"] == country]
            return tdf.groupby("Country/Region").sum().loc[:, start_date:].T
        else:
            return df.loc[(df["Province/State"] == state) & (df["Country/Region"] == country), start_date:].T

    def transform_labels(df, column_name):
        df.index.name = 'Date'
        df.reset_index(inplace = True)
        df.columns = ['Date', column_name]
        return df

    df = transform_labels(filter(confirmed_df, state, country, start_date), 'Confirmed Cases')
    ddf = transform_labels(filter(deaths_df, state, country, start_date), 'Deaths')
    rdf = transform_labels(filter(recovered_df, state, country, start_date), 'Recovered')

    df['Deaths'] = ddf['Deaths']
    df['Recovered'] = rdf['Recovered']
    df['Date'] = pd.to_datetime(df['Date'])
    return df

# Cell
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_style("whitegrid")

# Cell
import datetime

def plot_seaborn(df, state, country, start_date, figure, rows, columns, index):
    if state == "":
        region = f"{country}"
    else:
        region = f"{state}, {country}"

    figure.add_subplot(rows, columns, index)
    p = sns.lineplot(x='Date', y='value', hue='variable', data=pd.melt(df, ['Date']))
    p.set_title(f"{region} COVID19 cases from {start_date}", loc='left', fontdict={'fontweight': 'bold'})

    # Remove "variable" from the legend box
    ax = plt.gca()
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles[1:], labels=labels[1:])

    # Format the x axis and y axis values
    xticks = ax.get_xticks()
    yticks = ax.get_yticks()
    ax.set_xticklabels([datetime.datetime.fromordinal(int(tm)).strftime('%m-%d') for tm in xticks], rotation=45)
    ax.set_yticklabels([f"{val:0.0f}" for val in yticks])

    # Set the axis labels
    ax.set_ylabel("People")
    ax.set_xlabel("")
    return p

# Cell
import math
def generate_plots(regions, columns):
    # Calculate rows and columns - we want columns across per row
    count = len(regions)
    rows = math.ceil(count / columns)
    figure = plt.figure(figsize=(columns*6,rows*6))
    figure.subplots_adjust(hspace=0.5)
    plots = []
    for index, row in regions.iterrows():
        state = row['state']
        country = row['country']
        start_date = row['start_date']
        df = get_data(state, country, start_date)
        plot_seaborn(df, state, country, start_date, figure, rows, columns, index + 1)
    return figure