import pandas as pd
import numpy as np
from linearmodels import PanelOLS
import statsmodels.api as sm
import statsmodels.formula.api as smf

modeling_df_final = pd.read_parquet('../../data/cdc_scraper/random_effects_modeling_df.parquet')
modeling_df_final.columns = modeling_df_final.columns.str.replace(' ', '_')
modeling_df_final.columns = modeling_df_final.columns.str.replace('/', '_')
modeling_df_final.columns = modeling_df_final.columns.str.replace('-', '_')
modeling_df_final['date'] = pd.to_datetime(modeling_df_final['date'])
modeling_df_final['weekday'] = modeling_df_final['date'].dt.weekday.astype(str)
modeling_df_final['month'] = modeling_df_final['date'].dt.month.astype(str)
modeling_df_final['year'] = modeling_df_final['date'].dt.year.astype(str)
modeling_df_final = pd.get_dummies(modeling_df_final,columns=['weekday','year','month'])

formula = '''
moving_cases_per_100k ~
moving_cases_lag_1
+moving_cases_lag_2
+moving_cases_lag_3
+moving_cases_lag_4
+moving_cases_lag_5
+ unemployment_rate_2020
+ median_household_income_2019
+ poverty_frac_2019
+ no_high_school
+ high_school_only
+ college_only
+ voted_biden
+ percent_hispanic
+ percent_non_hispanic_black
+ percent_non_hispanic_white
+ face_masks_required_in_public_Public_mask_mandate
+ stay_at_home_Mandatory___all_people
+ gathering_ban_binary_Yes
+ pct_fully_vaccinated
+ weekday_0
+ weekday_1
+ weekday_2
+ weekday_3
+ weekday_4
+ weekday_5
+ year_2020
+ year_2021
+ month_1
+ month_10
+ month_11
+ month_2
+ month_3
+ month_4
+ month_5
+ month_6
+ month_7
+ month_8
+ month_9
'''

model = smf.mixedlm(formula,modeling_df_final, groups=modeling_df_final["fips_code_text"])
result = model.fit(method=["bfgs"])
print(result.summary())

df = pd.concat([result.params, result.pvalues], axis=1)
df.columns = ["coef", "pval"]
df.to_csv("../../data/results.csv")