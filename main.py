from flask import Flask, render_template_string, redirect, url_for, session, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
import os
from datetime import datetime, timedelta
import secrets
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campus_connect.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')

if not app.config['GOOGLE_CLIENT_ID'] or not app.config['GOOGLE_CLIENT_SECRET']:
    print("Warning: Google OAuth credentials not found in environment variables!")

db = SQLAlchemy(app)
oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# Enhanced Database Models
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

class Major(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    degree_type = db.Column(db.String(50))  # 'BS', 'BA', 'MS', 'PhD'

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

# Campus data with real universities
CAMPUS_DATA = [
    {"name": "University of Illinois at Urbana-Champaign", "city": "Champaign", "state": "IL", "code": "UIUC"},
    {"name": "Northwestern University", "city": "Evanston", "state": "IL", "code": "NU"},
    {"name": "University of Chicago", "city": "Chicago", "state": "IL", "code": "UC"},
    {"name": "DePaul University", "city": "Chicago", "state": "IL", "code": "DPU"},
    {"name": "Stanford University", "city": "Stanford", "state": "CA", "code": "STAN"},
    {"name": "MIT", "city": "Cambridge", "state": "MA", "code": "MIT"},
    {"name": "Harvard University", "city": "Cambridge", "state": "MA", "code": "HARV"},
    {"name": "UC Berkeley", "city": "Berkeley", "state": "CA", "code": "UCB"},
]

# Dining halls by campus
DINING_DATA = {
    "UIUC": ["Ikenberry Dining Center", "Lincoln Avenue Dining Hall", "Pennsylvania Avenue Dining Hall", "Busey-Evans Food Court", "57 North"],
    "NU": ["Allison Dining Hall", "Elder Dining Hall", "Sargent Dining Hall", "Plex West", "Norris Food Court"],
    "UC": ["Bartlett Dining Commons", "Baker Dining Commons", "Cathey Dining Commons", "South Campus Dining Hall"],
    "DPU": ["Student Center Dining", "Brownstone's Café", "Daley Building Food Court", "Loop Campus Dining"],
    "STAN": ["Stern Dining", "Wilbur Dining", "FloMo Café", "Lakeside Dining", "Arrillaga Family Dining Commons"],
    "MIT": ["Maseeh Dining", "Next House Dining", "Simmons Hall Dining", "Student Center Food Court"],
    "HARV": ["Annenberg Hall", "Adams House Dining", "Winthrop House Dining", "Leverett House Dining"],
    "UCB": ["Crossroads", "Foothill Dining", "Café 3", "Clark Kerr Campus Dining"]
}

# Study locations by campus
STUDY_DATA = {
    "UIUC": ["Main Library", "Undergraduate Library", "Engineering Library", "Grainger Library", "Study Room A101", "Union Study Lounge"],
    "NU": ["Main Library", "Mudd Science Library", "Deering Library", "Tech Study Rooms", "Norris Study Spaces"],
    "UC": ["Regenstein Library", "Crerar Library", "Mansueto Library", "Study Pods Level 2", "Harper Memorial Library"],
    "DPU": ["Richardson Library", "Loop Campus Library", "Study Commons", "Quiet Study Rooms", "Group Study Areas"],
    "STAN": ["Green Library", "Engineering Library", "Meyer Library", "Study Rooms Building 160", "24/7 Study Spaces"],
    "MIT": ["Hayden Library", "Rotch Library", "Study Rooms E25", "Stata Center Study", "Student Center Study"],
    "HARV": ["Widener Library", "Lamont Library", "Cabot Science Library", "Study Rooms Leverett", "24/7 Study Spaces"],
    "UCB": ["Doe Library", "Moffitt Library", "Engineering Library", "Study Rooms MLK", "24/7 Study Spaces"]
}

# Major categories
MAJORS_DATA = [
    {"name": "Computer Science", "department": "Engineering", "degree_type": "BS"},
    {"name": "Electrical Engineering", "department": "Engineering", "degree_type": "BS"},
    {"name": "Mechanical Engineering", "department": "Engineering", "degree_type": "BS"},
    {"name": "Civil Engineering", "department": "Engineering", "degree_type": "BS"},
    {"name": "Business Administration", "department": "Business", "degree_type": "BS"},
    {"name": "Economics", "department": "Liberal Arts", "degree_type": "BA"},
    {"name": "Psychology", "department": "Liberal Arts", "degree_type": "BA"},
    {"name": "Biology", "department": "Sciences", "degree_type": "BS"},
    {"name": "Chemistry", "department": "Sciences", "degree_type": "BS"},
    {"name": "Physics", "department": "Sciences", "degree_type": "BS"},
    {"name": "Mathematics", "department": "Sciences", "degree_type": "BS"},
    {"name": "Statistics", "department": "Sciences", "degree_type": "BS"},
    {"name": "English Literature", "department": "Liberal Arts", "degree_type": "BA"},
    {"name": "History", "department": "Liberal Arts", "degree_type": "BA"},
    {"name": "Political Science", "department": "Liberal Arts", "degree_type": "BA"},
    {"name": "International Relations", "department": "Liberal Arts", "degree_type": "BA"},
    {"name": "Pre-Med", "department": "Sciences", "degree_type": "Track"},
    {"name": "Pre-Law", "department": "Liberal Arts", "degree_type": "Track"},
]

# Course data by department
COURSES_DATA = {
    "Computer Science": [
        ("CS101", "Introduction to Computer Science", "Easy"),
        ("CS225", "Data Structures", "Medium"),
        ("CS233", "Computer Architecture", "Medium"),
        ("CS374", "Algorithms and Models of Computation", "Hard"),
        ("CS411", "Database Systems", "Medium"),
        ("CS440", "Artificial Intelligence", "Hard"),
        ("CS498", "Machine Learning", "Hard")
    ],
    "Mathematics": [
        ("MATH221", "Calculus I", "Medium"),
        ("MATH231", "Calculus II", "Medium"),
        ("MATH241", "Calculus III", "Hard"),
        ("MATH415", "Linear Algebra", "Medium"),
        ("MATH461", "Probability Theory", "Hard"),
        ("MATH464", "Statistical Theory", "Hard")
    ],
    "Physics": [
        ("PHYS211", "University Physics: Mechanics", "Medium"),
        ("PHYS212", "University Physics: Elec & Mag", "Medium"),
        ("PHYS213", "University Physics: Thermal Physics", "Hard"),
        ("PHYS435", "Electromagnetic Fields", "Hard")
    ],
    "Chemistry": [
        ("CHEM102", "General Chemistry I", "Medium"),
        ("CHEM104", "General Chemistry II", "Medium"),
        ("CHEM232", "Organic Chemistry I", "Hard"),
        ("CHEM233", "Organic Chemistry II", "Hard")
    ],
    "Business": [
        ("BUS101", "Introduction to Business", "Easy"),
        ("BUS200", "Financial Accounting", "Medium"),
        ("BUS300", "Corporate Finance", "Hard"),
        ("BUS400", "Strategic Management", "Hard")
    ],
    "Biology": [
        ("BIO101", "General Biology", "Easy"),
        ("BIO201", "Cell Biology", "Medium"),
        ("BIO301", "Genetics", "Hard"),
        ("BIO401", "Molecular Biology", "Hard")
    ]
}

# Demo user names for realistic matches
DEMO_NAMES = [
    "Alex Johnson", "Sarah Chen", "Michael Rodriguez", "Emily Davis", "James Wilson",
    "Jessica Garcia", "David Kim", "Amanda Miller", "Ryan Thompson", "Lauren Brown",
    "Kevin Lee", "Sophia Martinez", "Tyler Anderson", "Maya Patel", "Jordan White",
    "Chloe Taylor", "Nathan Moore", "Zoe Jackson", "Ethan Harris", "Grace Liu",
    "Brandon Clark", "Olivia Lewis", "Austin Walker", "Isabella Hall", "Logan Young"
]

def create_demo_users():
    """Create realistic demo users for matching"""
    existing_demo_count = User.query.filter_by(is_demo_user=True).count()
    if existing_demo_count >= 50:
        return  # Already have enough demo users
    
    campuses = Campus.query.all()
    majors = Major.query.all()
    
    for i in range(50):
        campus = random.choice(campuses)
        major = random.choice(majors)
        
        # Get dining halls and study locations for this campus
        dining_halls = DiningHall.query.filter_by(campus_id=campus.id).all()
        study_locations = StudyLocation.query.filter_by(campus_id=campus.id).all()
        
        demo_user = User(
            email=f"demo{i}@{campus.code.lower()}.edu",
            name=random.choice(DEMO_NAMES),
            campus_id=campus.id,
            major_id=major.id,
            year=random.choice(['Freshman', 'Sophomore', 'Junior', 'Senior', 'Graduate']),
            study_style=random.choice(['quiet', 'discussion', 'group']),
            preferred_dining_hall_id=random.choice(dining_halls).id if dining_halls else None,
            preferred_study_location_id=random.choice(study_locations).id if study_locations else None,
            gpa=round(random.uniform(2.5, 4.0), 2),
            bio=f"Hi! I'm studying {major.name} and love collaborating on projects. Always looking for study partners!",
            is_demo_user=True
        )
        
        db.session.add(demo_user)
        db.session.flush()  # Get the user ID
        
        # Add random courses for this demo user
        campus_courses = Course.query.filter_by(campus_id=campus.id).limit(20).all()
        selected_courses = random.sample(campus_courses, min(random.randint(3, 7), len(campus_courses)))
        
        for course in selected_courses:
            user_course = UserCourse(
                user_id=demo_user.id,
                course_id=course.id,
                grade_goal=random.choice(['A', 'A-', 'B+', 'B', 'B-'])
            )
            db.session.add(user_course)
    
    db.session.commit()

def find_study_matches(user_id):
    """Enhanced matching algorithm with guaranteed results"""
    current_user = User.query.get(user_id)
    if not current_user:
        return []
    
    user_courses = [uc.course_id for uc in current_user.courses]
    matches = []
    
    # First, try to find users with same study style and shared courses
    potential_matches = User.query.filter(
        User.id != user_id,
        User.campus_id == current_user.campus_id,
        User.study_style == current_user.study_style
    ).limit(15).all()
    
    for match in potential_matches:
        match_courses = [uc.course_id for uc in match.courses]
        common_courses = set(user_courses) & set(match_courses)
        
        if common_courses:
            course_names = [Course.query.get(course_id).name for course_id in common_courses]
            compatibility = (len(common_courses) / max(len(user_courses), 1)) * 100
            
            # Bonus points for same major, dining hall, study location
            if match.major_id == current_user.major_id:
                compatibility += 20
            if match.preferred_dining_hall_id == current_user.preferred_dining_hall_id:
                compatibility += 10
            if match.preferred_study_location_id == current_user.preferred_study_location_id:
                compatibility += 15
            
            matches.append({
                'user': match,
                'common_courses': course_names,
                'compatibility': min(compatibility, 100),
                'same_major': match.major_id == current_user.major_id,
                'same_dining': match.preferred_dining_hall_id == current_user.preferred_dining_hall_id,
                'same_study_spot': match.preferred_study_location_id == current_user.preferred_study_location_id
            })
    
    # If we don't have enough matches, add some from same campus/major
    if len(matches) < 8:
        backup_matches = User.query.filter(
            User.id != user_id,
            User.campus_id == current_user.campus_id,
            User.major_id == current_user.major_id,
            User.id.notin_([m['user'].id for m in matches])
        ).limit(12 - len(matches)).all()
        
        for match in backup_matches:
            match_courses = [uc.course_id for uc in match.courses]
            common_courses = set(user_courses) & set(match_courses)
            course_names = [Course.query.get(course_id).name for course_id in common_courses] if common_courses else ["Similar academic interests"]
            
            matches.append({
                'user': match,
                'common_courses': course_names,
                'compatibility': random.randint(65, 85),
                'same_major': True,
                'same_dining': match.preferred_dining_hall_id == current_user.preferred_dining_hall_id,
                'same_study_spot': match.preferred_study_location_id == current_user.preferred_study_location_id
            })
    
    # If still not enough, add more from same campus with different study styles
    if len(matches) < 6:
        more_matches = User.query.filter(
            User.id != user_id,
            User.campus_id == current_user.campus_id,
            User.id.notin_([m['user'].id for m in matches])
        ).limit(10 - len(matches)).all()
        
        for match in more_matches:
            match_courses = [uc.course_id for uc in match.courses]
            common_courses = set(user_courses) & set(match_courses)
            course_names = [Course.query.get(course_id).name for course_id in common_courses] if common_courses else ["Campus connection"]
            
            matches.append({
                'user': match,
                'common_courses': course_names,
                'compatibility': random.randint(45, 75),
                'same_major': match.major_id == current_user.major_id,
                'same_dining': match.preferred_dining_hall_id == current_user.preferred_dining_hall_id,
                'same_study_spot': match.preferred_study_location_id == current_user.preferred_study_location_id
            })
    
    # Sort by compatibility and return top matches
    matches.sort(key=lambda x: x['compatibility'], reverse=True)
    return matches[:8]  # Return top 8 matches

# Enhanced Templates
SETUP_PROFILE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Setup Profile - CampusConnect</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .card { border: none; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container">
            <span class="navbar-brand"><i class="bi bi-people-fill"></i> CampusConnect</span>
            <a href="{{ url_for('logout') }}" class="btn btn-outline-light btn-sm">Logout</a>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-md-10">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h4><i class="bi bi-gear me-2"></i>Complete Your Campus Profile</h4>
                        <p class="mb-0">Help us find your perfect study matches</p>
                    </div>
                    <div class="card-body p-4">
                        {% with messages = get_flashed_messages() %}
                            {% if messages %}
                                {% for message in messages %}
                                    <div class="alert alert-success">{{ message }}</div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <form method="POST" id="profileForm">
                            <!-- Campus Selection -->
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="bi bi-building me-2"></i>Campus</label>
                                    <select class="form-select" name="campus_id" id="campusSelect" required>
                                        <option value="">Select your campus</option>
                                        {% for campus in campuses %}
                                        <option value="{{ campus.id }}">{{ campus.name }} ({{ campus.city }}, {{ campus.state }})</option>
                                        {% endfor %}
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="bi bi-mortarboard me-2"></i>Major</label>
                                    <select class="form-select" name="major_id" required>
                                        <option value="">Select your major</option>
                                        {% for major in majors %}
                                        <option value="{{ major.id }}">{{ major.name }} ({{ major.department }})</option>
                                        {% endfor %}
                                    </select>
                                </div>
                            </div>
                            
                            <!-- Academic Info -->
                            <div class="row">
                                <div class="col-md-4 mb-3">
                                    <label class="form-label">Academic Year</label>
                                    <select class="form-select" name="year" required>
                                        <option value="">Select year</option>
                                        <option value="Freshman">Freshman</option>
                                        <option value="Sophomore">Sophomore</option>
                                        <option value="Junior">Junior</option>
                                        <option value="Senior">Senior</option>
                                        <option value="Graduate">Graduate Student</option>
                                    </select>
                                </div>
                                <div class="col-md-4 mb-3">
                                    <label class="form-label">Study Style</label>
                                    <select class="form-select" name="study_style" required>
                                        <option value="">Select style</option>
                                        <option value="quiet">🤫 Quiet Study</option>
                                        <option value="discussion">💬 Discussion-Based</option>
                                        <option value="group">👥 Group Study</option>
                                    </select>
                                </div>
                                <div class="col-md-4 mb-3">
                                    <label class="form-label">GPA (Optional)</label>
                                    <input type="number" class="form-control" name="gpa" min="0" max="4" step="0.01" placeholder="3.5">
                                </div>
                            </div>
                            
                            <!-- Campus Preferences -->
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="bi bi-cup-straw me-2"></i>Preferred Dining Hall</label>
                                    <select class="form-select" name="preferred_dining_hall_id" id="diningSelect">
                                        <option value="">Select dining preference</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label"><i class="bi bi-book me-2"></i>Preferred Study Location</label>
                                    <select class="form-select" name="preferred_study_location_id" id="studySelect">
                                        <option value="">Select study preference</option>
                                    </select>
                                </div>
                            </div>
                            
                            <!-- Bio -->
                            <div class="mb-3">
                                <label class="form-label">Bio (Optional)</label>
                                <textarea class="form-control" name="bio" rows="3" placeholder="Tell other students about yourself, your interests, and what you're looking for in a study partner..."></textarea>
                            </div>
                            
                            <!-- Course Selection -->
                            <div class="mb-4">
                                <label class="form-label"><i class="bi bi-journal-bookmark me-2"></i>Select Your Current Courses</label>
                                <div class="row" id="coursesContainer">
                                    <div class="col-12">
                                        <p class="text-muted">Please select a campus first to see available courses.</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="text-center">
                                <button type="submit" class="btn btn-primary btn-lg px-5">
                                    <i class="bi bi-check-circle me-2"></i>Complete Profile & Find Matches
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Campus selection handler
        document.getElementById('campusSelect').addEventListener('change', function() {
            const campusId = this.value;
            if (!campusId) {
                document.getElementById('diningSelect').innerHTML = '<option value="">Select dining preference</option>';
                document.getElementById('studySelect').innerHTML = '<option value="">Select study preference</option>';
                document.getElementById('coursesContainer').innerHTML = '<div class="col-12"><p class="text-muted">Please select a campus first.</p></div>';
                return;
            }
            
            // Fetch dining halls, study locations, and courses for selected campus
            fetch(`/api/campus-data/${campusId}`)
                .then(response => response.json())
                .then(data => {
                    // Update dining halls
                    const diningSelect = document.getElementById('diningSelect');
                    diningSelect.innerHTML = '<option value="">Select dining preference</option>';
                    data.dining_halls.forEach(hall => {
                        diningSelect.innerHTML += `<option value="${hall.id}">${hall.name}</option>`;
                    });
                    
                    // Update study locations
                    const studySelect = document.getElementById('studySelect');
                    studySelect.innerHTML = '<option value="">Select study preference</option>';
                    data.study_locations.forEach(location => {
                        studySelect.innerHTML += `<option value="${location.id}">${location.name} (${location.location_type})</option>`;
                    });
                    
                    // Update courses
                    const coursesContainer = document.getElementById('coursesContainer');
                    coursesContainer.innerHTML = '';
                    data.courses.forEach(course => {
                        coursesContainer.innerHTML += `
                            <div class="col-md-6 mb-2">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" name="courses" value="${course.id}" id="course_${course.id}">
                                    <label class="form-check-label" for="course_${course.id}">
                                        <strong>${course.code}</strong> - ${course.name}
                                        <span class="badge bg-${course.difficulty === 'Easy' ? 'success' : course.difficulty === 'Medium' ? 'warning' : 'danger'} ms-2">${course.difficulty}</span>
                                    </label>
                                </div>
                            </div>
                        `;
                    });
                });
        });
        
        // Form validation
        document.getElementById('profileForm').addEventListener('submit', function(e) {
            const selectedCourses = document.querySelectorAll('input[name="courses"]:checked');
            if (selectedCourses.length === 0) {
                e.preventDefault();
                alert('Please select at least one course to find study matches.');
            }
        });
    </script>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard - CampusConnect</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .match-card { transition: transform 0.2s; cursor: pointer; }
        .match-card:hover { transform: translateY(-5px); }
        .compatibility-badge { font-size: 0.9rem; font-weight: bold; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-primary">
        <div class="container">
            <span class="navbar-brand"><i class="bi bi-people-fill"></i> CampusConnect</span>
            <div class="dropdown">
                <button class="btn btn-outline-light dropdown-toggle" type="button" data-bs-toggle="dropdown">
                    {{ session.user.name }}
                </button>
                <ul class="dropdown-menu">
                    <li><a class="dropdown-item" href="{{ url_for('setup_profile') }}">Profile Settings</a></li>
                    <li><a class="dropdown-item" href="{{ url_for('logout') }}">Logout</a></li>
                </ul>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <!-- Welcome Header -->
        <div class="row mb-4">
            <div class="col-md-8">
                <h2>Welcome back, {{ user.name.split(' ')[0] }}! 👋</h2>
                <p class="text-muted">
                    <i class="bi bi-mortarboard me-1"></i>{{ user.major_info.name if user.major_info else 'Major not set' }} • 
                    <i class="bi bi-calendar me-1"></i>{{ user.year }} • 
                    <i class="bi bi-building me-1"></i>{{ user.campus_info.name if user.campus_info else 'Campus not set' }}
                </p>
            </div>
            <div class="col-md-4 text-end">
                <div class="card bg-primary text-white">
                    <div class="card-body text-center py-3">
                        <h4 class="mb-0">{{ matches|length }}</h4>
                        <small>Study Matches Found</small>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-8">
                <!-- Study Matches -->
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0"><i class="bi bi-people me-2"></i>Your Study Matches</h5>
                        <span class="badge bg-success">{{ matches|length }} matches found</span>
                    </div>
                    <div class="card-body">
                        {% if matches %}
                        <div class="mb-3">
                            <small class="text-muted">Showing {{ matches|length }} best matches • Sorted by compatibility</small>
                        </div>
                        <div class="row">
                            {% for match in matches %}
                            <div class="col-md-6 mb-3">
                                <div class="card match-card border-0 shadow-sm h-100">
                                    <div class="card-body">
                                        <div class="d-flex align-items-center mb-3">
                                            <div class="bg-primary rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 45px; height: 45px;">
                                                <i class="bi bi-person-fill text-white"></i>
                                            </div>
                                            <div class="flex-grow-1">
                                                <h6 class="mb-0">{{ match.user.name }}</h6>
                                                <small class="text-muted">
                                                    {{ match.user.major_info.name if match.user.major_info else 'Major not set' }} • {{ match.user.year }}
                                                </small>
                                            </div>
                                            <span class="badge bg-success compatibility-badge">{{ "%.0f"|format(match.compatibility) }}%</span>
                                        </div>
                                        
                                        <!-- Match Details -->
                                        <div class="mb-2">
                                            <small class="fw-bold text-primary">Common Interests:</small>
                                            <div class="mt-1">
                                                {% for course in match.common_courses[:2] %}
                                                <span class="badge bg-light text-dark me-1 mb-1">{{ course }}</span>
                                                {% endfor %}
                                                {% if match.common_courses|length > 2 %}
                                                <span class="badge bg-secondary mb-1">+{{ match.common_courses|length - 2 }} more</span>
                                                {% endif %}
                                            </div>
                                        </div>
                                        
                                        <!-- Compatibility Indicators -->
                                        <div class="mb-2">
                                            {% if match.same_major %}
                                            <span class="badge bg-primary me-1 mb-1"><i class="bi bi-mortarboard me-1"></i>Same Major</span>
                                            {% endif %}
                                            {% if match.same_dining %}
                                            <span class="badge bg-warning me-1 mb-1"><i class="bi bi-cup-straw me-1"></i>Same Dining</span>
                                            {% endif %}
                                            {% if match.same_study_spot %}
                                            <span class="badge bg-info me-1 mb-1"><i class="bi bi-book me-1"></i>Same Study Spot</span>
                                            {% endif %}
                                        </div>
                                        
                                        <!-- Study Preferences -->
                                        <div class="mb-2">
                                            <small class="text-muted">
                                                <i class="bi bi-chat-dots me-1"></i>{{ match.user.study_style.title() }} Study
                                                {% if match.user.gpa %} • <i class="bi bi-trophy me-1"></i>{{ match.user.gpa }} GPA{% endif %}
                                            </small>
                                        </div>
                                        
                                        <!-- Bio Preview -->
                                        {% if match.user.bio %}
                                        <div class="mb-3">
                                            <small class="text-muted">{{ match.user.bio[:80] }}{% if match.user.bio|length > 80 %}...{% endif %}</small>
                                        </div>
                                        {% endif %}
                                        
                                        <!-- Action Buttons -->
                                        <div class="d-flex gap-2 mt-auto">
                                            <button class="btn btn-primary btn-sm flex-grow-1" onclick="sendStudyRequest('{{ match.user.id }}', '{{ match.user.name }}')">
                                                <i class="bi bi-send me-1"></i>Send Request
                                            </button>
                                            <button class="btn btn-outline-secondary btn-sm" onclick="viewProfile('{{ match.user.id }}')">
                                                <i class="bi bi-eye me-1"></i>View
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                        
                        <!-- Show More Button -->
                        {% if matches|length >= 6 %}
                        <div class="text-center mt-3">
                            <button class="btn btn-outline-primary" onclick="alert('In a real app, this would load more matches!')">
                                <i class="bi bi-arrow-down-circle me-2"></i>Load More Matches
                            </button>
                        </div>
                        {% endif %}
                        {% else %}
                        <div class="text-center py-5">
                            <i class="bi bi-search text-muted" style="font-size: 4rem;"></i>
                            <h5 class="mt-3">No matches found yet</h5>
                            <p class="text-muted">Try updating your profile or adding more courses to find study buddies!</p>
                            <a href="{{ url_for('setup_profile') }}" class="btn btn-primary">
                                <i class="bi bi-gear me-2"></i>Update Profile
                            </a>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
            
            <!-- Sidebar -->
            <div class="col-md-4">
                <!-- Profile Summary -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h6 class="mb-0"><i class="bi bi-person-circle me-2"></i>Your Profile</h6>
                    </div>
                    <div class="card-body text-center">
                        <div class="bg-primary rounded-circle d-flex align-items-center justify-content-center mx-auto mb-3" style="width: 80px; height: 80px;">
                            <i class="bi bi-person-fill text-white" style="font-size: 2.5rem;"></i>
                        </div>
                        <h6>{{ user.name }}</h6>
                        <p class="text-muted small mb-3">{{ user.email }}</p>
                        
                        {% if user.major_info %}
                        <div class="mb-2">
                            <strong>Major:</strong>
                            <span class="badge bg-primary">{{ user.major_info.name }}</span>
                        </div>
                        {% endif %}
                        
                        <div class="mb-2">
                            <strong>Study Style:</strong>
                            <span class="badge bg-light text-dark">{{ user.study_style.title() if user.study_style else 'Not set' }}</span>
                        </div>
                        
                        <div class="mb-3">
                            <strong>Courses:</strong>
                            <div class="mt-1">
                                {% for user_course in user.courses[:4] %}
                                <span class="badge bg-secondary me-1 mb-1">{{ user_course.course.code }}</span>
                                {% endfor %}
                                {% if user.courses|length > 4 %}
                                <span class="badge bg-dark">+{{ user.courses|length - 4 }}</span>
                                {% endif %}
                            </div>
                        </div>
                        
                        <a href="{{ url_for('setup_profile') }}" class="btn btn-outline-primary btn-sm w-100">
                            <i class="bi bi-pencil me-2"></i>Edit Profile
                        </a>
                    </div>
                </div>
                
                <!-- Campus Info -->
                {% if user.campus_info %}
                <div class="card mb-3">
                    <div class="card-header">
                        <h6 class="mb-0"><i class="bi bi-building me-2"></i>Campus Info</h6>
                    </div>
                    <div class="card-body">
                        <div class="mb-2">
                            <strong>Campus:</strong><br>
                            <small>{{ user.campus_info.name }}</small>
                        </div>
                        {% if user.preferred_dining %}
                        <div class="mb-2">
                            <strong>Dining:</strong><br>
                            <small><i class="bi bi-cup-straw me-1"></i>{{ user.preferred_dining.name }}</small>
                        </div>
                        {% endif %}
                        {% if user.preferred_study %}
                        <div class="mb-2">
                            <strong>Study Spot:</strong><br>
                            <small><i class="bi bi-book me-1"></i>{{ user.preferred_study.name }}</small>
                        </div>
                        {% endif %}
                    </div>
                </div>
                {% endif %}
                
                <!-- Quick Stats -->
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0"><i class="bi bi-graph-up me-2"></i>Quick Stats</h6>
                    </div>
                    <div class="card-body">
                        <div class="row text-center">
                            <div class="col-6">
                                <h4 class="text-primary">{{ matches|length }}</h4>
                                <small class="text-muted">Study Matches</small>
                            </div>
                            <div class="col-6">
                                <h4 class="text-success">{{ user.courses|length }}</h4>
                                <small class="text-muted">Courses</small>
                            </div>
                        </div>
                        {% if user.gpa %}
                        <div class="text-center mt-3">
                            <h4 class="text-warning">{{ user.gpa }}</h4>
                            <small class="text-muted">Current GPA</small>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function sendStudyRequest(userId, userName) {
            // In a real app, this would send an actual request
            alert(`Study request sent to ${userName}! 📚\\n\\nIn a real app, they would receive an email notification and you could chat through the platform.`);
        }
        
        function viewProfile(userId) {
            // In a real app, this would show a detailed profile modal
            alert('Profile details would appear here in a real app! 👤\\n\\nThis would show their full course list, study schedule, and more details.');
        }
    </script>
</body>
</html>
"""

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>CampusConnect - Smart Study Buddy Matching</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            display: flex;
            align-items: center;
        }
        .card { border: none; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); }
        .feature-icon { font-size: 2.5rem; color: #667eea; }
        .stats-card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); }
    </style>
</head>
<body>
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-8 col-lg-6">
                <div class="card">
                    <div class="card-body text-center p-5">
                        <div class="mb-4">
                            <i class="bi bi-people-fill text-primary" style="font-size: 5rem;"></i>
                            <h1 class="h2 mb-3 fw-bold">CampusConnect</h1>
                            <p class="text-muted fs-5">The smartest way to find your perfect study buddy</p>
                        </div>
                        
                        {% with messages = get_flashed_messages() %}
                            {% if messages %}
                                {% for message in messages %}
                                    <div class="alert alert-info">{{ message }}</div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <div class="mb-4">
                            <h4 class="text-primary mb-3">Connect. Study. Succeed.</h4>
                            <div class="row text-start">
                                <div class="col-md-6 mb-3">
                                    <i class="bi bi-mortarboard feature-icon me-3"></i>
                                    <div class="d-inline-block">
                                        <strong>Smart Matching</strong><br>
                                        <small class="text-muted">AI-powered algorithm finds students in your courses with compatible study styles</small>
                                    </div>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <i class="bi bi-building feature-icon me-3"></i>
                                    <div class="d-inline-block">
                                        <strong>Campus Integration</strong><br>
                                        <small class="text-muted">Real dining halls, study spots, and course catalogs from your campus</small>
                                    </div>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <i class="bi bi-shield-check feature-icon me-3"></i>
                                    <div class="d-inline-block">
                                        <strong>Secure & Private</strong><br>
                                        <small class="text-muted">Google OAuth login with privacy controls and verified student accounts</small>
                                    </div>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <i class="bi bi-calendar-event feature-icon me-3"></i>
                                    <div class="d-inline-block">
                                        <strong>Study Sessions</strong><br>
                                        <small class="text-muted">Schedule group study sessions and track your academic progress</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <a href="{{ url_for('login') }}" class="btn btn-primary btn-lg w-100 mb-4 py-3">
                            <i class="bi bi-google me-2"></i>
                            Sign in with Google to Get Started
                        </a>
                        
                        <p class="text-muted small mb-0">
                            By signing in, you agree to our terms of service and privacy policy.<br>
                            We only access your basic profile information.
                        </p>
                    </div>
                </div>
                
                <!-- Stats Cards -->
                <div class="row mt-4 text-white">
                    <div class="col-4">
                        <div class="card stats-card text-center">
                            <div class="card-body py-3">
                                <i class="bi bi-people text-white mb-2" style="font-size: 2rem;"></i>
                                <h4 class="text-white">5,000+</h4>
                                <small>Active Students</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="card stats-card text-center">
                            <div class="card-body py-3">
                                <i class="bi bi-building text-white mb-2" style="font-size: 2rem;"></i>
                                <h4 class="text-white">8</h4>
                                <small>Universities</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="card stats-card text-center">
                            <div class="card-body py-3">
                                <i class="bi bi-calendar-event text-white mb-2" style="font-size: 2rem;"></i>
                                <h4 class="text-white">1,200+</h4>
                                <small>Study Sessions</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# API Routes
@app.route('/api/campus-data/<int:campus_id>')
def get_campus_data(campus_id):
    dining_halls = DiningHall.query.filter_by(campus_id=campus_id).all()
    study_locations = StudyLocation.query.filter_by(campus_id=campus_id).all()
    courses = Course.query.filter_by(campus_id=campus_id).all()
    
    return jsonify({
        'dining_halls': [{'id': d.id, 'name': d.name, 'cuisine_type': d.cuisine_type} for d in dining_halls],
        'study_locations': [{'id': s.id, 'name': s.name, 'location_type': s.location_type} for s in study_locations],
        'courses': [{'id': c.id, 'code': c.code, 'name': c.name, 'difficulty': c.difficulty} for c in courses]
    })

# Main Routes
@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/login')
def login():
    redirect_uri = url_for('callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/callback')
def callback():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if user_info:
            user = User.query.filter_by(email=user_info['email']).first()
            
            if not user:
                user = User(
                    email=user_info['email'],
                    name=user_info['name'],
                    profile_picture=user_info.get('picture', '')
                )
                db.session.add(user)
                db.session.commit()
            
            session['user'] = {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'profile_picture': user.profile_picture
            }
            
            if not user.campus_id or not user.courses:
                return redirect(url_for('setup_profile'))
            
            return redirect(url_for('dashboard'))
        else:
            flash('Failed to get user information from Google.', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        print(f"OAuth Error: {e}")
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/setup_profile', methods=['GET', 'POST'])
def setup_profile():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        user_id = session['user']['id']
        user = User.query.get(user_id)
        
        # Update user profile with enhanced data
        user.campus_id = request.form.get('campus_id') or None
        user.major_id = request.form.get('major_id') or None
        user.year = request.form.get('year')
        user.study_style = request.form.get('study_style')
        user.preferred_dining_hall_id = request.form.get('preferred_dining_hall_id') or None
        user.preferred_study_location_id = request.form.get('preferred_study_location_id') or None
        user.gpa = float(request.form.get('gpa')) if request.form.get('gpa') else None
        user.bio = request.form.get('bio')
        
        # Clear existing courses and add new ones
        UserCourse.query.filter_by(user_id=user.id).delete()
        
        selected_courses = request.form.getlist('courses')
        for course_id in selected_courses:
            if course_id:
                user_course = UserCourse(user_id=user.id, course_id=int(course_id))
                db.session.add(user_course)
        
        db.session.commit()
        flash('Profile updated successfully! Finding your study matches...', 'success')
        return redirect(url_for('dashboard'))
    
    # Get data for form
    campuses = Campus.query.all()
    majors = Major.query.order_by(Major.department, Major.name).all()
    
    return render_template_string(SETUP_PROFILE_TEMPLATE, campuses=campuses, majors=majors)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    user_id = session['user']['id']
    user = User.query.get(user_id)
    matches = find_study_matches(user_id)
    
    return render_template_string(DASHBOARD_TEMPLATE, user=user, matches=matches)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

def init_db():
    """Initialize database with comprehensive data"""
    with app.app_context():
        # Drop all tables and recreate (for development)
        db.drop_all()
        db.create_all()
        
        # Add campuses
        for campus_data in CAMPUS_DATA:
            campus = Campus(**campus_data)
            db.session.add(campus)
        db.session.commit()
        
        # Add dining halls for each campus
        for campus in Campus.query.all():
            if campus.code in DINING_DATA:
                for dining_name in DINING_DATA[campus.code]:
                    dining_hall = DiningHall(
                        name=dining_name,
                        campus_id=campus.id,
                        hours="7:00 AM - 10:00 PM",
                        cuisine_type=random.choice(['American', 'International', 'Asian', 'Mediterranean', 'Vegetarian'])
                    )
                    db.session.add(dining_hall)
            
            # Add study locations for each campus
            if campus.code in STUDY_DATA:
                for study_name in STUDY_DATA[campus.code]:
                    location_type = 'library' if 'Library' in study_name else \
                                  'study_room' if 'Study Room' in study_name or 'Room' in study_name else \
                                  'lounge' if 'Lounge' in study_name else 'other'
                    
                    study_location = StudyLocation(
                        name=study_name,
                        campus_id=campus.id,
                        location_type=location_type,
                        capacity=random.randint(20, 200),
                        amenities=random.choice(['WiFi, Power Outlets', 'Whiteboards, WiFi', 'Quiet Zone, WiFi', '24/7 Access, WiFi'])
                    )
                    db.session.add(study_location)
        
        db.session.commit()
        
        # Add majors
        for major_data in MAJORS_DATA:
            major = Major(**major_data)
            db.session.add(major)
        db.session.commit()
        
        # Add courses for each campus
        for campus in Campus.query.all():
            for dept, courses in COURSES_DATA.items():
                for code, name, difficulty in courses:
                    course = Course(
                        code=code,
                        name=name,
                        department=dept,
                        campus_id=campus.id,
                        credits=random.choice([3, 4]),
                        difficulty=difficulty
                    )
                    db.session.add(course)
        db.session.commit()
        
        # Create demo users
        create_demo_users()
        
        print("Database initialized with comprehensive campus data!")
        print(f"Created: {Campus.query.count()} campuses, {Major.query.count()} majors, {Course.query.count()} courses, {User.query.filter_by(is_demo_user=True).count()} demo users")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
