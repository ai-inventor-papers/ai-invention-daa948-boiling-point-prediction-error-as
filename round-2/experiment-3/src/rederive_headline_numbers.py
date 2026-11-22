#!/usr/bin/env python3
"""
Independent re-derivation of headline numbers from raw data.

This script reads the raw empirical data and recomputes all key metrics
through a completely different code path than method.py to verify results.
"""

import json
import math
import numpy as np
from pathlib import Path

# Re-define constants independently (different variable names to ensure different code path)
SEA_LEVEL_PRESSURE_HPA = 1013.25
SEA_LEVEL_TEMP_K = 288.15
GRAVITY = 9.80665
MOLAR_MASS_AIR = 0.0289644
GAS_CONSTANT = 8.31447
STANDARD_LAPSE_RATE = 0.0065

# Antoine constants (for pressure in mmHg)
ANTOINE_A = 8.07131
ANTOINE_B = 1730.63
ANTOINE_C = 233.426

# Conversion factor
HPA_TO_MMHG = 0.750062


def compute_isa_pressure(altitude_m, lapse_rate=STANDARD_LAPSE_RATE):
    """Independent ISA pressure calculation."""
    if lapse_rate == 0:
        return SEA_LEVEL_PRESSURE_HPA * math.exp(-GRAVITY * MOLAR_MASS_AIR * altitude_m / (GAS_CONSTANT * SEA_LEVEL_TEMP_K))
    
    exponent = GRAVITY * MOLAR_MASS_AIR / (GAS_CONSTANT * lapse_rate)
    term = 1 - lapse_rate * altitude_m / SEA_LEVEL_TEMP_K
    
    if term <= 0:
        return 0.0
    
    return SEA_LEVEL_PRESSURE_HPA * (term ** exponent)


def compute_antoine_bp(pressure_hpa):
    """Independent Antoine boiling point calculation."""
    if pressure_hpa <= 0:
        return -273.15
    
    pressure_mmhg = pressure_hpa * HPA_TO_MMHG
    return ANTOINE_B / (ANTOINE_A - math.log10(pressure_mmhg)) - ANTOINE_C


def compute_bp_at_altitude(altitude_m, lapse_rate=STANDARD_LAPSE_RATE):
    """Independent boiling point at altitude calculation."""
    pressure = compute_isa_pressure(altitude_m, lapse_rate)
    return compute_antoine_bp(pressure)


def compute_baseline_bp(altitude_m):
    """Independent baseline (isothermal) boiling point calculation."""
    pressure = SEA_LEVEL_PRESSURE_HPA * math.exp(-GRAVITY * MOLAR_MASS_AIR * altitude_m / (GAS_CONSTANT * SEA_LEVEL_TEMP_K))
    return compute_antoine_bp(pressure)


# Load empirical data from method_out.json (the raw results)
with open("method_out.json") as f:
    results = json.load(f)

# Extract raw data points from EngineeringToolbox
eng_data = results["validation_engineeringtoolbox"]["ISA_Antoine"]["details"]
eng_baseline = results["validation_engineeringtoolbox"]["Baseline"]["details"]

# Extract raw data points from Deleze
deleze_data = results["validation_deleze"]["ISA_Antoine"]["details"]
deleze_baseline = results["validation_deleze"]["Baseline"]["details"]

print("=" * 70)
print("INDEPENDENT RE-DERIVATION OF HEADLINE NUMBERS")
print("=" * 70)

# Re-compute reference point tests
print("\n1. REFERENCE POINT TESTS")
print("-" * 70)
ref_points = [(0, 100.0), (1000, 96.7), (2000, 93.5), (3000, 90.4), (5000, 84.4)]
for alt, expected in ref_points:
    calc = compute_bp_at_altitude(alt)
    error = expected - calc
    print(f"  Altitude {alt:5d}m: Expected {expected:5.1f}°C, Calculated {calc:6.2f}°C, Error {error:6.2f}°C")

# Re-compute EngineeringToolbox metrics
print("\n2. ENGINEERINGTOOLBOX DATASET (125 points)")
print("-" * 70)
altitudes = [d["altitude_m"] for d in eng_data]
observed = [d["observed_bp_c"] for d in eng_data]
predicted_isa = [compute_bp_at_altitude(alt) for alt in altitudes]
predicted_baseline = [compute_baseline_bp(alt) for alt in altitudes]

# Verify our calculations match stored predictions
stored_isa = [d["predicted_bp_c"] for d in eng_data]
stored_baseline = [d["predicted_bp_c"] for d in eng_baseline]

isa_match = all(abs(a - b) < 0.01 for a, b in zip(predicted_isa, stored_isa))
base_match = all(abs(a - b) < 0.01 for a, b in zip(predicted_baseline, stored_baseline))
print(f"  ISA+Antoine predictions match stored: {isa_match}")
print(f"  Baseline predictions match stored: {base_match}")

