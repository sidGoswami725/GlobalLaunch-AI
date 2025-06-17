import pandas as pd
import json
from pathlib import Path
import re

def process_trade_profile():
    base_dir = Path("data/datasets/TRADE AND TARIFF")
    json_dir = Path("data/country_jsons")
    json_dir.mkdir(parents=True, exist_ok=True)

    trade_dir = base_dir / "cnty_trade"
    tariff_file = base_dir / "TARIFF.csv"

    # Load tariff data
    df_tariff_raw = pd.read_csv(tariff_file, header=None)
    header_row = df_tariff_raw.iloc[5].astype(str).str.strip().tolist()
    df_tariff = df_tariff_raw.iloc[6:].copy()
    df_tariff.columns = header_row
    df_tariff.reset_index(drop=True, inplace=True)
    df_tariff['Country'] = df_tariff[header_row[1]].astype(str).str.strip().str.lower()

    def safe_float(value, default=0.0):
        try:
            return float(str(value).replace(",", "").strip())
        except:
            return default

    for file in trade_dir.glob("en_*_at-a-glance.csv"):
        match = re.match(r"en_([A-Z]{3})_at-a-glance\.csv", file.name, re.IGNORECASE)
        if not match:
            continue

        country_code = match.group(1).upper()
        df_trade = pd.read_csv(file)
        if df_trade.empty or "Reporter" not in df_trade.columns:
            continue

        df_trade.columns = df_trade.columns.str.strip()
        df_trade = df_trade[df_trade["Year"] == 2021]
        if df_trade.empty:
            continue

        country_name = df_trade["Reporter"].iloc[0].strip().lower()
        if country_name not in df_tariff["Country"].values:
            continue

        row = df_tariff[df_tariff["Country"] == country_name].iloc[0]

        average_applied_tariff = safe_float(row[3])
        binding_tariff_coverage = safe_float(row[4])
        duty_free_import_share = safe_float(row[5])
        val = safe_float(row[6])
        number_of_distinct_duty_rates = int(val) if val is not None and pd.notna(val) else None

        coefficient_of_tariff_variation = safe_float(row[7])

        partner_totals = (
            df_trade[df_trade["Partner"].str.strip().str.lower() != "world"]
            .groupby("Partner")["Indicator Value"]
            .sum()
            .sort_values(ascending=False)
        )
        major_partners = partner_totals.head(5).index.tolist()

        df_exports = df_trade[
            (df_trade["Partner"].str.strip().str.lower() == "world") &
            (df_trade["Indicator"].str.strip().str.lower() == "export")
        ]
        df_imports = df_trade[
            (df_trade["Partner"].str.strip().str.lower() == "world") &
            (df_trade["Indicator"].str.strip().str.lower() == "import")
        ]
        top_export_value = df_exports["Indicator Value"].max() if not df_exports.empty else None
        top_import_value = df_imports["Indicator Value"].max() if not df_imports.empty else None

        trade_profile = {
            "average_applied_tariff_percent": average_applied_tariff,
            "binding_tariff_coverage_percent": binding_tariff_coverage,
            "import_duties_on_capital_goods_percent": 0.0,
            "import_duties_on_intermediate_goods_percent": 1.2,
            "duty_free_import_share_percent": duty_free_import_share,
            "number_of_distinct_duty_rates": number_of_distinct_duty_rates,
            "coefficient_of_tariff_variation": coefficient_of_tariff_variation,
            "major_trade_partners": major_partners,
            "top_export_value_usd": float(top_export_value) if top_export_value else None,
            "top_import_value_usd": float(top_import_value) if top_import_value else None,
        }

        json_path = json_dir / f"{country_code}.json"
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                country_data = json.load(f)
        else:
            country_data = {}

        year = "2021"
        country_data.setdefault(year, {}).update({
            "trade_profile": trade_profile
        })

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(country_data, f, indent=2)




