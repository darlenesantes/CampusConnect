from app import db

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100))
    campus_id = db.Column(db.Integer, db.ForeignKey('campus.id'), nullable=False)
    credits = db.Column(db.Integer, default=3)
    difficulty = db.Column(db.String(20))  # 'Easy', 'Medium', 'Hard'

class UserCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    semester = db.Column(db.String(20), default='Fall 2025')
    grade_goal = db.Column(db.String(5))  # 'A', 'B', 'C', etc.
    
    course = db.relationship('Course')
