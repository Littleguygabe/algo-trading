from portfolio import Portoflio
from position_sizer import *
from datetime import datetime
from datetime import timedelta

def createTestingDateArray():
    dates = []
    for i in range(3):
        dates.append((datetime.today()-timedelta(days=1)).strftime('%Y-%m-%d'))
    for i in range(2):
        dates.append(datetime.today().strftime('%Y-%m-%d'))
    
    return dates
if __name__ == '__main__':
    test_dates = createTestingDateArray()
    testing_portfolio = Portoflio(1000)


    for date in test_dates:
        testing_portfolio.execute_purchase('test',-1,date)

    testing_portfolio.clearBufferedOrders()

    testing_portfolio.printTransactionHistory()