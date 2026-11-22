# Reproducibility Guide

This document provides complete step-by-step instructions to reproduce the exact results of the Boiling Point vs Humidity experiment on Ubuntu.

## 1. Getting the Artifact

```bash
# Clone the repository (this artifact is published as a folder in a public GitHub repo)
git clone https://github.com/ai-inventor/experiments.git
cd experiments/gen_art_experiment_2
```

## 2. System Requirements & Environment Setup

### System Packages (Ubuntu)
```bash
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv
```

### Python Virtual Environment
```bash
# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install exact pinned dependencies (matching pyproject.toml)
pip install matplotlib==3.11.2 numpy==2.5.5 pandas==3.1.1 scipy==1.18.1 loguru==0.7.2
```

### Verify Installation
```bash
python -c "import matplotlib; print('matplotlib', matplotlib.__version__); import numpy; print('numpy', numpy.__version__); import scipy; print('scipy', scipy.__version__); import pandas; print('pandas', pandas.__version__); import loguru; print('loguru', loguru.__version__)"
```

Expected output:
```
matplotlib 3.11.2
numpy 2.5.5
scipy 1.18.1
pandas 3.1.1
loguru 0.7.2
```

## 3. Data

This experiment uses **synthetic data** generated internally by the script (no external data downloads required). The synthetic dataset contains 1000 samples with:
- Ambient pressure: uniform 80-105 kPa
- Relative humidity: uniform 0-100%
- Theoretical boiling point: calculated via Clausius-Clapeyron equation
- Observed boiling point: theoretical + humidity effect (0.05 K per %RH) + Gaussian noise (σ=0.5 K)

Random seed is fixed to 42 for exact reproducibility.

## 4. Running the Experiment

### Step 1: Run Analysis
```bash
python method.py
```

**Expected runtime:** ~2 seconds on CPU (Apple M-series or x86_64)
**Hardware used:** CPU only (no GPU required), ~100 MB RAM

**Expected output:**
```
2026-11-21 17:34:18.046 | INFO     | __main__:run_analysis:109 - Analysis complete. Generated 10 examples.
2026-11-21 17:34:18.047 | INFO     | __main__:run_analysis:110 - First example: {'input': 'correlation analysis of boiling point error with relative humidity (seed=42)', 'output': 'pearson_r: 0.9482, p: 0.0000; spearman_r: 0.9504, p: 0.0000', 'predict_our_method': '0.9482', 'predict_baseline': '0.9504'}
```

### Step 2: Generate Figure
```bash
# The chart_gen.py script is part of the aii-data-fig-gen skill
# Copy it locally or use the skill path
python -c "
import json
with open('fig_data.json') as f:
    data = json.load(f)
spec = {
  'type': 'scatter',
  'title': 'Boiling Point Prediction Error vs Relative Humidity',
  'xlabel': 'Relative Humidity (%)',
  'ylabel': 'Boiling Point Error (K)',
  'aspect': '4:3',
  'fit': True,
  'series': [{'label': 'Data', 'x': data['Relative_Humidity'], 'values': data['T_err']}]
}
with open('fig_spec.json', 'w') as f:
    json.dump(spec, f)
"

# Generate figure (requires matplotlib)
# Note: chart_gen.py is from aii-data-fig-gen skill
# On Ubuntu, use the skill's chart_gen.py or the provided method
python -c "
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import json

with open('fig_data.json') as f:
    data = json.load(f)

rh = np.array(data['Relative_Humidity'])
err = np.array(data['T_err'])

fig, ax = plt.subplots(figsize=(6.5, 4.875), layout='constrained')
ax.scatter(rh, err, alpha=0.5, s=10, color='#0173b2')
# Fit line
coeff = np.polyfit(rh, err, 1)
x_fit = np.linspace(0, 100, 100)
ax.plot(x_fit, coeff[0]*x_fit + coeff[1], color='#de8f05', linewidth=2, label=f'Fit: y={coeff[0]:.4f}x+{coeff[1]:.4f}')
ax.set_xlabel('Relative Humidity (%)')
ax.set_ylabel('Boiling Point Error (K)')
ax.set_title('Boiling Point Prediction Error vs Relative Humidity')
ax.legend()
ax.grid(True, alpha=0.3)
fig.savefig('figures/fig1.png', dpi=150)
fig.savefig('figures/fig1.pdf')
plt.close()
print('Figures saved to figures/')
"
```

## 5. Expected Outputs & Verification

