import numpy as np
import yfinance as yf
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import datetime
import pandas as pd
from sklearn import linear_model
import matplotlib.pyplot as plt

def getBasketCloseData(basket):
    yesterday = datetime.date.today()-datetime.timedelta(1)
    start_date = datetime.date.today() - datetime.timedelta(366)
    end_date = yesterday

    basket_close_data = yf.download(basket,start=start_date,end=end_date)['Close']
    basket_close_data = pd.DataFrame(basket_close_data,columns=basket)

    return basket_close_data

def getStandardisedBasketReturns(data,train_size=0.8):
    data = data.ffill()
    data = data.dropna(axis=0)

    #remove any data that has a return outside 3 standard deviations
    data_returns = data.pct_change(1)
    data_returns = data_returns[data_returns.apply(lambda x: (x-x.mean()).abs()<(3*x.std())).all(1)]

    data_returns.dropna(how='any',inplace=True)

    percentage = int(len(data_returns)*train_size)
    X_train_raw = data_returns[:percentage]
    X_test_raw = data_returns[percentage:]


    scaler = StandardScaler().fit(X_train_raw) #fit the data on the training data otherwise the test data will have an impact on the calculated values

    X_train = pd.DataFrame(scaler.transform(X_train_raw),columns=data.columns)
    if train_size<1:
        X_test = pd.DataFrame(scaler.transform(X_test_raw),columns=data.columns)
    else:
        X_test = None

    return X_train,X_test

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


def compareHedgeStock(hedged_ticker,hedge_series,ticker_data):
    target_ticker_close = ticker_data[hedged_ticker]
    #get the aggregated synthetic portfolio values
    synthetic_values = ticker_data.drop(columns=[hedged_ticker]).values @ hedge_series.values
    comparison_df = pd.DataFrame()
    comparison_df[f'{hedged_ticker}_val'] = target_ticker_close
    comparison_df[f'synthetic_val'] = synthetic_values

    comparison_df[f'{hedged_ticker}_returns'] = target_ticker_close.pct_change(1)

    comparison_df[f'synthetic_returns'] = comparison_df['synthetic_val'].pct_change(1)

    comparison_df['translated_synthetic_val'] = comparison_df['synthetic_val']-(comparison_df['synthetic_val'].iloc[0]-comparison_df[f'{hedged_ticker}_val'].iloc[0])



    plt.plot(comparison_df['translated_synthetic_val'],alpha = 0.5,label='synthetic')
    plt.plot(comparison_df[f'{hedged_ticker}_val'],label='target')
    plt.legend()
    plt.show()


def hedgeCoordinator(target_ticker,basket):
    basket_close_data = getBasketCloseData(basket)
    train_basket_returns,test_basket_returns = getStandardisedBasketReturns(basket_close_data,1)

    hedge_position_series = generateSyntheticHedge(target_ticker,train_basket_returns,15)

    
    # compareHedgeStock(target_ticker,hedge_position_series,basket_close_data)

    return hedge_position_series


if __name__ == '__main__':
    basket = [
    'NVDA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'GOOG', 'META', 'TSLA', 'BRK-B', 'WMT',
    'LLY', 'JPM', 'V', 'ORCL', 'XOM', 'JNJ', 'MA', 'NFLX', 'PLTR', 'ABBV',
    'COST', 'BAC', 'AMD', 'HD', 'PG', 'GE', 'CSCO', 'CVX', 'KO', 'UNH',
    'IBM', 'WFC', 'CAT', 'MS', 'AXP', 'MU', 'GS', 'MRK', 'CRM', 'TMUS',
    'PM', 'APP', 'RTX', 'MCD', 'ABT', 'TMO', 'AMAT', 'ISRG', 'PEP', 'LRCX'
    ]

    target_ticker = 'NVDA'

    hedge_position_series = hedgeCoordinator(target_ticker,basket)


