# Final get_shortlist with Intelligent Heuristics + Caps + Boosting Logic

import os
import math
from dotenv import load_dotenv
from pymongo import MongoClient
from fallback_sector_detection import detect_sectors
import vertexai
from vertexai.preview.language_models import TextEmbeddingModel
from google.oauth2 import service_account

# === Setup: Load environment variables and initialize services ===
load_dotenv()

# Load Google Cloud credentials
credentials = service_account.Credentials.from_service_account_file(os.getenv("GOOGLE_CLOUD_CREDENTIALS"))

# Initialize Vertex AI with credentials and project settings
vertexai.init(
    project=os.getenv("PROJECT_ID"),
    location="us-central1",
    credentials=credentials
)

# Load embedding model
embedding_model = TextEmbeddingModel.from_pretrained("gemini-embedding-001")

# Connect to MongoDB
client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DB_NAME")]
semantics_col = db["country_semantics"]
profiles_col = db["country_profiles"]

# Embedding and index paths for vector search
PATH_NAME = os.getenv("SEMANTIC_EMBEDDING")
INDEX_NAME = os.getenv("SEMANTIC_IDX")

# Weights for each scoring dimension
WEIGHTS = {
    "vector": 0.4,
    "eodb": 0.15,
    "macro": 0.08,        # Slightly dampened macro
    "digital": 0.17,      # Slightly boosted digital
    "trade": 0.08,        # Slightly capped trade
    "fdi": 0.12           # Slightly dampened FDI
}

# === Embedding function: converts user query into embedding ===
def embed_query(text):
    return embedding_model.get_embeddings([text])[0].values

# === Vector Search: searches semantic collection using query embedding and sector ===
def vector_search_country_semantics(query_embedding, sector, top_k=200):
    return list(semantics_col.aggregate([
        {"$vectorSearch": {
            "index": INDEX_NAME,
            "path": PATH_NAME,
            "queryVector": query_embedding,
            "numCandidates": 500,
            "limit": top_k
        }},
        {"$match": {"sector": {"$regex": f"^{sector}$", "$options": "i"}}},
        {"$project": {
            "_id": 0,
            "country_code": 1,
            "score": {"$meta": "vectorSearchScore"}
        }}
    ]))

# === Field Utilities ===

# Extract latest value for a field that ends with the given suffix
def get_latest_field(data, suffix):
    values = [(k, v) for k, v in data.items() if k.endswith(suffix) and isinstance(v, (int, float))]
    if not values:
        return None
    return sorted(values, key=lambda x: x[0], reverse=True)[0][1]

# Flatten all chunks for a country into a single dict
def get_country_profile_flat(country_code):
    flat = {}
    for chunk in profiles_col.find({"country_code": country_code}):
        flat.update(chunk.get("chunk_data", {}))
    return flat

# Normalize a value to 0-1 range (optionally invert it)
def safe_norm(val, max_val=100, invert=False):
    if val is None:
        return 0.0
    norm = min(val / max_val, 1.0)
    return 1.0 - norm if invert else norm

# Apply log scaling to reduce skew of large values
def log_scale(val):
    return math.log(val + 1) / 10 if val and val > 0 else 0.0

