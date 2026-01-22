import numpy as np


def generatePosition(portfolio_capital, close_price, annualised_vol, num_positions):
    # This is a placeholder for your volatility targeting logic.
    # For example, you might divide your risk budget among the positions.
    if num_positions == 0:
        return 0

    # Example: allocate 2% of capital risk per day, spread across all positions
    daily_risk_budget = portfolio_capital * 0.02
    risk_per_position = daily_risk_budget / num_positions

    # Simplified position size based on volatility
    # Assumes annualised_vol is a decimal (e.g., 0.3 for 30%)
    if annualised_vol == 0:
        return 0
        
    dollar_amount = risk_per_position / (annualised_vol / np.sqrt(252)) # daily vol
    
    position_size = dollar_amount / close_price
    return position_size