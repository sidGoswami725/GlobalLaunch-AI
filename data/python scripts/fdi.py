import pandas as pd
import json
from pathlib import Path
from collections import defaultdict
import pycountry
from utils import ALLOWED_COUNTRIES
import os

def process_foreign_direct_investment():
    annex_tables = {
        '01': {'field': 'fdi_net_inflows_usd_millions', 'description': 'FDI inflows'},
        '03': {'field': 'fdi_inward_stock_usd_millions', 'description': 'FDI inward stock'},
        '06': {'field': 'cross_border_m_and_a.total_value_usd_millions', 'description': 'Net cross-border M&A purchases'},
        '10': {'field': 'cross_border_m_and_a.top_sectors_by_value', 'description': 'Net cross-border M&A purchases by sector'},
        '14': {'field': 'greenfield_fdi.value_usd_millions', 'description': 'Greenfield FDI projects value'},
        '15': {'field': 'greenfield_fdi.top_sectors_by_value', 'description': 'Greenfield FDI value by sector'},
        '17': {'field': 'greenfield_fdi.number_of_projects', 'description': 'Greenfield FDI project count'},
        '18': {'field': 'greenfield_fdi.top_sectors_by_project_count', 'description': 'Greenfield FDI project count by sector'}
    }

    years = ['2023', '2022', '2021']
    csv_path = Path('data/datasets/FDI')
    json_path = Path('data/country_jsons')
    json_path.mkdir(exist_ok=True)

    excluded_prefixes = ['Memorandum', 'Oceania', 'Europe', 'World', 'Develop', 'European']

    def read_table(table_number):
        file_path = csv_path / f'WIR2024_tab{table_number}.csv'
        try:
            df = pd.read_csv(file_path, skiprows=2)
            df.columns = [str(col).strip() for col in df.columns]
            return df
        except:
            return None

    def get_scalar_data(df, year):
        df = df.set_index(df.columns[0])
        if year not in df.columns:
            return {}
        data = {}
        for country, val in df[year].items():
            if pd.isna(val) or str(val).strip() == "-":
                data[country] = None
            else:
                cleaned = str(val).replace(" ", "").strip()
                try:
                    data[country] = float(cleaned)
                except ValueError:
                    data[country] = cleaned
        return data

    def get_sector_data(df, year):
        sector_data = defaultdict(list)
        for _, row in df.iterrows():
            country = row.iloc[0]
            sector = (
                row.get('Sector')
                or row.get('Sectors')
                or row.get('Industry')
                or row.get('Sector name')
                or row.get('Unnamed: 1')
            )
            value = row.get(year)
            if pd.notna(country) and pd.notna(sector) and pd.notna(value):
                val_str = str(value).replace(" ", "").strip()
                try:
                    cleaned_value = float(val_str)
                    sector_data[country].append((sector, cleaned_value))
                except ValueError:
                    continue
        return {
            country: [s for s, _ in sorted(sectors, key=lambda x: -x[1])[:3]]
            for country, sectors in sector_data.items()
        }

    def country_to_iso3(name):
        try:
            return pycountry.countries.lookup(name).alpha_3
        except LookupError:
            return None

    data_by_year = {year: {} for year in years}
    for table_num in annex_tables:
        df = read_table(table_num)
        if df is None:
            continue
        for year in years:
            if table_num in ['10', '15', '18']:
                data_by_year[year][table_num] = get_sector_data(df, year)
            else:
                data_by_year[year][table_num] = get_scalar_data(df, year)

    all_countries = set()
    for year in years:
        all_countries.update(data_by_year[year].get('01', {}).keys())

    for country in all_countries:
        if not isinstance(country, str):
            continue
        if any(country.startswith(prefix) for prefix in excluded_prefixes):
            continue

        iso_code = country_to_iso3(country)
        if not iso_code or iso_code not in ALLOWED_COUNTRIES:
            continue

        json_file = json_path / f"{iso_code}.json"
        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        else:
            existing_data = {}

        for year in years:
            fdi_entry = {
                "fdi_net_inflows_usd_millions": data_by_year[year].get('01', {}).get(country),
                "fdi_inward_stock_usd_millions": data_by_year[year].get('03', {}).get(country),
                "greenfield_fdi": {
                    "value_usd_millions": data_by_year[year].get('14', {}).get(country),
                    "number_of_projects": data_by_year[year].get('17', {}).get(country),
                },
                "cross_border_m_and_a": {
                    "total_value_usd_millions": data_by_year[year].get('06', {}).get(country),
                }
            }

            existing_data.setdefault(year, {})["foreign_direct_investment"] = fdi_entry

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2)
