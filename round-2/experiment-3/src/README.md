# Empirical Validation of Boiling Point Model

This artifact validates the ISA barometric formula and Antoine equation against empirical boiling point measurements at altitude, and assesses lapse rate sensitivity.

## Overview

The experiment tests how well a simple physics-based model (ISA + Antoine) predicts the boiling point of water at different altitudes compared to published empirical data from two sources:
- **EngineeringToolbox** (125 data points, altitudes -305m to 9144m)
- **Deleze** (130 data points, altitudes -500m to 12000m, 100m increments)

## Key Results

| Dataset | Model | RMSE (°C) | Bias (°C) |
|---------|-------|-----------|-----------|
| EngineeringToolbox | ISA+Antoine | 0.657 | +0.235 |
| EngineeringToolbox | Baseline (isothermal) | 0.840 | -0.750 |
| Deleze | ISA+Antoine | 0.891 | -0.748 |
| Deleze | Baseline (isothermal) | 3.000 | -2.451 |

### Lapse Rate Sensitivity
- **EngineeringToolbox**: Optimal L = 0.0050 K/m (RMSE = 0.397°C)
- **Deleze**: Optimal L = 0.0078 K/m (RMSE = 0.690°C)
- Standard ISA L = 0.0065 K/m

The ISA+Antoine model significantly outperforms the isothermal baseline, especially for the Deleze dataset. The standard lapse rate (0.0065 K/m) performs well for EngineeringToolbox data but the Deleze data suggests a higher lapse rate may be more appropriate for those conditions.

## Files

```
├── method.py                          # Main experiment script
├── convert_to_schema.py               # Converts output to exp_gen_sol_out.json schema
├── method_out.json                    # Complete experimental results
├── exp_gen_sol_out.json               # Schema-compliant output
├── logs/run.log                       # Execution log
├── figures/                           # Generated data figures
│   ├── fig_sensitivity_rmse.pdf/png   # RMSE vs lapse rate
│   ├── fig_sensitivity_bias.pdf/png   # Bias vs lapse rate
│   ├── fig_model_comparison.pdf/png   # Model comparison bar chart
│   ├── fig_pred_vs_obs_simple.pdf/png # Predicted vs observed scatter
│   ├── fig_error_vs_altitude_sampled.pdf/png # Error vs altitude
│   └── fig_bp_vs_altitude_sampled.pdf/png    # BP vs altitude comparison
└── .aii/manifest.yaml                 # Artifact manifest
```

## Running the Experiment

```bash
# Create virtual environment
uv venv .venv --python=3.12
source .venv/bin/activate
uv pip install numpy loguru matplotlib

# Run the experiment
uv run method.py

# Convert to schema format
uv run convert_to_schema.py

# Validate schema compliance
python -c "
import json
from jsonschema import validate
with open('exp_gen_sol_out.json') as f:
    data = json.load(f)
with open('/Users/Shared/aii_data/.claude/skills/aii-json/schemas/exp_gen_sol_out.json') as f:
    schema = json.load(f)
validate(instance=data, schema=schema)
print('Validation PASSED')
"
```

## Method Details

### ISA Barometric Formula
```
P(z) = P₀ × (1 - L×z/T₀)^(g×M/(R×L))
```
- P₀ = 1013.25 hPa (sea level pressure)
- T₀ = 288.15 K (sea level temperature)
- g = 9.80665 m/s²
- M = 0.0289644 kg/mol
- R = 8.31447 J/(mol·K)
- L = 0.0065 K/m (standard lapse rate)

### Antoine Equation (for water)
```
T = B / (A - log₁₀(P_mmHg)) - C
```
- A = 8.07131
- B = 1730.63
- C = 233.426
- P_mmHg = P_hPa × 0.750062

### Baseline Model
Isothermal atmosphere: P(z) = P₀ × exp(-g×M×z/(R×T₀))

## Figures

All figures are generated using `aii-data-fig-gen` with the project's house style:
- Vector PDF for publication
- PNG for preview
- Colorblind-safe palette
- Type 42 fonts for LaTeX compliance

## References

- EngineeringToolbox: Water - Boiling Points vs. Altitude (https://www.engineeringtoolbox.com/boiling-points-water-altitude-d_1344.html)
- Deleze: Boiling temperature of water as function of altitude (https://www.deleze.name/marcel/en/physique/TemperaturesEbullition/table_temperature-en.html)
- Antoine constants from NIST Chemistry WebBook
- ISA model from ICAO Standard Atmosphere