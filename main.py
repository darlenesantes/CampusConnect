from flask import Flask, render_template, redirect, url_for, session, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from pathlib import Path
import os
from datetime import datetime, timedelta
import secrets
import random
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import json

# Load environment variables
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
CORS(app, origins=['http://127.0.0.1:5000/', 'https://seocampusconnect.pythonanywhere.com/'])

# Configuration
app.config['SECRET_KEY'] = secrets.token_hex(16)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/SEOCampusConnect/CampusConnect/purdue_campus_connect.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///purdue_campus_connect.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')
app.config['EMAIL_USER'] = os.getenv('EMAIL_USER')
app.config['EMAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')

# Initialize database
db = SQLAlchemy(app)

# OAuth setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# Simple Database Models (No complex foreign keys)
class SimpleUser(db.Model):
    __tablename__ = 'simple_user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    profile_picture = db.Column(db.String(200))
    major = db.Column(db.String(100))
    year = db.Column(db.String(20))
    preferences = db.Column(db.String(50))  # 'quiet', 'collaborative', 'discussion'
    preferred_location = db.Column(db.String(200))  # Store location name as string
    gpa = db.Column(db.Float)
    bio = db.Column(db.Text)
    profile_completed = db.Column(db.Boolean, default=False)
    is_demo_user = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SimpleCourse(db.Model):
    __tablename__ = 'simple_course'
    id = db.Column(db.Integer, primary_key=True)
    course_number = db.Column(db.String(20), nullable=False)
    course_name = db.Column(db.String(200), nullable=False)
    course_subject = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Integer, default=3)
    description = db.Column(db.Text)

class UserCourseEnrollment(db.Model):
    __tablename__ = 'user_course_enrollment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # No foreign key constraint
    course_id = db.Column(db.Integer, nullable=False)  # No foreign key constraint
    grade_goal = db.Column(db.String(5))

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, nullable=False)
    recipient_id = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    message_type = db.Column(db.String(50), default='general')

class StudyPlan(db.Model):
    __tablename__ = 'study_plan'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, nullable=False)
    exam_name = db.Column(db.String(200), nullable=False)
    exam_date = db.Column(db.DateTime, nullable=False)
    prep_hours_needed = db.Column(db.Integer, default=20)
    hours_completed = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RoomBooking(db.Model):
    __tablename__ = 'room_booking'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    location_name = db.Column(db.String(200), nullable=False)
    room_number = db.Column(db.String(50), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    purpose = db.Column(db.String(200))
    group_size = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='active')  # active, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PurdueLocation(db.Model):
    __tablename__ = 'purdue_location'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    location_type = db.Column(db.String(50), nullable=False)
    building = db.Column(db.String(100))
    hours = db.Column(db.String(200))
    amenities = db.Column(db.Text)
    capacity = db.Column(db.Integer)

# Purdue.io API Integration
class PurdueAPI:
    BASE_URL = "https://api.purdue.io/odata"
    
    @staticmethod
    def get_courses():
        try:
            response = requests.get(f"{PurdueAPI.BASE_URL}/Courses", timeout=15)
            if response.status_code == 200:
                data = response.json()
                return data.get('value', [])
            return None
        except requests.RequestException as e:
            print(f"Error fetching Purdue courses: {e}")
            return None

# Real Purdue Data
PURDUE_DINING_HALLS = [
    {"name": "Wiley Dining Court", "building": "Wiley Residence Hall"},
    {"name": "Windsor Dining Court", "building": "Windsor Halls"},
    {"name": "Earhart Dining Court", "building": "Earhart Residence Hall"},
    {"name": "Hillenbrand Dining Court", "building": "Hillenbrand Residence Hall"},
    {"name": "Ford Dining Court", "building": "Ford Residence Hall"},
    {"name": "On the Go Market - WALC", "building": "WALC"},
]

