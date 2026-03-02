# ! Main issues to fix from v1:
    # fitting pca and linear regression for every single day of data
    # look ahead bias
    # running on mean reversion of daily signals
    # pca overiftting as number of assets > number of observations

# ! Actual Program workflow
    # ? 

from data_loader import *

if __name__ == '__main__':
    data_loader = DataLoader()