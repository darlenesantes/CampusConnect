# This is where we define course-related database models and queries
# Ex: Course model, queries for fetching courses, etc.
# This will also handle user course enrollments

from . import db

# Couse model:
# - represents a course
# - stores course code, name
# - linked to users via enrollments

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True) # course ID
    # course_number
    # course_name
    # course_subject