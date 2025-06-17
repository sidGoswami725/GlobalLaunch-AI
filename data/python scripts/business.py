import pandas as pd
import json
from pathlib import Path
from collections import defaultdict
from utils import ALLOWED_COUNTRIES
import os

def process_ease_of_doing_business():
    csv_path = "data/datasets/EASE_OF_DOING_BSNS.csv"
    df = pd.read_csv(csv_path)
    df.replace("..", pd.NA, inplace=True)
    for year in ["2017 [YR2017]", "2018 [YR2018]", "2019 [YR2019]"]:
        df[year] = pd.to_numeric(df[year], errors='coerce')

    series_to_json_path = {
        "Global: Ease of doing business score (DB17-20 methodology)": "overall_score",
        "Starting a business - Score": "starting_business_score",
        "Dealing with construction permits (DB16-20 methodology) - Score": "dealing_with_construction_permits_details.score",
        "Dealing with construction permits: Procedures (number) - Score": "dealing_with_construction_permits_details.procedures",
        "Dealing with construction permits: Time (days)  - Score": "dealing_with_construction_permits_details.time_days",
        "Dealing with construction permits: Cost (% of Warehouse value) - Score": "dealing_with_construction_permits_details.cost_percent_warehouse_value",
        "Dealing with construction permits: Building quality control index (0-15) (DB16-20 methodology) - Score": "dealing_with_construction_permits_details.building_quality_control_index",
        "Getting electricity (DB16-20 methodology) - Score": "getting_electricity.score",
        "Getting electricity: Cost to get electricity (% of income per capita) - Score": "getting_electricity.details.cost_score",
        "Getting electricity: Procedures (number) - Score": "getting_electricity.details.procedures_score",
        "Getting electricity: Time (days) - Score": "getting_electricity.details.time_score",
        "Getting electricity: Reliability of supply and transparency of tariff index (0-8) (DB16-20 methodology) - Score": "getting_electricity.details.reliability_score",
        "Registering property (DB17-20 methodology) - Score": "registering_property.score",
        "Registering property: Cost (% of property value) - Score": "registering_property.details.cost_score",
        "Registering property: Procedures (number) - Score": "registering_property.details.procedures_score",
        "Registering property: Time (days) - Score": "registering_property.details.time_score",
        "Registering property: Quality of land administration index (0-30) (DB17-20 methodology) - Score": "registering_property.details.quality_score",
        "Getting credit (DB15-20 methodology) - Score": "getting_credit.score",
        "Getting credit: Strength of legal rights index (0-12) (DB15-20 methodology) - Score": "getting_credit.details.legal_rights_score",
        "Getting credit: Depth of credit information index (0-8) (DB15-20 methodology) - Score": "getting_credit.details.credit_info_score",
        "Protecting minority investors (DB15-20 methodology) - Score": "protecting_minority_investors.score",
        "Protecting minority investors: Ease of shareholder suits index (0-10) (DB15-20 methodology) - Score": "protecting_minority_investors.details.shareholder_suits_score",
        "Protecting minority investors: Extent of corporate transparency index (0-7) (DB15-20 methodology) - Score": "protecting_minority_investors.details.transparency_score",
        "Protecting minority investors: Extent of disclosure index (0-10) - Score": "protecting_minority_investors.details.disclosure_score",
        "Protecting minority investors: Extent of ownership and control index (0-7) (DB15-20 methodology) - Score": "protecting_minority_investors.details.ownership_control_score",
        "Protecting minority investors: Extent of shareholder rights index (0-6) (DB15-20 methodology) - Score": "protecting_minority_investors.details.shareholder_rights_score",
        "Protecting minority investors: Extent of director liability index (0-10) - Score": "protecting_minority_investors.details.director_liability_score",
        "Protecting minority investors: Strength of minority investor protection index (0-50) (DB15-20 methodology)": "protecting_minority_investors.details.investor_protection_index",
        "Paying taxes (DB17-20 methodology) - Score": "paying_taxes.score",
        "Paying taxes: Total tax and contribution rate (% of profit) - Score": "paying_taxes.details.total_tax_rate_score",
        "Paying taxes: Total tax and contribution rate (% of profit)": "paying_taxes.details.total_tax_rate",
        "Paying taxes: Labor tax and contributions (% of profits)": "paying_taxes.details.labor_tax_rate",
        "Paying taxes: Profit tax (% of profits)": "paying_taxes.details.profit_tax_rate",
        "Paying taxes: Payments per year (number per year) - Score": "paying_taxes.details.payments_per_year_score",
        "Paying taxes: Time (hours per year) - Score": "paying_taxes.details.time_to_comply_score",
        "Paying taxes: Postfiling index (0-100) (DB17-20 methodology) - Score": "paying_taxes.details.postfiling_index_score",
        "Paying taxes: Time to obtain VAT refund (weeks) (DB17-20 methodology)": "paying_taxes.details.vat_refund_time_score",
        "Paying taxes: Time to comply with corporate income tax correction (hours) (DB17-20 methodology) - Score": "paying_taxes.details.correction_compliance_time_score",
        "Paying taxes: Time to complete a corporate income tax correction (weeks) (DB17-20 methodology) - Score": "paying_taxes.details.correction_total_time_score",
        "Trading across borders (DB16-20 methodology) - Score": "trading_across_borders.score",
        "Time to export: Border compliance (hours) (DB16-20 methodology)": "trading_across_borders.details.export_border_compliance_time_score",
        "Time to export: Documentary compliance (hours) (DB16-20 methodology)": "trading_across_borders.details.export_doc_compliance_time_score",
        "Time to import: Border compliance (hours) (DB16-20 methodology)": "trading_across_borders.details.import_border_compliance_time_score",
        "Time to import: Documentary compliance (hours) (DB16-20 methodology)": "trading_across_borders.details.import_doc_compliance_time_score",
        "Trading across borders: Cost to export: Border compliance (USD) (DB16-20 methodology) - Score": "trading_across_borders.details.export_border_cost_score",
        "Trading across borders: Cost to export: Documentary compliance (USD) (DB16-20 methodology) - Score": "trading_across_borders.details.export_doc_cost_score",
        "Trading across borders: Cost to import: Border compliance (USD) (DB16-20 methodology) - Score": "trading_across_borders.details.import_border_cost_score",
        "Trading across borders: Cost to import: Documentary compliance (USD) (DB16-20 methodology) - Score": "trading_across_borders.details.import_doc_cost_score",
        "Enforcing contracts (DB17-20 methodology) - Score": "enforcing_contracts.score",
        "Enforcing contracts: Quality of the judicial processes index (0-19) (DB17-20 methodology) - Score": "enforcing_contracts.details.quality_of_judicial_process_score",
        "Enforcing contracts: Time (days) - Score": "enforcing_contracts.details.time_to_enforce_score",
        "Enforcing contracts: Cost (% of claim) - Score": "enforcing_contracts.details.cost_to_enforce_score",
        "Enforcing contracts: Procedures (number) - Score": "enforcing_contracts.details.procedures_score",
        "Resolving insolvency - Score": "resolving_insolvency.score",
        "Resolving insolvency: Recovery rate (cents on the dollar) - Score": "resolving_insolvency.details.recovery_rate_score",
        "Resolving insolvency: Strength of insolvency framework index (0-16) - Score": "resolving_insolvency.details.strength_of_insolvency_framework_score",
        "Resolving insolvency: Commencement of proceedings index (0-3) (DB15-20 methodology)": "resolving_insolvency.details.commencement_proceedings_index",
        "Resolving insolvency: Management of debtor's assets index (0-6) (DB15-20 methodology)": "resolving_insolvency.details.management_of_debtor_assets_index",
        "Resolving insolvency: Participation of creditors index (0-4)": "resolving_insolvency.details.creditor_participation_index",
        "Resolving insolvency: Reorganization proceedings index (0-3)": "resolving_insolvency.details.reorganization_proceedings_index",
    }

    country_yearly_data = defaultdict(lambda: defaultdict(lambda: {
        "ease_of_doing_business": {
            "source": "World Bank Doing Business Index"
        }
    }))

    for _, row in df.iterrows():
        country = row["Country Code"]
        series_name = row["Series Name"]
        if series_name not in series_to_json_path:
            continue
        json_path = series_to_json_path[series_name].split(".")
        for year_column in ["2017 [YR2017]", "2018 [YR2018]", "2019 [YR2019]"]:
            year = year_column.split()[0]
            value = row[year_column]
            if pd.isnull(value):
                continue
            current = country_yearly_data[country][year]["ease_of_doing_business"]
            for part in json_path[:-1]:
                current = current.setdefault(part, {})
            try:
                current[json_path[-1]] = float(value)
            except ValueError:
                current[json_path[-1]] = value

    output_dir = Path("data/country_jsons")
    output_dir.mkdir(exist_ok=True)

    for country_code, yearly_data in country_yearly_data.items():
        if country_code not in ALLOWED_COUNTRIES:
            continue  # Skip countries not in the allowed list
        
        file_path = output_dir / f"{country_code}.json"
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        else:
            existing_data = {}

        for year, year_data in yearly_data.items():
            existing_data.setdefault(year, {}).update(year_data)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2)
