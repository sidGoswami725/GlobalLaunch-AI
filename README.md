# 🌍 GlobalLaunch AI  
**Your AI Co-Pilot for International Startup Expansion**

GlobalLaunch AI is an AI-powered platform that helps startups gain new perspectives on global expansion using public economic and regulatory data. By combining MongoDB's advanced vector search with Google's Gemini and Vertex AI, it transforms raw country indicators into strategic insights — letting users explore where and how to grow globally.

Whether you're building a cross-border SaaS or a cleantech company exploring incentives, this platform offers clarity, explainability, and speed — all wrapped in a modern UX.

---

## 📊 Public Dataset Used

We used country-level economic, regulatory, and digital development indicators — including:

- FDI inflows
- Corruption Index
- Ease of Starting a Business
- Digital Infrastructure Index
- Trade Incentives & Policy Snapshots

These were cleaned, parsed, and embedded using Google Vertex AI, then stored in MongoDB Atlas with vector search indexing.

---

## ✨ Features & Insights Unlocked

- 📄 **Idea Input via Text or PDF**  
  Upload a startup idea or pitch deck and extract insights instantly.

- 🔍 **Smart Sector Detection**  
  Uses Gemini to classify ideas into top 3 sectors (e.g., Fintech, AI-ML, Healthtech).

- 🌐 **Top Country Shortlisting**  
  Combines semantic embeddings + key indicators (FDI, corruption index, digital readiness) to rank best-fit countries.

- 📊 **AI-Generated Country Reports**  
  Each shortlisted country includes a 6-part report covering market opportunity, regulatory climate, risks, incentives, strategy, and localization.

- 💬 **Interactive Chatbot**  
  Ask custom questions like “What are Estonia’s licensing laws?” or “Compare Germany and Brazil.” Powered by Gemini + real-time RAG.

- ⚡ **Semantic Embeddings**  
  Each country-sector profile is embedded using Vertex AI for fast, accurate vector search.

---

## 🛠 Tech Stack

- **Backend**: Python, Flask, MongoDB Atlas (Vector Search)
- **AI Models**: Google Gemini 1.5 Pro (generation + embeddings), Vertex AI
- **Frontend**: HTML, TailwindCSS, JavaScript
- **PDF Parsing**: PyMuPDF
- **Deployment**: Local Flask / Render-ready / Docker-compatible

---

## 📦 Project Structure

```
GlobalLaunchAI/
├── backend/
│   ├── app.py                      # Main Flask API
│   ├── chatbot.py                  # RAG-style chatbot using Gemini
│   ├── fallback_sector_detection.py
│   ├── get_final_shortlist.py      # Semantic scoring + ranking logic
│   ├── generate_country_reports.py # Full report generation
│   ├── embed_sector_profiles.py    # Embeds all sector summaries
│   ├── pdf_reader.py               # PDF to text + sector detection
│   └── generate_semantics_from_chunks.py
├── frontend/
│   ├── index.html                  # Startup idea + report viewer
│   ├── report.html                 # Detailed report UI
│   ├── script.js                   # Client-side logic
│   └── styles.css
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Arshbir1/GlobalLaunchAI.git
cd GlobalLaunchAI
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the root directory with:

```
MONGODB_URI=your_mongo_uri
DB_NAME=global_launch
GOOGLE_API_KEY=your_gemini_key
GOOGLE_MAIN_API_KEY=your_secondary_key
PROJECT_ID=your_gcp_project_id
SERVICE_ACCOUNT_PATH=service-account.json
SEMANTIC_EMBEDDING=embedding_field
SEMANTIC_IDX=vector_index_name
```

### 4. Run the Flask Server

```bash
python app.py
```

Access the app at [http://localhost:8000](http://localhost:8000)

---

## 🤝 Contribute & Support

- **GitHub**: [GlobalLaunchAI Repo](https://github.com/Arshbir1/GlobalLaunchAI)
- **Issues**: Bug reports and feature requests welcome!
- **Contact**: Reach out via Discussions or Email

---

## 🏆 MongoDB Hackathon Submission

This project was developed for the **AI in Action 2025** under the MongoDB challenge — showing how AI and MongoDB vector search can help users explore real-world country data from a strategic business lens.

---

## 🙏 Thank You

Thanks for exploring GlobalLaunch AI — your global startup advisor, reimagined.
