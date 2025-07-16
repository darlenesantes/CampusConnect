<<<<<<< HEAD
# This is where we define course-related database models and queries
# Ex: Course model, queries for fetching courses, etc.
# This will also handle user course enrollments
=======
from app import db

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100))
    campus = db.Column(db.String(100))

class UserCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    course = db.relationship('Course', backref='enrolled_users')
>>>>>>> e86c179ae670f259e3f9485453cc6bd9771385c7
