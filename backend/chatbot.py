import os
import time
import random
from dotenv import load_dotenv
from pymongo import MongoClient
import google.generativeai as genai

# === Setup === 

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API with the provided key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the Gemini model
model = genai.GenerativeModel("gemini-1.5-pro")

# Set up MongoDB client and reference to country reports collection
client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DB_NAME")]
reports_col = db["country_reports"]

# === Chat Prompt Template ===

# Template for constructing the AI prompt based on user input and available country reports
CHAT_PROMPT_TEMPLATE = """
You are GlobalLaunch AI — a strategic advisor helping startup founders expand into global markets.

The user has already received a ranked list of top countries for expansion, along with detailed AI-generated reports for each.

Now they have a follow-up question. Use the following logic:
1. If the question can be answered using the provided reports, do so directly and clearly.
2. If it's about a top-listed country but info is missing, say "this is beyond the scope of the reports" and offer general, safe advice.
3. If it's about a country not in the list, say so explicitly and respond generally based on LLM knowledge.

Your inputs are structured, not prose — refer to actual indicators and signals when forming your reply. Keep your tone strategic and grounded in data.
Your answers should be crisp, clear and concise. The user wouldn't want to see very long answers from you.

--- USER QUESTION ---
{user_question}

--- TOP COUNTRY REPORTS (SUMMARIZED) ---
{formatted_reports}

Respond intelligently below:
"""

# === Report Formatter (new schema)

# Converts a report document into a concise, structured summary for the prompt
def format_report_for_prompt(report):
    return f"""
🔹 {report['country_code']}:
- Executive Summary: {report.get('executive_summary', '')[:300]}
- Business Environment: {" | ".join(report.get('business_environment', [])[:2])}
- Infrastructure & Digital: {" | ".join(report.get('infrastructure_and_digital', [])[:2])}
- Economic & Trade Outlook: {" | ".join(report.get('economic_and_trade_outlook', [])[:2])}
- Regulatory & Risk: {" | ".join(report.get('regulatory_and_risk', [])[:2])}
- Market Signals: {" | ".join(report.get('entry_considerations', {}).get('market_opportunity_signals', [])[:2])}
- GTM Advice: {" | ".join(report.get('entry_considerations', {}).get('go_to_market_advice', [])[:2])}
""".strip()

# === Gemini-safe wrapper

# Handles transient API failures using exponential backoff
def safe_generate(prompt, max_retries=5):
    for attempt in range(max_retries):
        try:
            return model.generate_content(prompt).text.strip()
        except Exception as e:
            wait_time = (2 ** attempt) + random.uniform(0.5, 3)
            print(f"Gemini error: {e} — retrying in {wait_time:.1f}s...")
            time.sleep(wait_time)
    raise RuntimeError("Gemini failed after max retries.")

# === Main Chat Handler

# Generates a Gemini-based answer using the top countries and user question
def generate_answer(question: str, top_countries: list) -> str:
    # Fetch reports only for the specified top countries
    reports_cursor = reports_col.find(
        {"country_code": {"$in": top_countries}},
        {"_id": 0}
    )
    reports = list(reports_cursor)

    # Determine which reports were found and which were missing
    available_codes = {r["country_code"] for r in reports}
    missing = [code for code in top_countries if code not in available_codes]

    # Handle cases with no or incomplete report data
    if len(reports) == 0:
        return "Sorry, my scope here is limited — I couldn't retrieve the reports for your top countries."
    elif missing:
        return f"Some country reports were missing ({', '.join(missing)}), so I may not be able to fully answer your question."

    # Format the reports into a readable block for the prompt
    formatted_reports = "\n\n".join(
        format_report_for_prompt(r) for r in reports
    )

    # Fill in the prompt template with user input and report data
    prompt = CHAT_PROMPT_TEMPLATE.format(
        user_question=question.strip(),
        formatted_reports=formatted_reports
    )

    print("🔍 Sending prompt to Gemini...")
    return safe_generate(prompt)
