import os
import hashlib
from flask import Flask, request, jsonify, send_from_directory, abort, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from pymongo import MongoClient
from io import BytesIO

# Local module imports for various pipeline steps
from fallback_sector_detection import detect_sectors
from pdf_reader import detect_sectors_from_pdf
from get_final_shortlist import get_shortlist
from generate_country_reports import generate_final_reports
from chatbot import generate_answer
from plot_graphs import generate_country_graphs

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app, resources={r"/*": {"origins": ["*"]}})  # Allow all origins (update in production)

# Set up MongoDB client and collection references
client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DB_NAME")]
report_col = db["country_reports"]
graph_col = db["country_graphs"]

# Set up upload folder
UPLOAD_FOLDER = "./Uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file types for upload
ALLOWED_EXTENSIONS = {"pdf"}

# Check if uploaded file is a PDF
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Generate session ID using hash of input text
def generate_session_id(text):
    return hashlib.sha256(text.encode()).hexdigest()[:12]

# Serve frontend landing page
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

# Handle PDF uploads and extract sectors
@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    file = request.files.get("file")
    if file is None or not allowed_file(file.filename):
        abort(400, "Invalid or missing PDF file")

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    sectors, extracted_text = detect_sectors_from_pdf(filepath)
    os.remove(filepath)  # Remove file after processing

    session_id = generate_session_id(extracted_text)
    return jsonify({"text": extracted_text, "sectors": sectors, "session_id": session_id})

# Handle text input submission
@app.route("/submit_text", methods=["POST"])
def submit_text():
    idea = request.form.get("text", "").strip()
    if not idea:
        abort(400, "Business idea text is required")

    sectors = detect_sectors(idea)
    session_id = generate_session_id(idea)
    return jsonify({"text": idea, "sectors": sectors, "session_id": session_id})

# Run the full country analysis pipeline
@app.route("/run_pipeline", methods=["POST"])
def run_pipeline():
    idea = request.form.get("idea", "").strip()
    print("/run_pipeline received idea:", idea)
    if not idea:
        print("Missing idea input")
        abort(400, "Business idea is required")

    session_id = generate_session_id(idea)
    final_top = get_shortlist(idea, top_n=5)
    final_codes = [c["country_code"] for c in final_top]

    generate_final_reports(idea, final_top)

    # Generate and store graphs for shortlisted countries
    graph_col = db["country_graphs"]
    profiles_col = db["country_profiles"]
    for code in final_codes:
        generate_country_graphs(code, profiles_col, graph_col)

    return jsonify({"top_countries": final_codes})

# Fetch all stored country reports
@app.route("/get_reports", methods=["GET"])
def get_reports():
    reports = list(report_col.find({}, {"_id": 0}))
    return jsonify(reports)

# Fetch a specific country graph based on country code and category
@app.route("/get_graph/<country_code>/<category>")
def get_graph(country_code, category):
    graph = db["country_graphs"].find_one({"country_code": country_code, "category": category})
    if not graph:
        abort(404, "Graph not found")
    return send_file(BytesIO(graph["image"]), mimetype="image/png")

# Handle chatbot queries
@app.route("/chat", methods=["POST"])
def chat_with_bot():
    question = request.form.get("question")
    top_countries = request.form.getlist("top_countries")

    print("Chatbot received question:", question)
    print("Top countries list:", top_countries)

    if not question:
        abort(400, "Question required")

    response = generate_answer(question, top_countries)
    return jsonify({"response": response})

# Reset the session (clears country reports)
@app.route("/reset", methods=["POST"])
def reset_session():
    deleted = report_col.delete_many({})
    return jsonify({"status": "reset", "deleted_count": deleted.deleted_count})

# Serve static files from the frontend
@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# Run the app on specified port
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)), debug=False)
