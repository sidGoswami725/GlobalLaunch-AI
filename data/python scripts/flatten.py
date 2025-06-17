# flatten_jsons.py

import os
import json
from pathlib import Path

INPUT_DIR = Path("data/country_jsons")
OUTPUT_DIR = Path("data/flat_country_jsons")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def flatten(d, parent_key=''):
    """Recursively flattens a nested dict using dot notation."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten(v, new_key).items())
        else:
            items.append((new_key, v))
    return dict(items)

def flatten_country_json(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    flat_data = {}
    for year, year_data in data.items():
        year_flat = flatten(year_data, parent_key=year)
        flat_data.update(year_flat)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(flat_data, f, indent=2)

def main():
    for file in INPUT_DIR.glob("*.json"):
        output_file = OUTPUT_DIR / file.name
        flatten_country_json(file, output_file)
        print(f"✅ Flattened: {file.name} -> {output_file.name}")

if __name__ == "__main__":
    main()
