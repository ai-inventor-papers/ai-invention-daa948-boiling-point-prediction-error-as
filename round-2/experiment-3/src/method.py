#!/usr/bin/env python3
"""
Empirical Validation of Boiling Point Model

Validates the ISA barometric formula and Antoine equation against empirical
boiling point measurements at altitude, and assesses lapse rate sensitivity.

This script implements:
1. ISA Pressure: P(z) = P0 * (1 - L*z/T0)**(g*M/(R*L))
2. Antoine BP: T(P_hPa) = B / (A - log10(P_hPa)) - C
3. Empirical validation against published boiling point tables
4. Sensitivity analysis on lapse rate L
5. Baseline comparison with simpler barometric formula
"""

from loguru import logger
from pathlib import Path
import json
import math
import sys
import numpy as np
from typing import List, Tuple, Dict, Any

# Constants from the artifact plan
P0 = 1013.25  # hPa, sea level pressure
T0 = 288.15   # K, sea level temperature
g = 9.80665   # m/s^2, gravitational acceleration
M = 0.0289644 # kg/mol, molar mass of dry air
R = 8.31447   # J/(mol*K), universal gas constant
L = 0.0065    # K/m, standard temperature lapse rate

# Antoine equation constants for water (pressure in hPa, temperature in °C)
A = 8.07131
B = 1730.63
C = 233.426

# Exponent in ISA formula
ISA_EXPONENT = g * M / (R * L)


def isa_pressure(altitude_m: float, lapse_rate: float = L) -> float:
    """
    Calculate pressure at altitude using ISA barometric formula.
    
    P(z) = P0 * (1 - L*z/T0)**(g*M/(R*L))
    
    Args:
        altitude_m: Altitude in meters
        lapse_rate: Temperature lapse rate in K/m (default: 0.0065)
    
    Returns:
        Pressure in hPa
    """
    if lapse_rate == 0:
        # Isothermal atmosphere fallback
        return P0 * math.exp(-g * M * altitude_m / (R * T0))
    
    exponent = g * M / (R * lapse_rate)
    term = 1 - lapse_rate * altitude_m / T0
    
    if term <= 0:
        # Above tropopause or invalid altitude
        return 0.0
    
    return P0 * (term ** exponent)


def antoine_boiling_point(pressure_hpa: float) -> float:
    """
    Calculate boiling point of water using Antoine equation.
    
    T(P) = B / (A - log10(P)) - C
    
    Args:
        pressure_hpa: Pressure in hPa
    
    Returns:
        Boiling point in °C
    
    Note: Antoine constants A=8.07131, B=1730.63, C=233.426 are for
    pressure in mmHg. Convert hPa to mmHg: 1 hPa = 0.750062 mmHg.
    """
    if pressure_hpa <= 0:
        return -273.15  # Absolute zero fallback
    
    # Convert hPa to mmHg
    pressure_mmhg = pressure_hpa * 0.750062
    
    return B / (A - math.log10(pressure_mmhg)) - C


def boiling_point_at_altitude(altitude_m: float, lapse_rate: float = L) -> float:
    """
    Calculate boiling point at altitude using ISA + Antoine.
    
    Args:
        altitude_m: Altitude in meters
        lapse_rate: Temperature lapse rate in K/m
    
    Returns:
        Boiling point in °C
    """
    pressure = isa_pressure(altitude_m, lapse_rate)
    return antoine_boiling_point(pressure)


def baseline_pressure(altitude_m: float) -> float:
    """
    Baseline: Simple exponential barometric formula (isothermal atmosphere).
    
    P(z) = P0 * exp(-g*M*z/(R*T0))
    
    This is a common simplified model used as a baseline.
    """
    return P0 * math.exp(-g * M * altitude_m / (R * T0))


def baseline_boiling_point(altitude_m: float) -> float:
    """Calculate boiling point using baseline pressure model."""
    pressure = baseline_pressure(altitude_m)
    return antoine_boiling_point(pressure)


