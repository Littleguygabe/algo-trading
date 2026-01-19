import numpy as np
import yfinance as yf
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import datetime
import pandas as pd
from sklearn import linear_model
import matplotlib.pyplot as plt

def getBasketData(basket):
    yesterday = datetime.date.today()-datetime.timedelta(1)
    start_date = datetime.date.today() - datetime.timedelta(732)
    end_date = yesterday

    basket_data = yf.download(basket,start=start_date,end=end_date)
    return basket_data

def getStandardisedBasketReturns(data):
    data = data.ffill()
    data = data.dropna(axis=0)

    #remove any data that has a return outside 3 standard deviations
    data_returns = data.pct_change(1)
    data_returns = data_returns[data_returns.apply(lambda x: (x-x.mean()).abs()<(3*x.std())).all(1)]

    data_returns.dropna(how='any',inplace=True)


    scaler = StandardScaler().fit(data_returns) #fit the data on the training data otherwise the test data will have an impact on the calculated values

    X_train = pd.DataFrame(scaler.transform(data_returns),columns=data.columns)

    return X_train

def getZscores(residuals_data):
    z_score_intervals = [10,20,30,40,50,60,70,80,90]
    z_scores_dict = {}

    for window in z_score_intervals:
        window_history = residuals_data[-window:]
        historical_mean = window_history.mean()
        historical_std = window_history.std()

        cur_residuals = window_history.iloc[-1]

        zscores = (cur_residuals-historical_mean)/historical_std
        z_scores_dict[window] = zscores

    zscores_df = pd.DataFrame(z_scores_dict)

    return zscores_df

def generateSyntheticHedge(target_ticker, returns_data, n_components=15):
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


def compareHedgeStock(hedged_ticker,hedge_dataframe,ticker_return_data,plot_data = False):
    returns_values = ticker_return_data.drop(columns=[hedged_ticker]).values
    weights_values = hedge_dataframe.values

    synthetic_returns = (returns_values*weights_values).sum(axis=1)

    real_returns = ticker_return_data[hedged_ticker].values

    #calculate the R2 score of the synthetic portfolio
    real_returns_average = np.average(real_returns)

    tss = ((real_returns - real_returns_average)**2).sum()
    rss = ((real_returns-synthetic_returns)**2).sum()
    
    r2 = 1 - (rss/tss)
    print(f'R2 Score > {r2}')

    if plot_data:
        plt.plot(real_returns,label='real',alpha=0.5)
        plt.plot(synthetic_returns,label='synthetic',alpha=0.5)
        plt.legend()
        plt.show()





def main(target_ticker,basket_data):
    print(' --- PCA Hedging Strategy ---')

    basket_close_data = basket_data['Close']
    basket_returns = getStandardisedBasketReturns(basket_close_data)

    portfolio_evolution_df = pd.DataFrame()

    # A rolling window of 126 days (approx 6 months) is used to calculate the hedge.
    rolling_window = 63
    n_components = 4

    if len(basket_returns) > rolling_window: 
        hedge_positions = []
        
        hedge_dates = basket_returns.index[rolling_window:]

        for i in range(len(basket_returns) - rolling_window):
            current_data_window = basket_returns.iloc[i:i+rolling_window]
            hedge_position_series = generateSyntheticHedge(target_ticker, current_data_window, min(n_components,rolling_window))
            hedge_positions.append(hedge_position_series)

        portfolio_evolution_df = pd.concat(hedge_positions, axis=1).T
        portfolio_evolution_df.index = hedge_dates


        compareHedgeStock(target_ticker,portfolio_evolution_df,basket_returns[rolling_window:])



    else:
        hedge_position_series = generateSyntheticHedge(target_ticker, basket_returns, min(j,rolling_window))
        portfolio_evolution_df = pd.DataFrame(hedge_position_series).T
        if not basket_returns.empty:
            portfolio_evolution_df.index = [basket_returns.index[-1]]

    return portfolio_evolution_df


if __name__ == '__main__':
    basket = [
    'NVDA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'GOOG', 'META', 'TSLA', 'BRK-B', 'WMT',
    'LLY', 'JPM', 'V', 'ORCL', 'XOM', 'JNJ', 'MA', 'NFLX', 'PLTR', 'ABBV',
    'COST', 'BAC', 'AMD', 'HD', 'PG', 'GE', 'CSCO', 'CVX', 'KO', 'UNH',
    'IBM', 'WFC', 'CAT', 'MS', 'AXP', 'MU', 'GS', 'MRK', 'CRM', 'TMUS',
    'PM', 'APP', 'RTX', 'MCD', 'ABT', 'TMO', 'AMAT', 'ISRG', 'PEP', 'LRCX'
    ]

    target_ticker = 'NVDA'
    basket_data = getBasketData(basket)
    hedge_portfolio_df = main(target_ticker,basket_data)
    # print(hedge_portfolio_df)


