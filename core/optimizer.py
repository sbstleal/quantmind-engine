import numpy as np
import pandas as pd

class PortfolioOptimizer:
    
    def __init__(self, returns: pd.DataFrame):
        self.returns = returns
        self.mean_returns = returns.mean()
        self.cov_matrix = returns.cov()

    def run_monte_carlo(self, n_simulations=5000):
        n_assets = len(self.mean_returns)
        results = np.zeros((3 + n_assets, n_simulations))
        
        for i in range(n_simulations):
            weights = np.random.random(n_assets)
            weights /= np.sum(weights)
            
            p_return = np.sum(self.mean_returns * weights) * 252
            p_std = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix * 252, weights)))
            
            results[0,i] = p_return
            results[1,i] = p_std
            results[2,i] = p_return / p_std
            
            for j in range(n_assets):
                results[3+j, i] = weights[j]
                
        columns = ['Return', 'Risk', 'Sharpe'] + [f'W_{t}' for t in self.returns.columns]
        return pd.DataFrame(results.T, columns=columns)