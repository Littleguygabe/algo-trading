import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from tabulate import tabulate

class PCAengine:
    def __init__(self,n_market_factors=1) -> None:
        self._n_components = n_market_factors
        self._hedge_weights = None

    def get_z_scores(self, window_data: pd.DataFrame) -> pd.DataFrame:
        T, N = window_data.shape
        
        if T / N < 3:
            print(f"Warning: Ratio {T/N:.1f}:1 is low.")

        pca = PCA(n_components=self._n_components)
        
        loadings = pca.fit_transform(window_data)
        

        # this step does all 3 of:
            # 1. Get the factors
            # 2. Perform the regression to find the betas for the eigenportfolios
            # 3. Multiply betas with eigen portfolios to get our replicating portfolios
        common_move = pca.inverse_transform(loadings)
        
        #get the replicating portolfios
        #row i holds the replicating portfolio for stock i
        #(i,i) shows the relation of stock to itself so needs to be managed
        
        # pca.components_.T is the same as getting the betas for a given row
        weights_matrix = pca.components_.T @ pca.components_
        
        scaling_factors = 1-np.diag(weights_matrix)

        scaling_factors = np.maximum(scaling_factors, 1e-8)

        W = weights_matrix.copy()

        np.fill_diagonal(W,0)

        scaled_weights = -(W.T/scaling_factors).T      

        np.fill_diagonal(scaled_weights,1.0)

        self._hedge_weights = pd.DataFrame(scaled_weights,index=window_data.columns,columns=window_data.columns)

        residuals = window_data - common_move
        
        spread = residuals.cumsum()

        std_dev = spread.std()
        
        std_dev = std_dev.replace(0, 1.0) 
        z_scores = (spread.tail(1) - spread.mean()) / std_dev

        return z_scores

    def get_hedge_weights(self, ticker=None) -> pd.Series:
        if ticker==None:
            return self._hedge_weights

        if self._hedge_weights is None or ticker not in self._hedge_weights.index:
            return pd.Series() 
        # Drop the ticker itself (which has weight 1.0) to get the synthetic hedge
        return self._hedge_weights.loc[ticker].drop(ticker)

    def print_hedge_weights(self) -> None:
        if self._hedge_weights is None:
            print("No weights calculated yet.")
            return
            
        printed_df = self._hedge_weights.copy()
        
        for col in printed_df.columns:
            printed_df.loc[col, col] = np.nan
            
        print(tabulate(
            printed_df,
            headers='keys',
            tablefmt='fancy_grid',
            missingval='-'
        ))
    
    def set_n_components(self,n_components:int) -> None:
        self._n_components = n_components