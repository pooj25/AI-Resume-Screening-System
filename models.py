from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    skills_required = db.Column(db.Text, nullable=False)   # comma-separated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    candidates = db.relationship('Candidate', backref='job', lazy=True, cascade='all, delete-orphan')

    def skills_list(self):
        return [s.strip() for s in self.skills_required.split(',') if s.strip()]


class Candidate(db.Model):
    __tablename__ = 'candidates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    resume_filename = db.Column(db.String(300), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    score = db.Column(db.Float, default=0.0)
    matched_skills = db.Column(db.Text, default='')  # comma-separated
    missing_skills = db.Column(db.Text, default='')  # comma-separated
    extracted_name = db.Column(db.String(150), nullable=True)
    name_match = db.Column(db.Boolean, default=True)
    label = db.Column(db.String(50), default='Review')  # Shortlist / Review / Reject
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def matched_list(self):
        return [s.strip() for s in self.matched_skills.split(',') if s.strip()]

    def missing_list(self):
        return [s.strip() for s in self.missing_skills.split(',') if s.strip()]
