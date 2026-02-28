# AI Resume Screening System 🤖

An **AI-powered HR Resume Screening System** that automatically analyzes resumes and matches them against job descriptions using NLP.

## 🚀 Features

- 📤 Upload resumes (PDF, DOCX, TXT)
- 🧠 NLP-based scoring using TF-IDF cosine similarity + skill matching
- 📊 Match score 0–100% with auto-labeling (Shortlist / Review / Reject)
- 💼 HR Dashboard — manage jobs & candidates
- 🎨 Premium dark glassmorphism UI

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3 (Glassmorphism) |
| Backend | Python 3, Flask |
| Database | SQLite (Flask-SQLAlchemy) |
| AI / NLP | scikit-learn (TF-IDF), NLTK |
| File Parsing | pdfminer.six, python-docx |

## 📦 Installation

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/ResumeScreener.git
cd ResumeScreener

# 2. Install dependencies
pip install Flask Flask-SQLAlchemy scikit-learn nltk pdfminer.six python-docx

# 3. Run the app
python app.py

# 4. Open in browser
# → http://127.0.0.1:5000
```

## 🧠 How It Works

```
Resume Upload → Text Extraction → Preprocess → TF-IDF Scoring → Match Score → Label
```

**Scoring Formula:**
```
Score = (0.6 × TF-IDF Cosine Similarity + 0.4 × Skill Keyword Match) × 100
```

## 📸 Pages

| Page | Description |
|---|---|
| `/` | Home — Stats & Recent Screenings |
| `/dashboard` | HR Dashboard — Job cards & Candidates |
| `/upload` | Resume Upload with drag & drop |
| `/result/<id>` | Score gauge + Skill breakdown |
| `/candidates` | Filter & manage all candidates |

## 📁 Project Structure

```
ResumeScreener/
├── app.py              # Flask routes
├── models.py           # SQLAlchemy DB models
├── nlp_engine.py       # NLP scoring engine
├── requirements.txt
├── static/
│   ├── css/style.css   # Dark theme CSS
│   └── js/main.js
└── templates/          # Jinja2 HTML templates
```

---
Built with ❤️ by Pooja
