#!/usr/bin/env python3
"""
Testing Boiling Point Non-Hydrostatic Signal.
This script calculates the theoretical boiling point based on pressure (hydrostatic baseline)
and compares it with observed boiling point, correlating the error with vertical wind velocity.
"""

from loguru import logger
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
from scipy import signal

# Setup logging
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/run.log", rotation="30 MB", level="DEBUG")

def calculate_boiling_point(pressure_hpa):
    """
    Using Antoine equation for water boiling point:
    log10(P_mmHg) = A - B / (T_celsius + C)
    T_celsius = B / (A - log10(P_mmHg)) - C
    """
    # 1 hPa = 0.750062 mmHg
    pressure_mmhg = pressure_hpa * 0.750062
    # Constants for water (valid for T in range 1-100 C)
    A, B, C = 8.07131, 1730.63, 233.426
    t_celsius = B / (A - np.log10(pressure_mmhg)) - C
    return t_celsius

def generate_synthetic_data(n_points=5000, fs=1.0, seed=None):
    """
    Generate synthetic high-frequency meteorological data.
    """
    if seed is not None:
        np.random.seed(seed)
    t = np.arange(n_points) / fs
    # Vertical velocity (w) - turbulence
    w = np.random.normal(0, 0.5, n_points)
    # Pressure (P_obs) - with some non-hydrostatic noise correlated with w
    # P_base is hydrostatic, P_non_hydro static is correlated with w
    p_base = 1013.25
    p_non_hydro = 0.1 * w  # Correlation
    p_obs = p_base + p_non_hydro + np.random.normal(0, 0.05, n_points)
    # Temperature (T_obs) - boiling point should be P_obs dependent
    t_base = calculate_boiling_point(p_base)
    t_obs = calculate_boiling_point(p_obs) + np.random.normal(0, 0.01, n_points)
    
    data = pd.DataFrame({
        'time': t,
        'P_obs': p_obs,
        'T_obs': t_obs,
        'w': w
    })
    return data

def run_single_experiment(n_points=5000, seed=None):
    """Run a single experiment and return metrics."""
    data = generate_synthetic_data(n_points=n_points, seed=seed)
    
    # Compute metrics
    data['T_calc'] = calculate_boiling_point(data['P_obs'])
    data['T_error'] = data['T_obs'] - data['T_calc']
    
    # Correlation and Spectral Analysis
    corr = np.corrcoef(data['T_error'], data['w'])[0, 1]
    mean_t_error = data['T_error'].mean()
    std_t_error = data['T_error'].std()
    
    # PSD
    f, psd_t_error = signal.welch(data['T_error'].values, fs=1.0)
    f, psd_w = signal.welch(data['w'].values, fs=1.0)
    
    return {
        'correlation': float(corr),
        'mean_t_error': float(mean_t_error),
        'std_t_error': float(std_t_error),
        'psd_frequencies': f.tolist(),
        'psd_t_error': psd_t_error.tolist(),
        'psd_w': psd_w.tolist()
    }

@logger.catch(reraise=True)
def main():
    logger.info("Starting experiment.")
    
    # Run multiple experiments with different seeds to get 10+ examples
    n_experiments = 12  # Generate 12 examples (more than minimum 10)
    n_points = 5000
    
    all_results = []
    all_psd = []
    
    for i in range(n_experiments):
        logger.info(f"Running experiment {i+1}/{n_experiments}")
        result = run_single_experiment(n_points=n_points, seed=i)
        all_results.append(result)
        all_psd.append({
            'frequencies': result['psd_frequencies'],
            'psd_t_error': result['psd_t_error'],
            'psd_w': result['psd_w']
        })
        
        logger.info(f"  Correlation: {result['correlation']:.6f}, Mean T_error: {result['mean_t_error']:.6f}, Std T_error: {result['std_t_error']:.6f}")
    
    # Build examples for output
    examples = []
    for i, result in enumerate(all_results):
        examples.append({
            "input": f"Calculate Pearson correlation between boiling point prediction error and vertical wind velocity (run {i+1})",
            "output": f"Pearson correlation: {result['correlation']:.6f}",
            "predict_correlation": f"{result['correlation']:.6f}",
            "predict_mean_t_error": f"{result['mean_t_error']:.6f}",
            "predict_std_t_error": f"{result['std_t_error']:.6f}",
            "metadata_analysis": "non_hydrostatic_test",
            "metadata_run": str(i+1),
            "metadata_seed": str(i)
        })
    
    # Save output in exp_gen_sol_out format
    results = {
        "metadata": {
            "method_name": "boiling_point_non_hydrostatic_test",
            "description": "Correlate boiling point prediction error with vertical wind turbulence to test the non-hydrostatic hypothesis.",
            "parameters": {
                "n_points": n_points,
                "fs": 1.0,
                "n_experiments": n_experiments
            }
        },
        "datasets": [
            {
                "dataset": "synthetic_meteorological_data",
                "examples": examples
            }
        ]
    }
    
    output_path = Path("results.json")
    output_path.write_text(json.dumps(results, indent=2))
    logger.info(f"Saved results to {output_path} with {len(examples)} examples")
    
    # Also save PSD data from first run
    psd_data = all_psd[0]
    Path("psd_data.json").write_text(json.dumps(psd_data, indent=2))

if __name__ == "__main__":
    main()
