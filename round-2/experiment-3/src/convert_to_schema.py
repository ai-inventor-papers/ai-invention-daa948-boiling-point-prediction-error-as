#!/usr/bin/env python3
"""
Convert method_out.json to exp_gen_sol_out.json schema format.
"""

import json
from pathlib import Path

# Load the original output
with open("method_out.json") as f:
    data = json.load(f)

# Create examples for engineeringtoolbox dataset
eng_examples = []
for isa_detail, base_detail in zip(
    data["validation_engineeringtoolbox"]["ISA_Antoine"]["details"],
    data["validation_engineeringtoolbox"]["Baseline"]["details"]
):
    eng_examples.append({
        "input": f"Altitude: {isa_detail['altitude_m']} m",
        "output": f"{isa_detail['observed_bp_c']:.1f} °C",
        "predict_isa_antoine": f"{isa_detail['predicted_bp_c']:.2f} °C",
        "predict_baseline": f"{base_detail['predicted_bp_c']:.2f} °C",
        "metadata_source": "engineeringtoolbox",
        "metadata_altitude_m": isa_detail["altitude_m"],
        "metadata_observed_bp_c": isa_detail["observed_bp_c"]
    })

# Create examples for deleze dataset
deleze_examples = []
for isa_detail, base_detail in zip(
    data["validation_deleze"]["ISA_Antoine"]["details"],
    data["validation_deleze"]["Baseline"]["details"]
):
    deleze_examples.append({
        "input": f"Altitude: {isa_detail['altitude_m']} m",
        "output": f"{isa_detail['observed_bp_c']:.1f} °C",
        "predict_isa_antoine": f"{isa_detail['predicted_bp_c']:.2f} °C",
        "predict_baseline": f"{base_detail['predicted_bp_c']:.2f} °C",
        "metadata_source": "deleze",
        "metadata_altitude_m": isa_detail["altitude_m"],
        "metadata_observed_bp_c": isa_detail["observed_bp_c"]
    })

# Build the schema-compliant output
schema_output = {
    "metadata": {
        "method_name": "ISA+Antoine",
        "description": "Empirical validation of ISA barometric formula + Antoine equation for boiling point prediction",
        "constants": data["constants"],
        "reference_point_tests": data["reference_point_tests"],
        "monotonic_decrease_verified": data["monotonic_decrease_verified"],
        "baseline_comparison": {
            "engineeringtoolbox": {
                "ISA_Antoine_rmse": data["validation_engineeringtoolbox"]["ISA_Antoine"]["metrics"]["rmse"],
                "ISA_Antoine_bias": data["validation_engineeringtoolbox"]["ISA_Antoine"]["metrics"]["bias"],
                "Baseline_rmse": data["validation_engineeringtoolbox"]["Baseline"]["metrics"]["rmse"],
                "Baseline_bias": data["validation_engineeringtoolbox"]["Baseline"]["metrics"]["bias"]
            },
            "deleze": {
                "ISA_Antoine_rmse": data["validation_deleze"]["ISA_Antoine"]["metrics"]["rmse"],
                "ISA_Antoine_bias": data["validation_deleze"]["ISA_Antoine"]["metrics"]["bias"],
                "Baseline_rmse": data["validation_deleze"]["Baseline"]["metrics"]["rmse"],
                "Baseline_bias": data["validation_deleze"]["Baseline"]["metrics"]["bias"]
            }
        },
        "sensitivity_analysis": {
            "optimal_engineeringtoolbox": data["sensitivity_analysis"]["optimal_engineeringtoolbox"],
            "optimal_deleze": data["sensitivity_analysis"]["optimal_deleze"]
        }
    },
    "datasets": [
        {
            "dataset": "boiling_point_engineeringtoolbox",
            "examples": eng_examples
        },
        {
            "dataset": "boiling_point_deleze",
            "examples": deleze_examples
        }
    ]
}

# Save the converted output
output_path = Path("exp_gen_sol_out.json")
output_path.write_text(json.dumps(schema_output, indent=2))
print(f"Saved schema-compliant output to {output_path}")
print(f"EngineeringToolbox examples: {len(eng_examples)}")
print(f"Deleze examples: {len(deleze_examples)}")