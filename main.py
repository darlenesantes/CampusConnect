from flask import Flask, render_template_string, redirect, url_for, session, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
from app.database.campus import Campus, DiningHall, StudyLocation
from app.database.user import User, Major
from app.database.course import Course, UserCourse
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
    return render_template_string(url_for('login'))

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
    
    return render_template_string(url_for('setup_profile'), campuses=campuses, majors=majors)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    user_id = session['user']['id']
    user = User.query.get(user_id)
    matches = find_study_matches(user_id)
    
    return render_template_string(url_for('dashboard'), user=user, matches=matches)

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
