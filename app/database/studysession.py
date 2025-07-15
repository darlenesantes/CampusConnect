# Contains database models and queries related to study groups
# Ex: StudyGroup model, queries for creating and fetching study groups

from . import db

class StudySession(db.Model):
    __tablename__ = 'study_sessions'

    #id -> primary key
    # course_id -> foreign key to Course
    # creator_id -> foreign key to User

    # Session details (columns)
    # location
    # time
    # duration
    # type (quiet, collaborative, etc.)

    # relationships
    # course
    # creator (user who created the session)
    # participants (users who joined the session)