# === Scoring Function: Compute a final score using all indicators ===
def compute_score(vec_score, flat, country_code=None):
    valid_fields = 0
    total_fields = 0

    # Local utility to normalize and track field coverage
    def norm_and_count(field, invert=False, max_val=100):
        nonlocal valid_fields, total_fields
        total_fields += 1
        val = get_latest_field(flat, field)
        if val is not None:
            valid_fields += 1
        return safe_norm(val, max_val=max_val, invert=invert)

    # EODB (Ease of Doing Business) sub-scores
    eodb_fields = [
        "ease_of_doing_business.starting_business_score",
        "ease_of_doing_business.getting_electricity.score",
        "ease_of_doing_business.registering_property.score",
        "ease_of_doing_business.getting_credit.score",
        "ease_of_doing_business.protecting_minority_investors.score",
        "ease_of_doing_business.paying_taxes.score",
        "ease_of_doing_business.trading_across_borders.score",
        "ease_of_doing_business.enforcing_contracts.score",
        "ease_of_doing_business.resolving_insolvency.score",
        "ease_of_doing_business.overall_score"
    ]
    eodb = sum(norm_and_count(f) for f in eodb_fields) / len(eodb_fields)

    # Macroeconomic indicators
    macro_fields = [
        ("macroeconomic_indicators.gdp_growth_percent", False),
        ("macroeconomic_indicators.inflation_rate_percent", True),
        ("macroeconomic_indicators.unemployment_rate_percent", True),
        ("macroeconomic_indicators.current_account_balance_percent_gdp", False),
        ("macroeconomic_indicators.public_debt_percent_of_gdp", True)
    ]
    macro = sum(norm_and_count(f, invert=inv) for f, inv in macro_fields) / len(macro_fields)

    # Digital infrastructure and readiness indicators
    digital_fields = [
        ("digital_connectivity.gsma_connectivity_index", False),
        ("digital_connectivity.mobile_broadband_coverage_percent", False),
        ("digital_connectivity.mobile_ownership_percent", False),
        ("connectivity.affordability.device_affordability_40pct_usd", True),
        ("connectivity.affordability.tax_mobile_data_percent", True),
        ("connectivity.affordability.tax_handsets_percent", True),
        ("connectivity.affordability.sector_specific_taxes_percent", True),
        ("connectivity.consumer_readiness.literacy_percent", False),
        ("connectivity.content_and_services.e_government_score", False),
        ("connectivity.content_and_services.social_media_penetration_percent", False),
        ("connectivity.online_security.cybersecurity_index_score", False)
    ]
    digital = sum(norm_and_count(f, invert=inv) for f, inv in digital_fields) / len(digital_fields)

    # Trade indicators (capped to 0.8 to avoid overboosting)
    trade_fields = [
        ("trade_profile.average_applied_tariff_percent", True),
        ("trade_profile.binding_tariff_coverage_percent", False),
        ("trade_profile.import_duties_on_capital_goods_percent", True),
        ("trade_profile.import_duties_on_intermediate_goods_percent", True),
        ("trade_profile.duty_free_import_share_percent", False)
    ]
    trade_raw = sum(norm_and_count(f, invert=inv) for f, inv in trade_fields) / len(trade_fields)
    trade = min(trade_raw, 0.8)

    # FDI indicators (log-scaled)
    fdi_vals = [
        get_latest_field(flat, "foreign_direct_investment.fdi_net_inflows_usd_millions"),
        get_latest_field(flat, "foreign_direct_investment.fdi_inward_stock_usd_millions")
    ]
    total_fields += len(fdi_vals)
    fdi_non_null = [v for v in fdi_vals if v is not None]
    valid_fields += len(fdi_non_null)
    fdi = sum(log_scale(v) for v in fdi_non_null) / len(fdi_vals) if fdi_vals else 0.0

    # Data coverage adjustment (boost for countries with more complete data)
    coverage = valid_fields / total_fields if total_fields > 0 else 1.0
    coverage_adjust = 0.5 + 0.5 * coverage

    # Final weighted score
    final_score = (
        vec_score * WEIGHTS["vector"] +
        eodb * WEIGHTS["eodb"] +
        macro * WEIGHTS["macro"] +
        digital * WEIGHTS["digital"] +
        trade * WEIGHTS["trade"] +
        fdi * WEIGHTS["fdi"]
    ) * coverage_adjust

    # Additional micro-boost for AI/digital/FDI-heavy performers (e.g. India)
    if vec_score > 0.8 and digital > 0.6 and fdi > 1.1:
        final_score += 0.01

    return round(final_score, 4)

# === Final Shortlist ===
def get_shortlist(user_input, top_n=5):
    # Detect relevant sectors from user input
    sectors = detect_sectors(user_input)

    # Generate embedding from user query
    query_vector = embed_query(user_input)

    print(f"🔎 Detected sectors: {sectors}")

    scored = {}

    # Iterate through all detected sectors and score each country
    for sector in sectors:
        for doc in vector_search_country_semantics(query_vector, sector):
            code = doc["country_code"]
            vec = doc["score"]
            if code not in scored:
                flat = get_country_profile_flat(code)
                final_score = compute_score(vec, flat, country_code=code)
                scored[code] = {
                    "aggregate_score": final_score,
                    "matched_sectors": set([sector])
                }
            else:
                scored[code]["matched_sectors"].add(sector)

    # Sort by score and return top N results
    result = [
        {
            "country_code": k,
            "aggregate_score": v["aggregate_score"],
            "matched_sectors": list(v["matched_sectors"])
        }
        for k, v in sorted(scored.items(), key=lambda x: -x[1]["aggregate_score"])
    ]
    return result[:top_n]

# === CLI Test ===
if __name__ == "__main__":
    user_input = "Property valuation API using public land records and AI"
    top = get_shortlist(user_input, top_n=5)

    print("\n🏁 Top Countries:")
    for item in top:
        print(f"{item['country_code']} → {item['aggregate_score']} via {item['matched_sectors']}")
