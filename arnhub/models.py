from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.dialects.sqlite import JSON

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_head_admin = db.Column(db.Boolean, default=False)

    # Relationships
    courses = db.relationship('Course', backref='creator', lazy=True)
    lessons_created = db.relationship('Lesson', backref='creator', lazy=True)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=False)

    # Metadata
    category = db.Column(db.String(100))
    difficulty = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lessons = db.relationship('Lesson', backref='course', lazy=True, cascade="all, delete-orphan")


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    title = db.Column(db.String(255), nullable=False)
    video_filename = db.Column(db.String(255))
    sections = db.Column(JSON, nullable=True)

    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)



class AdminRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=False)
    comment = db.Column(db.Text)

    status = db.Column(db.String(20), default="pending")
    user = db.relationship("User", backref="admin_request", lazy=True)