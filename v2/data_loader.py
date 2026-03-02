import pandas as pd
import questionary
import os

class DataLoader:
    def __init__(self) -> None:
        self._parent_data_folder = './data'

        self.loaded_data = self._load_data()

    def _load_data(self) -> None:
        # * get the name of the data folder from the user
        # ? Actually read the data from the folder
        # ? Merge the returned data into the correct format
        
        data_folder = self._get_data_folder_name()


        unformatted_dataframes = self._read_data_folder(data_folder)


    def _get_data_folder_name(self) -> str:
        data_options = os.listdir(self._parent_data_folder)
        data_options = [x for x in data_options if '.' not in x]
        result = questionary.select(
            'Choose a data folder to use:',
            choices=data_options
        ).ask()

        return result

    def _read_data_folder(self,data_folder:str) -> pd.DataFrame:
        folder_path = os.path.join(self._parent_data_folder,data_folder)
        filenames = os.listdir(folder_path)

        all_tickers_data = []

        for filename in filenames:
            ticker = filename.replace('.csv','')

            file_path = os.path.join(folder_path,filename)
            read_df = pd.read_csv(file_path)
            



