import sys

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit("❌ Error: Missing arguments. Usage: python script.py <trading engine filename> <data source filename>")

    trading_engine_name = sys.argv[1]
    data_source = sys.argv[2]

    print(f'Running {trading_engine_name} on {data_source}')
