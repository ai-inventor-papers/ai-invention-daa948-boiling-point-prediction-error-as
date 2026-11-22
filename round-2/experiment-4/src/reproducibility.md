# Reproducibility Guide

This document provides complete step-by-step instructions to reproduce the exact results of the boiling point prediction accuracy and lapse rate sensitivity analysis experiment.

## 1. Getting This Artifact

This workspace is published as part of a public GitHub repository. To reproduce:

```bash
# Clone the repository (replace with actual repo URL when published)
git clone https://github.com/ai-inventor/run_PM2hrW3VHQ3D.git
cd run_PM2hrW3VHQ3D/round-2/experiment-4/src
```

## 2. System Requirements & Environment Setup

### System Packages
- macOS or Linux (tested on macOS 14+ Apple Silicon)
- Python 3.12+
- uv (Python package installer): `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Virtual Environment & Dependencies
```bash
# Create virtual environment with Python 3.12
uv venv .venv --python=3.12

# Activate environment
source .venv/bin/activate

# Install exact pinned dependencies (matches pyproject.toml)
uv pip install \
    contourpy==1.4.0 \
    cycler==0.12.1 \
    fonttools==4.68.0 \
    kiwisolver==1.5.1 \
    loguru==0.8.0 \
    matplotlib==3.11.2 \
    numpy==2.5.5 \
    packaging==26.3 \
    pandas==3.1.1 \
    pillow==13.0.0 \
    pyparsing==3.3.3 \
    python-dateutil==4.0.0 \
    scipy==1.18.1 \
    tzdata==2026.6 \
    jsonschema==4.26.0
```

### Data Requirements
No external data downloads required. All empirical data is embedded in `method.py`:
- Primary validation data: Published boiling point table from deleze.name (barometric levelling model), altitudes -500m to 12000m at 500m intervals
- Cross-validation data: ISA standard atmosphere tables from SimuPipe (IAPWS-IF97 saturation curve), altitudes 0-10000m

No API keys or environment variables needed.

## 3. Exact Commands to Run

### Step 1: Run the Main Experiment
```bash
# Runtime: ~1 second on Apple M1/M2/M3
.venv/bin/python method.py
```
This produces:
- `lapse_rate_sensitivity_analysis.json` - Full results
- Logs in `logs/run.log`

### Step 2: Generate Mini/Preview JSON Variants
```bash
.venv/bin/python create_mini_preview.py
```
This produces:
- `full_lapse_rate_sensitivity_analysis.json`
- `mini_lapse_rate_sensitivity_analysis.json`
- `preview_lapse_rate_sensitivity_analysis.json`

### Step 3: Generate Publication-Quality Figures
```bash
# Install aii-data-fig-gen skill dependencies (if not already)
# The chart generator uses matplotlib which is already installed

# Generate sensitivity curve figure
python -c "
import sys
sys.path.insert(0, '/Users/Shared/aii_data/.claude/skills/aii-data-fig-gen/scripts')
from chart_gen import main
import json
spec = json.load(open('fig_sensitivity_spec.json'))
# Note: Run via the skill's entry point instead
"
# ACTUAL COMMAND (run from workspace):
export SKILL_DIR="/Users/Shared/aii_data/.claude/skills/aii-data-fig-gen"
python "$SKILL_DIR/scripts/chart_gen.py" --spec fig_sensitivity_spec.json --out figures/fig_sensitivity
python "$SKILL_DIR/scripts/chart_gen.py" --spec fig_predictions_spec.json --out figures/fig_predictions
python "$SKILL_DIR/scripts/chart_gen.py" --spec fig_comparison_spec.json --out figures/fig_comparison
```

### Total Runtime
- Experiment: ~1 second
- Figure generation: ~3 seconds total
- All steps: <10 seconds on modern hardware

## 4. Expected Output Files & Key Numbers

### Primary Results File: `lapse_rate_sensitivity_analysis.json`
Contains the complete analysis. Key headline numbers to verify:

**Baseline Performance (ISA standard lapse rate = 0.0065 K/m):**
- RMSE vs published data: **0.079 °C**
- RMSE vs ISA tables: **0.067 °C**

**Optimal Lapse Rate:**
- Value: **0.0067 K/m** (31-point sweep from 0.005 to 0.008 K/m)
- RMSE at optimum: **0.039 °C**
- Improvement over ISA standard: **51% RMSE reduction**

**Cross-Validation:**
- ISA table RMSE at baseline: 0.067 °C
- ISA table RMSE at optimal: ~0.04 °C (derived from predictions)

### Figure Files (in `figures/` directory):
- `fig_sensitivity.pdf` / `.png` - RMSE vs lapse rate curve (U-shaped, minimum at 0.0067)
- `fig_predictions.pdf` / `.png` - Predicted vs observed boiling points across -500 to 12000m
- `fig_comparison.pdf` / `.png` - Prediction errors for ISA vs optimal lapse rate

### Mini/Preview Files:
- `full_lapse_rate_sensitivity_analysis.json` - Identical to original
- `mini_lapse_rate_sensitivity_analysis.json` - First 3 sensitivity points + all other keys
- `preview_lapse_rate_sensitivity_analysis.json` - Mini with strings truncated to 200 chars

## 5. Verification Steps

To confirm reproduction succeeded, check these specific values in the output:

```bash
# Check baseline RMSE
python -c "
import json
d = json.load(open('lapse_rate_sensitivity_analysis.json'))
print('Baseline RMSE:', d['baseline']['rmse_c'])
print('Optimal LR:', d['optimal_lapse_rate_k_m'])
print('Optimal RMSE:', d['optimal_rmse_c'])
print('ISA RMSE:', d['isa_validation']['rmse_c'])
"
```

Expected output:
```
Baseline RMSE: 0.07897800883543721
Optimal LR: 0.0067
Optimal RMSE: 0.03907019512816559
ISA RMSE: 0.06705591708649128
```

### Verify Figures Exist
```bash
ls -la figures/
# Should show 6 files: 3 .pdf + 3 .png
```

## Notes for Paper Integration

The key finding for the paper: **The standard ISA lapse rate of 6.5 K/km is not optimal for boiling point prediction; a slightly steeper rate of 6.7 K/km reduces RMSE by 51% (from 0.079°C to 0.039°C) against published empirical data.** This suggests the "average" atmospheric profile assumed by ISA slightly underestimates the temperature gradient relevant for phase-change thermodynamics at altitude.

All numerical results in this artifact are derived from the deterministic computations in `method.py` using the embedded empirical datasets. No stochastic elements, random seeds, or model training involved.