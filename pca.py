#princple component analysis of stock data using scikit learn's PCA function
import numpy as np
import yfinance as yf
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import datetime
import pandas as pd
from sklearn import linear_model

def getEvalsEports(data):
    #the close is now auto adjusted in yfinance

    data = data.ffill()
    data = data.dropna(axis=0)

    #remove any data that has a return outside 3 standard deviations
    data_returns = data.pct_change(1)
    data_returns = data_returns[data_returns.apply(lambda x: (x-x.mean()).abs()<(3*x.std())).all(1)]

    data_returns.dropna(how='any',inplace=True)

    percentage = int(len(data_returns)*0.8)
    X_train_raw = data_returns[:percentage]
    X_test_raw = data_returns[percentage:]
 
    scaler = StandardScaler().fit(X_train_raw) #fit the data on the training data otherwise the test data will have an impact on the calculated values

    X_train = pd.DataFrame(scaler.transform(X_train_raw))
    X_test = pd.DataFrame(scaler.transform(X_test_raw))

    #now pre-processing has been performed we can start with PCA
    pca = PCA(n_components=15)
    pca.fit(X_train)

    #for now just returning the top 15 PC's -> need to implement more complex/accurate method
    return pca.explained_variance_ratio_,pca.components_

def getPersonalPortfolioDoDReturns():
    days = 252
    annualised_volatility = 0.2
    drift = 0.15

    daily_vol = annualised_volatility/np.sqrt(days)
    randomised_noise = np.random.normal(0,daily_vol,days)
    target_log_return = np.log(1+drift)
    
    current_sum = np.sum(randomised_noise)
    adjustment = (target_log_return - current_sum)/days
    daily_log_returns = randomised_noise+adjustment

    daily_simple_returns = np.exp(daily_log_returns)-1

    return pd.DataFrame({'DoD_Return':daily_simple_returns});

def getBetaCoefficients(personal_portfolio_returns,eigen_portfolios,basket_data):
    #get DoD returns for each of the stocks in the basket
    #then get values and dot product with eigen portfolios to get each portfolio performance
    
    basket_DoD_returns = basket_data.pct_change().dropna()
    # print(basket_DoD_returns)
    # print(basket_DoD_returns.values)
    eigen_portfolio_returns = pd.DataFrame({'Date':basket_data.index[1:]})


    basket_DoD_returns_matrix = basket_DoD_returns.values

    for i,eigen_portfolio in enumerate(eigen_portfolios):
        portfolio_return_vector = basket_DoD_returns_matrix @ eigen_portfolio
        eigen_portfolio_returns[f'pc_{i}'] = portfolio_return_vector

    aligned_df = pd.concat([eigen_portfolio_returns,personal_portfolio_returns],axis=1).dropna() #link the personal portfolio with the component returns
    regr = linear_model.LinearRegression()

    X = aligned_df.drop(columns=['DoD_Return','Date'])
    y = aligned_df['DoD_Return']
    
    regr.fit(X.values,y.values)
    return regr.coef_ #each of these coefs shows exposure to each pc

if __name__ == '__main__':
    basket = [
    'NVDA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'GOOG', 'META', 'TSLA', 'BRK-B', 'WMT',
    'LLY', 'JPM', 'V', 'ORCL', 'XOM', 'JNJ', 'MA', 'NFLX', 'PLTR', 'ABBV',
    'COST', 'BAC', 'AMD', 'HD', 'PG', 'GE', 'CSCO', 'CVX', 'KO', 'UNH',
    'IBM', 'WFC', 'CAT', 'MS', 'AXP', 'MU', 'GS', 'MRK', 'CRM', 'TMUS',
    'PM', 'APP', 'RTX', 'MCD', 'ABT', 'TMO', 'AMAT', 'ISRG', 'PEP', 'LRCX'
]

    yesterday = datetime.date.today()-datetime.timedelta(1)
    start_date = datetime.date.today() - datetime.timedelta(366)
    end_date = yesterday

    basket_close_data = yf.download(basket,start=start_date,end=end_date)['Close']

    eigen_vals,eigen_portfolios = getEvalsEports(basket_close_data)

    print(eigen_vals)    
    print(eigen_portfolios)

    #for when weve chosen which stock we want to buy based on its residual
    # simulated_personal_returns = getPersonalPortfolioDoDReturns()
    # exposure_coefficients = getPortfolioAnalysis(simulated_personal_returns,eigen_portfolios,basket_close_data)
    

    


    


