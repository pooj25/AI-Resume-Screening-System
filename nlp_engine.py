"""
NLP Engine — Resume Screening AI
- Extracts text from PDF / DOCX
- Matches skills
- Scores via TF-IDF cosine similarity
"""

import re
import io
import os
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download stopwords silently
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

from nltk.corpus import stopwords

STOPWORDS = set(stopwords.words('english'))

# ────────────────────────────────────────────
# Comprehensive skill keyword list
# ────────────────────────────────────────────
SKILL_KEYWORDS = {
    # Programming Languages
    "python", "java", "javascript", "c++", "c#", "c", "ruby", "go", "golang",
    "kotlin", "swift", "typescript", "php", "scala", "r", "matlab", "perl",
    "rust", "dart", "sql",
    # Web
    "html", "css", "react", "angular", "vue", "node", "nodejs", "express",
    "django", "flask", "fastapi", "spring", "asp.net", "bootstrap", "jquery",
    "tailwind", "rest", "graphql", "api", "json", "xml",
    # Data / AI / ML
    "machine learning", "deep learning", "nlp", "natural language processing",
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "pandas",
    "numpy", "matplotlib", "seaborn", "opencv", "computer vision",
    "neural network", "bert", "gpt", "transformers", "xgboost", "lightgbm",
    "data analysis", "data science", "statistics", "regression", "classification",
    "clustering", "reinforcement learning",
    # Databases
    "mysql", "postgresql", "mongodb", "sqlite", "redis", "elasticsearch",
    "oracle", "cassandra", "firebase", "dynamodb",
    # Cloud / DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "jenkins",
    "ci/cd", "git", "github", "gitlab", "linux", "bash", "terraform", "ansible",
    # Other Tech
    "excel", "powerbi", "tableau", "hadoop", "spark", "kafka", "airflow",
    "selenium", "pytest", "junit", "agile", "scrum", "jira", "figma",
    "photoshop", "canva", "networking", "cybersecurity", "blockchain",
    "android", "ios", "flutter", "react native",
    # Soft skills (frequently mentioned in JDs)
    "communication", "teamwork", "leadership", "problem solving", "analytical",
    "critical thinking", "time management", "project management"
}


# ────────────────────────────────────────────
# Text Extraction
# ────────────────────────────────────────────

def extract_text_from_pdf(filepath: str) -> str:
    """Extract text from PDF using pdfminer.six."""
    try:
        from pdfminer.high_level import extract_text as pdf_extract
        text = pdf_extract(filepath)
        return text or ""
    except Exception as e:
        return f"[PDF extraction error: {e}]"


def extract_text_from_docx(filepath: str) -> str:
    """Extract text from DOCX using python-docx."""
    try:
        from docx import Document
        doc = Document(filepath)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        return f"[DOCX extraction error: {e}]"


def extract_text(filepath: str) -> str:
    """Auto-detect file type and extract text."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(filepath)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(filepath)
    elif ext == ".txt":
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    return ""


# ────────────────────────────────────────────
# Text Preprocessing
# ────────────────────────────────────────────

def preprocess(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s\+\#]', ' ', text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 1]
    return " ".join(tokens)


# ────────────────────────────────────────────
# Skill Extraction
# ────────────────────────────────────────────

def extract_skills(text: str, skill_pool: set) -> set:
    """Match multi-word and single-word skills against text."""
    text_lower = text.lower()
    found = set()
    for skill in skill_pool:
        # Use word-boundary aware matching for single-word skills
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.add(skill)
    return found


# ────────────────────────────────────────────
# Name Extraction
# ────────────────────────────────────────────

def extract_name_from_text(text: str) -> str:
    """Extract name (assumes first non-empty line of the resume)."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        # Take the first line as the name
        return lines[0]
    return "Unknown"


# ────────────────────────────────────────────
# Scoring Engine
# ────────────────────────────────────────────

def compute_score(resume_path: str, job_description: str, job_skills_required: list) -> dict:
    """
    Main scoring function.
    Returns:
        {
            score: float (0-100),
            matched_skills: list,
            missing_skills: list,
            label: str,
            extracted_name: str
        }
    """
    # 1. Extract resume text
    resume_text = extract_text(resume_path)
    if not resume_text.strip():
        return {
            "score": 0, 
            "matched_skills": [], 
            "missing_skills": job_skills_required, 
            "label": "Reject",
            "extracted_name": "None"
        }

    # 2. Extract name
    extracted_name = extract_name_from_text(resume_text)

    # 3. TF-IDF cosine similarity
    processed_resume = preprocess(resume_text)
    processed_jd = preprocess(job_description)

    try:
        vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform([processed_jd, processed_resume])
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except Exception:
        cosine_sim = 0.0

    # 4. Skill matching
    # Combine job required skills + global keyword pool
    skill_pool = SKILL_KEYWORDS.union({s.lower() for s in job_skills_required})
    resume_skills = extract_skills(resume_text, skill_pool)
    required_skills = {s.lower() for s in job_skills_required if s.strip()}

    if required_skills:
        matched = resume_skills.intersection(required_skills)
        missing = required_skills - matched
        skill_ratio = len(matched) / len(required_skills)
    else:
        matched = set()
        missing = set()
        skill_ratio = 0.0

    # 5. Composite score (60% cosine sim + 40% skill match)
    raw_score = (0.6 * cosine_sim + 0.4 * skill_ratio) * 100
    score = round(min(raw_score, 100), 1)

    # 6. Label
    if score >= 60:
        label = "Shortlist"
    elif score >= 40:
        label = "Review"
    else:
        label = "Reject"

    return {
        "score": score,
        "matched_skills": sorted(list(matched)),
        "missing_skills": sorted(list(missing)),
        "label": label,
        "extracted_name": extracted_name
    }
