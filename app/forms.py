from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User, Quiz, Question
from flask_login import current_user
from app import db, app

import json

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    admin = BooleanField('Admin Account?')
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class UploadForm(FlaskForm):
    quizjson = FileField("Select File to upload", validators=[FileRequired()])
    #uizjsondata = FileField(validators=[FileRequired()])
    submit = SubmitField('Upload JSON')

    def validate_quizjson(self, quizjson):
        try:
            ALLOWED_EXTENSIONS = ['json', 'txt']
            filename = quizjson.data.filename

            if not ('.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
               raise ValidationError('Please upload a json File Format')

            file_content = quizjson.data.read()
            parsed_quiz = json.loads(file_content)
            
            mandatory_fields = ["name", "questions"]
            for key in mandatory_fields:
                if key not in parsed_quiz:
                    raise ValidationError(key + ' is a mandatory field.')

            ques = parsed_quiz['questions']
            if type(ques) != list:
                raise ValidationError('Questions should be list of disctionaries.')

            mandatory_fields_ques = ['type', 'question', 'correct']
            for qu in ques:
                for key in mandatory_fields_ques:
                    if key not in qu:
                        raise ValidationError(key + ' is mandatory for all questions.')
                if type(qu['type']) != int or qu['type'] < 1:
                    raise ValidationError('Question type should always be an integer greater than 0.')
                if 'marks' in qu and (type(qu['marks']) != int or qu['marks'] < 1):
                    raise ValidationError('Question marks should always be an integer greater than 0.')
                if qu['type'] == 1: 
                    if 'options' not in qu:
                        raise ValidationError('options is mandatory for question type 1 (MCQs).')
                    elif type(qu['options']) != list:
                        raise ValidationError('options should be comma sepearted list of values.')
            print('valid json')
            qu_id = Quiz.query.order_by(Quiz.id.desc()).first()
            q_id = 0
            if not qu_id:
                q_id = 1
            else:
                q_id += qu_id.id + 1
            print(q_id)
            print(parsed_quiz['name'])
            print(current_user)
            quiz = Quiz(name=parsed_quiz['name'], author=current_user)
            db.session.add(quiz)
            #db.session.commit()
            for que in ques:
                question = Question(quiz=quiz, ques_type=que['type'], question=que['question'], options=que['options'], correct_answer=que['correct'], marks=que['marks'])
                db.session.add(question)
                #db.session.commit()
            db.session.commit()

        except json.decoder.JSONDecodeError as e:
            raise ValidationError('Invalid JSON File: ' + str(e))