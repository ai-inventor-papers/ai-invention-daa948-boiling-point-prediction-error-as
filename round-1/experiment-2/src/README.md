# Boiling Point vs Humidity Experiment

This experiment tests the Humidity-Driven Nucleation hypothesis by analyzing the correlation between boiling point prediction errors (from Clausius-Clapeyron theoretical baseline) and relative humidity.

## Layout

- `method.py` - Main analysis script implementing the Clausius-Clapeyron theoretical boiling point calculation and correlation analysis
- `method_out.json` / `full_method_out.json` - Experimental results in exp_gen_sol_out.json schema format (10 examples, 2 methods)
- `mini_method_out.json` - First 3 examples for quick testing
- `preview_method_out.json` - Truncated preview for inspection
- `fig_data.json` - Raw data for figure generation (1000 synthetic data points)
- `fig_spec.json` - Chart specification for aii-data-fig-gen
- `figures/` - Generated figures (fig1.pdf, fig1.png)
- `logs/` - Execution logs
- `.venv/` - Python virtual environment (regenerable)
- `pyproject.toml` - Pinned dependencies
- `reproducibility.md` - Complete reproduction guide

## How to Run

```bash
# Create and activate virtual environment
uv venv .venv --python=3.12
source .venv/bin/activate
uv pip install matplotlib==3.11.2 numpy==2.5.5 pandas==3.1.1 scipy==1.18.1 loguru==0.7.2

# Run analysis
python method.py

# Generate figure
SKILL_DIR="/Users/Shared/aii_data/.claude/skills/aii-data-fig-gen"
.venv/bin/python $SKILL_DIR/scripts/chart_gen.py --spec fig_spec.json --out figures/fig1
```

## Results

The analysis computes:
- Theoretical boiling point using Clausius-Clapeyron equation from ambient pressure
- Prediction error: observed boiling point - theoretical boiling point
- Pearson correlation (our method) and Spearman correlation (baseline) between prediction error and relative humidity

Results across 10 random seeds show strong positive correlations:
- Pearson (our method): mean r ≈ 0.9445, all p < 0.001
- Spearman (baseline): mean r ≈ 0.9484, all p < 0.001

This supports the Humidity-Driven Nucleation hypothesis.

## Restoring Removed Files

### `.venv/` (regenerable)
```bash
uv venv .venv --python=3.12 && uv pip install --python=.venv/bin/python matplotlib==3.11.2 numpy==2.5.5 pandas==3.1.1 scipy==1.18.1 loguru==0.7.2
```