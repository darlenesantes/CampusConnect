from . import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    profile_picture = db.Column(db.String(200))
    campus_id = db.Column(db.Integer, db.ForeignKey('campus.id'))
    major_id = db.Column(db.Integer, db.ForeignKey('major.id'))
    year = db.Column(db.String(20))
    study_style = db.Column(db.String(50))
    preferred_dining_hall_id = db.Column(db.Integer, db.ForeignKey('dining_hall.id'))
    preferred_study_location_id = db.Column(db.Integer, db.ForeignKey('study_location.id'))
    gpa = db.Column(db.Float)
    bio = db.Column(db.Text)
    is_demo_user = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    courses = db.relationship('UserCourse', backref='user', lazy=True, cascade='all, delete-orphan')
    major_info = db.relationship('Major', backref='students')
    preferred_dining = db.relationship('DiningHall', backref='preferred_by_users')
    preferred_study = db.relationship('StudyLocation', backref='preferred_by_users')

class Major(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    degree_type = db.Column(db.String(50))  # 'BS', 'BA', 'MS', 'PhD'