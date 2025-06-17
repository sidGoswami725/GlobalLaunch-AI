import os
import google.generativeai as genai
from dotenv import load_dotenv

# === Setup === 

# Load environment variables (e.g., Google API key)
load_dotenv()

# Configure Gemini with your API key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# List of predefined business sectors to classify into
SECTORS = [
    "fintech", "healthtech", "edtech", "ecommerce", "cleantech",
    "logistics", "SaaS", "cybersecurity", "AI-ML", "retail",
    "agritech", "mobility", "proptech", "govtech", "biotech"
]

# === Sector Detection Function ===

def detect_sectors(user_input, max_results=3):
    """
    Classifies a user's business idea into up to `max_results` relevant sectors.
    Uses a Gemini model prompt and returns a list of sector strings.
    """
    # Construct prompt for the Gemini model
    prompt = f"""
You are a startup classification assistant. Your job is to classify a given business idea into at most {max_results} relevant sectors from this fixed list:

{", ".join(SECTORS)}

Business idea:
\"\"\"{user_input.strip()}\"\"\"

Respond ONLY with a valid Python list of up to {max_results} matching sector names. Do not explain or add anything else.
Example format: ["SaaS", "AI-ML"]. Note: You don't always have to pick 3 sectors, always choose according to relevance.
"""

    # Initialize the Gemini model
    model = genai.GenerativeModel("gemini-1.5-pro")

    # Get the response from Gemini
    response = model.generate_content(prompt)

    try:
        # Try to parse the model's output into a Python list
        result = eval(response.text.strip())

        # Validate and filter results to only include allowed sectors
        valid = [s for s in result if s in SECTORS]
        return valid[:max_results] if valid else ["general"]

    except Exception:
        # Fallback in case parsing or validation fails
        print("⚠️ Failed to parse Gemini response. Falling back to ['general'].")
        return ["general"]
