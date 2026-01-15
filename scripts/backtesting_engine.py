import importlib
import sys
import os
import pandas as pd

def readDataSource(data_source):
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
        script_module = importlib.import_module(f'scripts.{trading_engine_name}.py')
        if hasattr(script_module,'main'):
            script_module.main(data)

        else:
            print(f"ERROR: The module '{trading_engine_name}.py' does not have a 'main()' method")

    except ModuleNotFoundError:
        print(f"ERROR: module '{trading_engine_name}.py' not found")

    except Exception as e:
        print(f"ERROR: Unknown error occurred > {e}")