### Results File (`results.json` / `method_out.json`)
```json
{
  "datasets": [
    {
      "dataset": "synthetic_boiling_point_data",
      "examples": [
        {
          "input": "correlation analysis of boiling point error with relative humidity (seed=42)",
          "output": "pearson_r: 0.9482, p: 0.0000; spearman_r: 0.9504, p: 0.0000",
          "predict_our_method": "0.9482",
          "predict_baseline": "0.9504"
        },
        {
          "input": "correlation analysis of boiling point error with relative humidity (seed=142)",
          "output": "pearson_r: 0.9460, p: 0.0000; spearman_r: 0.9498, p: 0.0000",
          "predict_our_method": "0.9460",
          "predict_baseline": "0.9498"
        },
        {
          "input": "correlation analysis of boiling point error with relative humidity (seed=242)",
          "output": "pearson_r: 0.9430, p: 0.0000; spearman_r: 0.9468, p: 0.0000",
          "predict_our_method": "0.9430",
          "predict_baseline": "0.9468"
        },
        {
          "input": "correlation analysis of boiling point error with relative humidity (seed=342)",
          "output": "pearson_r: 0.9408, p: 0.0000; spearman_r: 0.9435, p: 0.0000",
          "predict_our_method": "0.9408",
          "predict_baseline": "0.9435"
        },
        {
          "input": "correlation analysis of boiling point error with relative humidity (seed=442)",
          "output": "pearson_r: 0.9437, p: 0.0000; spearman_r: 0.9473, p: 0.0000",
          "predict_our_method": "0.9437",
          "predict_baseline": "0.9473"
        },
        {
          "input": "correlation analysis of boiling point error with relative humidity (seed=542)",
          "output": "pearson_r: 0.9445, p: 0.0000; spearman_r: 0.9492, p: 0.0000",
          "predict_our_method": "0.9445",
          "predict_baseline": "0.9492"
        },
        {
          "input": "correlation analysis of boiling point error with relative humidity (seed=642)",
          "output": "pearson_r: 0.9418, p: 0.0000; spearman_r: 0.9472, p: 0.0000",
          "predict_our_method": "0.9418",
          "predict_baseline": "0.9472"
        },
        {
          "input": "correlation analysis of boiling point error with relative humidity (seed=742)",
          "output": "pearson_r: 0.9486, p: 0.0000; spearman_r: 0.9533, p: 0.0000",
          "predict_our_method": "0.9486",
          "predict_baseline": "0.9533"
        },
        {
          "input": "correlation analysis of boiling point error with relative humidity (seed=842)",
          "output": "pearson_r: 0.9450, p: 0.0000; spearman_r: 0.9486, p: 0.0000",
          "predict_our_method": "0.9450",
          "predict_baseline": "0.9486"
        },
        {
          "input": "correlation analysis of boiling point error with relative humidity (seed=942)",
          "output": "pearson_r: 0.9432, p: 0.0000; spearman_r: 0.9482, p: 0.0000",
          "predict_our_method": "0.9432",
          "predict_baseline": "0.9482"
        }
      ]
    }
  ]
}
```

### Key Numbers to Verify
| Metric | Expected Value | Tolerance |
|--------|----------------|-----------|
| Pearson correlation (r) - mean across 10 seeds | ~0.9445 | ±0.005 |
| Spearman correlation (r) - mean across 10 seeds | ~0.9484 | ±0.005 |
| p-value (both) | < 0.001 | exact 0.0000 |
| Sample size per example (n) | 1000 | exact |
| Number of examples | 10 | exact |
| Number of methods (predict_* fields) | 2 (our_method, baseline) | exact |

### Figure Files
- `figures/fig1.png` - PNG scatter plot with linear fit
- `figures/fig1.pdf` - PDF vector version

### Log File
- `logs/method.log` - Execution log with timestamp and results

## 6. Paper Reference

These results correspond to the "Humidity-Driven Nucleation" hypothesis test in the paper. The correlation coefficient (r ≈ 0.95) and p-value (< 0.001) appear in:
- Results section: correlation analysis
- Figure 1: Scatter plot of boiling point error vs relative humidity

## 7. Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: matplotlib` | Run `pip install matplotlib==3.11.2` |
| Font warnings (CMU Serif) | Ignore - uses fallback font, output is correct |
| Different random results | Ensure seed=42 in `method.py` line 22 |

## 8. Regenerating the Virtual Environment

If `.venv/` was deleted (marked as regenerable in manifest):

```bash
# From the manifest source command:
uv venv .venv --python=3.12 && uv pip install --python=.venv/bin/python matplotlib==3.11.2 numpy==2.5.5 pandas==3.1.1 scipy==1.18.1 loguru==0.7.2

# Or with standard pip:
python3.12 -m venv .venv
source .venv/bin/activate
pip install matplotlib==3.11.2 numpy==2.5.5 pandas==3.1.1 scipy==1.18.1 loguru==0.7.2
```