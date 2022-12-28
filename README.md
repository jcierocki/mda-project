# Modern Data Analytics

This repository contains whole codebase developed within the final assigment for *Modern Data Analytics* [[B-KUL-G0Z39B](https://onderwijsaanbod.kuleuven.be/2022/syllabi/e/G0Z39BE.htm#activetab=doelstellingen_idp29040)] course at KU Leuven, academic year 2021-2022, by a group of six students. The course itself was a broad introduction to Python for data science, with elements of ML and graph analysis.

Our team was given a topic of "COVID-19 pandemic in US". In specific we were asked to collect data and then develop: visualisations, explanatory data analysis and model-based analysis. We developed complex dashboard using such a tech stack:

- Python 3.9.5
- *pip* and *venv* for dependency managment and environment handling
- *Apache Airflow* for data pipeline
- *Apache Parquet* for initial storage
- *MongoDB* (hosted on *Atlas Cloud*) as database
- *Dash* + *Flask* for dashboard and webservice creation
- *Plotly* for visualisations
- *Heroku* for hosting our dashboard

Our model-based analysis included:
- univariate time-series forecasting using ETS model
- counterfactual analysis using XGBoost
- causal inference using linear mixed random effects model

The deployed dashboard is no longer available due to limitations of a free subscription bu can be rebuild if needed.
