# main.py
from business import process_ease_of_doing_business
from regulatory import process_regulatory_indicators
from trade import process_trade_profile
from fdi import process_foreign_direct_investment
from corruption import process_corruption_perceptions
from connectivity import process_digital_connectivity
from macro import process_macroeconomic_indicators


def main():
    process_ease_of_doing_business()
    process_regulatory_indicators()
    process_trade_profile()
    process_foreign_direct_investment()
    process_corruption_perceptions()
    process_digital_connectivity()
    process_macroeconomic_indicators()
    
    # The OG JSON files are made inside country_jsons


if __name__ == "__main__":
    main()
