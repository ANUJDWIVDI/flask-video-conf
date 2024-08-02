#Define your SQLAlchemy models here (e.g., User, Meeting, Attendance, Chat). Each model represents a table in your database and includes relationships between tables.# models.py

from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    meetings = db.relationship('Meeting', backref='host', lazy=True)
    attendances = db.relationship('Attendance', backref='user', lazy=True)
    chats = db.relationship('Chat', backref='user', lazy=True)

class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    code = db.Column(db.String(9), unique=True, nullable=False)
    invitees = db.Column(db.Text, nullable=False)
    attendances = db.relationship('Attendance', backref='meeting', lazy=True)
    chats = db.relationship('Chat', backref='meeting', lazy=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meeting.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(10), nullable=False)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meeting.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
