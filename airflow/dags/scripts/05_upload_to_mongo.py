import pandas as pd
import numpy as np
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client["MDAProjectDatabase"]

df_cases = pd.read_parquet("../../data/cases_daily.parquet")
df_cases.fips = df_cases.fips.astype(str).str.zfill(5)
client["MDAProjectDatabase"]["daily_covid_cases"].insert_many(df_cases.to_dict("records"))

df_socio_economic = pd.read_csv("../../data/non_epidemic_data.csv")

df_socio_economic = pd.read_csv("../../data/non_epidemic_data.csv")
print(df_socio_economic.shape)
df_socio_economic.head()

fipses_cases = pd.read_csv("../../data/county_daily_csv.csv", usecols=["fips"]).fips.values

df_socio_economic = df_socio_economic.loc[df_socio_economic.fips.isin(fipses_cases), :]
df_socio_economic.shape
client["MDAProjectDatabase"]["socio_economic_data"].insert_many(df_socio_economic.drop(columns=["area"]).to_dict("records"))

df_fips = pd.read_csv("../../data/fips.csv")

df_fips_states = df_fips.loc[df_fips.fips.values % 1000 == 0, :].copy()
df_fips_states.loc[:, "fips_state"] = [f"{int(fips / 1000):02d}" for fips in df_fips_states.fips]
df_fips_states = df_fips_states.drop(columns=["fips"]).rename(columns={"area": "state_name"})

df_fips = df_fips.loc[df_fips.fips.values % 1000 != 0, :]
df_fips.loc[:, "fips_state"] = [f"{fips:05d}"[:2] for fips in df_fips.fips]

df_fips = pd.merge(
    df_fips,
    df_fips_states,
    on="fips_state"
).drop(columns=["fips_state"])

df_fips.fips = df_fips.fips.astype(str).str.zfill(5)

df_fips.head()

df_fips.head().to_dict("records")

client["MDAProjectDatabase"]["fips_codes"].insert_many(df_fips.to_dict("records"))

df_fcst = pd.read_csv("../../data/country_level_cases_with_forecast.csv")
df_fcst.head()


dict_list_no_nan = df_fcst.astype(object).where(df_fcst.notna(), None).to_dict("records")
dict_list_no_nan[0]

db["country_level_cases_with_forecasts"].insert_many(dict_list_no_nan)

df_counterfactual2 = pd.read_csv("../../data/counterfactual_results_model_2.csv").rename(columns={"state_code": "state_name"})
df_counterfactual2.head()

db["counterfactual_model_results"].insert_many(df_counterfactual2.to_dict("records"))


df_abrev_state = pd.read_csv("../../data/state_abrev_dict.csv")
df_abrev_state.fips_state = df_abrev_state.fips_state.astype(str).str.zfill(2)

df_vaccinations = pd.read_csv(
    "../../data/vaccinations_by_state.csv", 
    dtype={"fully_vaccinated": int, "total_pop": int}
) \
    .rename(columns={"state_code": "abrev_state"})\
    .drop(columns=["pct_vaccinated"])

df_vaccinations = pd.merge(
    df_vaccinations,
    df_abrev_state,
    on="abrev_state",
    how="left"
).drop(columns=["abrev_state"])

df_vaccinations = pd.merge(
    df_vaccinations,
    pd.read_csv("../../data/fips_states.csv", dtype={"fips_state": str}),
    on="fips_state",
    how="left"
).drop(columns=["fips_state"])

df_vaccinations.state_name = df_vaccinations.state_name.str.title()
df_vaccinations = df_vaccinations.loc[:, ["date", "state_name", "fully_vaccinated", "total_pop"]]

df_vaccinations
db["vaccinations"].insert_many(df_vaccinations.to_dict("records"))

df_exp_smoothing_best_params = pd.read_csv("../data/best_exp_smoothing_params.csv")
df_exp_smoothing_best_params
db["df_exp_smoothing_best_params"].insert_many(df_exp_smoothing_best_params.to_dict("records"))

df_coefs = pd.read_csv("../data/mixed_reg_coef.csv").round(4).rename(columns={"Unnamed: 0": "paramerter"})
df_coefs.head()
db["mixed_random_effects_coefs"].insert_many(df_coefs.to_dict("records"))

