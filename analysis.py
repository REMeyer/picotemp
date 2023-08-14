import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
from time import time
from matplotlib import dates


def timer(func):
    def wrapper_timer(*args, **kwargs):
        print(f"Starting timer for {func.__name__}")
        t1 = time()
        value = func(*args, **kwargs)
        elapsed_time = time() - t1
        print(f"Elapsed time for {func.__name__}: {elapsed_time:0.4f} seconds")
        return value
    return wrapper_timer

@timer
def parse_envlog(fl):
    '''
    Parses the environment log from the pico weather station.
    Log is generated from the output of a minicom instance running in the 
    background in a tmux session. The minicom instance appends timestamps
    to each reading. 

    Input: 
        fl -> Path to logfile
    Output:
        df -> Parsed pandas dataframe of logfile with the following columns:
                    time:           str 
                    day:            str
                    datetimestr:    str
                    datetime:       datetime
                    temperature:    float
                    humidity:       float
    '''

    df = pd.read_csv(fl, skiprows=2, delim_whitespace=True,
                names=('day','time','temp','humid'))
    df['time'] = [x[:-1] for x in df['time'].values]
    df['day'] = [x[1:] for x in df['day'].values]

    df['datetimestr'] = df['day'] + 'T' + df['time']
    df['datetime'] = [datetime.datetime.fromisoformat(df['datetimestr'].values[x])
                        for x in range(len(df))]

    return df

@timer
def subplot_env(df, mask, title=''):

    fig, ax = plt.subplots(tight_layout=True)

    ax.plot(df['datetime'][mask], df['temp'][mask], color='tab:red', label='T (deg C)')
    ax.set_ylabel('T (deg C)', color='tab:red')
    ax.xaxis.set_major_formatter(dates.DateFormatter('%m-%d %H:%M'))
    ax.tick_params(axis='x', labelrotation=20)
    ax.tick_params(axis='y', color='tab:red', labelcolor='tab:red')
    ax.tick_params(axis='both', labelsize=13)
    ax.tick_params(which='major', length=7)
    ax.set_title(title, fontsize=15)

    ax2 = ax.twinx()
    ax2.tick_params(axis='both', labelsize=13)
    ax2.tick_params(axis='y', color='tab:blue', labelcolor='tab:blue')
    ax2.tick_params(which='major', length=7)
    ax2.plot(df['datetime'][mask], df['humid'][mask], color='tab:blue', label='Rel. Humid (%)')
    ax2.set_ylabel('Rel. Humid (%)', color='tab:blue')

    return fig, ax, ax2

@timer
def plot_env_data(df):
    '''Plots environment data stored in dataframe df for the last 72, 24, and
        6 hours'''

    last72 = df['datetime'] >= df['datetime'].iloc[-1] - np.timedelta64(3, 'D')
    last24 = df['datetime'] >= df['datetime'].iloc[-1] - np.timedelta64(1, 'D')
    last6 = df['datetime'] >= df['datetime'].iloc[-1] - np.timedelta64(6, 'h')

    fig, ax, ax2 = subplot_env(df, last72, title="Last 72 Hours")
    ax.xaxis.set_major_locator(dates.HourLocator(interval = 6))
    ax.xaxis.set_minor_locator(dates.HourLocator(interval = 2))
    plt.savefig('/home/meyer/readtemp/web/last72.png', dpi=100)

    fig, ax, ax2 = subplot_env(df, last24, title='Last 24 Hours')
    ax.xaxis.set_major_locator(dates.HourLocator(interval = 4))
    ax.xaxis.set_minor_locator(dates.HourLocator(interval = 1))
    plt.savefig('/home/meyer/readtemp/web/last24.png', dpi=100)

    fig, ax, ax2 = subplot_env(df, last6, title='Last 6 Hours')
    ax.xaxis.set_major_locator(dates.HourLocator(interval = 1))
    ax.xaxis.set_minor_locator(dates.MinuteLocator(byminute=[0,15,30,45]))
    plt.savefig('/home/meyer/readtemp/web/last6.png', dpi=100)

if __name__=='__main__':
    LOGFILE = '/home/meyer/readtemp/env.log'
    df = parse_envlog(LOGFILE)
    plot_env_data(df)

