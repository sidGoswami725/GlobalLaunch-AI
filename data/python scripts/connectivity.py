import pandas as pd
import json
from collections import defaultdict
from pathlib import Path
from utils import ALLOWED_COUNTRIES
import os

def process_digital_connectivity():
    csv_path = "C:/Users/Sid/Documents/GlobalLaunchAI/data/datasets/CONNECTIVITY.csv"
    df = pd.read_csv(csv_path, encoding="utf-8", header=2)
    df.columns = df.columns.str.strip()

    if not {"ISO Code", "Year"}.issubset(df.columns):
        return

    measure_to_json_path = {
        "Index": "gsma_connectivity_index",
        "Network coverage": "mobile_broadband_coverage_percent",
        "Mobile Ownership": "mobile_ownership_percent",
        "2G Population Coverage": "connectivity.infrastructure.2g_population_coverage_percent",
        "3G Population Coverage": "connectivity.infrastructure.3g_population_coverage_percent",
        "4G Population Coverage": "connectivity.infrastructure.4g_population_coverage_percent",
        "5G Population Coverage": "connectivity.infrastructure.5g_population_coverage_percent",
        "Mobile download speeds": "connectivity.infrastructure.download_speed_mbps",
        "Mobile upload speeds": "connectivity.infrastructure.upload_speed_mbps",
        "Mobile latencies": "connectivity.infrastructure.latency_ms",
        "Spectrum assigned in bands below 1GHz": "connectivity.infrastructure.spectrum.below_1ghz_mhz",
        "Spectrum assigned in bands between 1-3GHz": "connectivity.infrastructure.spectrum.between_1_3ghz_mhz",
        "Spectrum assigned in bands between 3-6GHz": "connectivity.infrastructure.spectrum.between_3_6ghz_mhz",
        "Spectrum assigned in mmWave bands": "connectivity.infrastructure.spectrum.mmwave_mhz",
        "Affordability of entry basket (1GB)": "connectivity.affordability.entry_basket_1gb_usd",
        "Affordability of higher basket (5GB)": "connectivity.affordability.higher_basket_5gb_usd",
        "Affordability of entry basket (1GB) for poorest 40%": "connectivity.affordability.entry_40pct_1gb_usd",
        "Affordability of higher basket (5GB) for poorest 40%": "connectivity.affordability.higher_40pct_5gb_usd",
        "Device affordability": "connectivity.affordability.device_affordability_usd",
        "Device affordability for poorest 40%": "connectivity.affordability.device_affordability_40pct_usd",
        "Cost of taxes on mobile data": "connectivity.affordability.tax_mobile_data_percent",
        "Cost of taxes on handsets": "connectivity.affordability.tax_handsets_percent",
        "Cost of sector specific taxes on mobile data": "connectivity.affordability.sector_specific_taxes_percent",
        "Literacy": "connectivity.consumer_readiness.literacy_percent",
        "School Life Expectancy": "connectivity.consumer_readiness.school_life_expectancy_years",
        "Gender gap in mobile ownership": "connectivity.consumer_readiness.gender_gap_mobile_ownership_percent",
        "Gender gap in mobile internet": "connectivity.consumer_readiness.gender_gap_mobile_internet_percent",
        "Top-Level Domains (TLDs) per person": "connectivity.content_and_services.tlds_per_person",
        "E-Government Score": "connectivity.content_and_services.e_government_score",
        "Mobile Social Media Penetration": "connectivity.content_and_services.social_media_penetration_percent",
        "Locally developed apps per person": "connectivity.content_and_services.local_apps_per_person",
        "Digital Language Support": "connectivity.content_and_services.language_support_score",
        "Language accessibility of top ranked apps": "connectivity.content_and_services.top_apps_language_accessibility_score",
        "Cybersecurity Index": "connectivity.online_security.cybersecurity_index_score"
    }

    df = df[df["Year"].isin([2021, 2022, 2023])]

    output_dir = Path("data/country_jsons")
    output_dir.mkdir(parents=True, exist_ok=True)

    for _, row in df.iterrows():
        country_code = row["ISO Code"]
        # ✅ Skip countries not in the allowlist
        if country_code not in ALLOWED_COUNTRIES:
            continue
        
        year = str(row["Year"])
        dc_data = {}

        for column_name, json_path in measure_to_json_path.items():
            if column_name in row and pd.notna(row[column_name]):
                parts = json_path.split(".")
                current = dc_data
                for part in parts[:-1]:
                    current = current.setdefault(part, {})
                current[parts[-1]] = row[column_name]

        if not dc_data:
            continue

        json_path = output_dir / f"{country_code}.json"
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        else:
            existing_data = {}

        existing_data.setdefault(year, {}).update({
            "digital_connectivity": dc_data
        })

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2)
