import pandas as pd
import numpy as np

def get_state_vaccination_rates():
    vaccinations = pd.read_parquet('../../data/cdc_scraper/cdc_vaccinations.parquet')
    vaccinations['fully_vaccinated'] = vaccinations['fully_vaccinated'].astype(float)
    vaccinations['total_pop'] = vaccinations['total_pop'].astype(float)
    state_vaccinated = vaccinations.groupby(['state_code','date']).agg({'fully_vaccinated':'sum'}).reset_index()
    state_pop = vaccinations[['state_code','fips_code','total_pop']].drop_duplicates().groupby(['state_code']).agg({'total_pop':'sum'}).reset_index()
    vaccination_rates = state_vaccinated.merge(state_pop)
    vaccination_rates['pct_vaccinated'] = vaccination_rates['fully_vaccinated']/vaccination_rates['total_pop']
    vaccination_rates.to_csv('../../data/vaccinations_by_state.csv',index=False)

def create_random_effects_df():
    mask_mandates = pd.read_parquet('../../data/cdc_scraper/cdc_mask_mandates.parquet')
    bar_closings = pd.read_parquet('../../data/cdc_scraper/cdc_bar_closings.parquet').rename(columns={'action':'bar_status'})
    restaurant_closing = pd.read_parquet('../../data/cdc_scraper/cdc_restaurant_closings.parquet').rename(columns={'action':'restaurant_status'})
    gathering_bans = pd.read_parquet('../../data/cdc_scraper/cdc_gathering_bans.parquet')
    stay_at_home = pd.read_parquet('../../data/cdc_scraper/cdc_stay_at_home.parquet').rename(columns={'current_order_status':'stay_at_home'})
    bar_closings['fips_code_text'] = bar_closings['state_fips'] + bar_closings['county_fips']
    restaurant_closing['fips_code_text'] = restaurant_closing['state_fips'] + restaurant_closing['county_fips']
    gathering_bans['fips_code_text'] = gathering_bans['state_fips'] + gathering_bans['county_fips']
    stay_at_home['fips_code_text'] = stay_at_home['state_fips'] + stay_at_home['county_fips']
    all_mandates = mask_mandates.merge(bar_closings[['fips_code_text','date','bar_status']]
                    ,left_on=['date','fips_code_text']
                    ,right_on=['date','fips_code_text'],
                              how='outer'
                   ).merge(restaurant_closing[['fips_code_text','date','restaurant_status']]
                    ,left_on=['date','fips_code_text']
                    ,right_on=['date','fips_code_text'],
                            how='outer'
                    ).merge(gathering_bans[['fips_code_text','date','general_gb_order_group']],
                             how='outer',
                   ).merge(stay_at_home[['fips_code_text','date','stay_at_home']],
                            how='outer'
                          ).sort_values(by=['fips_code_text','date'])
    mandate_list = ['face_masks_required_in_public', 'bar_status','restaurant_status', 
                    'general_gb_order_group','stay_at_home']
    for mandate in mandate_list:
        all_mandates[f'{mandate}'] = all_mandates.groupby('fips_code_text')[f'{mandate}'].ffill()
        all_mandates['gathering_ban_binary'] = np.where(all_mandates['general_gb_order_group']=='No order found','No','Yes')
    all_mandates_complete = all_mandates.dropna()
    vaccinations = pd.read_parquet('../../data/cdc_scraper/cdc_vaccinations.parquet').rename({'fips_code':'fips_code_text'})
    cases = pd.read_parquet('../../data/cases_daily.parquet')
    cases['fips_code_text'] = cases['fips'].astype(str).str.pad(width=5,fillchar='0')
    cases['date'] = pd.to_datetime(cases['date'])
    vaccine_hesitancy = pd.read_parquet('../../data/cdc_scraper/cdc_vaccine_hesitancy.parquet')
    vaccine_hesitancy['fips_code_text'] = vaccine_hesitancy['fips_code_text'].astype(str).str.pad(width=5,fillchar='0')
    non_epidemic = pd.read_csv('../../data/non_epidemic_data.csv')
    non_epidemic['fips_code_text'] = non_epidemic['fips'].astype(str).str.pad(width=5,fillchar='0')
    vaccinations = vaccinations[vaccinations['fips_code'] != 'UNK']
    vaccinations['fips_code_text'] = vaccinations['fips_code'].astype(int).astype(str).str.pad(width=5,fillchar='0')
    final_df = all_mandates_complete.merge(vaccinations[['fips_code_text','date','pct_fully_vaccinated']], left_on=['fips_code_text','date'],right_on=['fips_code_text','date']
                                       ,how='left'
                  ).merge(cases,how='left'
                         ).merge(non_epidemic.drop(columns=['fips'])
                                ).merge(vaccine_hesitancy.drop(columns=['state_code','state_fips','county_fips','county_name','state'])
                                                              )
    final_df['pct_fully_vaccinated'] = final_df['pct_fully_vaccinated'].astype(float).fillna(0)
    convert_cols = ['percent_hispanic', 'percent_non_hispanic_black', 'percent_non_hispanic_white', 'estimated_hesitant', 'estimated_strongly_hesitant']
    for col in convert_cols:
        final_df[f'{col}'] = final_df[f'{col}'].astype(float)
    final_df['moving'] = final_df.groupby('fips_code_text')['cases'].transform(lambda x: x.rolling(7, 1).mean())
    final_df['cases_per_100k'] = final_df['cases']/final_df['pop_estimate_2019'] * 100000
    final_df['moving_cases_per_100k'] = final_df['moving']/final_df['pop_estimate_2019'] * 100000
    for i in range(1,8):
        final_df[f'cases_lag_{i}'] = final_df.groupby('fips_code_text')['cases_per_100k'].shift(i)
        final_df[f'moving_cases_lag_{i}'] = final_df.groupby('fips_code_text')['moving_cases_per_100k'].shift(i)
    modeling_df = pd.get_dummies(final_df,columns=['face_masks_required_in_public', 'bar_status',
       'restaurant_status','stay_at_home','gathering_ban_binary'])
    modeling_vars = ['unemployment_rate_2020',
                    'median_household_income_2019',
                    'poverty_frac_2019',
                    'no_high_school',
                    'high_school_only',
                    'college_only',
                    'voted_biden',
                    'percent_hispanic',
                    'percent_non_hispanic_black',
                    'percent_non_hispanic_white',
                    'face_masks_required_in_public_Public mask mandate',
                    'moving_cases_lag_1',
                    'moving_cases_lag_2',
                    'moving_cases_lag_3',
                    'moving_cases_lag_4',
                    'moving_cases_lag_5',
                    'moving_cases_lag_6',
                    'estimated_hesitant',
                    'estimated_strongly_hesitant',
                    'pct_fully_vaccinated',
                    ]
    modeling_df_final = modeling_df[~modeling_df[modeling_vars].isna().any(axis=1)]
    modeling_df_final.to_parquet('../../data/cdc_scraper/random_effects_modeling_df.parquet',index=False)

