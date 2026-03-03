from tabulate import tabulate
from data_loader import DataLoader
from pca import PCAengine
import pandas as pd
import numpy as np
import vectorbt as vbt
import matplotlib.pyplot as plt

class HyperParameterTuner:
    def __init__(self) -> None:
        self.data_loader = DataLoader()
        self.PCAengine = PCAengine()
        self.setup_indicator_factory()

    def get_strategy_weights(self,close,window_size: int, n_components: int, z_threshold: float,exit_threshold: float):
        self.PCAengine.set_n_components(n_components)

        price_values = close.values if hasattr(close, 'values') else close
    
    # Calculate Log Returns for this specific run
        log_rets = np.log(price_values / np.roll(price_values, 1, axis=0))
        log_rets[0, :] = 0
        T, N  = price_values.shape
        final_weights = np.zeros((T,N))
        current_signals = np.zeros(N)

        for i in range(window_size, T):
            window_slice = pd.DataFrame(log_rets[i-window_size:i])
            z_scores = self.PCAengine.get_z_scores(window_slice)
            hedge_targets = self.PCAengine.get_hedge_weights()

            z_vals = z_scores.values.flatten()

            for j,z in enumerate(z_vals):
                if current_signals[j]==0:
                    if z < -z_threshold:current_signals[j] = 1
                    elif z > z_threshold:current_signals[j] = -1

                elif current_signals[j] == 1 and z >= -exit_threshold:
                    current_signals[j] = 0

                elif current_signals[j] == -1 and z <= exit_threshold:
                    current_signals[j] = 0

            final_weights[i,:] = current_signals@hedge_targets

        return final_weights


    def setup_indicator_factory(self):
        self.PCAstrategy = vbt.IndicatorFactory(
            class_name = 'PCA_strategy',
            short_name = 'pca_strat',
            input_names = ['close'],
            param_names=['window_size','n_components','z_threshold','exit_threshold'],
            output_names=['weights']
        ).from_apply_func(self.get_strategy_weights)

        self.res = self.PCAstrategy.run(
            self.data_loader.get_data(),
            window_size=np.arange(350, 451, 2).tolist(), 
            # n_components=np.arange(3, 13, 1).tolist(), 
            n_components=[7], 
            z_threshold=np.around(np.arange(2.0, 3.1, 0.05), 2).tolist(),
            exit_threshold=np.around(np.arange(-1.0,1.0,0.05), 2).tolist(),
            param_product=True,
            show_progress=True
        )

    def run_parameter_tuning(self):
        self.portfolio = vbt.Portfolio.from_orders(
            self.data_loader.get_data(),
            size = self.res.weights,
            size_type = 'target_percent',
            cash_sharing=True,
            group_by=self.res.weights.columns.droplevel(-1),
            fees=0.001,
            slippage=0.0005,
            init_cash=10000,
            freq='1D'
        )

    def print_results(self):
        sharpes = self.portfolio.sharpe_ratio()

        trade_counts = self.portfolio.trades.count()

        min_trades = 50
        sharpes = sharpes.replace([np.inf, -np.inf], 0)
        
        valid_mask = trade_counts >= min_trades
        sharpes = sharpes[valid_mask]


        best_params = sharpes.idxmax()
        print(f"Top Params: {best_params}")

        print("\n--- Top 5 by Sharpe ---")
        print(sharpes.sort_values(ascending=False).head(5))
        winner_stats = self.portfolio.xs(best_params, level=(0, 1, 2)).stats()

        print("\n--- Full Stats for Winner ---")
        print(tabulate(winner_stats.to_frame(), headers='keys', tablefmt='fancy_grid'))

    def display_hyper_tuning_results(self):
        sharpes = pd.DataFrame(self.portfolio.sharpe_ratio())
        # Convert the multi-indexed result into a flat DataFrame
        df_flat = sharpes.reset_index()
        
        df_flat.to_csv('output.csv')

        pivot_df = df_flat.pivot(
            index='pca_strat_window_size', 
            columns='pca_strat_z_threshold', 
            values='sharpe_ratio'
        )

        X, Y = np.meshgrid(pivot_df.columns, pivot_df.index)
        Z = pivot_df.values

        # Initialize the plot
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')

        # Plot the surface
        # rstride/cstride control how 'dense' the mesh lines are
        surf = ax.plot_surface(X, Y, Z, 
                            cmap='viridis', 
                            edgecolor='black', 
                            linewidth=0.2, 
                            antialiased=True)

        # Add aesthetic touches
        ax.set_xlabel('Z-Threshold (Standard Deviations)', labelpad=10)
        ax.set_ylabel('Window Size (Lookback)', labelpad=10)
        ax.set_zlabel('Sharpe Ratio', labelpad=10)
        ax.set_title('Strategy Optimization Surface (N-Components fixed by MP)', fontsize=15)

        # Add a colorbar
        fig.colorbar(surf, shrink=0.5, aspect=10, pad=0.1)

        plt.show()

if __name__ == '__main__':
    tuner = HyperParameterTuner()
    tuner.run_parameter_tuning()
    tuner.print_results()
    tuner.display_hyper_tuning_results()