PURDUE_STUDY_LOCATIONS = [
    {"name": "Hicks Undergraduate Library", "building": "Hicks Library", "capacity": 300},
    {"name": "WALC (Wilmeth Active Learning Center)", "building": "WALC", "capacity": 500},
    {"name": "MATH Library", "building": "Mathematical Sciences Building", "capacity": 100},
    {"name": "Physics Library", "building": "Physics Building", "capacity": 80},
    {"name": "Engineering Library", "building": "Potter Engineering Center", "capacity": 200},
    {"name": "Stewart Center Study Rooms", "building": "Stewart Center", "capacity": 50},
]

PURDUE_MAJORS = [
    "Computer Science", "Electrical Engineering", "Mechanical Engineering", "Civil Engineering",
    "Chemical Engineering", "Aerospace Engineering", "Industrial Engineering", "Biomedical Engineering",
    "Mathematics", "Statistics", "Physics", "Chemistry", "Biology", "Biochemistry",
    "Management", "Economics", "Accounting", "Finance", "Marketing", "Supply Chain Management",
    "Psychology", "Communication", "English", "History", "Political Science", "Sociology"
]

# Helper Functions
def send_email_notification(to_email, subject, message):
    """Send email notification"""
    try:
        if not app.config['EMAIL_USER']:
            return False
        
        msg = MIMEMultipart()
        msg['From'] = app.config['EMAIL_USER']
        msg['To'] = to_email
        msg['Subject'] = f"CampusConnect Purdue: {subject}"
        
        html_body = f"""
        <html><body style="font-family: Arial, sans-serif;">
            <div style="background: #CEB888; padding: 20px; text-align: center;">
                <h1 style="color: white;">CampusConnect Purdue</h1>
            </div>
            <div style="padding: 20px;">
                <h2>{subject}</h2>
                <p>{message}</p>
                <a href="http://localhost:5000/" style="background: #CEB888; color: white; padding: 10px 20px; text-decoration: none;">
                    View on CampusConnect
                </a>
            </div>
        </body></html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(app.config['EMAIL_USER'], app.config['EMAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def get_user_courses(user_id):
    """Get courses for a user"""
    enrollments = UserCourseEnrollment.query.filter_by(user_id=user_id).all()
    courses = []
    for enrollment in enrollments:
        course = SimpleCourse.query.get(enrollment.course_id)
        if course:
            courses.append(course)
    return courses

def find_study_matches(user_id):
    """Find study partners"""
    current_user = SimpleUser.query.get(user_id)
    if not current_user:
        return []
    
    user_courses = [e.course_id for e in UserCourseEnrollment.query.filter_by(user_id=user_id).all()]
    matches = []
    
    # Find users with similar preferences
    potential_matches = SimpleUser.query.filter(
        SimpleUser.id != user_id,
        SimpleUser.preferences == current_user.preferences
    ).limit(20).all()
    
    for match in potential_matches:
        match_courses = [e.course_id for e in UserCourseEnrollment.query.filter_by(user_id=match.id).all()]
        common_courses = set(user_courses) & set(match_courses)
        
        if common_courses:
            course_names = []
            for course_id in list(common_courses)[:3]:
                course = SimpleCourse.query.get(course_id)
                if course:
                    course_names.append(course.course_name)
            
            compatibility = (len(common_courses) / max(len(user_courses), 1)) * 100
            if match.major == current_user.major:
                compatibility += 25
            if match.preferred_location == current_user.preferred_location:
                compatibility += 15
            
            matches.append({
                'user': match,
                'common_courses': course_names,
                'compatibility': min(compatibility, 100),
                'same_major': match.major == current_user.major,
                'same_location': match.preferred_location == current_user.preferred_location
            })
    
    # Add backup matches
    if len(matches) < 6:
        backup_matches = SimpleUser.query.filter(
            SimpleUser.id != user_id,
            SimpleUser.major == current_user.major,
            SimpleUser.id.notin_([m['user'].id for m in matches])
        ).limit(8 - len(matches)).all()
        
        for match in backup_matches:
            matches.append({
                'user': match,
                'common_courses': ["Similar interests"],
                'compatibility': random.randint(60, 85),
                'same_major': True,
                'same_location': match.preferred_location == current_user.preferred_location
            })
    
    matches.sort(key=lambda x: x['compatibility'], reverse=True)
    return matches[:8]

def create_demo_users():
    """Create demo users"""
    if SimpleUser.query.filter_by(is_demo_user=True).count() >= 20:
        return
    
    demo_names = ["Alex Chen", "Sarah Johnson", "Michael Rodriguez", "Emily Davis", "James Wilson",
                  "Jessica Garcia", "David Kim", "Amanda Miller", "Ryan Thompson", "Lauren Brown"]
    
    courses = SimpleCourse.query.all()
    locations = [loc.name for loc in PurdueLocation.query.all()]
    
    for i in range(20):
        demo_user = SimpleUser(
            name=random.choice(demo_names),
            email=f"demo{i}@purdue.edu",
            major=random.choice(PURDUE_MAJORS),
            year=random.choice(['Freshman', 'Sophomore', 'Junior', 'Senior']),
            preferences=random.choice(['quiet', 'collaborative', 'discussion']),
            preferred_location=random.choice(locations) if locations else None,
            gpa=round(random.uniform(2.5, 4.0), 2),
            bio=f"Purdue Boilermaker studying {random.choice(PURDUE_MAJORS)}. Looking for study partners!",
            profile_completed=True,
            is_demo_user=True
        )
        
        db.session.add(demo_user)
        db.session.flush()
        
        # Add courses
        if courses:
            selected_courses = random.sample(courses, min(random.randint(3, 5), len(courses)))
            for course in selected_courses:
                enrollment = UserCourseEnrollment(
                    user_id=demo_user.id,
                    course_id=course.id,
                    grade_goal=random.choice(['A', 'A-', 'B+', 'B'])
                )
                db.session.add(enrollment)
    
    db.session.commit()

def init_db():
    """Initialize database"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Add Purdue locations
        for dining in PURDUE_DINING_HALLS:
            location = PurdueLocation(
                name=dining["name"],
                location_type="dining",
                building=dining["building"],
                hours="7:00 AM - 10:00 PM",
                amenities="Dining, WiFi, Study Space"
            )
            db.session.add(location)
        
        for study in PURDUE_STUDY_LOCATIONS:
            location = PurdueLocation(
                name=study["name"],
                location_type="library",
                building=study["building"],
                capacity=study["capacity"],
                amenities="WiFi, Study Space, Group Rooms"
            )
            db.session.add(location)
        
        db.session.commit()
        
        # Add courses from Purdue API
        print("Fetching Purdue courses...")
        with open('purdue_courses.json', 'r') as file:
            data = json.load(file)

        purdue_courses = data.get('value', [])
        
        added_courses = set()
        if purdue_courses:
            for course_data in purdue_courses[:50]:
                try:
                    course_number = course_data.get('Number', 'UNKNOWN')
                    if course_number in added_courses or course_number == 'UNKNOWN':
                        continue
                    
                    subject_info = course_data.get('Subject', {})
                    subject_abbrev = subject_info.get('Abbreviation', 'UNK') if isinstance(subject_info, dict) else 'UNK'
                    
                    course = SimpleCourse(
                        course_number=course_number,
                        course_name=course_data.get('Title', 'Unknown Course')[:200],
                        course_subject=subject_abbrev,
                        credits=int(course_data.get('CreditHours', 3) or 3),
                        description=course_data.get('Description', '')[:500] if course_data.get('Description') else ''
                    )
                    
                    db.session.add(course)
                    added_courses.add(course_number)
                    
                except Exception as e:
                    print(f"Error adding course: {e}")
                    continue
        
        # Add fallback courses
        fallback_courses = [
            ("CS180", "Problem Solving And Object-Oriented Programming", "CS"),
            ("CS240", "Programming in C", "CS"),
            ("CS251", "Data Structures and Algorithms", "CS"),
            ("MA161", "Plane Analytic Geometry And Calculus I", "MA"),
            ("PHYS172", "Modern Mechanics", "PHYS"),
            ("CHEM115", "General Chemistry", "CHEM"),
            ("ENGL106", "First-Year Composition", "ENGL"),
            ("ECON251", "Microeconomics", "ECON"),
        ]
        
        for number, name, subject in fallback_courses:
            if number not in added_courses:
                course = SimpleCourse(
                    course_number=number,
                    course_name=name,
                    course_subject=subject,
                    credits=3
                )
                db.session.add(course)
        
        db.session.commit()
        create_demo_users()
        
        print("Purdue database initialized!")
        print(f"Created: {SimpleCourse.query.count()} courses, {PurdueLocation.query.count()} locations, {SimpleUser.query.filter_by(is_demo_user=True).count()} demo users")
        print("Room booking system ready!")

