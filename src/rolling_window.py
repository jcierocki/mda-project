import pandas as pd
import numpy as np
from multiprocessing import Pool, cpu_count
from typing import Callable, Union


class RollingWindow(object):
    def __init__(self, data: Union[np.array, pd.Series], window_size: int, forecast_horizon: int = 1) -> None:
        self.__data = data
        self.__last_index = len(data)
        self.__window_size = window_size
        self.__forecast_horizon = forecast_horizon
        self.__cursor = window_size

    def __next__(self):
        if self.__cursor + self.__forecast_horizon > self.__last_index:
            raise StopIteration
        else:
            train_data = self.__data[(self.__cursor - self.__window_size):self.__cursor]
            test_data = self.__data[self.__cursor:(self.__cursor + self.__forecast_horizon)]
            self.__cursor += 1
            return train_data, test_data

    def __iter__(self):
        self.__cursor = self.__window_size
        return self


# meaninful only when horizon = 1
def basic_rollapply(fn: Callable, rolling_window: RollingWindow, window_size: int) -> np.array:
    with Pool(cpu_count() - 2) as p:
        output = p.map_async(
            fn,
            (train for train, _ in rolling_window)
        )
        return np.concatenate([np.repeat(np.NaN, window_size)] + output.get())