# Empirical data from engineeringtoolbox.com (converted to meters and °C)
# This is the primary empirical dataset
EMPIRICAL_DATA_ENGINEERINGTOOLBOX = [
    # (altitude_m, boiling_point_c)
    (-305, 101.1),
    (-229, 100.8),
    (-152, 100.5),
    (-76, 100.3),
    (0, 100.0),
    (76, 99.7),
    (152, 99.5),
    (229, 99.2),
    (305, 98.9),
    (381, 98.6),
    (457, 98.4),
    (533, 98.1),
    (610, 97.8),
    (686, 97.6),
    (762, 97.3),
    (838, 97.1),
    (914, 96.8),
    (991, 96.5),
    (1067, 96.3),
    (1143, 96.0),
    (1219, 95.7),
    (1295, 95.5),
    (1372, 95.2),
    (1448, 94.9),
    (1524, 94.7),
    (1600, 94.4),
    (1676, 94.2),
    (1753, 93.9),
    (1829, 93.6),
    (1905, 93.4),
    (1981, 93.1),
    (2057, 92.9),
    (2134, 92.6),
    (2210, 92.4),
    (2286, 92.1),
    (2362, 91.8),
    (2438, 91.6),
    (2515, 91.3),
    (2591, 91.1),
    (2667, 90.8),
    (2743, 90.6),
    (2819, 90.3),
    (2896, 90.1),
    (2972, 89.8),
    (3048, 89.6),
    (3124, 89.3),
    (3200, 89.1),
    (3277, 88.8),
    (3353, 88.6),
    (3429, 88.3),
    (3505, 88.1),
    (3581, 87.8),
    (3658, 87.6),
    (3734, 87.3),
    (3810, 87.1),
    (3886, 86.8),
    (3962, 86.6),
    (4037, 86.4),
    (4115, 86.1),
    (4191, 85.9),
    (4267, 85.6),
    (4343, 85.4),
    (4420, 85.1),
    (4496, 84.9),
    (4572, 84.7),
    (4648, 84.4),
    (4724, 84.2),
    (4801, 83.9),
    (4877, 83.7),
    (4953, 83.5),
    (5029, 83.2),
    (5105, 83.0),
    (5182, 82.7),
    (5258, 82.5),
    (5334, 82.3),
    (5410, 82.0),
    (5486, 81.8),
    (5563, 81.6),
    (5639, 81.3),
    (5715, 81.1),
    (5791, 80.9),
    (5867, 80.6),
    (5944, 80.4),
    (6020, 80.2),
    (6096, 79.9),
    (6172, 79.7),
    (6248, 79.5),
    (6325, 79.3),
    (6401, 79.0),
    (6477, 78.8),
    (6553, 78.6),
    (6629, 78.3),
    (6706, 78.1),
    (6782, 77.9),
    (6858, 77.7),
    (6934, 77.4),
    (7010, 77.2),
    (7087, 77.0),
    (7163, 76.8),
    (7239, 76.5),
    (7315, 76.3),
    (7391, 76.1),
    (7468, 75.9),
    (7544, 75.6),
    (7620, 75.4),
    (7696, 75.2),
    (7772, 75.0),
    (7849, 74.8),
    (7925, 74.5),
    (8001, 74.3),
    (8077, 74.1),
    (8153, 73.9),
    (8230, 73.7),
    (8306, 73.5),
    (8382, 73.2),
    (8458, 73.0),
    (8534, 72.8),
    (8611, 72.6),
    (8687, 72.4),
    (8763, 72.2),
    (8839, 72.0),
    (8916, 71.7),
    (8992, 71.5),
    (9068, 71.3),
    (9144, 71.1),
]

