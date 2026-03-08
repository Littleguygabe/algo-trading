import numpy as np
import pandas as pd
import questionary
import os

class DataLoader:
    def __init__(self) -> None:
        self._data = None

        self._parent_data_folder = './data'
        self._current_day = 0
        
        self._load_data()

        self.tickers = self._data.columns.tolist()        
        self.dates=self._data.index

    def _load_data(self) -> None:
        data_folder = self._get_data_folder_name()

        self._read_data_folder(data_folder)


    def _get_data_folder_name(self) -> str:
        data_options = os.listdir(self._parent_data_folder)
        data_options = [x for x in data_options if '.' not in x]
        result = questionary.select(
            'Choose a data folder to use:',
            choices=data_options
        ).ask()

        return result

    def _read_data_folder(self,data_folder:str) -> None:
        folder_path = os.path.join(self._parent_data_folder,data_folder)
        filenames = os.listdir(folder_path)

        all_tickers_data = []

        for filename in filenames:
            ticker = filename.replace('.csv','')

            file_path = os.path.join(folder_path,filename)
            df = pd.read_csv(file_path,index_col='Date',parse_dates=True)
            
            ticker_series = df['Close'].rename(ticker)
            all_tickers_data.append(ticker_series)

        complete_df = pd.concat(all_tickers_data,axis=1)
        complete_df.sort_index(inplace=True)

        self._data = complete_df.ffill().dropna()
        
        if self._data.empty:
            print("Warning: Your dataset is empty after dropna(). Check ticker date overlaps.")

    def increment_current_day(self, n_increments=1):
        self._current_day += n_increments

    def get_window(self, window_size: int, get_log_returns = False) -> pd.DataFrame:
        """Returns a window of prices ending at the current day (inclusive)."""

        if get_log_returns:
            start_idx = max(0, self._current_day - window_size)
            close_data_window = self._data.iloc[start_idx : self._current_day + 1]
            return np.log(close_data_window / close_data_window.shift(1)).dropna()
        
        else:
            start_idx = max(0, self._current_day - window_size + 1)
            return self._data.iloc[start_idx : self._current_day + 1]

    @property
    def is_finished(self) -> bool:
        """Returns True if we have reached the end of the dataset."""
        if self._data is None or self._current_day is None:
            return False
        return self._current_day >= len(self._data) - 1
        

    def get_data(self, log_returns=False):
        if log_returns:
            close = self._data.clip(lower=1e-8).values 
            log_rets = np.log(close / np.roll(close, 1, axis=0))
            log_rets[0, :] = 0
            
            return np.nan_to_num(log_rets, nan=0.0, posinf=0.0, neginf=0.0)

        return self._data


