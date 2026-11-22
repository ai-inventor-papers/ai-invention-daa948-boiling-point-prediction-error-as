#!/usr/bin/env python3
"""
Generate full, mini, and preview versions of a JSON file for exp_gen_sol_out schema.
The input must be an exp_gen_sol_out.json file with the datasets-grouped format.
"""

import json
import sys
from pathlib import Path

MAX_ARRAY_ITEMS = 3
MAX_STRING_LENGTH = 200
TRUNCATE_MARKER = "..."


def truncate_value(value):
    """Recursively truncate JSON data for preview."""
    if isinstance(value, list):
        return [truncate_value(item) for item in value[:MAX_ARRAY_ITEMS]]
    if isinstance(value, str):
        if len(value) > MAX_STRING_LENGTH:
            return value[:MAX_STRING_LENGTH] + TRUNCATE_MARKER
        return value
    if isinstance(value, dict):
        return {k: truncate_value(v) for k, v in value.items()}
    return value


def process_datasets_grouped(data, max_items=MAX_ARRAY_ITEMS):
    """Process datasets-grouped format (exp_gen_sol_out, etc.)"""
    if "datasets" in data and isinstance(data["datasets"], list):
        # Slice datasets to max_items
        data["datasets"] = data["datasets"][:max_items]
        # For each dataset, slice examples
        for ds in data["datasets"]:
            if "examples" in ds and isinstance(ds["examples"], list):
                ds["examples"] = ds["examples"][:max_items]


def main():
    input_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else input_path.parent
    
    if not input_path.exists():
        print(f"Error: Input file does not exist: {input_path}")
        sys.exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = input_path.stem
    
    # Load JSON data
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)
    
    # Validate it has the expected structure
    if "datasets" not in data:
        print(f"Error: Input file does not have 'datasets' key (not exp_gen_sol_out format)")
        sys.exit(1)
    
    # Full version - identical to original
    full_path = output_dir / f"full_{base_name}.json"
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Full: {full_path}")
    
    # Mini version - slice datasets and examples
    mini_data = json.loads(json.dumps(data))  # Deep copy
    process_datasets_grouped(mini_data)
    
    mini_path = output_dir / f"mini_{base_name}.json"
    with open(mini_path, "w", encoding="utf-8") as f:
        json.dump(mini_data, f, indent=2)
    print(f"Mini: {mini_path}")
    
    # Preview version - mini with truncated strings
    preview_data = truncate_value(mini_data)
    preview_path = output_dir / f"preview_{base_name}.json"
    with open(preview_path, "w", encoding="utf-8") as f:
        json.dump(preview_data, f, indent=2)
    print(f"Preview: {preview_path}")
    
    print("\nGenerated 3 versions successfully!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_json_versions.py <input.json> [output_dir]")
        print("  Input must be an exp_gen_sol_out.json file")
        sys.exit(1)
    main()