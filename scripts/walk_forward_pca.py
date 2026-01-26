from portfolio import Portfolio
import pandas as pd
import yfinance as yf
import datetime
import numpy as np
from sklearn import linear_model
from sklearn.decomposition import PCA

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

def generateExecutePositionPurchase(active_portfolio,entry_points,returns_data,close_data,
                                    target_annualised_vol=0.15,
                                    target_capacity = 25,
                                    max_gross_leverage = 2 #max leverage size across this block of trades
                                    ):

    variance_rolling_window_size = 30
    current_date = returns_data.index[-1]

    latest_close_data = close_data.iloc[-1]

    # crop the returns data so that we arent doing uneccessary calculations

    daily_volatility_target = target_annualised_vol/np.sqrt(252)
    vol_df = returns_data.ewm(span=variance_rolling_window_size).std()

    entry_points.sort(key = lambda x: abs(x[1]),reverse=True)

    if len(entry_points)>target_capacity:
        entry_points = entry_points[:target_capacity]


    current_holdings = len(active_portfolio.active_positions)
    spare_capacity = target_capacity - current_holdings

    if spare_capacity <= 0:
        entry_points = []

    elif len(entry_points) > spare_capacity:
        entry_points = entry_points[:spare_capacity]

    entry_points_dict = {}
    for entry in entry_points:
        entry_points_dict[entry[0]] = (entry[1],entry[2])


    ## section for calculating position size
    most_recent_vols = vol_df[list(entry_points_dict.keys())].iloc[-1]
    daily_capital_risk_value = active_portfolio.capital*daily_volatility_target
    risk_value_per_trade = daily_capital_risk_value/np.sqrt(target_capacity) #design the system to make 25 trades on any given day
    max_leverage_per_trade = max_gross_leverage/target_capacity

    # volatility based position sizing - volatility targeting
    for ticker,vol in most_recent_vols.items():
        ideal_position_size = risk_value_per_trade/vol
        max_size_value = active_portfolio.capital*max_leverage_per_trade
        actual_position_size = min(ideal_position_size,max_size_value)

        z_score = entry_points_dict[ticker][0]
        sl_indicator = 1 if z_score<0 else -1

        active_portfolio.openStrategy(ticker,current_date,actual_position_size*sl_indicator,entry_points_dict[ticker][1],latest_close_data) 

def main(basket_data,portfolio):
    close_data = basket_data['Close']
    universe = close_data.columns.values

    returns_data = getLogReturnsDataFromClose(close_data)
    rolling_window_size = 63 #roughly 1 quarter

    entry_points = []

    daily_z_scores = {}

    for ticker in universe: #this calculates the Z score for the most recent day, so in backtesting loop over this passing cropped data in
        # #convert to vectorised operation
        if len(returns_data)<2*rolling_window_size:
            print(f'ERROR > Not enough returns data, needed {rolling_window_size*2} rows and got {len(returns_data)} rows')

        returns_data_window = returns_data[-rolling_window_size*2:]
        replicating_portfolio = generateSyntheticHedge(ticker,returns_data_window)

        X_window = returns_data_window.drop(columns=[ticker])
        y_window = returns_data_window[ticker]

        synthetic_hedge_returns = X_window.values @ replicating_portfolio.values
        residuals = y_window - synthetic_hedge_returns

        std_dev = residuals.std()
        latest_residual = residuals.iloc[-1]

        if std_dev == 0:
            z_score = 0
        else:
            z_score = (latest_residual - residuals.mean())/std_dev

        daily_z_scores[ticker] = z_score

        # print('\t✅')

        #logic for closing a positios

        if abs(z_score)>=2:
            entry_points.append((ticker,z_score,replicating_portfolio))


    portfolio.checkPositionsToClose(daily_z_scores,close_data.iloc[-1],close_data.index[-1])

    if len(entry_points)>0:
        generateExecutePositionPurchase(portfolio,entry_points,returns_data,close_data)

    portfolio.logPortfolioValue(close_data.iloc[-1],close_data.index[-1])

if __name__ == '__main__':
    universe = [
    'NVDA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'GOOG', 'META', 'TSLA', 'BRK-B', 'WMT',
    'LLY', 'JPM', 'V', 'ORCL', 'XOM', 'JNJ', 'MA', 'NFLX', 'PLTR', 'ABBV',
    'COST', 'BAC', 'AMD', 'HD', 'PG', 'GE', 'CSCO', 'CVX', 'KO', 'UNH',
    'IBM', 'WFC', 'CAT', 'MS', 'AXP', 'MU', 'GS', 'MRK', 'CRM', 'TMUS',
    'PM', 'APP', 'RTX', 'MCD', 'ABT', 'TMO', 'AMAT', 'ISRG', 'PEP', 'LRCX'
    ]

    basket_data = getBasketData(universe)
    test_portfolio = Portfolio(100000)
    main(basket_data,test_portfolio)
    test_portfolio.printTransactionHistory()
    test_portfolio.printPrimaryStrategies()