import importlib
import sys
import os
import pandas as pd

# Add the directory of this script to the Python path.
# This allows us to import other scripts in the same directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def readDataSource(data_source):
    data_source = f'data/{data_source}'

    if not os.path.isdir(data_source):
        raise ValueError(f"Data source '{data_source}' is not a directory.")

    csv_files = [f for f in os.listdir(data_source) if f.endswith('.csv') and not f.startswith('.')]
    if not csv_files:
        raise ValueError(f"No CSV files found in '{data_source}'.")

    all_dfs = []
    for filename in csv_files:
        ticker = os.path.splitext(filename)[0]
        filepath = os.path.join(data_source, filename)
        df = pd.read_csv(filepath, index_col='Date', parse_dates=True)
        df['Ticker'] = ticker
        all_dfs.append(df)

    if not all_dfs:
        return pd.DataFrame()

    combined_df = pd.concat(all_dfs)
    combined_df.reset_index(inplace=True)
    
    multi_level_df = combined_df.pivot(index='Date', columns='Ticker')
    
    return multi_level_df


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit("❌ Error: Missing arguments. Usage: python script.py <trading engine filename> <data source filename>")

    trading_engine_name = sys.argv[1]
    data_source = sys.argv[2]

    data = readDataSource(data_source)

    if data is not None and not data.empty:
        print("Successfully loaded data")

    try:
        module_name = os.path.splitext(trading_engine_name)[0]
        script_module = importlib.import_module(module_name)
        
        if hasattr(script_module, 'main'):
            target_ticker = 'NVDA'
            return_data = script_module.main(target_ticker, data)
        else:
            print(f"ERROR: The module '{trading_engine_name}' does not have a 'main()' method")

    except ModuleNotFoundError:
        print(f"ERROR: module '{trading_engine_name}' not found. Ensure it is in the 'scripts' directory.")
    except Exception as e:
        print(f"ERROR: An error occurred while running the trading engine: {e}")
