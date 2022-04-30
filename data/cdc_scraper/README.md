# CDC Data Description

## Time series of Community Transmission and Positivity rates 
This [public use dataset](https://data.cdc.gov/Public-Health-Surveillance/United-States-COVID-19-County-Level-of-Community-T/nra9-vzzn) has 7 data elements reflecting historical data for community transmission levels for all available counties. This dataset contains historical data for the county level of community transmission and includes updated data submitted by states and jurisdiction.

- `state_name`
- `county_name` 
- `fips_code`: 5 digit in data, split in scraping
- `date`: Week ending date for the 7-day period for the case rate and the percent positivity
- `cases_per_100k_7_day_count`: Total number of new cases per 100,000 persons within the last 7 days
- `percent_test_results_reported`: Percentage of positive diagnostic and screening nucleic acid amplification tests (NAAT) during the last 7 days
- `community_transmission_level`: Community Transmission Level Indicator [low, moderate, substantial, high, blank]  

    - Low Transmission Threshold: Counties with fewer than 10 total cases per 100,000 population in the past 7 days, and a NAAT percent test positivity in the past 7 days below 5%;

    - Moderate Transmission Threshold: Counties with 10-49 total cases per 100,000 population in the past 7 days or a NAAT test percent positivity in the past 7 days of 5.0-7.99%;

    - Substantial Transmission Threshold: Counties with 50-99 total cases per 100,000 population in the past 7 days or a NAAT test percent positivity in the past 7 days of 8.0-9.99%;

    - High Transmission Threshold: Counties with 100 or more total cases per 100,000 population in the past 7 days or a NAAT test percent positivity in the past 7 days of 10.0% or greater.

    - Blank : total new cases in the past 7 days are not reported (county data known to be unavailable) and the percentage of positive NAATs tests during the past 7 days (blank) are not reported.
## Vaccine Hesitancy Estimates by county
This [dataset](https://data.cdc.gov/Vaccinations/Vaccine-Hesitancy-for-COVID-19-County-and-local-es/q9mh-h2tw) contains estimates for hesitancy rates at the state level using the U.S. Census Bureau’s Household Pulse Survey data and utilize the estimated values to predict hesitancy rates at the Public Use Microdata Areas (PUMA) level using the Census Bureau’s 2019 American Community Survey (ACS) 1-year Public Use Microdata Sample (PUMS)

Column Name	Description	Type
- `County_Name`
- `FIPS_Code`	
- `State`	
- `Estimated_hesitant`: Estimate of percentage of adults who describe themselves as “probably not” or “definitely not” going to get a COVID-19 vaccine once one is available to them, based on national survey data.
Number
- `Estimated_hesitant_or_unsure`: Estimate of percentage of adults who describe themselves as “unsure”, “probably not”, or “definitely not” going to get a COVID-19 vaccine once one is available to them, based on national survey data.
- `Estimated_strongly_hesitant`: Estimate of percentage of adults who describe themselves as “definitely not” going to get a COVID-19 vaccine once one is available to them, based on national survey data.
- `Social_Vulnerability_Index`
SVI values range from 0 (least vulnerable) to 1 (most vulnerable).
- `SVI_Category`: SVI categorized as follows: Very Low (0.0-0.19), Low (0.20-0.39); Moderate (0.40-0.59); High (0.60-0.79); Very High (0.80-1.0)
- `CVAC level of concern for vaccination rollout`:	
CVAC Index values range from 0 (lowest concern) to 1 (highest concern)
- `CVAC Level Of Concern`: CVAC categorized as follows: Very Low (0.0-0.19), Low (0.20-0.39); Moderate (0.40-0.59); High (0.60-0.79); Very High (0.80-1.0)
- `Percent adults fully vaccinated against COVID-19` (as of 6/10/21)	
- `Percent Hispanic`
- `Percent non-Hispanic American Indian/Alaska Native`
- `Percent non-Hispanic Asian`
- `Percent non-Hispanic Black`
- `Percent non-Hispanic Native Hawaiian/Pacific Islander`
- `Percent non-Hispanic White`


## Time series of vaccinations by county

## Time series of public mask mandates by county [April 10 2020-August 15 2021]


## Time series of stay at home orders [March 15 2020-August 15 2021]
## Time series of public gathering bans [March 11 2020- August 15 2021]
## Time series of bar closings and reopenings  [March 11 2020- August 15 2021]
## Time series of restaurant closings and reopenings  [March 11 2020- August 15 2021]
