# Testing Boiling Point Non-Hydrostatic Signal

## Overview
This experiment tests the hypothesis that boiling point prediction errors (observed minus calculated from hydrostatic pressure) correlate with vertical wind turbulence, which would indicate non-hydrostatic pressure components in the atmosphere.

## Methodology
Following the artifact plan:
1. **Hydrostatic Baseline**: Calculate boiling point using the Antoine equation from observed pressure
2. **Synthetic Data Generation**: Created high-frequency (1 Hz) synthetic meteorological data with:
   - Pressure (P_obs): Base pressure + non-hydrostatic component correlated with vertical wind
   - Temperature (T_obs): Boiling point from pressure + measurement noise
   - Vertical velocity (w): Turbulent wind component
3. **Analysis**:
   - Pearson correlation between boiling point prediction error (T_obs - T_calc) and vertical velocity (w)
   - Power Spectral Density (PSD) analysis to verify atmospheric signal characteristics

## Results
- **Pearson Correlation**: -0.0190 (near zero, no significant correlation detected in synthetic data)
- **Mean T_error**: ~0°C
- **Std T_error**: 0.010°C

The synthetic data was designed with a small non-hydrostatic pressure component (0.1 * w), but the boiling point calculation uses the observed pressure, so the correlation is near zero as expected.

## Files
- `method.py`: Main experiment script
- `results.json`: Experiment results in exp_gen_sol_out format
- `psd_data.json`: Power spectral density data
- `figures/`: Generated plots (PSD, scatter, bar charts)

## Running the Experiment
```bash
uv run python3 method.py
```

## Restoring removed files
No files were removed - all results and code are in the workspace.