"""Unit tests for database helper functions in a Flask application."""
import unittest
from flask import Flask
from datetime import datetime

from app.database import db
from app.database.user import User
from app.database.course import Course
from app.database.studysession import StudySession
from app.database.helpers import (
    enroll_user_in_course,
    remove_user_from_course,
    get_user_courses,
    mark_profile_complete,
    create_study_session,
    get_user_study_sessions,
    get_course_study_sessions,
    join_study_session,
    leave_study_session
)

class HelpersTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db.init_app(self.app)
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        self.user = User(name="Darlene", email="darlenesantes@utexas.edu", preferences="quiet")
        self.course = Course(course_number="12345", course_name="MIS 325", course_subject="MIS")

        db.session.add(self.user)
        db.session.add(self.course)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_enroll_user_in_course(self):
        """Test enrolling a user in a course."""
        result = enroll_user_in_course(self.user.id, self.course.id)
        self.assertTrue(result)
        self.assertIn(self.course, self.user.courses)

    def test_remove_user_from_course(self):
        """Test removing a user from a course."""
        self.user.courses.append(self.course)
        db.session.commit()

        result = remove_user_from_course(self.user.id, self.course.id)
        self.assertTrue(result)
        self.assertNotIn(self.course, self.user.courses)

    def test_get_user_courses(self):
        """Test getting all courses a user is enrolled in."""
        self.user.courses.append(self.course)
        db.session.commit()

        courses = get_user_courses(self.user.id)
        self.assertEqual(len(courses), 1)
        self.assertEqual(courses[0].course_name, "MIS 325")

    def test_mark_profile_complete(self):
        """Test marking a user's profile as complete."""
        self.assertFalse(self.user.profile_completed)
        result = mark_profile_complete(self.user.id)
        self.assertTrue(result)
        db.session.refresh(self.user)
        self.assertTrue(self.user.profile_completed)

    def test_create_study_session(self):
        """Test creating a study session."""
        result = create_study_session(
            course_id=self.course.id,
            creator_id=self.user.id,
            location="PCL",
            time=datetime.now(),
            duration=90,
            session_type="quiet"
        )
        self.assertTrue(result)
        sessions = StudySession.query.filter_by(course_id=self.course.id).all()
        self.assertEqual(len(sessions), 1)

    def test_get_user_study_sessions(self):
        """Test getting all study sessions created by a user."""
        # Create 2 sessions by the user
        for _ in range(2):
            create_study_session(
                course_id=self.course.id,
                creator_id=self.user.id,
                location="PCL",
                time=datetime.now(),
                duration=90,
                session_type="quiet"
            )

        sessions = get_user_study_sessions(self.user.id)
        self.assertEqual(len(sessions), 2)
        self.assertEqual(sessions[0].creator_id, self.user.id)

    def test_get_course_study_sessions(self):
        """Test getting all study sessions for a specific course."""
        create_study_session(
            course_id=self.course.id,
            creator_id=self.user.id,
            location="PCL",
            time=datetime.now(),
            duration=60,
            session_type="collaborative"
        )

        sessions = get_course_study_sessions(self.course.id)
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0].location, "PCL")

    def test_join_and_leave_study_session(self):
        """Test joining and leaving a study session."""
        result = create_study_session(
            course_id=self.course.id,
            creator_id=self.user.id,
            location="PCL",
            time=datetime.now(),
            duration=60,
            session_type="collaborative"
        )

        self.assertTrue(result)

        session = StudySession.query.first()

        joined = join_study_session(session.id, self.user.id)
        self.assertTrue(joined)
        db.session.refresh(session)
        self.assertIn(self.user, session.participants)

        left = leave_study_session(session.id, self.user.id)
        self.assertTrue(left)
        db.session.refresh(session)
        self.assertNotIn(self.user, session.participants)

    def test_double_join_study_session(self):
        """Test that a user cannot join the same study session twice."""
        result = create_study_session(
            course_id=self.course.id,
            creator_id=self.user.id,
            location="PCL",
            time=datetime.now(),
            duration=60,
            session_type="collaborative"
        )
        self.assertTrue(result)

        session = StudySession.query.first()

        joined_first = join_study_session(session.id, self.user.id)
        self.assertTrue(joined_first)

        joined_second = join_study_session(session.id, self.user.id)
        self.assertFalse(joined_second)  # Should return False since already joined
