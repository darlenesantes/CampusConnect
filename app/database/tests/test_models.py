""" This is where we define tests for our database models """
# test_models.py
import unittest
from flask import Flask
from datetime import datetime

from app.database import db
from app.database.course import Course, enrollments
from app.database.user import User
from app.database.studysession import StudySession

class ModelsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['TESTING'] = True

        db.init_app(self.app)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_user(self):
        user = User(name = 'Test User', email = 'test@example.com', preferences = 'quiet')
        db.session.add(user)
        db.session.commit()
        self.assertIsNotNone(user.id)
        self.assertEqual(user.name, 'Test User')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.preferences, 'quiet')

    def test_duplicate_user_email(self):
        user1 = User(name='User A', email='duplicate@example.com', preferences='quiet')
        user2 = User(name='User B', email='duplicate@example.com', preferences='loud')
        db.session.add(user1)
        db.session.commit()
        db.session.add(user2)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_create_course(self):
        course = Course(course_number='12345', course_name='Test Course', course_subject='Test Subject')
        db.session.add(course)
        db.session.commit()
        self.assertIsNotNone(course.id)
        self.assertEqual(course.course_number, '12345')
        self.assertEqual(course.course_name, 'Test Course')
        self.assertEqual(course.course_subject, 'Test Subject')

    def test_user_course_enrollment(self):
        user = User(name='Test User', email='test@example.com', preferences='collaborative')
        course = Course(course_number='12345', course_name='Test Course', course_subject='Test Subject')
        db.session.add(user)
        db.session.add(course)
        db.session.commit()

        user.courses.append(course)
        db.session.commit()

        self.assertIsNotNone(user.id)
        self.assertIsNotNone(course.id)

        self.assertIn(course, user.courses)
        self.assertIn(user, course.users)

    def test_create_study_session(self):
        user = User(name='Test User', email='test@example.com', preferences='collaborative')
        course = Course(course_number='12345', course_name='Test Course', course_subject='Test Subject')
        db.session.add(user)
        db.session.add(course)
        db.session.commit()

        study_session = StudySession(location='Library', time=datetime.now(), duration=60, session_type='collaborative', course_id=course.id, creator_id=user.id)
        db.session.add(study_session)
        db.session.commit()

        self.assertIsNotNone(study_session.id)
        self.assertEqual(study_session.location, 'Library')
        self.assertEqual(study_session.time, study_session.time)
        self.assertEqual(study_session.duration, 60)
        self.assertEqual(study_session.session_type, 'collaborative')
        self.assertEqual(study_session.course_id, course.id)
        self.assertEqual(study_session.creator_id, user.id)

    def test_remove_user_course_enrollment(self):
        user = User(name='Test User', email='example@example.com', preferences='collaborative')
        course = Course(course_number='12345', course_name='Test Course', course_subject='Test Subject')
        db.session.add(user)
        db.session.add(course)
        db.session.commit()

        user.courses.append(course)
        db.session.commit()

        self.assertIn(course, user.courses)

        user.courses.remove(course)
        db.session.commit()

        self.assertNotIn(course, user.courses)
