import os
import json
import time
import random
from dotenv import load_dotenv
from pymongo import MongoClient
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor, as_completed

# === Environment & API Setup ===

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DB_NAME")]
profiles_col = db["country_profiles"]
reports_col = db["country_reports"]

# === Prompt Templates ===

# Prompt used to analyze a single chunk of structured data and return sector-relevant insights.
CHUNK_PROMPT = """
You are GlobalLaunch AI, a strategic market advisor helping startups assess country-specific expansion opportunities.

Below is a structured chunk of economic, digital, and regulatory data for the country {country_code}, relevant to sectors: {sectors}.

Your task is to extract insights and trend interpretations that rely primarily on **top-level numerical signals**.

Focus on fields with exactly two dots in the key — for example:
- `2023.digital_connectivity.mobile_ownership_percent`
- `2018.ease_of_doing_business.getting_credit.score`
-  using `.details.` or any deeper keys in final output.

However, if **no usable data is found for a category**, you must still write a general but realistic insight based on the country's profile. Stay sector-relevant and strategic even without numbers.

Return your output as strict minified JSON. Do **not** use markdown, do **not** prefix with ```json, and do **not** format it as YAML or list-based text. Just valid machine-parseable JSON.
Your output must start with `{{` and contain only these five keys:
- "business_environment"
- "infrastructure_and_digital"
- "economic_and_trade_outlook"
- "regulatory_and_risk"
- "entry_considerations"

Each value must be a list of 1–3 short strings. Example:
{{
  "business_environment": ["GDP rose 3.2% in 2023...", "..."],
  "infrastructure_and_digital": ["4G coverage reached 91%...", "..."],
  "economic_and_trade_outlook": ["FDI inflows increased..."],
  "regulatory_and_risk": ["Ease of Doing Business score at 72.5..."],
  "entry_considerations": ["Microfinance sector expanding...", "..."]
}}

---

{chunk_data}
"""

# Prompt to synthesize all insights into a final startup-friendly report.
FINAL_REPORT_PROMPT = """
You are GlobalLaunch AI, helping a startup founder evaluate expansion into {country_code}.

Startup: {startup_desc}
Sectors: {sectors}

Below are the categorized insights extracted from national statistics:

{insights}

Using these, generate a **founder-facing**, clear, and data-supported report. Structure it as:
{{
  "executive_summary": "...",

  "business_environment": ["...", "..."],
  "infrastructure_and_digital": ["...", "..."],
  "economic_and_trade_outlook": ["...", "..."],
  "regulatory_and_risk": ["...", "..."],

  "entry_considerations": {{
    "market_opportunity_signals": ["...", "..."],
    "sector_specific_notes": ["...", "..."],
    "go_to_market_advice": ["...", "..."]
  }}
}}

Be concise and use numbers for every insight when available.
If no relevant numeric fields exist for a category, synthesize a general insight based on your understanding of the country's environment.
Emphasize percentage shifts, scores, and changes across years.
"""

# === Utility Functions ===

def safe_generate(prompt, max_retries=5):
    """Robust Gemini API wrapper with retries and exponential backoff."""
    for attempt in range(max_retries):
        try:
            return model.generate_content(prompt).text.strip()
        except Exception as e:
            wait = (2 ** attempt) + random.uniform(0.5, 3)
            print(f"Gemini error: {e} — retrying in {wait:.1f}s...")
            time.sleep(wait)
    raise RuntimeError("Gemini failed after max retries.")

def parse_gemini_json(text):
    """Clean and parse a JSON-like string response from Gemini."""
    try:
        text = text.strip().strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
        if not text.startswith("{"):
            text = "{" + text
        if not text.endswith("}"):
            text += "}"

        parsed = json.loads(text)

        # Ensure required keys are present
        required_keys = [
            "business_environment",
            "infrastructure_and_digital",
            "economic_and_trade_outlook",
            "regulatory_and_risk",
            "entry_considerations",
        ]
        for key in required_keys:
            if key not in parsed:
                raise ValueError(f"Missing key: {key}")

        return parsed

    except Exception as e:
        print("Failed to parse Gemini JSON:")
        print(text[:500])
        raise RuntimeError(f"JSONParseError: {e}")

def process_chunk(chunk_data, country_code, sectors):
    """Generate insights for a single chunk of profile data."""
    try:
        trimmed_data = json.dumps(chunk_data)[:11000]  # Truncate oversized chunks
        prompt = CHUNK_PROMPT.format(
            country_code=country_code,
            sectors=", ".join(sectors),
            chunk_data=trimmed_data
        )
        response = safe_generate(prompt)

        if response.startswith("```json"):
            response = response.strip("` \n")[len("json"):].strip()

        return json.loads(response)

    except Exception as e:
        print(f"Chunk error: {e}")
        return None

def merge_structured_insights(insights):
    """Merge multiple chunk-level insights into a unified structure."""
    merged = {
        "business_environment": [],
        "infrastructure_and_digital": [],
        "economic_and_trade_outlook": [],
        "regulatory_and_risk": [],
        "entry_considerations": []
    }
    for insight in insights:
        for key in merged:
            merged[key].extend(insight.get(key, []))
    return merged

# === Main Pipeline Function ===

def generate_final_reports(startup_desc: str, shortlist: list):
    """
    For each country in the shortlist:
    - Load chunked profile data
    - Generate insights from chunks
    - Merge and summarize into a final report
    - Store in MongoDB
    """
    for item in shortlist:
        country_code = item["country_code"]
        sectors = item["matched_sectors"]

        # Check cache to avoid reprocessing
        cached = reports_col.find_one({
            "country_code": country_code,
            "matched_sectors": {"$all": sectors},
            "report_generated": True
        })
        if cached:
            print(f"Skipping (cached): {country_code}")
            continue

        # Load chunked profile data for the country
        chunks = list(profiles_col.find({"country_code": country_code}))
        if not chunks:
            print(f"Skipping {country_code} — no profile chunks found.")
            continue

        # Run chunk processing in parallel using threads
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(
                    process_chunk,
                    chunk.get("chunk_data", {}),
                    country_code,
                    sectors
                )
                for chunk in chunks
            ]
            all_insights = [r for r in (f.result() for f in as_completed(futures)) if r]

        try:
            # Combine chunk-level insights
            merged = merge_structured_insights(all_insights)
            final_insights = json.dumps(merged, indent=2)

            # Format final prompt for Gemini
            final_prompt = FINAL_REPORT_PROMPT.format(
                country_code=country_code,
                sectors=", ".join(sectors),
                insights=final_insights,
                startup_desc=startup_desc
            )

            response = safe_generate(final_prompt)

            if response.startswith("```json"):
                response = response.strip("` ").split("\n", 1)[1].strip()

            # Parse and store the final report in MongoDB
            parsed = parse_gemini_json(response)
            reports_col.update_one(
                {"country_code": country_code},
                {"$set": {
                    "country_code": country_code,
                    "matched_sectors": sectors,
                    "startup_desc": startup_desc,
                    "report_generated": True,
                    **parsed
                }},
                upsert=True
            )
            print(f"Report saved: {country_code}")

        except Exception as e:
            print(f"Failed {country_code} — {e}")



