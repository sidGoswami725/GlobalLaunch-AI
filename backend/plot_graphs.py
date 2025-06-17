# === graph_generator.py ===

import os
import re
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for headless environments

import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from pymongo import MongoClient
from dotenv import load_dotenv
from io import BytesIO
import base64

# === Environment & Mongo Setup ===
load_dotenv()  # Load .env variables
client = MongoClient(os.getenv("MONGODB_URI"))  # Connect to MongoDB
db = client[os.getenv("DB_NAME")]
profiles_col = db["country_profiles"]  # Collection with raw numeric data
graphs_col = db["country_graphs"]      # Collection to store generated graph images

# === Field Definitions for Charting ===
# Each category includes title, field set, and optional regex pattern for dynamic matching
FIELDS = {
    "ease_of_doing_business": {
        "title": "Ease of Doing Business Scores",
        "pattern": re.compile(r"(\d{4})\.ease_of_doing_business\.([^.]+)$"),
        "fields": {
            "starting_business_score",
            "overall_score",
            "getting_electricity.score",
            "registering_property.score",
            "getting_credit.score",
            "protecting_minority_investors.score",
            "paying_taxes.score",
            "trading_across_borders.score",
            "enforcing_contracts.score",
            "resolving_insolvency.score"
        }
    },
    "macroeconomic_indicators": {
        "title": "Macroeconomic Indicators",
        "fields": {
            "gdp_current_usd_billions",
            "gdp_growth_percent",
            "inflation_rate_percent",
            "unemployment_rate_percent",
            "current_account_balance_percent_gdp",
            "public_debt_percent_of_gdp",
            "exchange_rate_vs_usd"
        }
    },
    "digital_connectivity": {
        "title": "Digital Connectivity Indicators",
        "fields": {
            "gsma_connectivity_index",
            "mobile_broadband_coverage_percent",
            "mobile_ownership_percent",
            "connectivity.affordability.device_affordability_40pct_usd",
            "connectivity.affordability.tax_mobile_data_percent",
            "connectivity.affordability.tax_handsets_percent",
            "connectivity.affordability.sector_specific_taxes_percent",
            "connectivity.consumer_readiness.literacy_percent",
            "connectivity.content_and_services.e_government_score",
            "connectivity.content_and_services.social_media_penetration_percent",
            "connectivity.online_security.cybersecurity_index_score"
        }
    },
    "trade_profile": {
        "title": "Trade Profile Indicators",
        "fields": {
            "average_applied_tariff_percent",
            "binding_tariff_coverage_percent",
            "import_duties_on_capital_goods_percent",
            "import_duties_on_intermediate_goods_percent",
            "duty_free_import_share_percent",
            "number_of_distinct_duty_rates",
            "coefficient_of_tariff_variation"
        }
    }
}

# === Chart Generator ===
def plot_grouped_bar_chart_to_bytes(data_dict, title):
    """
    Plots a grouped bar chart from a nested dictionary of values:
        {year: {field: value}}
    Returns:
        PNG image bytes.
    """
    years = sorted(data_dict.keys())
    fields = sorted({f for y in data_dict.values() for f in y})
    n_years = len(years)
    bar_width = 0.8 / n_years
    x = np.arange(len(fields))

    fig, ax = plt.subplots(figsize=(max(12, 0.6 * len(fields)), 6))

    for i, year in enumerate(years):
        offset = (i - n_years / 2) * bar_width + bar_width / 2
        values = [data_dict[year].get(field, 0) for field in fields]
        ax.bar(x + offset, values, width=bar_width, label=year)

    ax.set_xticks(x)
    ax.set_xticklabels(fields, rotation=60, ha="right", fontsize=8)
    ax.set_title(title)
    ax.set_ylabel("Value")
    ax.legend(title="Year", fontsize="small", loc="upper right")
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')  # Save to buffer instead of file
    plt.close()
    buf.seek(0)
    return buf.getvalue()  # Return image bytes (PNG)


# === Main Driver Function ===
def generate_country_graphs(country_code, profiles_col, graphs_col):
    """
    Generates missing indicator charts for a given country and stores them in MongoDB.
    Only creates graphs that are not already cached.
    """
    # Fetch categories already present in the graph collection
    existing_categories = set()
    for doc in graphs_col.find({"country_code": country_code}, {"category": 1}):
        existing_categories.add(doc["category"])

    required_categories = set(FIELDS.keys())

    # Skip country if all categories are already present
    if existing_categories == required_categories:
        print(f"Skipping {country_code} — graphs already cached.")
        return

    # Initialize structure to hold time-series numeric data per category
    chunks = profiles_col.find({"country_code": country_code})
    data_map = {cat: defaultdict(dict) for cat in required_categories}

    for chunk in chunks:
        data = chunk.get("chunk_data", {})
        for key, val in data.items():
            if not isinstance(val, (int, float)):
                continue

            # Special pattern-based match for doing business scores
            match = FIELDS["ease_of_doing_business"]["pattern"].match(key)
            if match:
                year, field = match.groups()
                if field in FIELDS["ease_of_doing_business"]["fields"]:
                    data_map["ease_of_doing_business"][year][field] = val
                continue

            # General case: year.category.field
            parts = key.split(".")
            if len(parts) < 3:
                continue

            year, category = parts[0], parts[1]
            field = ".".join(parts[2:])
            if category in FIELDS and field in FIELDS[category]["fields"]:
                data_map[category][year][field] = val

    # Generate and store missing graphs
    new_graphs = []
    for category, yearly_data in data_map.items():
        if category in existing_categories or not yearly_data:
            continue
        img_bytes = plot_grouped_bar_chart_to_bytes(yearly_data, FIELDS[category]["title"])
        new_graphs.append({
            "country_code": country_code,
            "category": category,
            "title": FIELDS[category]["title"],
            "image": img_bytes
        })

    if new_graphs:
        graphs_col.insert_many(new_graphs)
        print(f"Saved {country_code} graphs: {[g['category'] for g in new_graphs]}")
    else:
        print(f"No new graphs generated for {country_code}")
