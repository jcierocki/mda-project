import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_percentage_error
from statsmodels.tsa.api import ExponentialSmoothing
from itertools import product
from typing import Literal, Union, Callable
import warnings
from functools import partial

import sys
sys.path.insert(1, '../../src')

from rolling_window import RollingWindow, basic_rollapply
from ts_funs import exp_smooth_wrapper, metric_eval_wrapper, calc_score 

SEED = 1234

df = pd.read_parquet("../../data/cases_daily.parquet")

x = df.groupby("date")["cases"].sum()
x[:5]

def expand_grid(d: dict):
   return pd.DataFrame([row for row in product(*d.values())], 
                       columns=d.keys())
params_grid = expand_grid({
    "trend": ["add", "mul"],
    "damped_trend": [True, False],
    "seasonal": ["add", "mul"],
    "initialization_method": ["estimated", "heuristic"],
    "use_boxcox": [True, False]
})
params_grid.head()

FRAC = 0.15
HORIZON_FORECAST = 30

test_size = round(FRAC * len(x))
val_size = round(FRAC * (1 - FRAC) * len(x))

window_size = len(x) - val_size - test_size

x_train1 = x[:(len(x) - test_size)]
x_train2 = x[val_size:]

len(x_train1), len(x_train2)

rw_tuning = RollingWindow(
    x_train1,
    window_size,
    HORIZON_FORECAST
)

rw_eval = RollingWindow(
    x_train2,
    window_size,
    HORIZON_FORECAST
)

fn = partial(calc_score, model_wrapper=exp_smooth_wrapper, rolling_window=rw_tuning, forecast_horizon=HORIZON_FORECAST)

metrics = np.array([], dtype=np.double)
for p in params_grid.to_dict("records"):
    metrics = np.append(metrics, [fn(p)])

params_grid["MAPE"] = metrics
df_best_params = params_grid.sort_values("MAPE", ascending=True).head(3)
df_best_params

best_params = df_best_params.drop(columns=["MAPE"]).head(1).to_dict("records")[0]
best_params

calc_score(
    best_params,
    model_wrapper=exp_smooth_wrapper,
    rolling_window=rw_eval,
    forecast_horizon=HORIZON_FORECAST
)

x1 = x[val_size:-test_size]
x2 = x[-window_size:]

fcst1 = exp_smooth_wrapper(x1, HORIZON_FORECAST, **best_params)
fcst2 = exp_smooth_wrapper(x2, HORIZON_FORECAST, **best_params)

fcst1.index.dtype

x.index = pd.to_datetime(x.index)

plot_df = x \
    .to_frame() \
    .join(fcst1.rename("Forecast 1"), on="date", how="outer") \
    .join(fcst2.rename("Forecast 2"), on="date", how="outer") \
    .reset_index() \
    .drop(columns=["index"])

plot_df.head()

plot_df.to_csv("../.../data/country_level_cases_with_forecast.csv", index=False)

df_fips_states = pd.read_csv("../../data/fips_states.csv", dtype={"fips_state": str})
df_fips_states.state_name = df_fips_states.state_name.str.title()

df_states = df.copy()
df_states["fips_state"] = [f"{fips:05d}"[:2] for fips in df_states.fips]

df_states = pd.merge(
    df_states,
    df_fips_states,
    how="left",
    on="fips_state"
).drop(columns=["fips_state"])

df_states.head()

state_dict = {}

for state, df in df_states.groupby("state_name"):
    state_dict[state] = df.groupby("date")["cases"].sum()

results_list = []
for state_name, df_state in state_dict.items():
    train = df_state[val_size:]
    rw = RollingWindow(train, window_size, HORIZON_FORECAST)

    score = calc_score(
        best_params,
        exp_smooth_wrapper,
        rw, 
        HORIZON_FORECAST
    )

    results_list.append({"state": state_name, "MAPE": score})

results_df = pd.DataFrame.from_records(results_list)
results_df.head()


