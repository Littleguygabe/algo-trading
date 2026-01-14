import pandas as pd
import yfinance as yf
import logging
import os
logging.basicConfig(level=logging.INFO)

basket = [
    'NVDA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'GOOG', 'META', 'TSLA', 'BRK-B', 'WMT',
    'LLY', 'JPM', 'V', 'ORCL', 'XOM', 'JNJ', 'MA', 'NFLX', 'PLTR', 'ABBV',
    'COST', 'BAC', 'AMD', 'HD', 'PG', 'GE', 'CSCO', 'CVX', 'KO', 'UNH',
    'IBM', 'WFC', 'CAT', 'MS', 'AXP', 'MU', 'GS', 'MRK', 'CRM', 'TMUS',
    'PM', 'APP', 'RTX', 'MCD', 'ABT', 'TMO', 'AMAT', 'ISRG', 'PEP', 'LRCX'
    ]

output_dir = 'data/historical_data'

logging.info("Updating Historical Data")

for filename in os.listdir(output_dir):
    os.remove(os.path.join(output_dir,filename))

for ticker in basket:
    yf_ticker = yf.Ticker(ticker)
    data = yf_ticker.history(period='5y')
    data.to_csv(os.path.join(output_dir,f'{ticker}.csv'))
    logging.info(f"{ticker} data updated")

logging.info("Finished Updating Historical Data")

