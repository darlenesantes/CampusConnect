""" This is where we define user-related database models and queries """
# user.py
from . import db

# User model:
# - represents a user in the system
# - stores user details like username, email, etc.
# - linked to courses via enrollments

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)  # user ID
    # name
    name = db.Column(db.String(100), nullable=False)
    # email
    email = db.Column(db.String(120), unique=True, nullable=False)
    # preferences (quiet, collaborative, etc.)
    preferences = db.Column(db.String(50), nullable=True)

    # This will keep track of whether the user has completed their profile setup
    # profile_completed (boolean)
    profile_completed = db.Column(db.Boolean, default=False)

    # courses that the user is enrolled in (once that has been implemented)
    courses = db.relationship('Course', secondary='enrollments', backref='users')
