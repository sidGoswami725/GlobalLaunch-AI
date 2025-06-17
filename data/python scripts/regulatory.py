import pandas as pd
import json
from collections import defaultdict
from pathlib import Path
from utils import ALLOWED_COUNTRIES
import os

def process_regulatory_indicators():
    csv_path = "C:/Users/Sid/Documents/GlobalLaunchAI/data/datasets/REGULATORY.csv"
    df = pd.read_csv(csv_path, encoding="utf-8")

    required_columns = {"REF_AREA", "MEASURE", "OBS_VALUE", "TIME_PERIOD"}
    if not required_columns.issubset(df.columns):
        return

    measure_to_json_path = {
        "PMR": "product_market_regulation_score",
        "DISTORT_PUBLIC": "distortions_by_public_ownership.quality_and_scope_of_public_ownership",
        "GOVERNANCE": "distortions_by_public_ownership.governance_of_state_owned_enterprises",
        "PRICE": "involvement_in_business_operations.retail_price_controls_and_regulation",
        "INV_BUS_NET": "involvement_in_business_operations.involvement_in_network_sectors",
        "INV_BUS_SER": "involvement_in_business_operations.involvement_in_service_sectors",
        "PUBLIC_PROCUREMENT": "involvement_in_business_operations.public_procurement",
        "IMPACT_ASSESSMENT": "regulations_impact_evaluation.assessment_of_impact_on_competition",
        "STAKEHOLDER_ENGAG": "regulations_impact_evaluation.interaction_with_stakeholders",
        "LLC_POE": "barriers_to_domestic_and_foreign_entry.admin_and_regulatory_burden.llc_poe_requirements",
        "COMMANDSIMPLIF_BURDEN": "barriers_to_domestic_and_foreign_entry.admin_and_regulatory_burden.communication_and_simplification",
        "SERVBARRIER": "barriers_to_domestic_and_foreign_entry.barriers_in_service_and_network_sectors.barriers_to_entry_service_sectors",
        "BARRIER_SECT": "barriers_to_domestic_and_foreign_entry.barriers_in_service_and_network_sectors.barriers_to_entry_network_sectors",
        "FDI_INDEX": "barriers_to_domestic_and_foreign_entry.barriers_to_trade_and_investment.barriers_to_foreign_direct_investment"
    }

    df_filtered = df[df["MEASURE"].isin(measure_to_json_path)]

    output_dir = Path("data/country_jsons")
    output_dir.mkdir(parents=True, exist_ok=True)

    for _, row in df_filtered.iterrows():
        country_code = row["REF_AREA"]
        if country_code not in ALLOWED_COUNTRIES:
            continue
        
        year = str(row["TIME_PERIOD"])
        value = row["OBS_VALUE"]
        json_path = measure_to_json_path[row["MEASURE"]].split(".")

        # Load existing file if present
        json_file = output_dir / f"{country_code}.json"
        if json_file.exists():
            with open(json_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        else:
            existing_data = {}

        # Navigate and insert
        year_block = existing_data.setdefault(year, {})
        reg_block = year_block.setdefault("regulatory_indicators", {})
        current = reg_block
        for part in json_path[:-1]:
            current = current.setdefault(part, {})
        current[json_path[-1]] = value

        # Save updated file
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2)
