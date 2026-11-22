#!/usr/bin/env python3
"""
Compile empirical water boiling point altitude dataset from multiple sources.
Standardizes all data to: altitude (meters), ambient pressure (hPa), measured boiling point (°C).
"""

import json
from pathlib import Path

# Forbes 1857 dataset - 17 observations from the Alps
# x = boiling point (°F), y = 100 * log10(pressure in inHg)
forbes_raw = [
    (194.5, 131.79), (194.3, 131.79), (197.9, 135.02), (198.4, 135.55),
    (199.4, 136.46), (199.9, 136.83), (200.9, 137.75), (201.1, 138.08),
    (201.4, 138.33), (201.3, 138.41), (203.6, 141.17), (204.6, 142.51),
    (209.5, 148.62), (208.6, 147.38), (210.7, 149.84), (211.9, 151.52),
    (212.2, 151.85)
]

# Convert Forbes data
forbes_data = []
for bp_f, logp100 in forbes_raw:
    # y = 100 * log10(pressure_inHg) => pressure_inHg = 10^(y/100)
    pressure_inhg = 10 ** (logp100 / 100)
    pressure_hpa = pressure_inhg * 33.8639  # 1 inHg = 33.8639 hPa
    bp_c = (bp_f - 32) * 5 / 9
    # Estimate altitude from pressure using ISA barometric formula
    # P = 1013.25 * (1 - 2.25577e-5 * h)^5.25588
    # h = (1 - (P/1013.25)^(1/5.25588)) / 2.25577e-5
    if pressure_hpa > 0:
        altitude_m = (1 - (pressure_hpa / 1013.25) ** (1/5.25588)) / 2.25577e-5
    else:
        altitude_m = None
    forbes_data.append({
        "altitude_m": round(altitude_m, 1) if altitude_m else None,
        "pressure_hpa": round(pressure_hpa, 1),
        "boiling_point_c": round(bp_c, 1),
        "source": "Forbes (1857) - Alps measurements",
        "source_detail": "Transactions of the Royal Society of Edinburgh, 21, 235-243",
        "notes": "Original: boiling point °F, 100*log10(pressure inHg); converted to SI units"
    })

# Law Supply table - altitude (ft), pressure (inHg, mmHg, PSIA), boiling point (°F)
law_supply_raw = [
    (-1000, 31.0, 788, 15.2, 213.8),
    (-500, 30.5, 775, 15.0, 212.9),
    (0, 29.9, 760, 14.7, 212.0),
    (500, 29.4, 747, 14.4, 211.1),
    (1000, 28.9, 734, 14.2, 210.2),
    (1500, 28.3, 719, 13.9, 209.3),
    (2000, 27.8, 706, 13.7, 208.4),
    (2500, 27.3, 694, 13.4, 207.4),
    (3000, 26.8, 681, 13.2, 206.5),
    (3500, 26.3, 668, 12.9, 205.6),
    (4000, 25.8, 655, 12.7, 204.7),
    (4500, 25.4, 645, 12.4, 203.8),
    (5000, 24.9, 633, 12.2, 202.9),
    (5500, 24.4, 620, 12.0, 201.9),
    (6000, 24.0, 610, 11.8, 201.0),
    (6500, 23.5, 597, 11.5, 200.1),
    (7000, 23.1, 587, 11.3, 199.2),
    (7500, 22.7, 577, 11.1, 198.3),
    (8000, 22.2, 564, 10.9, 197.4),
    (8500, 21.8, 554, 10.7, 196.5),
    (9000, 21.4, 544, 10.5, 195.5),
    (9500, 21.0, 533, 10.3, 194.6),
    (10000, 20.6, 523, 10.1, 193.7),
    (15000, 16.9, 429, 8.3, 184.0),
]

law_supply_data = []
for alt_ft, inhg, mmhg, psia, bp_f in law_supply_raw:
    alt_m = alt_ft * 0.3048
    pressure_hpa = inhg * 33.8639
    bp_c = (bp_f - 32) * 5 / 9
    law_supply_data.append({
        "altitude_m": round(alt_m, 1),
        "pressure_hpa": round(pressure_hpa, 1),
        "boiling_point_c": round(bp_c, 1),
        "source": "Law Supply Inc. - Boiling Point of Water at Various Altitudes and Pressures",
        "source_detail": "Web page last updated 05/19/2003, www.lawsupply.net/tech_data/water_boiling_point.htm",
        "notes": "Engineering reference table; pressure in inHg converted to hPa"
    })

