import os
import json
from app import app, db
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, UploadForm
from app.models import User, Quiz, Question
from werkzeug.urls import url_parse
#from werkzeug.utils import secure_filename


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template("index.html", title='Home Page')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid Username or Password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title="Sign In", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data,
            fname=form.fname.data, lname=form.lname.data, admin=form.admin.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    # TODO: add logic for quizzes answered and created
    return render_template('user.html', user=user)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if not current_user.admin:
        return redirect(url_for('index'))
    form = UploadForm()
    # f = form.quizjsondata.data = form.quizjson.data
    if form.validate_on_submit():
        #f = form.quizjson.data
        #content = f.read()

        #print(f.filename)
        #print(content)

        #filename = secure_filename(f.filename)
        #f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        #data = json.loads(content)
        #q_id = Quiz.query.order_by(Quiz.id.desc()).first()
        #if not q_id:
        #    q_id = 1
        #else:
        #    q_id += 1
        #quiz = Quiz(id=q_id, name=data['name'], created_by=current_user)
        #db.session.add(quiz)
        #ques = data['questions']
        #for que in ques:
        #    question = Question(quiz_id=q_id, ques_type=que['type'], question=que['question'], options=que['options'], correct_answer=que['correct'], marks=que['marks'])
        #    db.session.add(question)
        #db.session.commit()
        return redirect(url_for('index'))
    return render_template('upload.html', form=form)