import pandas as pd
import yfinance as yf
import logging

logging.basicConfig(level=logging.INFO)

basket = [
    'NVDA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'GOOG', 'META', 'TSLA', 'BRK-B', 'WMT',
    'LLY', 'JPM', 'V', 'ORCL', 'XOM', 'JNJ', 'MA', 'NFLX', 'PLTR', 'ABBV',
    'COST', 'BAC', 'AMD', 'HD', 'PG', 'GE', 'CSCO', 'CVX', 'KO', 'UNH',
    'IBM', 'WFC', 'CAT', 'MS', 'AXP', 'MU', 'GS', 'MRK', 'CRM', 'TMUS',
    'PM', 'APP', 'RTX', 'MCD', 'ABT', 'TMO', 'AMAT', 'ISRG', 'PEP', 'LRCX'
    ]

if __name__ == '__main__':
    logging.info("Updating Historical Data")

    for ticker in basket:
        yf_ticker = yf.Ticker(ticker)
        data = yf_ticker.history(period='5y')
        data.to_csv(f'historical_data/{ticker}.csv')
        logging.info(f"{ticker} data updated")

    logging.info("Finished Updating Historical Data")

    