from app import db

class Campus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    
    users = db.relationship('User', backref='campus_info', lazy=True)
    dining_halls = db.relationship('DiningHall', backref='campus', lazy=True)
    study_locations = db.relationship('StudyLocation', backref='campus', lazy=True)
    courses = db.relationship('Course', backref='campus', lazy=True)

class DiningHall(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    campus_id = db.Column(db.Integer, db.ForeignKey('campus.id'), nullable=False)
    hours = db.Column(db.String(100))
    cuisine_type = db.Column(db.String(100))

class StudyLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    campus_id = db.Column(db.Integer, db.ForeignKey('campus.id'), nullable=False)
    location_type = db.Column(db.String(50))  # 'library', 'study_room', 'lounge', 'outdoor'
    capacity = db.Column(db.Integer)
    amenities = db.Column(db.String(500))