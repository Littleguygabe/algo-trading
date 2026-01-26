import datetime
import yfinance as yf
import walk_forward_pca as wf_pca
from portfolio import Portfolio
from tqdm import tqdm

def getBasketData(basket):
    yesterday = datetime.date.today()-datetime.timedelta(1)
    start_date = datetime.date.today() - datetime.timedelta(1464)
    end_date = yesterday

    basket_data = yf.download(basket,start=start_date,end=end_date)
    return basket_data


if __name__ == '__main__':
    universe = [
    'NVDA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'GOOG', 'META', 'TSLA', 'BRK-B', 'WMT',
    'LLY', 'JPM', 'V', 'ORCL', 'XOM', 'JNJ', 'MA', 'NFLX', 'PLTR', 'ABBV',
    'COST', 'BAC', 'AMD', 'HD', 'PG', 'GE', 'CSCO', 'CVX', 'KO', 'UNH',
    'IBM', 'WFC', 'CAT', 'MS', 'AXP', 'MU', 'GS', 'MRK', 'CRM', 'TMUS',
    'PM', 'APP', 'RTX', 'MCD', 'ABT', 'TMO', 'AMAT', 'ISRG', 'PEP', 'LRCX'
    ]

    # Expanded S&P 500 Universe (~120 Tickers)
# Selected for high liquidity and sector representation.

    expanded_universe = [
    # --- TECHNOLOGY (High Beta, Growth Factors) ---
    'AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL', 'META', 'TSLA', 'AVGO', 'AMD', 'QCOM',
    'TXN', 'INTC', 'AMAT', 'LRCX', 'MU', 'ADI', 'IBM', 'ORCL', 'CRM', 'ADBE',
    'INTU', 'NOW', 'CSCO', 'PANW', 'SNPS', 'CDNS', 'KLAC', 'MCHP', 'APH', 'GLW',

    # --- FINANCIALS (Interest Rate Sensitive) ---
    'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'BLK', 'AXP', 'V', 'MA',
    'PYPL', 'SCHW', 'SPGI', 'MCO', 'PGR', 'CB', 'MMC', 'AON', 'USB', 'PNC',
    'TFC', 'BK', 'STT', 'COF', 'FITB', 'HIG', 'ALL', 'TRV', 'AIG', 'MET',

    # --- HEALTHCARE (Defensive Growth) ---
    'LLY', 'JNJ', 'MRK', 'ABBV', 'PFE', 'BMY', 'AMGN', 'GILD', 'VRTX', 'REGN',
    'UNH', 'ELV', 'CVS', 'CI', 'HUM', 'TMO', 'DHR', 'ABT', 'SYK', 'MDT',
    'BSX', 'ISRG', 'ZTS', 'IDXX', 'IQV', 'A', 'BAX', 'BDX', 'EW', 'HCA',

    # --- CONSUMER DISCRETIONARY (Cyclical) ---
    'HD', 'LOW', 'MCD', 'SBUX', 'CMG', 'NKE', 'LULU', 'TJX', 'TGT', 'BKNG',
    'MAR', 'HLT', 'F', 'GM', 'TSCO', 'ORLY', 'AZO', 'ROST', 'YUM', 'DRI',

    # --- CONSUMER STAPLES (Defensive, Low Vol) ---
    'WMT', 'COST', 'PG', 'KO', 'PEP', 'MNST', 'PM', 'MO', 'CL', 'EL',
    'KMB', 'GIS', 'K', 'HSY', 'SYY', 'KR', 'ADM', 'STZ', 'TSN', 'CAG',

    # --- INDUSTRIALS & ENERGY (Value / Commodity) ---
    'CAT', 'DE', 'HON', 'GE', 'RTX', 'LMT', 'NOC', 'GD', 'BA', 'UPS',
    'FDX', 'UNP', 'CSX', 'NSC', 'ETN', 'ITW', 'EMR', 'PH', 'CMI', 'PCAR',
    'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'MPC', 'PSX', 'VLO', 'OXY', 'KMI'
    ]

    basket_data = getBasketData(universe)
    window_size = 130
    testing_portfolio = Portfolio(100000)
    for i in tqdm(range(window_size,len(basket_data)),desc='Backtesting...'):
        data_window = basket_data.iloc[i-window_size:i]
        wf_pca.main(data_window,testing_portfolio)

    testing_portfolio.printValueHistory()
    testing_portfolio.printTransactionHistory()

    testing_portfolio.cleanUp(basket_data.iloc[-1]['Close'])