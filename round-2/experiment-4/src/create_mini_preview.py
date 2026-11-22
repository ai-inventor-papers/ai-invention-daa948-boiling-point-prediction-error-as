#!/usr/bin/env python3
"""Generate full, mini, and preview versions of the results JSON (exp_gen_sol_out schema)."""
import json
from pathlib import Path

def truncate_value(value, max_len=200, marker="..."):
    """Recursively truncate JSON data for preview."""
    if isinstance(value, list):
        return [truncate_value(item, max_len, marker) for item in value[:3]]
    if isinstance(value, str):
        if len(value) > max_len:
            return value[:max_len] + marker
        return value
    if isinstance(value, dict):
        return {key: truncate_value(val, max_len, marker) for key, val in value.items()}
    return value

# Load the original data (method_out.json in exp_gen_sol_out schema)
input_path = Path("method_out.json")
with open(input_path, "r") as f:
    data = json.load(f)

# Full version: identical to original
full_data = data
full_file = Path("full_method_out.json")
with open(full_file, "w") as f:
    json.dump(full_data, f, indent=2)

# Mini version: keep metadata and datasets but slice examples to first 3
mini_data = {
    "metadata": data["metadata"],
    "datasets": [
        {
            "dataset": data["datasets"][0]["dataset"],
            "examples": data["datasets"][0]["examples"][:3]
        }
    ]
}
mini_file = Path("mini_method_out.json")
with open(mini_file, "w") as f:
    json.dump(mini_data, f, indent=2)

# Preview version: truncate strings in mini_data
preview_data = truncate_value(mini_data)
preview_file = Path("preview_method_out.json")
with open(preview_file, "w") as f:
    json.dump(preview_data, f, indent=2)

print(f"Generated:")
print(f"  {full_file} ({full_file.stat().st_size} bytes)")
print(f"  {mini_file} ({mini_file.stat().st_size} bytes)")
print(f"  {preview_file} ({preview_file.stat().st_size} bytes)")