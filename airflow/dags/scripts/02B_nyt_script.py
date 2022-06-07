import pandas as pd
from datetime import datetime
import numpy as np

county_daily_urls = ['https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us-counties-2020.csv',
                     'https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us-counties-2021.csv',
                     'https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us-counties-2022.csv',
                     'https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us-counties-recent.csv'
                    ]

def get_county_daily_infections_nyt(urls):
    county_dfs = [pd.read_csv(url) for url in urls]
    df = pd.concat(county_dfs, ignore_index=True)
    # Column fips
    df. rename(columns = {'geoid':'fips'}, inplace = True)
    df['fips'] = df['fips'].str[4:]
    # Removing 2 columns
    df = df.drop(['cases_avg_per_100k', 'deaths_avg_per_100k', 'cases_avg', 'deaths_avg'], axis = 1)
    # Deleteing data for "Unknown" county 
    df = df.query('county != "Unknown"')
    df.sort_values(by=['fips', 'date'], inplace=True)
    # Remove duplicates
    df = df.drop_duplicates()
    # Add rows that are not there (dates that were without data)
    ## Get range of dates and all unique FIPS
    dates = pd.date_range(datetime.strptime(df['date'].agg('min'), '%Y-%m-%d'), datetime.strptime(df['date'].agg('max'), '%Y-%m-%d'))
    unique_fips = df.fips.unique()
    ## Map fips to counties and states
    map_county = df.set_index('fips')['county'].dropna().to_dict()
    map_state = df.set_index('fips')['state'].dropna().to_dict()
    ## NumPy array with all dates in df
    df_from_df = df[["date", "fips"]]
    df_from_df_new = df_from_df.to_numpy()
    df_from_df_new = df_from_df_new.astype('<U10')
    ## NumPy array with all dates in range
    df_from_dates = []
    for date in dates:
        for fips_code in unique_fips:
            lst = [str(date.date()), fips_code]
            df_from_dates.append(lst)
    df_from_dates_new = np.array(df_from_dates)
    ## Combine 2 NumPy arrays
    combined = np.concatenate((df_from_df_new, df_from_dates_new))
    ## Get rows that were not in the original df
    df_new = pd.DataFrame(combined, columns = ['date','fips'])
    df_new_all_columns = df_new.drop_duplicates(keep=False)
    df_new_all_columns['county'] = df_new['fips'].map(map_county)
    df_new_all_columns['state'] = df_new['fips'].map(map_state)
    df_new_all_columns['cases'] = 0
    df_new_all_columns['deaths'] = 0
    # New df with all dates
    df = pd.concat([df, df_new_all_columns], ignore_index=True)
    df.sort_values(by=['fips', 'date'], inplace=True)
    df = df.drop_duplicates()
    # Change values where < 0 cases and deaths
    df.loc[df['cases'] <= -1, 'cases'] = 0
    df.loc[df['deaths'] <= -1, 'deaths'] = 0
    df = df.reset_index(drop=True)
    return df

county_daily_df = get_county_daily_infections_nyt(county_daily_urls)
county_daily_df.to_parquet('../../data/cases_daily.parquet')

