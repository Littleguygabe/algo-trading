import portfolio

test_portfolio = portfolio.Portfolio(1000)

test_portfolio.executePurchase('today','TEST',100,'PRIMARY',100)

test_portfolio.executePurchase('today','TEST',50,'PRIMARY',50)

test_portfolio.executePurchase('today','TEST',-300,'PRIMARY',100)
