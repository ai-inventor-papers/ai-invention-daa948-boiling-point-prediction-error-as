#!/usr/bin/env python3
"""
Generate mini and preview versions of full_data_out.json
"""

import json
from pathlib import Path

# Load full data
with open("full_data_out.json", 'r') as f:
    data = json.load(f)

# Create mini: first 3 datasets, each with first 3 examples
mini_data = {
    "metadata": data["metadata"],
    "datasets": []
}
for ds in data["datasets"][:3]:
    mini_ds = {
        "dataset": ds["dataset"],
        "examples": ds["examples"][:3]
    }
    mini_data["datasets"].append(mini_ds)

# Create preview: mini with strings truncated to 200 chars
def truncate_strings(obj, max_len=200):
    if isinstance(obj, str):
        if len(obj) > max_len:
            return obj[:max_len] + "..."
        return obj
    elif isinstance(obj, dict):
        return {k: truncate_strings(v, max_len) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [truncate_strings(v, max_len) for v in obj]
    return obj

preview_data = truncate_strings(mini_data)

# Save
with open("mini_full_data_out.json", 'w') as f:
    json.dump(mini_data, f, indent=2)

with open("preview_full_data_out.json", 'w') as f:
    json.dump(preview_data, f, indent=2)

# Also save full copy
with open("full_full_data_out.json", 'w') as f:
    json.dump(data, f, indent=2)

print("Created:")
print("  full_full_data_out.json")
print("  mini_full_data_out.json")
print("  preview_full_data_out.json")

print(f"\nMini: {len(mini_data['datasets'])} datasets")
for ds in mini_data['datasets']:
    print(f"  {ds['dataset']}: {len(ds['examples'])} examples")