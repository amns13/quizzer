from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from datetime import datetime
from hashlib import md5

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(64), nullable=False)
    lname = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    admin = db.Column(db.Boolean, default=False)
    quizzes_created = db.relationship('Quiz', backref='author', lazy=True)
    quizzes_attempted = db.relationship('Attempt', backref='candidate', lazy=True)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), index=True) #, default=current_user.id)
    created_on = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime)
    tags = db.Column(db.JSON, nullable=True)
    questions = db.relationship('Question', backref='quiz', lazy=True)
    attempts = db.relationship('Attempt', backref='quiz', lazy=True)

    def __repr__(self):
        return '<Quiz {}>'.format(self.name)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False, index=True)
    ques_type = db.Column(db.Integer, nullable=False)
    #ques_json = db.Column(db.JSON, nullable=False)
    question = db.Column(db.String(255), nullable=False)
    options = db.Column(db.JSON, nullable=True)
    correct_answer = db.Column(db.String(64), nullable=False)
    marks = db.Column(db.Integer, default=1)

    def __repr__(self):
        return '<Question {}>'.format(self.question)

class Attempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True) #, default=current_user.id)
    response = db.Column(db.JSON, nullable=True)
    score = db.Column(db.Integer, default=0)
    comments = db.Column(db.String(256), nullable=True)

    def __repr__(self):
        return '<Attempt {}>'.format(self.id)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))