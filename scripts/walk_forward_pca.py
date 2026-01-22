import pandas as pd
import yfinance as yf
import datetime
import numpy as np
from sklearn import linear_model
from sklearn.decomposition import PCA
from position_sizer import generatePosition

#create a portfolio class in the backtesting engine.

def getBasketData(basket):
    yesterday = datetime.date.today()-datetime.timedelta(1)
    start_date = datetime.date.today() - datetime.timedelta(732)
    end_date = yesterday

    basket_data = yf.download(basket,start=start_date,end=end_date)
    return basket_data

def getLogReturnsDataFromClose(close_data):
    log_returns = np.log(close_data/close_data.shift(1))
    log_returns.dropna(inplace=True)
    return log_returns

def generateSyntheticHedge(target_ticker, returns_data, n_components=5):
    X = returns_data.drop(columns = [target_ticker])
    y = returns_data[target_ticker]

    pca = PCA(n_components=n_components)
    pca.fit(X)

    factor_returns = pca.transform(X)

    regr = linear_model.LinearRegression()
    regr.fit(factor_returns,y)

    betas = regr.coef_

    synthetic_weights = betas@pca.components_ #components are the eigen portfolios
    hedge_series = pd.Series(synthetic_weights,index = X.columns)

    return hedge_series


def getExpectedReturns(replicating_portfolio,latest_returns):

    filtered_returns = latest_returns[replicating_portfolio.index]
    expected_return = filtered_returns.values @ replicating_portfolio.values
    return expected_return

def main(basket_data,testing_portfolio):
    close_data = basket_data['Close']
    universe = close_data.columns.values

    returns_data = getLogReturnsDataFromClose(close_data)
    rolling_window_size = 63 #roughly 1 quarter

    entry_points = []

    for ticker in universe: #this calculates the Z score for the most recent day, so in backtesting loop over this passing cropped data in
        print(f'Processing PCA for {ticker}... ',end='')
        history = []

        for start_offset in range(rolling_window_size,0,-1): #offset so we dont get todays returns in the train data
            train_start = -(rolling_window_size+start_offset)
            train_end = -start_offset

            data_window = returns_data.iloc[train_start:train_end]
            today_data = returns_data.iloc[-start_offset]

            replicating_portfolio = generateSyntheticHedge(ticker,data_window)

            expected_return = getExpectedReturns(replicating_portfolio,today_data)
            actual_return = today_data[ticker]
            residual_return = actual_return-expected_return

            date = today_data.name
            history.append((date,actual_return,expected_return,residual_return))
            #now have returns window, calculate the replicating portfolio for the given rolling window
        
        df_results = pd.DataFrame(history, columns=['Date', 'Actual', 'Expected', 'Residual'])
        df_results.set_index('Date', inplace=True)
        
        print('\t✅')

        std_dev = df_results['Residual'].std()
        latest_residual = df_results['Residual'].iloc[-1]
        z_score = latest_residual/std_dev
        if abs(z_score)>=2:
            entry_points.append((ticker,z_score,replicating_portfolio))

        #generate a position here
        #as we record the stocks we want to buy for each day

if __name__ == '__main__':
    universe = [
    'NVDA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'GOOG', 'META', 'TSLA', 'BRK-B', 'WMT',
    'LLY', 'JPM', 'V', 'ORCL', 'XOM', 'JNJ', 'MA', 'NFLX', 'PLTR', 'ABBV',
    'COST', 'BAC', 'AMD', 'HD', 'PG', 'GE', 'CSCO', 'CVX', 'KO', 'UNH',
    'IBM', 'WFC', 'CAT', 'MS', 'AXP', 'MU', 'GS', 'MRK', 'CRM', 'TMUS',
    'PM', 'APP', 'RTX', 'MCD', 'ABT', 'TMO', 'AMAT', 'ISRG', 'PEP', 'LRCX'
    ]

    basket_data = getBasketData(universe)
    hedge_portfolio_df = main(basket_data)