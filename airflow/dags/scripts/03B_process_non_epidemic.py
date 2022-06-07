import pandas as pd
from pandas.api.types import is_numeric_dtype
import numpy as np
import chardet


df_counties = pd.read_csv(
    "../../data/raw/fips_lookup.csv",
    dtype={"state_fips": str, "county_fips": str}
).rename(columns={"county_name": "area"})

df_counties["fips"] = df_counties.state_fips + df_counties.county_fips
df_counties = df_counties.loc[:, ["fips", "area"]]
df_counties.sort_values("fips", axis=0, inplace=True)

_, counts = np.unique(df_counties.fips.values, return_counts=True)
print(f"All FIPS unique: {np.all(counts == 1)}")

df_counties.head()

df_unemp = pd.read_excel(
    "../../data/raw/Unemployment.xlsx", 
    sheet_name="Unemployment Med HH Income", 
    skiprows=4, 
    usecols=["FIPS_Code", "Area_name", "Unemployment_rate_2020", "Median_Household_Income_2019"],
    dtype={"FIPS_Code": str}
).rename(columns={"FIPS_Code": "fips", "Area_name": "area"})

df_unemp.columns = df_unemp.columns.str.lower()
# df_unemp.insert(1, "county", df_unemp.area_name.str.extract(r"(.*(?=County,\s[A-Z]{2}$))")[0])
# df_unemp.drop(columns=["area_name"], inplace=True)
# df_unemp.dropna(subset=["county"], inplace=True)

print(df_unemp.shape)

_, counts = np.unique(df_unemp.fips.values, return_counts=True)
print(f"All FIPS unique: {np.all(counts == 1)}")

df_unemp.head()


with open("../../data/raw/co-est2019-alldata.csv", "rb") as file:
    best_encoding = chardet.detect(file.read())

df_pop = pd.read_csv(
    "../../data/raw/co-est2019-alldata.csv",
    usecols=["STATE", "COUNTY", "CTYNAME", "POPESTIMATE2019"],
    dtype={"STATE": str, "COUNTY": str},
    encoding=best_encoding["encoding"]
).rename(columns={"POPESTIMATE2019": "pop_estimate_2019", "CTYNAME": "area"})

# df_pop.rename(columns={"POPESTIMATE2019": "pop_estimate_2019"}, inplace=True)
# df_pop["county"] = df_pop.CTYNAME.str.extract(r"(.*(?=\sCounty))")[0]
df_pop["fips"] = df_pop.STATE.values + df_pop.COUNTY.values
df_pop = df_pop.loc[:, ["fips", "area", "pop_estimate_2019"]]
# df_pop.dropna(subset=["county"], inplace=True)

print(df_pop.shape)

_, counts = np.unique(df_pop.fips.values, return_counts=True)
print(f"All FIPS unique: {np.all(counts == 1)}")

df_pop.head()

df_election = pd.read_csv(
    "../../data/raw/countypres_2000-2020.csv",
    usecols=["year", "county_name", "county_fips", "candidate", "party", "candidatevotes", "totalvotes"],
    dtype={"county_fips": str}
).rename(columns={"county_name": "area", "county_fips": "fips"})

df_election = df_election.loc[(df_election.year == 2020) & (df_election.candidate != "OTHER"), :]
df_election["votes"] = df_election.candidatevotes / df_election.totalvotes
df_election["area"] = df_election.area.str.title()
df_election.drop(columns=["year", "candidatevotes", "totalvotes"], inplace=True)

df_votes_democrats = df_election.loc[df_election.party == "DEMOCRAT", ["fips", "area", "votes"]]\
    .rename(columns={"votes": "voted_biden"}) \
    .groupby(["fips", "area"], as_index=False) \
    .sum() \

fipses, counts = np.unique(df_votes_democrats.fips.values.astype(str), return_counts=True)
print(f"All FIPS unique: {np.all(counts == 1)}")

df_votes_democrats.head()

df_poverty = pd.read_excel(
    "../../data/raw/PovertyEstimates.xls",
    usecols=["FIPStxt", "Area_name", "PCTPOVALL_2019"],
    dtype={"FIPStxt": str},
    skiprows=4
).rename(columns={
    "FIPStxt": "fips",
    "Area_name": "area",
    "PCTPOVALL_2019": "poverty_frac_2019"
})

df_poverty["poverty_frac_2019"] = df_poverty.poverty_frac_2019 / 100

print(df_poverty.shape)

fipses, counts = np.unique(df_poverty.fips.values.astype(str), return_counts=True)
print(f"All FIPS unique: {np.all(counts == 1)}")

df_poverty.head()

df_education = pd.read_excel(
    "../../data/raw/Education.xls",
    usecols=[
        "FIPS Code", 
        "Area name", 
        "Percent of adults with less than a high school diploma, 2015-19", 
        "Percent of adults with a high school diploma only, 2015-19",
        "Percent of adults completing some college or associate's degree, 2015-19",
        "Percent of adults with a bachelor's degree or higher, 2015-19"
    ],
    dtype={"FIPS Code": str},
    skiprows=4
)

for c in df_education.columns:
    if is_numeric_dtype(df_education[c]):
        df_education[c] = df_education[c] / 100

df_education.columns = ["fips", "area", "no_high_school", "high_school_only", "college_only", "bachelor_or_higher"]

print(df_education.shape)

fipses, counts = np.unique(df_education.fips.values.astype(str), return_counts=True)
print(f"All FIPS unique: {np.all(counts == 1)}")

df_education.head()


df_full = df_counties.copy()

for df in [df_pop, df_unemp, df_poverty, df_education, df_votes_democrats]:
    df_full = pd.merge(
         df_full,
         df.drop(columns=["area"]),
         on="fips",
         how="left"
     )

print(df_full.shape)

df_full.head()
df_full.dropna().shape[0]
df_full.to_csv("../../data/non_epidemic_data.csv", index=False)
