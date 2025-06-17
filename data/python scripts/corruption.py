import pandas as pd
import json
from collections import defaultdict
from pathlib import Path
from utils import ALLOWED_COUNTRIES
import os

def process_corruption_perceptions():
    cpi_files = {
        "2022": "C:/Users/Sid/Documents/GlobalLaunchAI/data/datasets/CORRUPTION/CPI_2022.csv",
        "2023": "C:/Users/Sid/Documents/GlobalLaunchAI/data/datasets/CORRUPTION/CPI_2023.csv",
        "2024": "C:/Users/Sid/Documents/GlobalLaunchAI/data/datasets/CORRUPTION/CPI_2024.csv"
    }

    indicator_mapping = {
        "Economist Intelligence Unit Country Ratings": "economist_intelligence_unit_country_rating",
        "S&P Country Risk Rating": "s_and_p_country_risk_rating",
        "IMD World Competitiveness Yearbook": "imd_world_competitiveness",
        "PRS International Country Risk Guide": "prs_international_country_risk_guide",
        "World Bank CPIA": "world_bank_cpia",
        "World Economic Forum EOS": "wef_eos",
        "World Justice Project Rule of Law Index": "world_justice_project_rule_of_law_index"
    }

    output_dir = Path("C:/Users/Sid/Documents/GlobalLaunchAI/data/country_jsons")
    output_dir.mkdir(parents=True, exist_ok=True)

    for year, filename in cpi_files.items():
        df = pd.read_csv(filename, skiprows=2, header=0)
        for _, row in df.iterrows():
            country_code = row.get("ISO3")
            # ✅ Skip countries not in the allowlist
            if country_code not in ALLOWED_COUNTRIES:
                continue
            
            if pd.isna(country_code):
                continue

            try:
                cpi_score_key = "CPI score " + year if year != "2024" else "CPI 2024 score"
                corruption_block = {
                    "overview": {
                        "cpi_score": float(row.get(cpi_score_key)),
                        "cpi_rank": int(row.get("Rank")),
                        "region_average_cpi": None,
                        "region": str(row.get("Region")),
                        "confidence_interval": {
                            "lower": float(row.get("Lower CI")),
                            "upper": float(row.get("Upper CI"))
                        },
                        "source": "Transparency International CPI"
                    },
                    "explanatory_indicators": {}
                }

                for col, json_key in indicator_mapping.items():
                    value = row.get(col)
                    if pd.notna(value):
                        corruption_block["explanatory_indicators"][json_key] = float(value)

                # Load existing JSON if present
                file_path = output_dir / f"{country_code}.json"
                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8") as f:
                        existing_data = json.load(f)
                else:
                    existing_data = {}

                # Merge data for this year
                existing_data.setdefault(year, {}).update({
                    "corruption_perceptions": corruption_block
                })

                # Save updated JSON
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(existing_data, f, indent=2)

            except Exception:
                continue
