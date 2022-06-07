import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_percentage_error
from statsmodels.tsa.api import ExponentialSmoothing
from typing import Literal, Union, Callable
from multiprocessing import Pool, cpu_count
from functools import partial
import warnings

from rolling_window import RollingWindow

def exp_smooth_wrapper(
        train: Union[np.array, pd.Series],
        forecast_horizon: int,
        **params
):
    train  += 1 # Ex Smoothing models require strictly positive data

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        return ExponentialSmoothing(
            train,
            seasonal_periods=7, # Weekly seasonality due to work week influencing collecting data
            **params
        ) \
            .fit() \
            .forecast(forecast_horizon) - 1


def metric_eval_wrapper(
        train: Union[np.array, pd.Series],
        test: Union[np.array, pd.Series],
        model_wrapper: Callable,
        forecast_horizon: int,
        **kwargs
):
    try: # some model combinations are unstable (forbidden) and may generate NaN forecast, this try-block is to catch them
        y_forecast = model_wrapper(train, forecast_horizon=forecast_horizon, **kwargs)
        score = mean_absolute_percentage_error(test, y_forecast)
    except ValueError:
        return 100.0

    return score


def calc_score(args, model_wrapper: Callable, rolling_window: RollingWindow, forecast_horizon: int):
    with Pool(cpu_count() - 2) as p:
        output = p.starmap_async(
            partial(
                metric_eval_wrapper,
                model_wrapper=model_wrapper,
                forecast_horizon=forecast_horizon,
                **args
            ),
            ((train, test) for train, test in rolling_window)
        )
        out = output.get()
    
    return np.mean(out)
