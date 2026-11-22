# Reproducibility Instructions

This document provides complete step-by-step instructions to reproduce the empirical water boiling point altitude dataset artifact on Ubuntu.

## 1. Getting This Artifact

This workspace is published as part of a public GitHub repository. To get started:

```bash
# Clone the repository (replace with actual repo URL when published)
git clone <repository-url>
cd <repository-folder>/round-2/dataset-1/src
```

## 2. System Requirements

### System Packages
```bash
# Ubuntu 22.04+
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv build-essential
```

### Python Version
- Python 3.12.x (tested with 3.12.10)

### Virtual Environment & Dependencies
```bash
# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install exact pinned versions from pyproject.toml
.venv/bin/pip install --upgrade pip
.venv/bin/pip install \
    anyio==4.16.0 \
    attrs==26.1.0 \
    certifi==2026.11.20 \
    click==8.5.1 \
    datasets==5.2.0 \
    dill==0.4.1 \
    filelock==4.3.0 \
    fsspec==2026.9.0 \
    h11==0.16.0 \
    hf-xet==1.8.0 \
    httpcore==1.0.9 \
    httpcore2==2.16.2 \
    httpx==0.28.1 \
    httpx2==2.16.2 \
    huggingface-hub==2.4.0 \
    idna==3.20 \
    jsonschema==4.26.0 \
    jsonschema-specifications==2025.9.1 \
    multiprocess==0.70.19 \
    numpy==2.5.5 \
    packaging==26.3 \
    pandas==3.1.1 \
    pyarrow==26.0.1 \
    python-dateutil==4.0.0 \
    python-dotenv==1.2.4 \
    pyyaml==6.0.4 \
    referencing==0.37.0 \
    rpds-py==2026.9.1 \
    tqdm==4.70.1 \
    truststore==0.10.5 \
    typing-extensions==4.16.0 \
    tzdata==2026.6 \
    xxhash==4.1.0
```

Alternative: use uv (faster)
```bash
uv pip install -r pyproject.toml --python .venv/bin/python
```

## 3. Data Sources & Environment

No API keys or external downloads required - all source data was fetched during artifact creation and is included in the repository.

The following source data files are in `temp/datasets/`:
- `full_boiling_point_altitude_dataset.json` - raw combined data from 6 sources
- `full_boiling_point_altitude_dataset_validated.json` - validated with ISA/Antoine predictions
- `full_boiling_point_altitude_empirical.json` - empirical measurements only

These were created by fetching data from:
1. Forbes (1857) - Alps measurements (R package documentation)
2. Law Supply Inc. - Boiling point tables (web)
3. UC Davis / Snyder (2016) - Calibration tables (PDF)
4. Engineering ToolBox - Boiling points vs altitude (web)
5. Deleze (marcel.deleze.name) - Model-derived table (web)
6. SimuPipe - ISA Standard Atmosphere (web)

All fetching was done via `aii-web-tools` skill (web search + fetch) during artifact creation. The raw fetched HTML/PDF content is not saved - only the extracted numerical tables.

## 4. Commands to Run

### Step 1: Compile raw dataset from sources
```bash
cd /path/to/gen_art_dataset_1
.venv/bin/python compile_dataset.py
```
- **Runtime**: ~2 seconds
- **Output**: `temp/datasets/full_boiling_point_altitude_dataset.json` and variants

### Step 2: Validate against ISA/Antoine models
```bash
.venv/bin/python validate_dataset.py
```
- **Runtime**: ~1 second
- **Output**: `temp/datasets/full_boiling_point_altitude_dataset_validated.json` and empirical subset

### Step 3: Generate standardized schema format (exp_sel_data_out.json)
```bash
.venv/bin/python data.py
```
- **Runtime**: ~1 second
- **Output**: `full_data_out.json` (129 examples, 5 datasets)

### Step 4: Validate schema compliance
```bash
.venv/bin/python -c "
import json
from jsonschema import Draft7Validator
with open('/Users/Shared/aii_data/.claude/skills/aii-json/schemas/exp_sel_data_out.json') as f:
    schema = json.load(f)
with open('full_data_out.json') as f:
    data = json.load(f)
validator = Draft7Validator(schema)
errors = list(validator.iter_errors(data))
print(f'Errors: {len(errors)}')
"
```
- **Runtime**: <1 second
- **Expected**: 0 errors

### Step 5: Generate mini and preview variants
```bash
.venv/bin/python generate_outputs.py
```
- **Runtime**: <1 second
- **Output**: `mini_data_out.json`, `preview_data_out.json`

## 5. Expected Output Files

After running all steps, you should have:

| File | Size | Description |
|------|------|-------------|
| `full_data_out.json` | ~77 KB | Main dataset (129 examples, 5 datasets) |
| `mini_data_out.json` | ~6 KB | First 3 datasets × 3 examples each |
| `preview_data_out.json` | ~6 KB | Mini with strings truncated to 200 chars |
| `temp/datasets/full_boiling_point_altitude_dataset.json` | ~108 KB | Raw combined data (259 entries) |
| `temp/datasets/full_boiling_point_altitude_dataset_validated.json` | ~169 KB | Validated with ISA/Antoine |
| `temp/datasets/full_boiling_point_altitude_empirical.json` | ~109 KB | Empirical subset (165 entries) |

### Key Metrics to Verify

In `full_data_out.json`:
- 5 datasets: `Forbes_1857_Alps` (17), `LawSupply_Engineering` (24), `UCDavis_Snyder_2016` (21), `EngineeringToolBox` (49), `SimuPipe_ISA` (18)
- Total examples: 129
- Schema validation: 0 errors

In `validate_dataset.py` output:
- Empirical mean absolute error vs ISA+Antoine: **0.15°C**
- Max absolute error: 2.50°C (Forbes 1857 outliers)
- 4 empirical sources within 0.2°C of theoretical prediction

## 6. Hardware & Runtime

- **Hardware**: CPU-only (no GPU required)
- **Total runtime**: ~5 seconds for all steps
- **Memory**: <100 MB
- **Disk**: ~500 KB for outputs + ~500 MB for .venv

## 7. Notes for Readers

- The `.venv/` directory is NOT published (listed in `.aii/manifest.yaml` for deletion). You must recreate it using the instructions above.
- All paths in this document and in the Python scripts are **relative to the workspace root** (`gen_art_dataset_1/`).
- The `data.py` script uses `Path(__file__)` anchoring for portability.
- Source data in `temp/datasets/` IS published and should be present in the cloned repository.
- If you want to re-fetch the web sources yourself, you would need the `aii-web-tools` skill environment (not included here).

## 8. Artifact Context

This artifact was created as part of the AI Inventor invention loop (Iteration 2, GenArt step 3.3) to provide empirical boiling point data for evaluating the International Standard Atmosphere (ISA) barometric formula and Antoine equation predictions. The dataset enables RMSE calculation between predicted and measured boiling points at various altitudes.