# Routes
@app.route('/')
def index():
    init_db()
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

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
            user = SimpleUser.query.filter_by(email=user_info['email']).first()
            
            if not user:
                user = SimpleUser(
                    name=user_info['name'],
                    email=user_info['email'],
                    profile_picture=user_info.get('picture', ''),
                    preferences='quiet',
                    profile_completed=False
                )
                db.session.add(user)
                db.session.commit()
            
            session['user'] = {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'profile_picture': user.profile_picture
            }
            
            if not user.profile_completed:
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
        user = SimpleUser.query.get(user_id)
        
        user.major = request.form.get('major')
        user.year = request.form.get('year')
        user.preferences = request.form.get('preferences')
        user.preferred_location = request.form.get('preferred_location')
        user.gpa = float(request.form.get('gpa')) if request.form.get('gpa') else None
        user.bio = request.form.get('bio')
        user.profile_completed = True
        
        # Clear existing courses and add new ones
        UserCourseEnrollment.query.filter_by(user_id=user.id).delete()
        
        selected_courses = request.form.getlist('courses')
        for course_id in selected_courses:
            if course_id:
                enrollment = UserCourseEnrollment(user_id=user.id, course_id=int(course_id))
                db.session.add(enrollment)
        
        db.session.commit()
        flash('Profile updated successfully! Finding your study matches...', 'success')
        return redirect(url_for('dashboard'))
    
    majors = PURDUE_MAJORS
    courses = SimpleCourse.query.limit(40).all()
    locations = PurdueLocation.query.all()
    
    return render_template('setup_profile.html', majors=majors, courses=courses, locations=locations)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    user_id = session['user']['id']
    user = SimpleUser.query.get(user_id)
    
    if not user.profile_completed:
        return redirect(url_for('setup_profile'))
    
    matches = find_study_matches(user_id)
    user.courses = get_user_courses(user_id)  # Add courses for template
    unread_messages = Message.query.filter_by(recipient_id=user_id, is_read=False).count()
    upcoming_exams = StudyPlan.query.filter_by(user_id=user_id).filter(StudyPlan.exam_date > datetime.now()).limit(3).all()
    
    return render_template('dashboard.html', user=user, matches=matches, unread_messages=unread_messages, upcoming_exams=upcoming_exams)

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    try:
        data = request.get_json()
        sender_id = session['user']['id']
        recipient_id = data.get('recipient_id')
        subject = data.get('subject', 'Study Partner Message')
        content = data.get('content')
        
        message = Message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            subject=subject,
            content=content,
            message_type=data.get('message_type', 'general')
        )
        db.session.add(message)
        
        # Send email notification
        recipient = SimpleUser.query.get(recipient_id)
        sender = SimpleUser.query.get(sender_id)
        
        if recipient and sender:
            email_content = f"You have a new message from {sender.name}: {content}"
            send_email_notification(recipient.email, subject, email_content)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Message sent successfully!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/study_planner')
