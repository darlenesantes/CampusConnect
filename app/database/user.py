from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    profile_picture = db.Column(db.String(200))
    campus = db.Column(db.String(100))
    major = db.Column(db.String(100))
    year = db.Column(db.String(20))
    study_style = db.Column(db.String(50))
    preferred_location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    courses = db.relationship('UserCourse', backref='user', lazy=True, cascade='all, delete-orphan')