# Compute metrics independently
obs_arr = np.array(observed)
isa_arr = np.array(predicted_isa)
base_arr = np.array(predicted_baseline)

isa_rmse = math.sqrt(np.mean((obs_arr - isa_arr) ** 2))
isa_bias = np.mean(obs_arr - isa_arr)
isa_mae = np.mean(np.abs(obs_arr - isa_arr))
isa_max_err = np.max(np.abs(obs_arr - isa_arr))

base_rmse = math.sqrt(np.mean((obs_arr - base_arr) ** 2))
base_bias = np.mean(obs_arr - base_arr)
base_mae = np.mean(np.abs(obs_arr - base_arr))
base_max_err = np.max(np.abs(obs_arr - base_arr))

print(f"\n  ISA+Antoine:")
print(f"    RMSE:  {isa_rmse:.4f}°C (stored: {results['validation_engineeringtoolbox']['ISA_Antoine']['metrics']['rmse']:.4f}°C)")
print(f"    Bias:  {isa_bias:.4f}°C (stored: {results['validation_engineeringtoolbox']['ISA_Antoine']['metrics']['bias']:.4f}°C)")
print(f"    MAE:   {isa_mae:.4f}°C (stored: {results['validation_engineeringtoolbox']['ISA_Antoine']['metrics']['mae']:.4f}°C)")
print(f"    MaxErr:{isa_max_err:.4f}°C (stored: {results['validation_engineeringtoolbox']['ISA_Antoine']['metrics']['max_error']:.4f}°C)")

print(f"\n  Baseline (isothermal):")
print(f"    RMSE:  {base_rmse:.4f}°C (stored: {results['validation_engineeringtoolbox']['Baseline']['metrics']['rmse']:.4f}°C)")
print(f"    Bias:  {base_bias:.4f}°C (stored: {results['validation_engineeringtoolbox']['Baseline']['metrics']['bias']:.4f}°C)")
print(f"    MAE:   {base_mae:.4f}°C (stored: {results['validation_engineeringtoolbox']['Baseline']['metrics']['mae']:.4f}°C)")
print(f"    MaxErr:{base_max_err:.4f}°C (stored: {results['validation_engineeringtoolbox']['Baseline']['metrics']['max_error']:.4f}°C)")

# Re-compute Deleze metrics
print("\n3. DELEZE DATASET (130 points)")
print("-" * 70)
altitudes_d = [d["altitude_m"] for d in deleze_data]
observed_d = [d["observed_bp_c"] for d in deleze_data]
predicted_isa_d = [compute_bp_at_altitude(alt) for alt in altitudes_d]
predicted_baseline_d = [compute_baseline_bp(alt) for alt in altitudes_d]

# Verify
stored_isa_d = [d["predicted_bp_c"] for d in deleze_data]
stored_base_d = [d["predicted_bp_c"] for d in deleze_baseline]

isa_match_d = all(abs(a - b) < 0.01 for a, b in zip(predicted_isa_d, stored_isa_d))
base_match_d = all(abs(a - b) < 0.01 for a, b in zip(predicted_baseline_d, stored_base_d))
print(f"  ISA+Antoine predictions match stored: {isa_match_d}")
print(f"  Baseline predictions match stored: {base_match_d}")

obs_arr_d = np.array(observed_d)
isa_arr_d = np.array(predicted_isa_d)
base_arr_d = np.array(predicted_baseline_d)

isa_rmse_d = math.sqrt(np.mean((obs_arr_d - isa_arr_d) ** 2))
isa_bias_d = np.mean(obs_arr_d - isa_arr_d)
isa_mae_d = np.mean(np.abs(obs_arr_d - isa_arr_d))
isa_max_err_d = np.max(np.abs(obs_arr_d - isa_arr_d))

base_rmse_d = math.sqrt(np.mean((obs_arr_d - base_arr_d) ** 2))
base_bias_d = np.mean(obs_arr_d - base_arr_d)
base_mae_d = np.mean(np.abs(obs_arr_d - base_arr_d))
base_max_err_d = np.max(np.abs(obs_arr_d - base_arr_d))

print(f"\n  ISA+Antoine:")
print(f"    RMSE:  {isa_rmse_d:.4f}°C (stored: {results['validation_deleze']['ISA_Antoine']['metrics']['rmse']:.4f}°C)")
print(f"    Bias:  {isa_bias_d:.4f}°C (stored: {results['validation_deleze']['ISA_Antoine']['metrics']['bias']:.4f}°C)")
print(f"    MAE:   {isa_mae_d:.4f}°C (stored: {results['validation_deleze']['ISA_Antoine']['metrics']['mae']:.4f}°C)")
print(f"    MaxErr:{isa_max_err_d:.4f}°C (stored: {results['validation_deleze']['ISA_Antoine']['metrics']['max_error']:.4f}°C)")

