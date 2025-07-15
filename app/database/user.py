# This is where we define user-related database models and queries
from . import db
from .course import Course

# User model:
# - represents a user in the system
# - stores user details like username, email, etc.
# - linked to courses via enrollments

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)  # user ID
    # name
    # email
    # preferences (quiet, collaborative, etc.)

    # courses that the user is enrolled in
    # db.relationship('Course', secondary='enrollments', backref='users')