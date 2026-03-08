import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
import pandas as pd
class Portfolio:
    def __init__(self,init_cap) -> None:
        self.capital = init_cap
        self.transaction_history = pd.DataFrame(columns=['Date','Ticker','Value','Share_price','N_shares','Order_Type','Realised_PnL'])
        self.active_positions = pd.DataFrame(columns=['Ticker','Value','Net_share_price','N_shares'])
        self.total_realised_pnl = 0
        self.portfolio_val_evolution = pd.DataFrame(columns=['Total_equity','Capital','Realised_PnL','UnRealised_PnL','Date'])
        #holds the data for primary strategies 'Ticker':{'primary_shares','hedge ratios'}
        self.strategy_book = {}


    def executePurchase(self,date,ticker,value,order_type,share_price = -1):
        n_shares = value / share_price
        trade_pnl = 0

        mask = self.active_positions['Ticker'] == ticker
        
        if ticker in self.active_positions['Ticker'].values:
            existing_n_shares = self.active_positions.loc[mask, 'N_shares'].item()
            existing_value = self.active_positions.loc[mask, 'Value'].item()
            current_avg_price = self.active_positions.loc[mask, 'Net_share_price'].item()

            new_n_shares = existing_n_shares + n_shares

            if (existing_n_shares>0 and new_n_shares<0) or (existing_n_shares<0 and new_n_shares>0):
                #logic for changing the position from one side to the other
                new_avg_price = abs(share_price)

                #would calculate realised PnL here
                trade_pnl = (share_price-current_avg_price) * existing_n_shares

            
            elif abs(new_n_shares)>abs(existing_n_shares):
                #extending a position
                # so average the new value
                new_avg_price = abs((existing_value+value)/(new_n_shares))

            else:
                #reducing a position
                trade_pnl = (share_price-current_avg_price) * (-n_shares)

                new_avg_price = current_avg_price
                
            self.total_realised_pnl +=trade_pnl
            
    

            if abs(new_n_shares) < 0.0001:
                self.active_positions = self.active_positions[self.active_positions['Ticker'] != ticker].reset_index(drop=True)

            else:
                new_value = new_n_shares*new_avg_price
                self.active_positions.loc[mask,['Value','Net_share_price','N_shares']] = [new_value,new_avg_price,new_n_shares]

        else:
            self.active_positions.loc[len(self.active_positions)] = [ticker, value, abs(share_price), n_shares]


        self.transaction_history.loc[len(self.transaction_history)] = [date, ticker, value, share_price, n_shares, order_type,trade_pnl]

    def openStrategy(self,primary_ticker,date,position_size,hedge_weights,market_values):
        #Create a position from a primary ticker, position size and hedge weights

        if primary_ticker in self.strategy_book: #already have a position open for the primary ticker 
            return

        if primary_ticker not in market_values:
            print(f'ERROR > No price data for {primary_ticker} on {date}')
            return

        #execute the primary position purchase
        self.executePurchase(date,primary_ticker,position_size,'PRIMARY',market_values[primary_ticker])
        self.strategy_book[primary_ticker] = {'n_shares':position_size/market_values[primary_ticker],'hedge_weights':hedge_weights,'date':date}

        #execute the hedge orders
        for hedge_ticker,weight in hedge_weights.items():
            hedge_position_value = position_size*weight*-1
            self.executePurchase(date,hedge_ticker,hedge_position_value,'HEDGE',market_values[hedge_ticker]) 

    def checkPositionsToClose(self,z_score_dict,market_values,current_date):
        z_score_risk_threshold = 0.5
        
        tickers_to_unwind = []
        for ticker in self.strategy_book:
            if ticker not in z_score_dict:
                continue
            ticker_z_score = z_score_dict[ticker]
            position = self.strategy_book[ticker]

            should_unwind = False

            if (position['n_shares'] > 0 and ticker_z_score>-z_score_risk_threshold) or (position['n_shares']<0 and ticker_z_score<z_score_risk_threshold):
                should_unwind = True
            
            if (current_date-position['date']).days>30:
                should_unwind = True

            if should_unwind:
                tickers_to_unwind.append(ticker)

        for ticker in tickers_to_unwind:
            position = self.strategy_book[ticker]
            primary_position_value = -1 * position['n_shares'] * market_values[ticker]
            self.executePurchase(current_date,ticker,primary_position_value,'PRIMARY_CLOSE',market_values[ticker])

            for hedge_ticker, weight in position['hedge_weights'].items():
                hedge_value = primary_position_value * weight * -1
                self.executePurchase(current_date,hedge_ticker,hedge_value,'HEDGE_CLOSE',market_values[hedge_ticker])
            
            del self.strategy_book[ticker]

    def printTransactionHistory(self):
        print(tabulate(self.transaction_history,headers='keys',tablefmt='psql'))

    def printActivePositions(self):
        print(tabulate(self.active_positions,headers='keys',tablefmt='psql'))

    def logPortfolioValue(self,current_market_prices,current_date):
        #get the total equity for the portfolio


        unrealised_pnl = 0

        for index,row in self.active_positions.iterrows():
            ticker = row['Ticker']
            if ticker in current_market_prices:
                current_ticker_price = current_market_prices[ticker]
                entry_price = row['Net_share_price']
                n_shares = row['N_shares']

                unrealised_pnl+=(current_ticker_price-entry_price)*n_shares

        equity = self.capital + self.total_realised_pnl + unrealised_pnl
        #intial capital + total realised pnl + unrealised pnl
        self.portfolio_val_evolution.loc[len(self.portfolio_val_evolution)] = [equity,self.capital,self.total_realised_pnl,unrealised_pnl,current_date]

    def printValueHistory(self):
        print(tabulate(self.portfolio_val_evolution,headers='keys',tablefmt='psql'))

    def printPrimaryStrategies(self):
        strat_book_df = pd.DataFrame(columns=['Ticker','Date','N_shares'])
        for key in self.strategy_book:
            inner_dict = self.strategy_book[key]
            strat_book_df.loc[len(strat_book_df)] = [key,inner_dict['date'],inner_dict['n_shares']]

        print(tabulate(strat_book_df,headers='keys',tablefmt='psql'))

    def plotPortfolioValueEvolution(self):
        dates = self.portfolio_val_evolution['Date']
        equity_evolution = self.portfolio_val_evolution['Total_equity']

        plt.plot(dates,equity_evolution)
        plt.show()

    def cleanUp(self,market_values):
        print('--- Positions To Close ---')
        self.printActivePositions()
        active_positions_pnl = 0

        for index,row in self.active_positions.iterrows():
            ticker = row['Ticker']
            position_pnl = (market_values[ticker] - row['Net_share_price']) * row['N_shares']
            active_positions_pnl+=position_pnl

        print(f'Realised PnL: {self.total_realised_pnl}')
        print(f'Un-Realised PnL: {active_positions_pnl}')

        #get the sharpe ratio
        portfolio_returns = self.portfolio_val_evolution['Total_equity'].pct_change()
        portfolio_returns.dropna(inplace=True)
        
        if len(portfolio_returns)>1:
            daily_ret_mean = portfolio_returns.mean()
            daily_ret_std = portfolio_returns.std()
            sharpe_ratio = (daily_ret_mean/daily_ret_std) * np.sqrt(252) # annualises performance
            print(f'Sharpe Ratio: {sharpe_ratio:.4f}')

        else:
            print('Not enough data to calculate performance metrics')

        # plot the portfolio value evolution
        self.plotPortfolioValueEvolution()


