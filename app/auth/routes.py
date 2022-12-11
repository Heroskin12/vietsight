from flask import abort, flash, redirect, render_template, request, url_for
from app.translate import translate
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import get_locale
from app import db
from app.auth.email import send_password_reset_email
from app.models import User
from langdetect import detect, LangDetectException
from werkzeug.urls import url_parse
from app.auth import bp
from app.auth.forms import LoginForm, RegisterForm, \
    ResetPasswordRequestForm, ResetPasswordForm

# Routes
@bp.route('/mission')
def mission():
    return render_template('auth/mission.html', title="Our Mission")

@bp.route('/login', methods=["GET", "POST"])
def login():

    # If the user is already logged in.
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()

    #Post Method
    if form.validate_on_submit():
        # Returns the first result of any matching username.
        user = User.query.filter_by(username = form.username.data).first()

        # If there is no matching username, or if the password doesn't match the one stored in the user object.
        if user is None or not user.check_password(form.password.data):
            flash('Invaid username or password.')
            return redirect(url_for('auth.login'))
        
        # If all good, log the user in. If they reached login from an inauthenticated view, send them back there. If not, send them to home page.
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.home')
        return redirect(next_page)
        

    return render_template('auth/login.html', title='Log In', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.landing'))


@bp.route('/register', methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegisterForm()
    #Post Method
    if form.validate_on_submit():
        # Create the user object.
        user = User(
            firstName = form.first_name.data,
            lastName = form.last_name.data,
            username = form.username.data,
            email = form.email.data
            )
        # Hash the password before storing.
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)