# Deleze table - altitude (m), boiling point (°C) at 100m intervals
deleze_raw = [
    (-500, 101.7), (-400, 101.3), (-300, 101.0), (-200, 100.7), (-100, 100.3),
    (0, 100.0), (100, 99.7), (200, 99.3), (300, 99.0), (400, 98.7),
    (500, 98.3), (600, 98.0), (700, 97.7), (800, 97.3), (900, 97.0),
    (1000, 96.7), (1100, 96.3), (1200, 96.0), (1300, 95.7), (1400, 95.3),
    (1500, 95.0), (1600, 94.7), (1700, 94.3), (1800, 94.0), (1900, 93.7),
    (2000, 93.3), (2100, 93.0), (2200, 92.7), (2300, 92.3), (2400, 92.0),
    (2500, 91.7), (2600, 91.3), (2700, 91.0), (2800, 90.7), (2900, 90.3),
    (3000, 90.0), (3100, 89.7), (3200, 89.3), (3300, 89.0), (3400, 88.6),
    (3500, 88.3), (3600, 88.0), (3700, 87.6), (3800, 87.3), (3900, 87.0),
    (4000, 86.6), (4100, 86.3), (4200, 85.9), (4300, 85.6), (4400, 85.3),
    (4500, 84.9), (4600, 84.6), (4700, 84.3), (4800, 83.9), (4900, 83.6),
    (5000, 83.3), (5100, 82.9), (5200, 82.6), (5300, 82.2), (5400, 81.9),
    (5500, 81.6), (5600, 81.2), (5700, 80.9), (5800, 80.6), (5900, 80.2),
    (6000, 79.9), (6100, 79.5), (6200, 79.2), (6300, 78.9), (6400, 78.5),
    (6500, 78.2), (6600, 77.8), (6700, 77.5), (6800, 77.2), (6900, 76.8),
    (7000, 76.5), (7100, 76.1), (7200, 75.8), (7300, 75.5), (7400, 75.1),
    (7500, 74.8), (7600, 74.4), (7700, 74.1), (7800, 73.8), (7900, 73.4),
    (8000, 73.1), (8100, 72.7), (8200, 72.4), (8300, 72.0), (8400, 71.7),
    (8500, 71.4), (8600, 71.0), (8700, 70.7), (8800, 70.3), (8900, 70.0),
    (9000, 69.6), (9100, 69.3), (9200, 69.0), (9300, 68.6), (9400, 68.3),
    (9500, 67.9), (9600, 67.6), (9700, 67.2), (9800, 66.9), (9900, 66.5),
    (10000, 66.2), (10100, 65.8), (10200, 65.5), (10300, 65.2), (10400, 64.8),
    (10500, 64.5), (10600, 64.1), (10700, 63.8), (10800, 63.4), (10900, 63.1),
    (11000, 62.7), (11100, 62.4), (11200, 62.0), (11300, 61.7), (11400, 61.3),
    (11500, 61.0), (11600, 60.6), (11700, 60.3), (11800, 59.9), (11900, 59.6),
    (12000, 59.2), (12100, 58.9), (12200, 58.5), (12300, 58.2), (12400, 57.8),
]

deleze_data = []
for alt_m, bp_c in deleze_raw:
    # Calculate ISA pressure at this altitude
    pressure_hpa = 1013.25 * (1 - 2.25577e-5 * alt_m) ** 5.25588
    deleze_data.append({
        "altitude_m": alt_m,
        "pressure_hpa": round(pressure_hpa, 1),
        "boiling_point_c": bp_c,
        "source": "Deleze (marcel.deleze.name) - Boiling temperature of water vs altitude",
        "source_detail": "Numerical table based on barometric levelling model, calculated values represent average state of atmosphere",
        "notes": "Theoretical/model-derived table from ISA barometric formula; not empirical measurements"
    })

# UC Davis / Snyder table - altitude (ft), pressure (inHg), boiling point (°F)
ucdavis_raw = [
    (-500, 30.466, 212.9), (0, 29.921, 212.0), (500, 29.384, 211.1),
    (1000, 28.855, 210.2), (2000, 27.821, 208.4), (2500, 27.315, 207.5),
    (3000, 26.817, 206.6), (3500, 26.326, 205.7), (4000, 25.842, 204.8),
    (4500, 25.365, 203.9), (5000, 24.896, 203.0), (5500, 24.434, 202.0),
    (6000, 23.978, 201.1), (6500, 23.530, 200.2), (7000, 23.088, 199.3),
    (7500, 22.653, 198.3), (8000, 22.225, 197.4), (8500, 21.803, 196.4),
    (9000, 21.388, 195.5), (9500, 20.979, 194.6), (10000, 20.577, 193.6),
]

