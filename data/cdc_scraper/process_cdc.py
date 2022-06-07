import pandas as pd
import numpy as np

def get_state_vaccination_rates():
    vaccinations = pd.read_parquet('cdc_vaccinations.parquet')
    vaccinations['fully_vaccinated'] = vaccinations['fully_vaccinated'].astype(float)
    vaccinations['total_pop'] = vaccinations['total_pop'].astype(float)
    state_vaccinated = vaccinations.groupby(['state_code','date']).agg({'fully_vaccinated':'sum'}).reset_index()
    state_pop = vaccinations[['state_code','fips_code','total_pop']].drop_duplicates().groupby(['state_code']).agg({'total_pop':'sum'}).reset_index()
    vaccination_rates = state_vaccinated.merge(state_pop)
    vaccination_rates['pct_vaccinated'] = vaccination_rates['fully_vaccinated']/vaccination_rates['total_pop']
    vaccination_rates.to_csv('vaccinations_by_state.csv',index=False)


def create_counterfactual_frame():
    masks = pd.read_parquet('cdc_mask_mandates.parquet').sort_values(['fips_code_text','date'])
    masks['face_masks_required_in_public'] = masks.groupby('fips_code_text')['face_masks_required_in_public'].ffill()
    masks = masks.dropna().copy()
    masks['date'] = masks['date'].dt.strftime('%Y-%m-%d')
    vaccinations = pd.read_parquet(r'cdc_vaccinations.parquet')
    vaccinations = vaccinations[vaccinations['fips_code'] != 'UNK']
    vaccinations['date'] = pd.to_datetime(vaccinations['date']).dt.strftime('%Y-%m-%d')
    vaccinations['fips_code_text'] = vaccinations['fips_code'].astype(int)
    vaccine_hesitancy = pd.read_parquet('cdc_vaccine_hesitancy.parquet')
    # CHANGE THIS GUY WHEN MERGING TO MASTER
    cases = pd.read_csv('../county_daily.csv')
    non_epidemic = pd.read_csv('../non_epidemic_data.csv')
    masks['fips_code_text'] = masks['fips_code_text'].astype(int)
    vaccine_hesitancy['fips_code_text'] = vaccine_hesitancy['fips_code_text'].astype(int)
    df_merged = masks.merge(cases,left_on=['fips_code_text','date'],right_on=['fips','date']).sort_values(by=['fips_code_text','date'])
    df_merged = df_merged.merge(vaccinations[['fips_code_text','date','pct_fully_vaccinated']], left_on=['fips_code_text','date'], right_on=['fips_code_text','date'], how='left')
    df_merged = pd.merge(df_merged,vaccine_hesitancy.drop(columns=['state_code','state_fips','county_fips','county_name','state']),
                  left_on='fips_code_text',right_on='fips_code_text').merge(non_epidemic, left_on='fips_code_text',right_on='fips')
    df_merged['pct_fully_vaccinated'] = df_merged['pct_fully_vaccinated'].astype(float)
    df_merged['pct_fully_vaccinated'] = df_merged['pct_fully_vaccinated'].fillna(0)


    df_merged['moving'] = df_merged.groupby('fips_code_text')['cases'].transform(lambda x: x.rolling(7, 1).mean())
    df_merged['cases_per_100k'] = df_merged['cases']/df_merged['pop_estimate_2019'] * 100000
    df_merged['moving_cases_per_100k'] = df_merged['moving']/df_merged['pop_estimate_2019'] * 100000
    for i in range(1,8):
        df_merged[f'cases_lag_{i}'] = df_merged.groupby('fips_code_text')['cases_per_100k'].shift(i)
        df_merged[f'moving_cases_lag_{i}'] = df_merged.groupby('fips_code_text')['moving_cases_per_100k'].shift(i)

    df_merged = pd.get_dummies(df_merged,columns=['face_masks_required_in_public'])
    modeling_df = df_merged.dropna().copy()
    modeling_df['date'] = pd.to_datetime(modeling_df['date'])
    modeling_df['weekday'] = modeling_df['date'].dt.weekday.astype(str)
    modeling_df['month'] = modeling_df['date'].dt.month.astype(str)
    modeling_df['year'] = modeling_df['date'].dt.year.astype(str)
    modeling_df = pd.get_dummies(modeling_df,columns=['weekday','year','month'])
    convert_cols = ['percent_hispanic', 'percent_non_hispanic_black', 'percent_non_hispanic_white', 'estimated_hesitant', 'estimated_strongly_hesitant']
    for col in convert_cols:
        modeling_df[f'{col}'] = modeling_df[f'{col}'].astype(float)
    
    modeling_df.to_parquet('modeling_df.parquet')

    
get_state_vaccination_rates()
create_counterfactual_frame()