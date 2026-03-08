# ! Main issues to fix from v1:
    # fitting pca and linear regression for every single day of data
    # look ahead bias
    # running on mean reversion of daily signals
    # pca overiftting as number of assets > number of observations

# ! Actual Program workflow
    # * 1. Windowing: Pull $T$ days of returns for $N$ stocks.
    # * 2. Factor Extraction: Run PCA once on the $N \times T$ return matrix to get the Top $K$ "market factors."
    # * 3. Beta Estimation: For each stock, regress its returns against those $K$ factors to find its sensitivity (Betas).
    # * 4. Signal Generation: 
        # * Calculate the residual: $StockReturn - (Beta \times FactorReturns)$.
        # * Calculate the cumulative sum of these residuals (this is your "Spread").
        # * Compute the Z-score of this Spread.
    # * 5. Execution: If $Z < -2$, Buy the Stock + Sell the Factor-weighted Basket. If $Z > 2$, Sell the Stock + Buy the Factor-weighted Basket.
    # * 6. Netting: Sum all these individual trade components to get a single "Net Buy/Sell Order" per ticker for the day.


from data_loader import DataLoader
from pca import PCAengine 
import pandas as pd
import numpy as np
import vectorbt as vbt
from tabulate import tabulate


def runAlgo(window_size=392,z_score_threshold=2.65,n_components=7,exit_threshold=0.25):
    data_loader = DataLoader()
    pca_engine = PCAengine(n_components)
    data_loader.increment_current_day(window_size)

    current_signals = np.zeros(len(data_loader.tickers))

    all_target_weights = []

    active_dates = []

    while not data_loader.is_finished:
        active_dates.append(data_loader.dates[data_loader._current_day])
        
        log_ret_data = data_loader.get_window(window_size, True)
        z_scores = pca_engine.get_z_scores(log_ret_data)
        
        H_t = pca_engine.get_hedge_weights().values 
        
        z_vals = z_scores.values.flatten()
        for i, z in enumerate(z_vals):
            if current_signals[i] == 0:
                if z < -(z_score_threshold): current_signals[i] = 1
                elif z > z_score_threshold: current_signals[i] = -1
            elif current_signals[i] == 1 and z >= -exit_threshold:
                current_signals[i] = 0
            elif current_signals[i] == -1 and z <= exit_threshold:
                current_signals[i] = 0

        target_net_weights = current_signals @ H_t
        all_target_weights.append(target_net_weights)

        data_loader.increment_current_day(1)

    weights_df = pd.DataFrame(all_target_weights,index=active_dates,columns=data_loader.tickers)

    vbt_weights = weights_df.shift(1).fillna(0)

    price_data = data_loader.get_data().loc[weights_df.index]

    vbt_weights = vbt_weights.sort_index(axis=1)
    price_data = price_data.sort_index(axis=1)

    portfolio = vbt.Portfolio.from_orders(
        price_data,
        size=vbt_weights,
        size_type='target_percent',
        group_by=True,
        cash_sharing=True,
        init_cash=10000,
        fees=0.001,
        slippage=0.0005,
        freq='1D'
    )
    
    
    print(tabulate(portfolio.stats().items(), headers=['Metric', 'Value'], tablefmt='fancy_grid'))
    portfolio.plot().show()

if __name__ == '__main__':
    runAlgo()