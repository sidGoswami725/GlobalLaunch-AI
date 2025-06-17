# chunks.py
# Extracts and saves 3 RAG-friendly chunks per country-year

import os
import json
from pathlib import Path

# === CONFIG ===
INPUT_DIR = Path("data/flat_country_jsons")
CHUNK_OUTPUT_DIR = Path("data/chunked_country_jsons")
CHUNK_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MAX_CHARS = 11000

CHUNK_KEYS = {
    "chunk1_market_opportunity": [
        # FDI breakdown
        "foreign_direct_investment.fdi_net_inflows_usd_millions",
        "foreign_direct_investment.fdi_inward_stock_usd_millions",
        "foreign_direct_investment.greenfield_fdi.value_usd_millions",
        "foreign_direct_investment.greenfield_fdi.number_of_projects",
        "foreign_direct_investment.cross_border_m_and_a.total_value_usd_millions",

        # Connectivity: Index-level
        "digital_connectivity.gsma_connectivity_index",
        "digital_connectivity.mobile_broadband_coverage_percent",
        "digital_connectivity.mobile_ownership_percent",

        # Infrastructure
        "digital_connectivity.connectivity.infrastructure.2g_population_coverage_percent",
        "digital_connectivity.connectivity.infrastructure.3g_population_coverage_percent",
        "digital_connectivity.connectivity.infrastructure.4g_population_coverage_percent",
        "digital_connectivity.connectivity.infrastructure.5g_population_coverage_percent",
        "digital_connectivity.connectivity.infrastructure.download_speed_mbps",
        "digital_connectivity.connectivity.infrastructure.upload_speed_mbps",
        "digital_connectivity.connectivity.infrastructure.latency_ms",
        "digital_connectivity.connectivity.infrastructure.spectrum.below_1ghz_mhz",
        "digital_connectivity.connectivity.infrastructure.spectrum.between_1_3ghz_mhz",
        "digital_connectivity.connectivity.infrastructure.spectrum.between_3_6ghz_mhz",
        "digital_connectivity.connectivity.infrastructure.spectrum.mmwave_mhz",

        # Affordability
        "digital_connectivity.connectivity.affordability.entry_basket_1gb_usd",
        "digital_connectivity.connectivity.affordability.higher_basket_5gb_usd",
        "digital_connectivity.connectivity.affordability.entry_40pct_1gb_usd",
        "digital_connectivity.connectivity.affordability.higher_40pct_5gb_usd",
        "digital_connectivity.connectivity.affordability.device_affordability_usd",
        "digital_connectivity.connectivity.affordability.device_affordability_40pct_usd",
        "digital_connectivity.connectivity.affordability.tax_mobile_data_percent",
        "digital_connectivity.connectivity.affordability.tax_handsets_percent",
        "digital_connectivity.connectivity.affordability.sector_specific_taxes_percent",

        # Consumer readiness
        "digital_connectivity.connectivity.consumer_readiness.literacy_percent",
        "digital_connectivity.connectivity.consumer_readiness.school_life_expectancy_years",
        "digital_connectivity.connectivity.consumer_readiness.gender_gap_mobile_ownership_percent",
        "digital_connectivity.connectivity.consumer_readiness.gender_gap_mobile_internet_percent",

        # Content & services
        "digital_connectivity.connectivity.content_and_services.tlds_per_person",
        "digital_connectivity.connectivity.content_and_services.e_government_score",
        "digital_connectivity.connectivity.content_and_services.social_media_penetration_percent",
        "digital_connectivity.connectivity.content_and_services.local_apps_per_person",
        "digital_connectivity.connectivity.content_and_services.language_support_score",
        "digital_connectivity.connectivity.content_and_services.top_apps_language_accessibility_score",

        # Online security
        "digital_connectivity.connectivity.online_security.cybersecurity_index_score",

        # Macroeconomic context
        "macroeconomic_indicators.gdp_current_usd_billions",
        "macroeconomic_indicators.gdp_growth_percent",
        "macroeconomic_indicators.inflation_rate_percent",
        "macroeconomic_indicators.unemployment_rate_percent",
        "macroeconomic_indicators.current_account_balance_percent_gdp",
        "macroeconomic_indicators.public_debt_percent_of_gdp",
        "macroeconomic_indicators.interest_rate_percent",
        "macroeconomic_indicators.exchange_rate_vs_usd",

        # Doing business: Business environment
        "ease_of_doing_business.starting_business_score",
        "ease_of_doing_business.getting_credit",
        "ease_of_doing_business.registering_property",
        "ease_of_doing_business.protecting_minority_investors",
        "ease_of_doing_business.dealing_with_construction_permits_details"
    ],

    "chunk2_regulatory_risk": [
        # Regulatory indicators (assumed separate structure)
        "regulatory_indicators.product_market_regulation_score",
        "regulatory_indicators.distortions_by_public_ownership.quality_and_scope_of_public_ownership",
        "regulatory_indicators.distortions_by_public_ownership.governance_of_state_owned_enterprises",
        "regulatory_indicators.involvement_in_business_operations.retail_price_controls_and_regulation",
        "regulatory_indicators.involvement_in_business_operations.involvement_in_network_sectors",
        "regulatory_indicators.involvement_in_business_operations.involvement_in_service_sectors",
        "regulatory_indicators.involvement_in_business_operations.public_procurement",
        "regulatory_indicators.regulations_impact_evaluation.assessment_of_impact_on_competition",
        "regulatory_indicators.regulations_impact_evaluation.interaction_with_stakeholders",
        "regulatory_indicators.barriers_to_domestic_and_foreign_entry.admin_and_regulatory_burden.llc_poe_requirements",
        "regulatory_indicators.barriers_to_domestic_and_foreign_entry.admin_and_regulatory_burden.communication_and_simplification",
        "regulatory_indicators.barriers_to_domestic_and_foreign_entry.barriers_in_service_and_network_sectors.barriers_to_entry_service_sectors",
        "regulatory_indicators.barriers_to_domestic_and_foreign_entry.barriers_in_service_and_network_sectors.barriers_to_entry_network_sectors",
        "regulatory_indicators.barriers_to_domestic_and_foreign_entry.barriers_to_trade_and_investment.barriers_to_foreign_direct_investment",

        # Corruption perceptions: overview
        "corruption_perceptions.overview.cpi_score",
        "corruption_perceptions.overview.cpi_rank",
        "corruption_perceptions.overview.region_average_cpi",
        "corruption_perceptions.overview.region",
        "corruption_perceptions.overview.confidence_interval.lower",
        "corruption_perceptions.overview.confidence_interval.upper",

        # Corruption perceptions: explanatory indicators
        "corruption_perceptions.explanatory_indicators.economist_intelligence_unit_country_rating",
        "corruption_perceptions.explanatory_indicators.s_and_p_country_risk_rating",
        "corruption_perceptions.explanatory_indicators.imd_world_competitiveness",
        "corruption_perceptions.explanatory_indicators.prs_international_country_risk_guide",
        "corruption_perceptions.explanatory_indicators.world_bank_cpia",
        "corruption_perceptions.explanatory_indicators.wef_eos",
        "corruption_perceptions.explanatory_indicators.world_justice_project_rule_of_law_index",

        # Doing business: Legal/regulatory risk aspects
        "ease_of_doing_business.paying_taxes",
        "ease_of_doing_business.enforcing_contracts",
        "ease_of_doing_business.resolving_insolvency"
    ],

    "chunk3_trade_infra": [
        # Trade Profile
        "trade_profile.average_applied_tariff_percent",
        "trade_profile.binding_tariff_coverage_percent",
        "trade_profile.import_duties_on_capital_goods_percent",
        "trade_profile.import_duties_on_intermediate_goods_percent",
        "trade_profile.duty_free_import_share_percent",
        "trade_profile.number_of_distinct_duty_rates",
        "trade_profile.coefficient_of_tariff_variation",
        "trade_profile.major_trade_partners",
        "trade_profile.top_export_value_usd",
        "trade_profile.top_import_value_usd",
        
        "ease_of_doing_business.getting_electricity",
        "ease_of_doing_business.trading_across_borders"
    ]
}