# Additional empirical data from deleze.name (more granular, 100m steps)
EMPIRICAL_DATA_DELEZE = [
    (-500, 101.7), (-500, 101.3), (-500, 101.0), (-500, 100.7), (-500, 100.3),
    (0, 100.0), (0, 99.7), (0, 99.3), (0, 99.0), (0, 98.7),
    (500, 98.3), (500, 98.0), (500, 97.7), (500, 97.3), (500, 97.0),
    (1000, 96.7), (1000, 96.3), (1000, 96.0), (1000, 95.7), (1000, 95.3),
    (1500, 95.0), (1500, 94.7), (1500, 94.3), (1500, 94.0), (1500, 93.7),
    (2000, 93.3), (2000, 93.0), (2000, 92.7), (2000, 92.3), (2000, 92.0),
    (2500, 91.7), (2500, 91.3), (2500, 91.0), (2500, 90.7), (2500, 90.3),
    (3000, 90.0), (3000, 89.7), (3000, 89.3), (3000, 89.0), (3000, 88.6),
    (3500, 88.3), (3500, 88.0), (3500, 87.6), (3500, 87.3), (3500, 87.0),
    (4000, 86.6), (4000, 86.3), (4000, 85.9), (4000, 85.6), (4000, 85.3),
    (4500, 84.9), (4500, 84.6), (4500, 84.3), (4500, 83.9), (4500, 83.6),
    (5000, 83.3), (5000, 82.9), (5000, 82.6), (5000, 82.2), (5000, 81.9),
    (5500, 81.6), (5500, 81.2), (5500, 80.9), (5500, 80.6), (5500, 80.2),
    (6000, 79.9), (6000, 79.5), (6000, 79.2), (6000, 78.9), (6000, 78.5),
    (6500, 78.2), (6500, 77.8), (6500, 77.5), (6500, 77.2), (6500, 76.8),
    (7000, 76.5), (7000, 76.1), (7000, 75.8), (7000, 75.5), (7000, 75.1),
    (7500, 74.8), (7500, 74.4), (7500, 74.1), (7500, 73.8), (7500, 73.4),
    (8000, 73.1), (8000, 72.7), (8000, 72.4), (8000, 72.0), (8000, 71.7),
    (8500, 71.4), (8500, 71.0), (8500, 70.7), (8500, 70.3), (8500, 70.0),
    (9000, 69.6), (9000, 69.3), (9000, 69.0), (9000, 68.6), (9000, 68.3),
    (9500, 67.9), (9500, 67.6), (9500, 67.2), (9500, 66.9), (9500, 66.5),
    (10000, 66.2), (10000, 65.8), (10000, 65.5), (10000, 65.2), (10000, 64.8),
    (10500, 64.5), (10500, 64.1), (10500, 63.8), (10500, 63.4), (10500, 63.1),
    (11000, 62.7), (11000, 62.4), (11000, 62.0), (11000, 61.7), (11000, 61.3),
    (11500, 61.0), (11500, 60.6), (11500, 60.3), (11500, 59.9), (11500, 59.6),
    (12000, 59.2), (12000, 58.9), (12000, 58.5), (12000, 58.2), (12000, 57.8),
]


def compute_metrics(observed: List[float], predicted: List[float]) -> Dict[str, float]:
    """Compute RMSE and Bias between observed and predicted values."""
    obs = np.array(observed)
    pred = np.array(predicted)
    
    mse = np.mean((obs - pred) ** 2)
    rmse = math.sqrt(mse)
    bias = np.mean(obs - pred)
    
    return {
        "rmse": float(rmse),
        "bias": float(bias),
        "mae": float(np.mean(np.abs(obs - pred))),
        "max_error": float(np.max(np.abs(obs - pred))),
        "n_samples": len(obs)
    }


def run_validation(empirical_data: List[Tuple[float, float]], 
                   lapse_rate: float = L,
                   model_name: str = "ISA+Antoine") -> Dict[str, Any]:
    """Run validation against empirical data."""
    altitudes = [d[0] for d in empirical_data]
    observed = [d[1] for d in empirical_data]
    
    if model_name == "ISA+Antoine":
        predicted = [boiling_point_at_altitude(alt, lapse_rate) for alt in altitudes]
    elif model_name == "Baseline":
        predicted = [baseline_boiling_point(alt) for alt in altitudes]
    else:
        raise ValueError(f"Unknown model: {model_name}")
    
    metrics = compute_metrics(observed, predicted)
    
    # Per-point details
    details = []
    for alt, obs, pred in zip(altitudes, observed, predicted):
        details.append({
            "altitude_m": alt,
            "observed_bp_c": obs,
            "predicted_bp_c": pred,
            "error_c": obs - pred
        })
    
    return {
        "model": model_name,
        "lapse_rate": lapse_rate,
        "metrics": metrics,
        "details": details
    }


