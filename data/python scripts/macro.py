import pandas as pd
import json
from utils import ALLOWED_COUNTRIES
import os

def process_macroeconomic_indicators():
    def load_csv(path, skiprows=0):
        return pd.read_csv(path, skiprows=skiprows)

    df1 = load_csv("data/datasets/MACROECONOMIC/MACRO1.csv")
    df2 = load_csv("data/datasets/MACROECONOMIC/MACRO2.csv", skiprows=3)
    df3 = load_csv("data/datasets/MACROECONOMIC/MACRO3.csv", skiprows=3)

    YEARS = ["2020", "2021", "2022"]
    COUNTRY_CODES = df1["ISO"].unique()
    name_to_iso = {row["Country"]: row["ISO"] for _, row in df1.iterrows()}

    def extract_from_df1(df, indicator_code, json_key, scale=1.0):
        subset = df[df["WEO Subject Code"] == indicator_code]
        data = {}
        for _, row in subset.iterrows():
            country = row["ISO"]
            for year in YEARS:
                val = row.get(year)
                if pd.notnull(val):
                    val_str = str(val).replace(",", "").strip()
                    if val_str in ["--", "n/a", ""]:
                        continue
                    try:
                        clean_val = float(val_str)
                        data.setdefault(country, {})[year] = round(clean_val * scale, 4)
                    except ValueError:
                        pass
        return json_key, data

    def extract_from_transposed_df(df, indicator_name, json_key, scale=1.0):
        data = {}
        subset = df[df["Indicator Name"] == indicator_name]
        for _, row in subset.iterrows():
            iso_code = name_to_iso.get(row["Country Name"])
            if not iso_code:
                continue
            for year in YEARS:
                val = row.get(year)
                if pd.notnull(val):
                    try:
                        data.setdefault(iso_code, {})[year] = round(float(val) * scale, 4)
                    except:
                        continue
        return json_key, data

    INDICATORS = [
        ("NGDPD", "gdp_current_usd_billions", 1 / 1e3),
        ("NGDP_RPCH", "gdp_growth_percent", 1.0),
        ("PCPIPCH", "inflation_rate_percent", 1.0),
        ("LUR", "unemployment_rate_percent", 1.0),
        ("BCA", "current_account_balance_percent_gdp", 1.0),
        ("GGXWDG_NGDP", "public_debt_percent_of_gdp", 1.0),
    ]

    TRANSPOSED_INDICATORS = [
        ("Real interest rate (%)", "interest_rate_percent", 1.0),
        ("Official exchange rate (LCU per US$, period average)", "exchange_rate_vs_usd", 1.0),
    ]

    all_data = {code: {} for code in COUNTRY_CODES}

    for ind_code, json_key, scale in INDICATORS:
        key, values = extract_from_df1(df1, ind_code, json_key, scale)
        for country, year_data in values.items():
            for year, val in year_data.items():
                all_data[country].setdefault(year, {})[key] = val

    key, values = extract_from_transposed_df(df2, *TRANSPOSED_INDICATORS[0])
    for country, year_data in values.items():
        for year, val in year_data.items():
            all_data[country].setdefault(year, {})[key] = val

    key, values = extract_from_transposed_df(df3, *TRANSPOSED_INDICATORS[1])
    for country, year_data in values.items():
        for year, val in year_data.items():
            all_data[country].setdefault(year, {})[key] = val

    os.makedirs("data/country_jsons", exist_ok=True)
    for country, year_dict in all_data.items():
        if country not in ALLOWED_COUNTRIES:
            continue  # ✅ Skip countries not in your target set
        
        json_path = f"data/country_jsons/{country}.json"
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        else:
            existing_data = {}

        for year in YEARS:
            if year in year_dict:
                existing_data.setdefault(year, {}).update({
                    "macroeconomic_indicators": year_dict[year]
                })

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2)