def create_counterfactual_frame():
    masks = pd.read_parquet('../../data/cdc_scraper/cdc_mask_mandates.parquet').sort_values(['fips_code_text','date'])
    masks['face_masks_required_in_public'] = masks.groupby('fips_code_text')['face_masks_required_in_public'].ffill()
    masks = masks.dropna().copy()
    masks['date'] = masks['date'].dt.strftime('%Y-%m-%d')
    vaccinations = pd.read_parquet('../../data/cdc_scraper/cdc_vaccinations.parquet')
    vaccinations = vaccinations[vaccinations['fips_code'] != 'UNK']
    vaccinations['date'] = pd.to_datetime(vaccinations['date']).dt.strftime('%Y-%m-%d')
    vaccinations['fips_code_text'] = vaccinations['fips_code'].astype(int)
    vaccine_hesitancy = pd.read_parquet('../../data/cdc_scraper/cdc_vaccine_hesitancy.parquet')
    cases = pd.read_parquet('../../data/cases_daily.parquet')
    cases['fips'] = cases['fips'].astype(int)
    non_epidemic = pd.read_csv('../../data/non_epidemic_data.csv')
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
    
    modeling_df.to_parquet('../../data/cdc_scraper/counterfactual_modeling_df.parquet')

    
get_state_vaccination_rates()
create_random_effects_df()
create_counterfactual_frame()