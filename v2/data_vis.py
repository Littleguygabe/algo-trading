import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    # Read the optimization results from CSV
    df = pd.read_csv('./v2/output.csv')
    
    # Clean data: Replace any infinite Sharpe Ratios (common in backtesting errors) with 0
    df['sharpe_ratio'] = df['sharpe_ratio'].replace([np.inf, -np.inf], 0)

    # Pivot the flat CSV data into a 2D matrix suitable for surface plotting
    # Rows: Window Size, Columns: Z-Threshold, Values: Sharpe Ratio
    pivot_df = df.pivot_table(
        index='pca_strat_window_size', 
        columns='pca_strat_z_threshold', 
        values='sharpe_ratio',
        aggfunc='first'
    )

    # Create coordinate matrices for the 3D plot
    X, Y = np.meshgrid(pivot_df.columns, pivot_df.index)
    Z = pivot_df.values

    # Initialize the 3D figure
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Plot the optimization surface
    # rstride/cstride control mesh density; viridis provides clear performance gradients
    surf = ax.plot_surface(X, Y, Z, 
                        cmap='viridis', 
                        edgecolor='black', 
                        linewidth=0.2, 
                        antialiased=True)

    # Labeling and styling consistent with the tuning script
    ax.set_xlabel('Z-Threshold (Standard Deviations)', labelpad=10)
    ax.set_ylabel('Window Size (Lookback)', labelpad=10)
    ax.set_zlabel('Sharpe Ratio', labelpad=10)
    ax.set_title('Strategy Optimization Surface (Loaded from output.csv)', fontsize=15)

    # Add a colorbar for visual reference of the Sharpe Ratio scale
    fig.colorbar(surf, shrink=0.5, aspect=10, pad=0.1)

    plt.tight_layout()
    plt.show()