def extract_keys(flat_data, prefix):
    """Extracts keys from flat JSON where prefix appears after year."""
    return {
        k: v for k, v in flat_data.items()
        if f".{prefix}" in k or k.endswith(prefix)
    }



def chunk_thematic_data(flat_data, chunk_def):
    themed_chunks = {}
    for chunk_name, prefixes in chunk_def.items():
        extracted = {}
        for prefix in prefixes:
            extracted.update(extract_keys(flat_data, prefix))

        # Split large chunks into a, b, ... if needed
        total_json = json.dumps(extracted)
        if len(total_json) <= MAX_CHARS:
            themed_chunks[chunk_name] = extracted
        else:
            # Greedy split by number of items
            items = list(extracted.items())
            subchunks = []
            current = {}
            current_len = 0
            for k, v in items:
                entry_len = len(json.dumps({k: v}))
                if current_len + entry_len > MAX_CHARS and current:
                    subchunks.append(current)
                    current = {}
                    current_len = 0
                current[k] = v
                current_len += entry_len
            if current:
                subchunks.append(current)

            # Name subchunks: chunk1a, chunk1b, ...
            base = chunk_name.replace("chunk", "")
            for i, sub in enumerate(subchunks):
                suffix = chr(ord('a') + i)
                new_name = f"chunk{base}{suffix}"
                themed_chunks[new_name] = sub

    return themed_chunks


def process_all_flattened():
    for file in INPUT_DIR.glob("*.json"):
        country_code = file.stem
        with open(file, "r", encoding="utf-8") as f:
            flat_data = json.load(f)

        themed = chunk_thematic_data(flat_data, CHUNK_KEYS)

        for chunk_name, chunk_content in themed.items():
            out_path = CHUNK_OUTPUT_DIR / f"{country_code}_{chunk_name}.json"
            with open(out_path, "w", encoding="utf-8") as out:
                json.dump(chunk_content, out, indent=2)
            print(f"✅ {country_code} → {chunk_name} ({len(json.dumps(chunk_content))} chars)")

if __name__ == "__main__":
    process_all_flattened()