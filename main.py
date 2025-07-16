from flask import Flask, render_template_string, redirect, url_for, session, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
import os
from datetime import datetime, timedelta
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campus_connect.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Get OAuth credentials from environment variables
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')

# Check if credentials are loaded
if not app.config['GOOGLE_CLIENT_ID'] or not app.config['GOOGLE_CLIENT_SECRET']:
    print("Warning: Google OAuth credentials not found in environment variables!")
    print("Please create a .env file with GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")

# Initialize extensions
db = SQLAlchemy(app)
oauth = OAuth(app)

# Configure Google OAuth
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    profile_picture = db.Column(db.String(200))
    campus = db.Column(db.String(100))
    major = db.Column(db.String(100))
    year = db.Column(db.String(20))
    study_style = db.Column(db.String(50))
    preferred_location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    courses = db.relationship('UserCourse', backref='user', lazy=True, cascade='all, delete-orphan')

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100))

class UserCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    course = db.relationship('Course')

# Templates as strings
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>CampusConnect - Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .card { border: none; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
    </style>
</head>
<body class="d-flex align-items-center">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-4">
                <div class="card">
                    <div class="card-body text-center p-5">
                        <i class="bi bi-people-fill text-primary mb-3" style="font-size: 4rem;"></i>
                        <h1 class="h3 mb-3">CampusConnect</h1>
                        <p class="text-muted mb-4">Find your perfect study buddy</p>
                        
                        {% with messages = get_flashed_messages() %}
                            {% if messages %}
                                {% for message in messages %}
                                    <div class="alert alert-info">{{ message }}</div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <a href="{{ url_for('login') }}" class="btn btn-primary btn-lg w-100 mb-3">
                            <i class="bi bi-google me-2"></i>Sign in with Google
                        </a>
                        
                        <div class="mt-4">
                            <div class="row text-center">
                                <div class="col-4">
                                    <h6 class="text-primary">1000+</h6>
                                    <small class="text-muted">Students</small>
                                </div>
                                <div class="col-4">
                                    <h6 class="text-primary">50+</h6>
                                    <small class="text-muted">Courses</small>
                                </div>
                                <div class="col-4">
                                    <h6 class="text-primary">200+</h6>
                                    <small class="text-muted">Sessions</small>
                                </div>
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

SETUP_PROFILE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Setup Profile - CampusConnect</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-primary">
        <div class="container">
            <span class="navbar-brand"><i class="bi bi-people-fill"></i> CampusConnect</span>
            <a href="{{ url_for('logout') }}" class="btn btn-outline-light btn-sm">Logout</a>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h4><i class="bi bi-gear me-2"></i>Complete Your Profile</h4>
                    </div>
                    <div class="card-body">
                        {% with messages = get_flashed_messages() %}
                            {% if messages %}
                                {% for message in messages %}
                                    <div class="alert alert-success">{{ message }}</div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <form method="POST">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Campus</label>
                                    <select class="form-select" name="campus" required>
                                        <option value="">Select campus</option>
                                        <option value="University of Illinois">University of Illinois</option>
                                        <option value="Northwestern University">Northwestern University</option>
                                        <option value="DePaul University">DePaul University</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Major</label>
                                    <input type="text" class="form-control" name="major" required>
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Year</label>
                                    <select class="form-select" name="year" required>
                                        <option value="">Select year</option>
                                        <option value="Freshman">Freshman</option>
                                        <option value="Sophomore">Sophomore</option>
                                        <option value="Junior">Junior</option>
                                        <option value="Senior">Senior</option>
                                        <option value="Graduate">Graduate</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Study Style</label>
                                    <select class="form-select" name="study_style" required>
                                        <option value="">Select style</option>
                                        <option value="quiet">Quiet Study</option>
                                        <option value="discussion">Discussion-Based</option>
                                        <option value="group">Group Study</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Preferred Location</label>
                                <input type="text" class="form-control" name="preferred_location" placeholder="e.g., Main Library">
                            </div>
                            
                            <div class="mb-4">
                                <label class="form-label">Select Courses</label>
                                <div class="row">
                                    {% for course in courses %}
                                    <div class="col-md-6 mb-2">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" name="courses" value="{{ course.code }}" id="course_{{ course.id }}">
                                            <label class="form-check-label" for="course_{{ course.id }}">
                                                <strong>{{ course.code }}</strong> - {{ course.name }}
                                            </label>
                                        </div>
                                    </div>
                                    {% endfor %}
                                </div>
                            </div>
                            
                            <button type="submit" class="btn btn-primary btn-lg w-100">
                                <i class="bi bi-check-circle me-2"></i>Complete Profile
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
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
</head>
<body class="bg-light">
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
        <div class="row">
            <div class="col-md-8">
                <h2>Welcome back, {{ user.name.split(' ')[0] }}!</h2>
                <p class="text-muted">{{ user.major }} • {{ user.year }} • {{ user.campus }}</p>
                
                <div class="card mt-4">
                    <div class="card-header">
                        <h5><i class="bi bi-people me-2"></i>Your Study Matches</h5>
                    </div>
                    <div class="card-body">
                        {% if matches %}
                        <div class="row">
                            {% for match in matches %}
                            <div class="col-md-6 mb-3">
                                <div class="card border-0 shadow-sm">
                                    <div class="card-body">
                                        <div class="d-flex align-items-center mb-2">
                                            <div class="bg-primary rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px;">
                                                <i class="bi bi-person-fill text-white"></i>
                                            </div>
                                            <div>
                                                <h6 class="mb-0">{{ match.user.name }}</h6>
                                                <small class="text-muted">{{ match.user.major }}</small>
                                            </div>
                                            <span class="badge bg-success ms-auto">{{ "%.0f"|format(match.compatibility) }}%</span>
                                        </div>
                                        <div class="mb-2">
                                            <strong>Common courses:</strong>
                                            {% for course in match.common_courses %}
                                            <span class="badge bg-light text-dark me-1">{{ course }}</span>
                                            {% endfor %}
                                        </div>
                                        <button class="btn btn-outline-primary btn-sm" onclick="alert('Study request sent!')">
                                            <i class="bi bi-send me-1"></i>Send Request
                                        </button>
                                    </div>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                        {% else %}
                        <div class="text-center py-4">
                            <i class="bi bi-search text-muted" style="font-size: 3rem;"></i>
                            <h5 class="mt-3">No matches found yet</h5>
                            <p class="text-muted">Try updating your profile or adding more courses!</p>
                            <a href="{{ url_for('setup_profile') }}" class="btn btn-outline-primary">Update Profile</a>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h6><i class="bi bi-person-circle me-2"></i>Your Profile</h6>
                    </div>
                    <div class="card-body text-center">
                        <div class="bg-primary rounded-circle d-flex align-items-center justify-content-center mx-auto mb-3" style="width: 80px; height: 80px;">
                            <i class="bi bi-person-fill text-white" style="font-size: 2rem;"></i>
                        </div>
                        <h6>{{ user.name }}</h6>
                        <p class="text-muted small">{{ user.email }}</p>
                        
                        <div class="mb-3">
                            <strong>Courses:</strong>
                            <div class="mt-1">
                                {% for user_course in user.courses %}
                                <span class="badge bg-primary me-1">{{ user_course.course.code }}</span>
                                {% endfor %}
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <strong>Study Style:</strong>
                            <span class="badge bg-light text-dark">{{ user.study_style.title() if user.study_style else 'Not set' }}</span>
                        </div>
                        
                        <a href="{{ url_for('setup_profile') }}" class="btn btn-outline-primary btn-sm w-100">
                            <i class="bi bi-pencil me-2"></i>Edit Profile
                        </a>
                    </div>
                </div>
                
                <div class="card mt-3">
                    <div class="card-header">
                        <h6><i class="bi bi-graph-up me-2"></i>Quick Stats</h6>
                    </div>
                    <div class="card-body text-center">
                        <div class="row">
                            <div class="col-6">
                                <h4 class="text-primary">{{ matches|length }}</h4>
                                <small class="text-muted">Study Matches</small>
                            </div>
                            <div class="col-6">
                                <h4 class="text-success">{{ user.courses|length }}</h4>
                                <small class="text-muted">Courses</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Helper function
def find_study_matches(user_id):
    current_user = User.query.get(user_id)
    if not current_user:
        return []
    
    user_courses = [uc.course_id for uc in current_user.courses]
    matches = []
    
    potential_matches = User.query.filter(
        User.id != user_id,
        User.study_style == current_user.study_style
    ).all()
    
    for match in potential_matches:
        match_courses = [uc.course_id for uc in match.courses]
        common_courses = set(user_courses) & set(match_courses)
        
        if common_courses:
            course_names = [Course.query.get(course_id).name for course_id in common_courses]
            matches.append({
                'user': match,
                'common_courses': course_names,
                'compatibility': len(common_courses) / len(user_courses) * 100
            })
    
    return sorted(matches, key=lambda x: x['compatibility'], reverse=True)[:10]

# Routes
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
            
            if not user.campus or not user.courses:
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
        
        user.campus = request.form.get('campus')
        user.major = request.form.get('major')
        user.year = request.form.get('year')
        user.study_style = request.form.get('study_style')
        user.preferred_location = request.form.get('preferred_location')
        
        # Clear existing courses
        UserCourse.query.filter_by(user_id=user.id).delete()
        
        # Add new courses
        selected_courses = request.form.getlist('courses')
        for course_code in selected_courses:
            course = Course.query.filter_by(code=course_code).first()
            if course:
                user_course = UserCourse(user_id=user.id, course_id=course.id)
                db.session.add(user_course)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    courses = Course.query.limit(20).all()
    return render_template_string(SETUP_PROFILE_TEMPLATE, courses=courses)

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

# Initialize database
def init_db():
    with app.app_context():
        db.create_all()
        
        if Course.query.count() == 0:
            sample_courses = [
                Course(code='CS101', name='Introduction to Computer Science', department='Computer Science'),
                Course(code='CS225', name='Data Structures', department='Computer Science'),
                Course(code='CS374', name='Algorithms', department='Computer Science'),
                Course(code='MATH221', name='Calculus I', department='Mathematics'),
                Course(code='MATH231', name='Calculus II', department='Mathematics'),
                Course(code='PHYS211', name='University Physics', department='Physics'),
                Course(code='CHEM102', name='General Chemistry', department='Chemistry'),
                Course(code='ENGL101', name='English Composition', department='English'),
                Course(code='HIST101', name='World History', department='History'),
                Course(code='PSYC100', name='Introduction to Psychology', department='Psychology'),
            ]
            
            for course in sample_courses:
                db.session.add(course)
            
            db.session.commit()
            print("Sample courses added to database")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
