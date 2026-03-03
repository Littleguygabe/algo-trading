import yfinance as yf
import os

basket = ['NVDA','AMD','TSM','MU','MSFT','ADBE','CRM','NOW','AAPL','GOOGL']



output_dir = './data/10_ticker_data'

for filename in os.listdir(output_dir):
    os.remove(os.path.join(output_dir,filename))

for ticker in basket:
    yf_ticker = yf.Ticker(ticker)
    data = yf_ticker.history(period='5y')
    data.to_csv(os.path.join(output_dir,f'{ticker}.csv'))