from loguru import logger
import sys
import json
import numpy as np
from pathlib import Path

# Setup logging
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add("logs/run.log", rotation="30 MB", level="DEBUG")

def barometric_formula(altitude, lapse_rate=0.0065, T0=288.15, P0=101325):
    """Calculates pressure at altitude (Pa) using the ISA barometric formula."""
    return P0 * (1 - (lapse_rate * altitude / T0))**(9.80665 / (287.05 * lapse_rate))

def antoine_equation(pressure_pa):
    """Calculates boiling point (T) from pressure (Pa) using the Antoine equation.
    Uses NIST water constants: A=8.07131, B=1730.63, C=233.426 for pressure in mmHg, temp in Celsius.
    Valid for 1 to 100°C.
    """
    p_mmhg = pressure_pa / 133.322  # Convert Pa to mmHg
    A, B, C = 8.07131, 1730.63, 233.426
    T_c = B / (A - np.log10(p_mmhg)) - C
    return T_c

def compute_rmse(predictions, observations):
    """Compute Root Mean Square Error between predictions and observations."""
    return float(np.sqrt(np.mean((np.array(predictions) - np.array(observations))**2)))

def main():
    logger.info("Starting boiling point prediction experiment")
    
    # Published empirical data: boiling points from deleze.name (barometric levelling model)
    # Altitudes in meters, boiling points in Celsius
    # Source: https://www.deleze.name/marcel/en/physique/TemperaturesEbullition/table_temperature-en.html
    published_data = [
        {"altitude": -500, "boiling_point": 101.7},
        {"altitude": 0, "boiling_point": 100.0},
        {"altitude": 500, "boiling_point": 98.3},
        {"altitude": 1000, "boiling_point": 96.7},
        {"altitude": 1500, "boiling_point": 95.0},
        {"altitude": 2000, "boiling_point": 93.3},
        {"altitude": 2500, "boiling_point": 91.7},
        {"altitude": 3000, "boiling_point": 90.0},
        {"altitude": 3500, "boiling_point": 88.3},
        {"altitude": 4000, "boiling_point": 86.6},
        {"altitude": 4500, "boiling_point": 84.9},
        {"altitude": 5000, "boiling_point": 83.3},
        {"altitude": 5500, "boiling_point": 81.6},
        {"altitude": 6000, "boiling_point": 79.9},
        {"altitude": 6500, "boiling_point": 78.2},
        {"altitude": 7000, "boiling_point": 76.5},
        {"altitude": 7500, "boiling_point": 74.8},
        {"altitude": 8000, "boiling_point": 73.1},
        {"altitude": 8500, "boiling_point": 71.4},
        {"altitude": 9000, "boiling_point": 69.6},
        {"altitude": 9500, "boiling_point": 67.9},
        {"altitude": 10000, "boiling_point": 66.2},
        {"altitude": 10500, "boiling_point": 64.5},
        {"altitude": 11000, "boiling_point": 62.7},
        {"altitude": 11500, "boiling_point": 61.0},
        {"altitude": 12000, "boiling_point": 59.2},
    ]
    
    # Also include ISA table data from SimuPipe as secondary validation
    # Source: https://simupipe.com/resources/atmospheric-pressure-altitude
    isa_data = [
        {"altitude": 0, "boiling_point": 100.0},
        {"altitude": 250, "boiling_point": 99.1},
        {"altitude": 500, "boiling_point": 98.3},
        {"altitude": 750, "boiling_point": 97.5},
        {"altitude": 1000, "boiling_point": 96.6},
        {"altitude": 1250, "boiling_point": 95.8},
        {"altitude": 1500, "boiling_point": 95.0},
        {"altitude": 1750, "boiling_point": 94.1},
        {"altitude": 2000, "boiling_point": 93.3},
        {"altitude": 2500, "boiling_point": 91.6},
        {"altitude": 3000, "boiling_point": 90.0},
        {"altitude": 3500, "boiling_point": 88.3},
        {"altitude": 4000, "boiling_point": 86.6},
        {"altitude": 4500, "boiling_point": 84.9},
        {"altitude": 5000, "boiling_point": 83.3},
        {"altitude": 6000, "boiling_point": 79.9},
        {"altitude": 8000, "boiling_point": 73.1},
        {"altitude": 10000, "boiling_point": 66.2},
    ]
    
    # Use the more granular published_data as primary ground truth
    altitudes = np.array([d["altitude"] for d in published_data])
    observed_temps = np.array([d["boiling_point"] for d in published_data])
    
    # 1. Validation: Compare baseline (ISA lapse rate 0.0065) against published data
    baseline_lr = 0.0065
    baseline_pressures = barometric_formula(altitudes, lapse_rate=baseline_lr)
    baseline_predictions = np.array([antoine_equation(p) for p in baseline_pressures])
    baseline_rmse = compute_rmse(baseline_predictions, observed_temps)
    
    logger.info(f"Baseline lapse rate: {baseline_lr} K/m")
    logger.info(f"Baseline RMSE: {baseline_rmse:.4f} °C")
    logger.info(f"Predictions at key altitudes: {baseline_predictions[::5]}")
    logger.info(f"Observed at key altitudes: {observed_temps[::5]}")
    
    # 2. Sensitivity analysis for lapse rate (0.005 to 0.008 K/m)
    lapse_rates = np.linspace(0.005, 0.008, 31)  # 31 points for smooth curve
    
    sensitivity_results = []
    
    for lr in lapse_rates:
        pressures = barometric_formula(altitudes, lapse_rate=lr)
        predictions = np.array([antoine_equation(p) for p in pressures])
        rmse = compute_rmse(predictions, observed_temps)
        
        sensitivity_results.append({
            'lapse_rate_k_m': float(lr),
            'rmse_c': float(rmse),
            'predictions_at_key_altitudes': [float(p) for p in predictions[::5]]  # every 5th point
        })
        
    # Find optimal lapse rate
    best_idx = np.argmin([r['rmse_c'] for r in sensitivity_results])
    best_lr = sensitivity_results[best_idx]['lapse_rate_k_m']
    best_rmse = sensitivity_results[best_idx]['rmse_c']
    
    logger.info(f"Optimal lapse rate: {best_lr:.6f} K/m with RMSE: {best_rmse:.4f} °C")
    
    # 3. Also evaluate against ISA data for cross-validation
    isa_altitudes = np.array([d["altitude"] for d in isa_data])
    isa_observed = np.array([d["boiling_point"] for d in isa_data])
    isa_pressures = barometric_formula(isa_altitudes, lapse_rate=baseline_lr)
    isa_predictions = np.array([antoine_equation(p) for p in isa_pressures])
    isa_rmse = compute_rmse(isa_predictions, isa_observed)
    
    logger.info(f"ISA data RMSE (at baseline lr): {isa_rmse:.4f} °C")
    
    # 4. Build output in exp_gen_sol_out schema format
    # Each sensitivity point is an example
    examples = []
    for r in sensitivity_results:
        examples.append({
            "input": f"lapse_rate={r['lapse_rate_k_m']:.4f}",
            "output": f"rmse={r['rmse_c']:.6f}",
            "metadata_lapse_rate_k_m": r['lapse_rate_k_m'],
            "metadata_rmse_c": r['rmse_c'],
            "predict_baseline_rmse": f"{baseline_rmse:.6f}",
            "predict_optimal_rmse": f"{best_rmse:.6f}",
            "predict_optimal_lapse_rate": f"{best_lr:.4f}"
        })
    
    # Also add baseline and ISA validation as examples
    examples.insert(0, {
        "input": "baseline_validation",
        "output": f"rmse={baseline_rmse:.6f}",
        "metadata_lapse_rate_k_m": baseline_lr,
        "metadata_rmse_c": baseline_rmse,
        "metadata_dataset": "published_data",
        "metadata_num_points": len(altitudes),
        "predict_baseline_rmse": f"{baseline_rmse:.6f}",
        "predict_optimal_rmse": f"{best_rmse:.6f}",
        "predict_optimal_lapse_rate": f"{best_lr:.4f}"
    })
    
    examples.append({
        "input": "isa_cross_validation",
        "output": f"rmse={isa_rmse:.6f}",
        "metadata_lapse_rate_k_m": baseline_lr,
        "metadata_rmse_c": isa_rmse,
        "metadata_dataset": "isa_tables",
        "metadata_num_points": len(isa_altitudes),
        "predict_baseline_rmse": f"{baseline_rmse:.6f}",
        "predict_optimal_rmse": f"{best_rmse:.6f}",
        "predict_optimal_lapse_rate": f"{best_lr:.4f}"
    })
    
    output = {
        "metadata": {
            "method_name": "barometric_formula_antoine",
            "description": "Boiling point prediction using ISA barometric formula + Antoine equation with lapse rate sensitivity analysis",
            "parameters": {
                "baseline_lapse_rate_k_m": baseline_lr,
                "optimal_lapse_rate_k_m": best_lr,
                "lapse_rate_sweep_range": [0.005, 0.008],
                "lapse_rate_sweep_points": 31
            }
        },
        "datasets": [
            {
                "dataset": "boiling_point_lapse_rate_sensitivity",
                "examples": examples
            }
        ]
    }
    
    output_path = Path("method_out.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
        
    logger.info(f"Saved complete analysis to {output_path}")

if __name__ == "__main__":
    main()
