#!/usr/bin/env python3
"""
Validate compiled boiling point dataset against ISA/Antoine models.
Check for outliers and separate empirical vs theoretical data.
"""

import json
import math
from pathlib import Path

# Load full dataset
full_path = Path("temp/datasets/full_boiling_point_altitude_dataset.json")
with open(full_path, 'r') as f:
    data = json.load(f)

print(f"Loaded {len(data)} entries")

# ISA barometric formula: P = 1013.25 * (1 - 2.25577e-5 * h)^5.25588
def isa_pressure(altitude_m):
    if altitude_m < 11000:  # Troposphere
        return 1013.25 * (1 - 2.25577e-5 * altitude_m) ** 5.25588
    else:
        # Stratosphere (simplified)
        return 226.32 * math.exp(-0.0001577 * (altitude_m - 11000))

# Antoine equation for water: log10(P) = A - B/(C+T)
# P in mmHg, T in °C
# For water 1-100°C: A=8.07131, B=1730.63, C=233.426
# For water 100-374°C: A=8.14019, B=1810.94, C=244.485
def antoine_boiling_point(pressure_hpa):
    pressure_mmhg = pressure_hpa / 1.33322  # hPa to mmHg
    if pressure_mmhg <= 760:  # Below 100°C
        A, B, C = 8.07131, 1730.63, 233.426
    else:
        A, B, C = 8.14019, 1810.94, 244.485
    T = B / (A - math.log10(pressure_mmhg)) - C
    return T

# Validate each entry
for entry in data:
    alt = entry["altitude_m"]
    bp_measured = entry["boiling_point_c"]
    p_measured = entry["pressure_hpa"]
    
    # ISA predicted pressure at this altitude
    if alt is not None:
        p_isa = isa_pressure(alt)
        entry["pressure_isa_hpa"] = round(p_isa, 1)
        entry["pressure_diff_hpa"] = round(p_measured - p_isa, 1)
        entry["pressure_diff_pct"] = round((p_measured - p_isa) / p_isa * 100, 1)
    
    # Antoine predicted boiling point at measured pressure
    bp_antoine = antoine_boiling_point(p_measured)
    entry["boiling_point_antoine_c"] = round(bp_antoine, 1)
    entry["boiling_point_diff_c"] = round(bp_measured - bp_antoine, 1)
    
    # Also Antoine at ISA pressure
    if alt is not None:
        bp_antoine_isa = antoine_boiling_point(p_isa)
        entry["boiling_point_antoine_isa_c"] = round(bp_antoine_isa, 1)
        entry["boiling_point_diff_isa_c"] = round(bp_measured - bp_antoine_isa, 1)

# Separate empirical vs theoretical
empirical = [e for e in data if "empirical" in e.get("notes", "").lower() or "measurement" in e.get("notes", "").lower() or e["source"] == "Forbes (1857) - Alps measurements"]
theoretical = [e for e in data if e not in empirical]

print(f"\nEmpirical entries: {len(empirical)}")
print(f"Theoretical/model entries: {len(theoretical)}")

# Check outliers for empirical data
print("\n=== Empirical Data Validation (vs ISA/Antoine) ===")
for e in empirical:
    alt = e["altitude_m"]
    bp_meas = e["boiling_point_c"]
    bp_antoine_isa = e.get("boiling_point_antoine_isa_c")
    diff = e.get("boiling_point_diff_isa_c")
    if diff is not None and abs(diff) > 1.0:
        print(f"  OUTLIER: {e['id']} alt={alt}m bp_meas={bp_meas}°C bp_ISA={bp_antoine_isa}°C diff={diff}°C source={e['source']}")
    elif diff is not None:
        print(f"  OK: {e['id']} alt={alt}m bp_meas={bp_meas}°C bp_ISA={bp_antoine_isa}°C diff={diff}°C")

# Check theoretical data consistency
print("\n=== Theoretical Data Consistency Check ===")
for e in theoretical:
    alt = e["altitude_m"]
    bp_meas = e["boiling_point_c"]
    bp_antoine_isa = e.get("boiling_point_antoine_isa_c")
    diff = e.get("boiling_point_diff_isa_c")
    if diff is not None and abs(diff) > 0.5:
        print(f"  INCONSISTENT: {e['id']} alt={alt}m bp={bp_meas}°C ISA_pred={bp_antoine_isa}°C diff={diff}°C source={e['source']}")

# Save validated dataset
validated_path = Path("temp/datasets/full_boiling_point_altitude_dataset_validated.json")
with open(validated_path, 'w') as f:
    json.dump(data, f, indent=2)
print(f"\nSaved validated dataset to {validated_path}")

# Save empirical-only dataset
empirical_path = Path("temp/datasets/full_boiling_point_altitude_empirical.json")
with open(empirical_path, 'w') as f:
    json.dump(empirical, f, indent=2)
print(f"Saved empirical dataset ({len(empirical)} entries) to {empirical_path}")

# Create mini/preview for empirical
mini_emp = empirical[:3]
preview_emp = []
for entry in empirical[:3]:
    preview_entry = {}
    for k, v in entry.items():
        if isinstance(v, str) and len(v) > 200:
            preview_entry[k] = v[:200] + "..."
        else:
            preview_entry[k] = v
    preview_emp.append(preview_entry)

mini_emp_path = Path("temp/datasets/mini_boiling_point_altitude_empirical.json")
with open(mini_emp_path, 'w') as f:
    json.dump(mini_emp, f, indent=2)

preview_emp_path = Path("temp/datasets/preview_boiling_point_altitude_empirical.json")
with open(preview_emp_path, 'w') as f:
    json.dump(preview_emp, f, indent=2)

print(f"Saved empirical mini/preview")

# Summary stats for empirical data
if empirical:
    alts = [e["altitude_m"] for e in empirical if e["altitude_m"] is not None]
    bps = [e["boiling_point_c"] for e in empirical]
    diffs = [e.get("boiling_point_diff_isa_c", 0) for e in empirical if e.get("boiling_point_diff_isa_c") is not None]
    
    print(f"\n=== Empirical Dataset Summary ===")
    print(f"Entries: {len(empirical)}")
    print(f"Altitude range: {min(alts):.1f}m to {max(alts):.1f}m")
    print(f"Boiling point range: {min(bps):.1f}°C to {max(bps):.1f}°C")
    print(f"Mean absolute diff from ISA/Antoine: {sum(abs(d) for d in diffs)/len(diffs):.2f}°C")
    print(f"Max absolute diff: {max(abs(d) for d in diffs):.2f}°C")