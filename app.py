import random
import copy
from questions import questions
from flask import render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Length, Email, ValidationError
from QuizApp import User
from appInit import app, db
import database
from flask_bcrypt import Bcrypt
from flask_login import login_user, current_user, logout_user

bcrypt = Bcrypt(app)

database.createdb()


class loginForm(FlaskForm):
    email = StringField('Email Address', validators=[Email('Email is REQUIRED!'),
                                                     Length(min=6, max=35)])

    password = PasswordField('Password', validators=[InputRequired('Password is REQUIRED!'),
                                                     Length(min=8, message='Must be one Uppercase letter and one number'
                                                                           ' and symbol ')])
    remember = BooleanField('Remember Me')
    recaptcha = RecaptchaField()


class RegisterForm(FlaskForm):
    username = StringField('Name', validators=[InputRequired('A name is REQUIRED!'),
                                               Length(min=5, max=20, message='Must be filled')])

    password = PasswordField('Password', validators=[InputRequired('Password is REQUIRED!'),
                                                     Length(min=8, message='Must be one Uppercase letter and one number'
                                                                           ' and symbol ')])

    email = StringField('Email Address', validators=[Email('Email is REQUIRED!'),
                                                     Length(min=6, max=35)])

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already in use.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


@app.route('/')
def base():
    return render_template('main.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('base'))
    login = loginForm()

    if login.validate_on_submit():
        user = User.query.filter_by(email=format(login.email.data)).first()
        if user == None:
            flash(u'Email or password wrong', category='success')
        else:
            if user and bcrypt.check_password_hash(user.password, login.password.data):
                login_user(user, remember=login.remember.data)
                flash(u'Welcome {user.username}', category='success')
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                else:
                    return redirect(url_for('base'))
            else:
                flash(u'Email or password wrong', category='success')
    return render_template('login.html', login=login)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('base'))
    register = RegisterForm()
    if register.validate_on_submit():
        user = User()
        if User.query.filter_by(email=format(register.email.data)).first() == None:
            user.username = format(register.username.data)
            user.email = format(register.email.data)
            user.password = bcrypt.generate_password_hash(format(register.password.data), 10)
            db.session.add(user)
            db.session.commit()
            flash(u'Account created for {register.username.data}!', category='success')
            return redirect(url_for('login'))
        else:
            flash(u'This user already exist', category='success')
    return render_template('register.html', register=register)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('base'))


questions = copy.deepcopy(questions)


def my_shuffle(array):
    random.shuffle(array)

    return array


@app.route('/quiz', methods=['GET'])
def quiz():
    # Shuffle options
    i = 0
    while i < len(questions):
        questions[i]['options'] = my_shuffle(questions[i]['options'])
        i = i + 1

    # Shuffle questions
    questions_shuffled = my_shuffle(questions)

    return render_template('quiz.html', q=questions_shuffled, t='7 Wonders of the World')


@app.route('/result', methods=['POST'])
def result_quiz():
    correct = 0
    i = 0
    while i < len(questions):
        answered = request.form.get(str(questions[i]['id']))
        if questions[i]['correct_answer'] == answered:
            correct = correct + 1
        i = i + 1

    return render_template('result.html', c=correct, t=len(questions))


if __name__ == '__main__':
    app.run(debug=True)
