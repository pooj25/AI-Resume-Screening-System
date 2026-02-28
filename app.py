"""
AI Resume Screening System — Flask Application
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from models import db, Job, Candidate
from nlp_engine import compute_score
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'resume_screener_secret_2024'

# ── Configuration ──────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'resume_screener.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

db.init_app(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ── Seed Data ──────────────────────────────────────────────
def seed_jobs():
    if Job.query.count() == 0:
        sample_jobs = [
            Job(
                title="Software Engineer",
                description="We are looking for a skilled Software Engineer with experience in Python, Java, and web technologies. The candidate should have strong knowledge of REST APIs, databases, object-oriented design, and cloud services. Agile/Scrum experience is a plus.",
                skills_required="python,java,rest,api,sql,git,docker,agile,problem solving"
            ),
            Job(
                title="Data Scientist / ML Engineer",
                description="Seeking a Data Scientist with hands-on expertise in machine learning, deep learning, and NLP. Must be proficient in Python, TensorFlow or PyTorch, sklearn, pandas, and numpy. Experience with data pipelines and cloud ML platforms preferred.",
                skills_required="python,machine learning,deep learning,nlp,tensorflow,pytorch,sklearn,pandas,numpy,sql,statistics"
            ),
            Job(
                title="Frontend Web Developer",
                description="We need a creative Frontend Developer with strong skills in HTML, CSS, and JavaScript. Experience with React or Angular frameworks is required. Knowledge of responsive design, UI/UX principles, and version control with Git is essential.",
                skills_required="html,css,javascript,react,angular,git,bootstrap,figma,api"
            ),
            Job(
                title="Data Analyst",
                description="Looking for a Data Analyst to interpret data and turn it into actionable insights. Must have experience with SQL, Excel, Tableau or PowerBI, and Python or R for data analysis. Strong communication and analytical skills required.",
                skills_required="sql,excel,tableau,powerbi,python,r,statistics,data analysis,communication,analytical"
            ),
            Job(
                title="HR Manager",
                description="We're hiring an HR Manager with experience in recruitment, employee relations, training, and performance management. Strong communication, leadership, and organizational skills are essential. Knowledge of HR software and labor laws preferred.",
                skills_required="communication,leadership,teamwork,problem solving,time management,project management,excel,analytical"
            ),
            Job(
                title="DevOps Engineer",
                description="Looking for a DevOps Engineer skilled in CI/CD pipelines, Docker, Kubernetes, cloud platforms (AWS/Azure/GCP), and Linux. Experience with Terraform, Ansible, and monitoring tools is a strong advantage.",
                skills_required="docker,kubernetes,aws,azure,linux,git,ci/cd,bash,terraform,ansible,python"
            ),
        ]
        for job in sample_jobs:
            db.session.add(job)
        db.session.commit()


# ── Routes ─────────────────────────────────────────────────

@app.route('/')
def index():
    total_jobs = Job.query.count()
    total_candidates = Candidate.query.count()
    shortlisted = Candidate.query.filter_by(label='Shortlist').count()
    recent_candidates = Candidate.query.order_by(Candidate.uploaded_at.desc()).limit(5).all()
    return render_template('index.html',
                           total_jobs=total_jobs,
                           total_candidates=total_candidates,
                           shortlisted=shortlisted,
                           recent_candidates=recent_candidates)


@app.route('/dashboard')
def dashboard():
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    candidates = Candidate.query.order_by(Candidate.uploaded_at.desc()).all()
    job_stats = []
    for job in jobs:
        count = Candidate.query.filter_by(job_id=job.id).count()
        shortlist_count = Candidate.query.filter_by(job_id=job.id, label='Shortlist').count()
        job_stats.append({'job': job, 'total': count, 'shortlisted': shortlist_count})
    return render_template('dashboard.html', job_stats=job_stats, candidates=candidates)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    jobs = Job.query.all()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        job_id = request.form.get('job_id')
        file = request.files.get('resume')

        if not name or not job_id or not file:
            flash('Please fill all required fields and select a resume.', 'error')
            return render_template('upload.html', jobs=jobs)

        if not allowed_file(file.filename):
            flash('Only PDF, DOCX, DOC, and TXT files are allowed.', 'error')
            return render_template('upload.html', jobs=jobs)

        job = Job.query.get(job_id)
        if not job:
            flash('Invalid job selected.', 'error')
            return render_template('upload.html', jobs=jobs)

        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # ── Run NLP Scoring ──
        result = compute_score(filepath, job.description, job.skills_list())
        
        # ── Name Verification ──
        extracted_name = result.get('extracted_name', 'Unknown')
        # Simple comparison: check if input name is roughly in extracted name or vice versa
        name_clean = name.lower().strip()
        extracted_clean = extracted_name.lower().strip()
        
        # Common comparison: check if all words in input name are in extracted name
        name_words = name_clean.split()
        match_status = any(word in extracted_clean for word in name_words) if name_words else False

        candidate = Candidate(
            name=name,
            email=email,
            resume_filename=filename,
            job_id=int(job_id),
            score=result['score'],
            matched_skills=','.join(result['matched_skills']),
            missing_skills=','.join(result['missing_skills']),
            extracted_name=extracted_name,
            name_match=match_status,
            label=result['label']
        )
        db.session.add(candidate)
        db.session.commit()

        return redirect(url_for('result', candidate_id=candidate.id))

    return render_template('upload.html', jobs=jobs)


@app.route('/result/<int:candidate_id>')
def result(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    job = Job.query.get(candidate.job_id)
    return render_template('result.html', candidate=candidate, job=job)


@app.route('/candidates')
def candidates():
    job_filter = request.args.get('job_id', type=int)
    label_filter = request.args.get('label', '')
    query = Candidate.query
    if job_filter:
        query = query.filter_by(job_id=job_filter)
    if label_filter:
        query = query.filter_by(label=label_filter)
    all_candidates = query.order_by(Candidate.score.desc()).all()
    jobs = Job.query.all()
    return render_template('candidates.html', candidates=all_candidates, jobs=jobs,
                           job_filter=job_filter, label_filter=label_filter)


@app.route('/add-job', methods=['POST'])
def add_job():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    skills = request.form.get('skills_required', '').strip()
    if title and description:
        job = Job(title=title, description=description, skills_required=skills)
        db.session.add(job)
        db.session.commit()
        flash(f'Job "{title}" added successfully!', 'success')
    else:
        flash('Job title and description are required.', 'error')
    return redirect(url_for('dashboard'))


@app.route('/delete-job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash(f'Job "{job.title}" deleted.', 'info')
    return redirect(url_for('dashboard'))


@app.route('/delete-candidate/<int:candidate_id>', methods=['POST'])
def delete_candidate(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    # Remove file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], candidate.resume_filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    db.session.delete(candidate)
    db.session.commit()
    flash('Candidate removed.', 'info')
    return redirect(url_for('candidates'))


# ── Init ───────────────────────────────────────────────────
if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    with app.app_context():
        db.create_all()
        seed_jobs()
    print("\n🚀 AI Resume Screener running at http://127.0.0.1:5000\n")
    app.run(debug=True)
