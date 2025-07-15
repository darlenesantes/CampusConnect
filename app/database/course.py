""" This is where we define course-related database models and queries"""
# course.py
# Ex: Course model, queries for fetching courses, etc.
# This will also handle user course enrollments

from . import db

# Couse model:
# - represents a course
# - stores course code, name
# - linked to users via enrollments

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True) # course unique ID
    # course_number, 5 digit code like 12345
    course_number = db.Column(db.String(5), nullable=False)
    # course_name (called Title in the API)
    course_name = db.Column(db.String(100), nullable=False)
    # course_subject
    course_subject = db.Column(db.String(50), nullable=False)


# Enrollments table:
# - many-to-many relationship between users and courses
# - stores user_id and course_id

enrollments = db.Table(
    'enrollments',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True)
)