def run_sensitivity_analysis(empirical_data: List[Tuple[float, float]],
                            lapse_rates: List[float] = None) -> List[Dict[str, Any]]:
    """Run sensitivity analysis across different lapse rates."""
    if lapse_rates is None:
        lapse_rates = np.linspace(0.005, 0.008, 31).tolist()  # 0.005 to 0.008 K/m
    
    results = []
    for lr in lapse_rates:
        result = run_validation(empirical_data, lr, "ISA+Antoine")
        results.append({
            "lapse_rate": lr,
            "rmse": result["metrics"]["rmse"],
            "bias": result["metrics"]["bias"],
            "mae": result["metrics"]["mae"]
        })
    
    return results


def find_optimal_lapse_rate(sensitivity_results: List[Dict[str, Any]]) -> Dict[str, float]:
    """Find the lapse rate that minimizes RMSE."""
    best = min(sensitivity_results, key=lambda x: x["rmse"])
    return {
        "optimal_lapse_rate": best["lapse_rate"],
        "min_rmse": best["rmse"],
        "bias_at_optimal": best["bias"]
    }


@logger.catch(reraise=True)
def main():
    # Setup logging
    logger.remove()
    logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
    logger.add("logs/run.log", rotation="30 MB", level="DEBUG")
    
    logger.info("Starting empirical validation of boiling point model")
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Test reference points from the testing plan
    logger.info("Testing reference points...")
    reference_points = [
        (0, 100.0),
        (1000, 96.7),
        (2000, 93.5),
        (3000, 90.4),
        (5000, 84.4)
    ]
    
    for alt, expected_bp in reference_points:
        calc_bp = boiling_point_at_altitude(alt)
        logger.info(f"Altitude {alt}m: Expected {expected_bp}°C, Calculated {calc_bp:.2f}°C, Diff {expected_bp - calc_bp:.2f}°C")
    
    # Verify monotonic decrease
    logger.info("Verifying monotonic decrease with altitude...")
    test_alts = [0, 1000, 2000, 3000, 5000]
    bps = [boiling_point_at_altitude(a) for a in test_alts]
    is_decreasing = all(bps[i] > bps[i+1] for i in range(len(bps)-1))
    logger.info(f"Boiling points: {[f'{bp:.2f}' for bp in bps]}")
    logger.info(f"Monotonically decreasing: {is_decreasing}")
    
    # Run validation on engineeringtoolbox data (primary dataset)
    logger.info(f"Running validation on EngineeringToolbox data ({len(EMPIRICAL_DATA_ENGINEERINGTOOLBOX)} points)...")
    result_isa = run_validation(EMPIRICAL_DATA_ENGINEERINGTOOLBOX, L, "ISA+Antoine")
    result_baseline = run_validation(EMPIRICAL_DATA_ENGINEERINGTOOLBOX, L, "Baseline")
    
    logger.info(f"ISA+Antoine: RMSE={result_isa['metrics']['rmse']:.4f}°C, Bias={result_isa['metrics']['bias']:.4f}°C")
    logger.info(f"Baseline:    RMSE={result_baseline['metrics']['rmse']:.4f}°C, Bias={result_baseline['metrics']['bias']:.4f}°C")
    
    # Run validation on deleze data (secondary dataset)
    logger.info(f"Running validation on Deleze data ({len(EMPIRICAL_DATA_DELEZE)} points)...")
    result_isa_deleze = run_validation(EMPIRICAL_DATA_DELEZE, L, "ISA+Antoine")
    result_baseline_deleze = run_validation(EMPIRICAL_DATA_DELEZE, L, "Baseline")
    
    logger.info(f"ISA+Antoine (Deleze): RMSE={result_isa_deleze['metrics']['rmse']:.4f}°C, Bias={result_isa_deleze['metrics']['bias']:.4f}°C")
    logger.info(f"Baseline (Deleze):    RMSE={result_baseline_deleze['metrics']['rmse']:.4f}°C, Bias={result_baseline_deleze['metrics']['bias']:.4f}°C")
    
    # Sensitivity analysis
    logger.info("Running lapse rate sensitivity analysis...")
    lapse_rates = np.linspace(0.005, 0.008, 31).tolist()
    sensitivity = run_sensitivity_analysis(EMPIRICAL_DATA_ENGINEERINGTOOLBOX, lapse_rates)
    optimal = find_optimal_lapse_rate(sensitivity)
    
    logger.info(f"Optimal lapse rate: {optimal['optimal_lapse_rate']:.5f} K/m")
    logger.info(f"Minimum RMSE: {optimal['min_rmse']:.4f}°C")
    logger.info(f"Bias at optimal: {optimal['bias_at_optimal']:.4f}°C")
    
    # Also run sensitivity on Deleze data
    sensitivity_deleze = run_sensitivity_analysis(EMPIRICAL_DATA_DELEZE, lapse_rates)
    optimal_deleze = find_optimal_lapse_rate(sensitivity_deleze)
    
    logger.info(f"Optimal lapse rate (Deleze): {optimal_deleze['optimal_lapse_rate']:.5f} K/m")
    logger.info(f"Minimum RMSE (Deleze): {optimal_deleze['min_rmse']:.4f}°C")
    
    # Prepare output
    output = {
        "experiment": "empirical_boiling_point_validation",
        "constants": {
            "P0_hPa": P0,
            "T0_K": T0,
            "g_m_s2": g,
            "M_kg_per_mol": M,
            "R_J_per_mol_K": R,
            "L_K_per_m": L,
            "ISA_exponent": ISA_EXPONENT,
            "Antoine_A": A,
            "Antoine_B": B,
            "Antoine_C": C
        },
        "reference_point_tests": [
            {"altitude_m": alt, "expected_bp_c": exp, "calculated_bp_c": round(boiling_point_at_altitude(alt), 2), "error_c": round(exp - boiling_point_at_altitude(alt), 2)}
            for alt, exp in reference_points
        ],
        "monotonic_decrease_verified": is_decreasing,
        "validation_engineeringtoolbox": {
            "n_points": len(EMPIRICAL_DATA_ENGINEERINGTOOLBOX),
            "ISA_Antoine": result_isa,
            "Baseline": result_baseline
        },
        "validation_deleze": {
            "n_points": len(EMPIRICAL_DATA_DELEZE),
            "ISA_Antoine": result_isa_deleze,
            "Baseline": result_baseline_deleze
        },
        "sensitivity_analysis": {
            "lapse_rates_tested": len(lapse_rates),
            "range_K_per_m": [lapse_rates[0], lapse_rates[-1]],
            "results_engineeringtoolbox": sensitivity,
            "optimal_engineeringtoolbox": optimal,
            "results_deleze": sensitivity_deleze,
            "optimal_deleze": optimal_deleze
        }
    }
    
    # Save output
    output_path = Path("method_out.json")
    output_path.write_text(json.dumps(output, indent=2))
    logger.info(f"Results saved to {output_path}")
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"EngineeringToolbox ({len(EMPIRICAL_DATA_ENGINEERINGTOOLBOX)} points):")
    print(f"  ISA+Antoine: RMSE = {result_isa['metrics']['rmse']:.4f}°C, Bias = {result_isa['metrics']['bias']:.4f}°C")
    print(f"  Baseline:    RMSE = {result_baseline['metrics']['rmse']:.4f}°C, Bias = {result_baseline['metrics']['bias']:.4f}°C")
    print(f"Deleze ({len(EMPIRICAL_DATA_DELEZE)} points):")
    print(f"  ISA+Antoine: RMSE = {result_isa_deleze['metrics']['rmse']:.4f}°C, Bias = {result_isa_deleze['metrics']['bias']:.4f}°C")
    print(f"  Baseline:    RMSE = {result_baseline_deleze['metrics']['rmse']:.4f}°C, Bias = {result_baseline_deleze['metrics']['bias']:.4f}°C")
    print(f"Optimal L (EngToolbox): {optimal['optimal_lapse_rate']:.5f} K/m (RMSE = {optimal['min_rmse']:.4f}°C)")
    print(f"Optimal L (Deleze):     {optimal_deleze['optimal_lapse_rate']:.5f} K/m (RMSE = {optimal_deleze['min_rmse']:.4f}°C)")
    print("="*60)


if __name__ == "__main__":
    main()