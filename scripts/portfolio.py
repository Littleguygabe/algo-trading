from tabulate import tabulate
import pandas as pd
class Portoflio:
    def __init__(self,init_cap) -> None:
        self.capital = init_cap
        self.transaction_history = pd.DataFrame(columns=['Date','Ticker','Value'])
        self.currentdate = None
        self.buffered_orders = []
        self.open_positions = []


    def execute_purchase(self,ticker,close,date):
        if self.currentdate == date:
            self.buffered_orders.append((ticker,close,date))

        else:
            if len(self.buffered_orders)!=0:
                self.executeBufferedOrders()
            self.currentdate = date
            self.buffered_orders.append((ticker,close,date))

    def executeBufferedOrders(self):
        for order in self.buffered_orders:
            #logic to perform an order and adjust the portfolio accordingly
            self.transaction_history.loc[len(self.transaction_history)]=[order[2],order[0],order[1]]

        self.buffered_orders = []

    def clearBufferedOrders(self):
        if len(self.buffered_orders)!=0:
            self.executeBufferedOrders()

    def printTransactionHistory(self):
        print(tabulate(self.transaction_history,headers='keys',tablefmt='psql'))