def study_planner():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    user_id = session['user']['id']
    study_plans = StudyPlan.query.filter_by(user_id=user_id).order_by(StudyPlan.exam_date).all()
    
    # Add course info to study plans
    for plan in study_plans:
        plan.course = SimpleCourse.query.get(plan.course_id)
    
    courses = get_user_courses(user_id)
    
    return render_template('study_planner.html', study_plans=study_plans, courses=courses, now=datetime.now)

@app.route('/create_study_plan', methods=['POST'])
def create_study_plan():
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    try:
        data = request.get_json()
        user_id = session['user']['id']
        
        study_plan = StudyPlan(
            user_id=user_id,
            course_id=data.get('course_id'),
            exam_name=data.get('exam_name'),
            exam_date=datetime.strptime(data.get('exam_date'), '%Y-%m-%d'),
            prep_hours_needed=data.get('prep_hours_needed', 20)
        )
        
        db.session.add(study_plan)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Study plan created successfully!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/messages')
def messages():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    user_id = session['user']['id']
    received_messages = Message.query.filter_by(recipient_id=user_id).order_by(Message.timestamp.desc()).all()
    sent_messages = Message.query.filter_by(sender_id=user_id).order_by(Message.timestamp.desc()).all()
    
    # Add sender/recipient info
    for msg in received_messages:
        msg.sender = SimpleUser.query.get(msg.sender_id)
    for msg in sent_messages:
        msg.recipient = SimpleUser.query.get(msg.recipient_id)
    
    Message.query.filter_by(recipient_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()
    
    return render_template('messages.html', received_messages=received_messages, sent_messages=sent_messages)

@app.route('/log_study_hours', methods=['POST'])
def log_study_hours():
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    try:
        data = request.get_json()
        plan_id = data.get('plan_id')
        hours = float(data.get('hours', 0))
        
        if hours <= 0:
            return jsonify({'success': False, 'error': 'Hours must be greater than 0'})
        
        study_plan = StudyPlan.query.get(plan_id)
        if not study_plan:
            return jsonify({'success': False, 'error': 'Study plan not found'})
        
        if study_plan.user_id != session['user']['id']:
            return jsonify({'success': False, 'error': 'Unauthorized'})
        
        # Add hours to the plan
        study_plan.hours_completed += hours
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Logged {hours} hours successfully!',
            'total_hours': study_plan.hours_completed,
            'progress_percent': min((study_plan.hours_completed / study_plan.prep_hours_needed) * 100, 100)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/book_room', methods=['POST'])
def book_room():
    """Book a study room"""
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    try:
        data = request.get_json()
        user_id = session['user']['id']
        
        # Validate booking data
        required_fields = ['location_name', 'room_number', 'booking_date', 'start_time', 'end_time', 'group_size']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing {field}'})
        
        booking_date = datetime.strptime(data['booking_date'], '%Y-%m-%d').date()
        start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        
        # Check for conflicts
        existing_booking = RoomBooking.query.filter_by(
            location_name=data['location_name'],
            room_number=data['room_number'],
            booking_date=booking_date,
            status='active'
        ).filter(
            ((RoomBooking.start_time <= start_time) & (RoomBooking.end_time > start_time)) |
            ((RoomBooking.start_time < end_time) & (RoomBooking.end_time >= end_time)) |
            ((RoomBooking.start_time >= start_time) & (RoomBooking.end_time <= end_time))
        ).first()
        
        if existing_booking:
            return jsonify({'success': False, 'error': 'Room is already booked for this time slot'})
        
        # Create booking
        booking = RoomBooking(
            user_id=user_id,
            location_name=data['location_name'],
            room_number=data['room_number'],
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            purpose=data.get('purpose', ''),
            group_size=int(data['group_size'])
        )
        
        db.session.add(booking)
        db.session.commit()
        
        # Send confirmation email
        user = SimpleUser.query.get(user_id)
        if user:
            email_subject = f"Room Booking Confirmation - {data['room_number']}"
            email_content = f"""
            Your study room has been successfully booked!
            
            Details:
            • Room: {data['room_number']} at {data['location_name']}
            • Date: {booking_date.strftime('%B %d, %Y')}
            • Time: {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}
            • Group Size: {data['group_size']} people
            • Purpose: {data.get('purpose', 'Study session')}
            
            Please arrive on time and follow all library policies. Boiler Up!
            """
            send_email_notification(user.email, email_subject, email_content)
        
        return jsonify({
            'success': True, 
            'message': 'Room booked successfully!',
            'booking_id': booking.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/my_bookings')
def my_bookings():
    """View user's room bookings"""
    if 'user' not in session:
        return redirect(url_for('index'))
    
    user_id = session['user']['id']
    
    # Get upcoming bookings
    upcoming_bookings = RoomBooking.query.filter_by(
        user_id=user_id, 
        status='active'
    ).filter(
        RoomBooking.booking_date >= datetime.now().date()
    ).order_by(RoomBooking.booking_date, RoomBooking.start_time).all()
    
    # Get past bookings (last 30 days)
    past_date = datetime.now().date() - timedelta(days=30)
    past_bookings = RoomBooking.query.filter_by(
        user_id=user_id
    ).filter(
        RoomBooking.booking_date >= past_date,
        RoomBooking.booking_date < datetime.now().date()
    ).order_by(RoomBooking.booking_date.desc(), RoomBooking.start_time.desc()).all()
    
    return render_template('my_bookings.html', 
                         upcoming_bookings=upcoming_bookings, 
                         past_bookings=past_bookings,
                         now=datetime.now())

@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    """Cancel a room booking"""
    if 'user' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    try:
        booking = RoomBooking.query.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'error': 'Booking not found'})
        
        if booking.user_id != session['user']['id']:
            return jsonify({'success': False, 'error': 'Unauthorized'})
        
        # Can only cancel future bookings
        booking_datetime = datetime.combine(booking.booking_date, booking.start_time)
        if booking_datetime <= datetime.now():
            return jsonify({'success': False, 'error': 'Cannot cancel past bookings'})
        
        booking.status = 'cancelled'
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Booking cancelled successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/find_study_rooms')
def find_study_rooms():
    """Get available study rooms at Purdue with real booking status"""
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    # Get study locations from database
    study_locations = PurdueLocation.query.filter_by(location_type='library').all()
    
    # Get current date and time for availability checking
    current_date = datetime.now().date()
    current_time = datetime.now().time()
    
    rooms = []
    for location in study_locations:
        available_rooms = []
        room_count = min(location.capacity // 20, 8)  # Estimate rooms based on capacity
        
        for i in range(1, room_count + 1):
            room_number = f'Room {i:03d}'
            
            # Check if room is currently booked
            current_booking = RoomBooking.query.filter_by(
                location_name=location.name,
                room_number=room_number,
                booking_date=current_date,
                status='active'
            ).filter(
                RoomBooking.start_time <= current_time,
                RoomBooking.end_time > current_time
            ).first()
            
            # Check next available slot
            next_booking = RoomBooking.query.filter_by(
                location_name=location.name,
                room_number=room_number,
                booking_date=current_date,
                status='active'
            ).filter(
                RoomBooking.start_time > current_time
            ).order_by(RoomBooking.start_time).first()
            
            status = 'booked' if current_booking else 'available'
            next_available = None
            if current_booking and next_booking:
                next_available = current_booking.end_time.strftime('%I:%M %p')
            elif current_booking:
                next_available = current_booking.end_time.strftime('%I:%M %p')
            
            available_rooms.append({
                'room_number': room_number,
                'capacity': random.choice([4, 6, 8, 12]),
                'status': status,
                'next_available': next_available,
                'current_booking': {
                    'user': f"User {current_booking.user_id}" if current_booking else None,
                    'end_time': current_booking.end_time.strftime('%I:%M %p') if current_booking else None,
                    'purpose': current_booking.purpose if current_booking else None
                } if current_booking else None,
                'amenities': location.amenities.split(', ') if location.amenities else []
            })
        
        rooms.append({
            'location': location.name,
            'building': location.building,
            'rooms': available_rooms
        })
    
    return jsonify({'study_locations': rooms})

@app.route('/get_user_profile/<int:user_id>')
def get_user_profile(user_id):
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user = SimpleUser.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user_courses = get_user_courses(user_id)
    
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'major': user.major,
        'year': user.year,
        'preferences': user.preferences,
        'preferred_location': user.preferred_location,
        'gpa': user.gpa,
        'bio': user.bio,
        'courses': [{'course_number': c.course_number, 'course_name': c.course_name} for c in user_courses]
    })

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out. Boiler Up!', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