ucdavis_data = []
for alt_ft, inhg, bp_f in ucdavis_raw:
    alt_m = alt_ft * 0.3048
    pressure_hpa = inhg * 33.8639
    bp_c = (bp_f - 32) * 5 / 9
    ucdavis_data.append({
        "altitude_m": round(alt_m, 1),
        "pressure_hpa": round(pressure_hpa, 1),
        "boiling_point_c": round(bp_c, 1),
        "source": "UC Davis / Snyder (2016) - Calibrating Thermometers in Boiling Water",
        "source_detail": "O. Peter Snyder Jr., Ph.D., Hospitality Institute of Technology and Management; References: ASHRAE Handbook 1997, Perry's Chemical Engineers' Handbook 1984",
        "notes": "Engineering calibration table with ASHRAE/Perry references; pressure from barometric formula"
    })

# Engineering Toolbox table - altitude (ft, m), boiling point (°F, °C)
engtool_raw = [
    (-1000, -305, 213.9, 101.1), (-750, -229, 213.5, 100.8), (-500, -152, 213.0, 100.5),
    (-250, -76, 212.5, 100.3), (0, 0, 212.0, 100.0), (250, 76, 211.5, 99.7),
    (500, 152, 211.0, 99.5), (750, 229, 210.5, 99.2), (1000, 305, 210.1, 98.9),
    (1250, 381, 209.6, 98.6), (1500, 457, 209.1, 98.4), (1750, 533, 208.6, 98.1),
    (2000, 610, 208.1, 97.8), (2250, 686, 207.6, 97.6), (2500, 762, 207.2, 97.3),
    (2750, 838, 206.7, 97.1), (3000, 914, 206.2, 96.8), (3250, 991, 205.7, 96.5),
    (3500, 1067, 205.3, 96.3), (3750, 1143, 204.8, 96.0), (4000, 1219, 204.3, 95.7),
    (4250, 1295, 203.8, 95.5), (4500, 1372, 203.4, 95.2), (4750, 1448, 202.9, 94.9),
    (5000, 1524, 202.4, 94.7), (5250, 1600, 202.0, 94.4), (5500, 1676, 201.5, 94.2),
    (5750, 1753, 201.0, 93.9), (6000, 1829, 200.6, 93.6), (6250, 1905, 200.1, 93.4),
    (6500, 1981, 199.6, 93.1), (6750, 2057, 199.2, 92.9), (7000, 2134, 198.7, 92.6),
    (7250, 2210, 198.2, 92.4), (7500, 2286, 197.8, 92.1), (7750, 2362, 197.3, 91.8),
    (8000, 2438, 196.9, 91.6), (8250, 2515, 196.4, 91.3), (8500, 2591, 196.0, 91.1),
    (8750, 2667, 195.5, 90.8), (9000, 2743, 195.0, 90.6), (9250, 2819, 194.6, 90.3),
    (9500, 2896, 194.1, 90.1), (9750, 2972, 193.7, 89.8), (10000, 3048, 193.2, 89.6),
    (15000, 4572, 184.4, 84.7), (20000, 6096, 175.9, 79.9), (25000, 7620, 167.8, 75.4),
    (30000, 9144, 160.0, 71.1),
]

engtool_data = []
for alt_ft, alt_m, bp_f, bp_c in engtool_raw:
    # Calculate ISA pressure at this altitude
    pressure_hpa = 1013.25 * (1 - 2.25577e-5 * alt_m) ** 5.25588
    engtool_data.append({
        "altitude_m": alt_m,
        "pressure_hpa": round(pressure_hpa, 1),
        "boiling_point_c": bp_c,
        "source": "Engineering ToolBox - Water Boiling Points vs. Altitude",
        "source_detail": "www.engineeringtoolbox.com/boiling-points-water-altitude-d_1344.html",
        "notes": "Engineering reference table; widely used in industry; boiling points given in both °F and °C"
    })

