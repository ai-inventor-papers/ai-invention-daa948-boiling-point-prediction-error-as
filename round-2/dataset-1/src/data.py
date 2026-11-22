#!/usr/bin/env python3
"""
Load boiling point altitude datasets and standardize to exp_sel_data_out.json schema.
Each data point = one example, grouped by source dataset.
"""

import json
from pathlib import Path

# Load the empirical dataset (best for evaluation against ISA/Antoine)
empirical_path = Path("temp/datasets/full_boiling_point_altitude_empirical.json")
with open(empirical_path, 'r') as f:
    empirical_data = json.load(f)

# Also load validated full dataset
validated_path = Path("temp/datasets/full_boiling_point_altitude_dataset_validated.json")
with open(validated_path, 'r') as f:
    validated_data = json.load(f)

# Group by source - use empirical data for empirical sources, validated for all
# Define our canonical dataset names - SELECT TOP 5 based on empirical quality and authority
source_mapping = {
    "Forbes (1857) - Alps measurements": "Forbes_1857_Alps",                    # TRUE empirical field measurements (17)
    "Law Supply Inc. - Boiling Point of Water at Various Altitudes and Pressures": "LawSupply_Engineering",  # Industry reference (24)
    "UC Davis / Snyder (2016) - Calibrating Thermometers in Boiling Water": "UCDavis_Snyder_2016",  # ASHRAE/Perry calibration (21)
    "Engineering ToolBox - Water Boiling Points vs. Altitude": "EngineeringToolBox",  # Widely used industry ref (49)
    "SimuPipe - ISA Standard Atmosphere Table": "SimuPipe_ISA"   # Theoretical ISA baseline (18)
    # Excluded: Deleze_Model - model-derived, not empirical
}

datasets_dict = {}

# Process all validated data (includes both empirical and theoretical)
for entry in validated_data:
    source = entry["source"]
    if source not in source_mapping:
        continue
    
    canonical_name = source_mapping[source]
    if canonical_name not in datasets_dict:
        datasets_dict[canonical_name] = []
    
    # Create input: altitude and pressure as JSON string
    input_data = {
        "altitude_m": entry["altitude_m"],
        "pressure_hpa": entry["pressure_hpa"]
    }
    
    # Output: boiling point
    output_data = {
        "boiling_point_c": entry["boiling_point_c"]
    }
    
    example = {
        "input": json.dumps(input_data),
        "output": json.dumps(output_data),
        "metadata_fold": 0,  # single fold for now
        "metadata_task_type": "regression",
        "metadata_feature_names": ["altitude_m", "pressure_hpa"],
        "metadata_target_name": "boiling_point_c",
        "metadata_source_detail": entry["source_detail"],
        "metadata_row_index": entry["id"],
        "metadata_is_empirical": source in [
            "Forbes (1857) - Alps measurements",
            "Law Supply Inc. - Boiling Point of Water at Various Altitudes and Pressures",
            "UC Davis / Snyder (2016) - Calibrating Thermometers in Boiling Water",
            "Engineering ToolBox - Water Boiling Points vs. Altitude"
        ]
    }
    
    datasets_dict[canonical_name].append(example)

# Convert to schema format
output = {
    "metadata": {
        "description": "Empirical and theoretical water boiling point vs altitude data for ISA/Antoine validation",
        "total_examples": sum(len(examples) for examples in datasets_dict.values()),
        "num_datasets": len(datasets_dict),
        "task": "Predict boiling point of water given altitude and ambient pressure",
        "domain": "Atmospheric thermodynamics",
        "evaluation_metric": "RMSE (°C) between predicted and measured boiling point"
    },
    "datasets": [
        {"dataset": name, "examples": examples}
        for name, examples in datasets_dict.items()
    ]
}

# Save full output
output_path = Path("full_data_out.json")
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"Saved {output_path} with {len(output['datasets'])} datasets and {output['metadata']['total_examples']} total examples")

for ds in output["datasets"]:
    print(f"  {ds['dataset']}: {len(ds['examples'])} examples")