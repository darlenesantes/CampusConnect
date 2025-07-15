""" This module contains helper functions for database operations. """
# helpers.py

from app.database import db
from app.database.user import User
from app.database.course import Course
from app.database.studysession import StudySession
# from datetime import datetime -> If we want to make current time default or something

# User and course enrollments
def enroll_user_in_course(user_id, course_id):
    """Enroll a user in a course."""
    user = db.session.get(User, user_id)
    course = db.session.get(Course, course_id)

    # Check if user and course exist
    if not user or not course:
        print("User or Course not found.")
        return False

    # Check if user is already enrolled in the course
    if course in user.courses:
        print("User is already enrolled in this course.")
        return False

    # Enroll user in the course
    user.courses.append(course)
    db.session.commit()
    print("User enrolled in course successfully.")
    return True

def remove_user_from_course(user_id, course_id):
    """Remove a user from a course."""
    user = db.session.get(User, user_id)
    course = db.session.get(Course, course_id)

    # Check if user and course exist
    if not user or not course:
        print("User or Course not found.")
        return False

    # Check if user is enrolled in the course
    if course not in user.courses:
        print("User is not enrolled in this course.")
        return False

    # Remove user from the course
    user.courses.remove(course)
    db.session.commit()
    print("User removed from course successfully.")
    return True

def get_user_courses(user_id):
    """Get all courses a user is enrolled in."""
    user = db.session.get(User, user_id)

    # Check if user exists
    if not user:
        print("User not found.")
        return []

    # Get all courses the user is enrolled in
    courses = user.courses
    if not courses:
        print("No courses found for this user.")
        return []
    return courses

# profile set up
def mark_profile_complete(user_id):
    """Mark a user's profile as complete."""
    user = db.session.get(User, user_id)

    # Check if user exists
    if not user:
        print("User not found.")
        return False

    # Mark the profile as complete
    user.profile_completed = True
    db.session.commit()
    print("User profile marked as complete.")
    return True

# Study Session Management
def create_study_session(course_id, creator_id, location, time, duration, session_type):
    """Create a new study session."""
    user = db.session.get(User, creator_id)
    course = db.session.get(Course, course_id)

    # Check if user and course exist
    if not user or not course:
        print("User or Course not found.")
        return False

    # Create the study session
    session = StudySession(
        course_id=course.id,
        creator_id=user.id,
        location=location,
        time=time,
        duration=duration,
        session_type=session_type
    )

    db.session.add(session)
    db.session.commit()
    print("Study session created successfully. Session ID: " + str(session.id))
    return True

def get_user_study_sessions(user_id):
    """Get all study sessions created by a user."""
    user = db.session.get(User, user_id)

    # Check if user exists
    if not user:
        print("User not found.")
        return []

    # Get all study sessions created by the user
    sessions = StudySession.query.filter_by(creator_id=user.id).all()
    if not sessions:
        print("No study sessions found for this user.")
        return []
    return sessions

def get_course_study_sessions(course_id):
    """Get all study sessions for a specific course."""
    course = db.session.get(Course, course_id)

    # Check if course exists
    if not course:
        print("Course not found.")
        return []

    # Get all study sessions for the course
    sessions = StudySession.query.filter_by(course_id=course.id).all()
    if not sessions:
        print("No study sessions found for this course.")
        return []
    return sessions
