""" Contains database models and queries related to study groups"""
# studysession.py
# Ex: StudySession model, queries for creating and fetching study groups

from . import db

# Session participants table:
# - many-to-many relationship between users and study sessions
session_participants = db.Table(
    'session_participants',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('session_id', db.Integer, db.ForeignKey('study_sessions.id'), primary_key=True)
)

class StudySession(db.Model):
    __tablename__ = 'study_sessions'

    #id -> primary key
    id = db.Column(db.Integer, primary_key=True)  # unique ID for the session
    # course_id -> foreign key to Course
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    # creator_id -> foreign key to User
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Session details (columns)
    # location
    location = db.Column(db.String(100), nullable=False)
    # time
    time = db.Column(db.DateTime, nullable=False)
    # duration in minutes
    duration = db.Column(db.Integer, nullable=False)
    # type (quiet, collaborative, etc.)
    session_type = db.Column(db.String(50), nullable=False)

    # relationships
    # course
    course = db.relationship('Course', backref='study_sessions')
    # creator (user who created the session)
    creator = db.relationship('User', backref='created_sessions')
    # participants (users who joined the session?) -> come back and add if needed
    participants = db.relationship('User', secondary=session_participants, backref='joined_sessions')