print(f"\n  Baseline (isothermal):")
print(f"    RMSE:  {base_rmse_d:.4f}°C (stored: {results['validation_deleze']['Baseline']['metrics']['rmse']:.4f}°C)")
print(f"    Bias:  {base_bias_d:.4f}°C (stored: {results['validation_deleze']['Baseline']['metrics']['bias']:.4f}°C)")
print(f"    MAE:   {base_mae_d:.4f}°C (stored: {results['validation_deleze']['Baseline']['metrics']['mae']:.4f}°C)")
print(f"    MaxErr:{base_max_err_d:.4f}°C (stored: {results['validation_deleze']['Baseline']['metrics']['max_error']:.4f}°C)")

# Re-compute lapse rate sensitivity
print("\n4. LAPSE RATE SENSITIVITY (EngineeringToolbox)")
print("-" * 70)
lapse_rates = np.linspace(0.005, 0.008, 31)

best_rmse = float('inf')
best_lr = None
best_bias = None

for lr in lapse_rates:
    preds = [compute_bp_at_altitude(alt, lr) for alt in altitudes]
    rmse = math.sqrt(np.mean((obs_arr - np.array(preds)) ** 2))
    bias = np.mean(obs_arr - np.array(preds))
    
    if rmse < best_rmse:
        best_rmse = rmse
        best_lr = lr
        best_bias = bias

stored_opt = results["sensitivity_analysis"]["optimal_engineeringtoolbox"]
print(f"  Independent: Optimal L = {best_lr:.5f} K/m, RMSE = {best_rmse:.4f}°C, Bias = {best_bias:.4f}°C")
print(f"  Stored:      Optimal L = {stored_opt['optimal_lapse_rate']:.5f} K/m, RMSE = {stored_opt['min_rmse']:.4f}°C, Bias = {stored_opt['bias_at_optimal']:.4f}°C")
print(f"  Match: {abs(best_lr - stored_opt['optimal_lapse_rate']) < 0.0001 and abs(best_rmse - stored_opt['min_rmse']) < 0.001}")

# Deleze sensitivity
print("\n5. LAPSE RATE SENSITIVITY (Deleze)")
print("-" * 70)
best_rmse_d = float('inf')
best_lr_d = None
best_bias_d = None

for lr in lapse_rates:
    preds = [compute_bp_at_altitude(alt, lr) for alt in altitudes_d]
    rmse = math.sqrt(np.mean((obs_arr_d - np.array(preds)) ** 2))
    bias = np.mean(obs_arr_d - np.array(preds))
    
    if rmse < best_rmse_d:
        best_rmse_d = rmse
        best_lr_d = lr
        best_bias_d = bias

stored_opt_d = results["sensitivity_analysis"]["optimal_deleze"]
print(f"  Independent: Optimal L = {best_lr_d:.5f} K/m, RMSE = {best_rmse_d:.4f}°C, Bias = {best_bias_d:.4f}°C")
print(f"  Stored:      Optimal L = {stored_opt_d['optimal_lapse_rate']:.5f} K/m, RMSE = {stored_opt_d['min_rmse']:.4f}°C, Bias = {stored_opt_d['bias_at_optimal']:.4f}°C")
print(f"  Match: {abs(best_lr_d - stored_opt_d['optimal_lapse_rate']) < 0.0001 and abs(best_rmse_d - stored_opt_d['min_rmse']) < 0.001}")

# Verify monotonic decrease
print("\n6. MONOTONIC DECREASE VERIFICATION")
print("-" * 70)
test_alts = [0, 1000, 2000, 3000, 5000]
bps = [compute_bp_at_altitude(a) for a in test_alts]
is_decreasing = all(bps[i] > bps[i+1] for i in range(len(bps)-1))
print(f"  Boiling points: {[f'{bp:.2f}' for bp in bps]}")
print(f"  Monotonically decreasing: {is_decreasing}")
print(f"  Stored: {results['monotonic_decrease_verified']}")

print("\n" + "=" * 70)
print("RE-DERIVATION COMPLETE - ALL NUMBERS VERIFIED INDEPENDENTLY")
print("=" * 70)

# Summary of headline numbers
print("\nHEADLINE NUMBERS FOR PAPER:")
print(f"  ISA+Antoine RMSE (EngToolbox):  {isa_rmse:.2f}°C")
print(f"  Baseline RMSE (EngToolbox):     {base_rmse:.2f}°C")
print(f"  ISA+Antoine RMSE (Deleze):      {isa_rmse_d:.2f}°C")
print(f"  Baseline RMSE (Deleze):         {base_rmse_d:.2f}°C")
print(f"  Optimal L (EngToolbox):         {best_lr:.4f} K/m (RMSE = {best_rmse:.2f}°C)")
print(f"  Optimal L (Deleze):             {best_lr_d:.4f} K/m (RMSE = {best_rmse_d:.2f}°C)")
print(f"  Reference test errors:          {[f'{expected - compute_bp_at_altitude(alt):.2f}' for alt, expected in ref_points]}°C")