# SimuPipe ISA table - altitude (m, ft), pressure (kPa, psia), ISA temp (°C), boiling point (°C)
simupipe_raw = [
    (0, 0, 101.325, 14.70, 15.0, 100.0),
    (250, 820, 98.358, 14.27, 13.4, 99.1),
    (500, 1640, 95.461, 13.85, 11.8, 98.3),
    (750, 2461, 92.634, 13.44, 10.1, 97.5),
    (1000, 3281, 89.875, 13.04, 8.5, 96.6),
    (1250, 4101, 87.182, 12.64, 6.9, 95.8),
    (1500, 4921, 84.556, 12.26, 5.3, 95.0),
    (1750, 5741, 81.994, 11.89, 3.6, 94.1),
    (2000, 6562, 79.495, 11.53, 2.0, 93.3),
    (2500, 8202, 74.683, 10.83, -1.3, 91.6),
    (3000, 9843, 70.109, 10.17, -4.5, 90.0),
    (3500, 11483, 65.764, 9.54, -7.8, 88.3),
    (4000, 13123, 61.640, 8.94, -11.0, 86.6),
    (4500, 14764, 57.728, 8.37, -14.3, 84.9),
    (5000, 16404, 54.020, 7.83, -17.5, 83.3),
    (6000, 19685, 47.181, 6.84, -24.0, 79.9),
    (8000, 26247, 35.600, 5.16, -37.0, 73.1),
    (10000, 32808, 26.436, 3.83, -50.0, 66.2),
]

simupipe_data = []
for alt_m, alt_ft, pressure_kpa, pressure_psia, isa_temp_c, bp_c in simupipe_raw:
    pressure_hpa = pressure_kpa * 10  # kPa to hPa
    simupipe_data.append({
        "altitude_m": alt_m,
        "pressure_hpa": round(pressure_hpa, 1),
        "boiling_point_c": bp_c,
        "source": "SimuPipe - ISA Standard Atmosphere Table",
        "source_detail": "simupipe.com/resources/atmospheric-pressure-altitude; ISA model per ISO 2533 / ICAO; boiling point from IAPWS-IF97 saturation curve",
        "notes": "ISA standard atmosphere computed values; pressure from barometric formula; boiling point from IAPWS-IF97; NOT empirical measurements"
    })

# Combine all data
all_data = []
all_data.extend(forbes_data)
all_data.extend(law_supply_data)
all_data.extend(deleze_data)
all_data.extend(ucdavis_data)
all_data.extend(engtool_data)
all_data.extend(simupipe_data)

# Add unique IDs
for i, entry in enumerate(all_data):
    entry["id"] = f"bp_{i:04d}"

# Save full dataset
output_dir = Path("temp/datasets")
output_dir.mkdir(parents=True, exist_ok=True)

full_path = output_dir / "full_boiling_point_altitude_dataset.json"
with open(full_path, 'w') as f:
    json.dump(all_data, f, indent=2)

print(f"Saved full dataset with {len(all_data)} entries to {full_path}")

# Create mini (first 3) and preview (first 3, truncated)
mini_data = all_data[:3]
preview_data = []
for entry in all_data[:3]:
    preview_entry = {}
    for k, v in entry.items():
        if isinstance(v, str) and len(v) > 200:
            preview_entry[k] = v[:200] + "..."
        else:
            preview_entry[k] = v
    preview_data.append(preview_entry)

mini_path = output_dir / "mini_boiling_point_altitude_dataset.json"
with open(mini_path, 'w') as f:
    json.dump(mini_data, f, indent=2)

preview_path = output_dir / "preview_boiling_point_altitude_dataset.json"
with open(preview_path, 'w') as f:
    json.dump(preview_data, f, indent=2)

print(f"Saved mini dataset to {mini_path}")
print(f"Saved preview dataset to {preview_path}")

# Print summary statistics
sources = {}
for entry in all_data:
    src = entry["source"]
    sources[src] = sources.get(src, 0) + 1

print("\n=== Dataset Summary ===")
print(f"Total entries: {len(all_data)}")
print("\nBy source:")
for src, count in sources.items():
    print(f"  {src}: {count} entries")

altitudes = [e["altitude_m"] for e in all_data if e["altitude_m"] is not None]
print(f"\nAltitude range: {min(altitudes):.1f}m to {max(altitudes):.1f}m")
bps = [e["boiling_point_c"] for e in all_data]
print(f"Boiling point range: {min(bps):.1f}°C to {max(bps):.1f}°C")
pressures = [e["pressure_hpa"] for e in all_data]
print(f"Pressure range: {min(pressures):.1f} hPa to {max(pressures):.1f} hPa")