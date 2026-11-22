import numpy as np
import pandas as pd
from scipy.stats import pearsonr
import json
from loguru import logger
import os

# Set up logging
logger.add("logs/method.log", rotation="10 MB")

# Constants
L = 2260.0
R_water = 0.4615
T0 = 373.15
P0 = 101.325

def calculate_theoretical_boiling_point(p_kpa):
    t = 1.0 / (1.0/T0 - (R_water/L) * np.log(p_kpa/P0))
    return t

def generate_synthetic_data(n=1000, seed=42):
    np.random.seed(seed)
    p = np.random.uniform(80, 105, n)
    rh = np.random.uniform(0, 100, n)
    t_theoretical = calculate_theoretical_boiling_point(p)
    t_observed = t_theoretical + (rh * 0.05) + np.random.normal(0, 0.5, n)
    
    data = pd.DataFrame({
        'P_ambient': p,
        'T_boiling_observed': t_observed,
        'Relative_Humidity': rh,
        'T_theoretical': t_theoretical
    })
    return data

def compute_correlation(data, method='pearson'):
    """Compute correlation between T_err and RH."""
    if method == 'pearson':
        return pearsonr(data['T_err'], data['Relative_Humidity'])
    elif method == 'spearman':
        from scipy.stats import spearmanr
        return spearmanr(data['T_err'], data['Relative_Humidity'])
    else:
        raise ValueError(f"Unknown method: {method}")

def baseline_predictor(data):
    """Baseline: predicts zero correlation (mean error)."""
    return 0.0

def our_method_predictor(data):
    """Our method: Pearson correlation between T_err and RH."""
    corr_coeff, _ = pearsonr(data['T_err'], data['Relative_Humidity'])
    return corr_coeff

def run_analysis():
    # Generate 10 different datasets (different seeds) for multiple examples
    n_examples = 10
    examples = []
    
    # Use first dataset for main figure data
    main_data = generate_synthetic_data(n=1000, seed=42)
    main_data['T_err'] = main_data['T_boiling_observed'] - main_data['T_theoretical']
    
    for i in range(n_examples):
        # Each example uses a different random seed
        seed = 42 + i * 100
        data = generate_synthetic_data(n=1000, seed=seed)
        data['T_err'] = data['T_boiling_observed'] - data['T_theoretical']
        
        # Our method: Pearson correlation
        our_corr, our_p = pearsonr(data['T_err'], data['Relative_Humidity'])
        
        # Baseline: Spearman correlation (different method)
        baseline_corr, baseline_p = compute_correlation(data, method='spearman')
        
        # Also test baseline as zero predictor
        baseline_zero = baseline_predictor(data)
        
        example = {
            "input": f"correlation analysis of boiling point error with relative humidity (seed={seed})",
            "output": f"pearson_r: {our_corr:.4f}, p: {our_p:.4f}; spearman_r: {baseline_corr:.4f}, p: {baseline_p:.4f}",
            "predict_our_method": f"{our_corr:.4f}",
            "predict_baseline": f"{baseline_corr:.4f}"
        }
        examples.append(example)
    
    # Format for exp_gen_sol_out.json schema
    results = {
        "datasets": [
            {
                "dataset": "synthetic_boiling_point_data",
                "examples": examples
            }
        ]
    }
    
    # Save results
    with open('results.json', 'w') as f:
        json.dump(results, f, indent=4)
        
    # Save data for figure (use main dataset)
    fig_data = {
        "Relative_Humidity": main_data['Relative_Humidity'].tolist(),
        "T_err": main_data['T_err'].tolist()
    }
    with open('fig_data.json', 'w') as f:
        json.dump(fig_data, f)
        
    logger.info(f"Analysis complete. Generated {n_examples} examples.")
    logger.info(f"First example: {examples[0]}")

if __name__ == "__main__":
    if not os.path.exists("logs"):
        os.makedirs("logs")
    run_analysis()
