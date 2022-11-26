from flask import flash, redirect, render_template, url_for
from app import app
from app.forms import LoginForm, RegisterForm

@app.route('/')
@app.route('/landing')
def landing():
    user = {'username': 'Miguel'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title="Welcome")

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    #Post Method
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('landing'))
    return render_template('login.html', title='Log In', form=form)


@app.route('/register', methods=["GET", "POST"] )
def register():
    form = RegisterForm()
    #Post Method
    if form.validate_on_submit():
        flash('Account requested for user {}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('landing'))
    return render_template('register.html', title='Register', form=form)

@app.route('/mission')
def mission():
    return render_template('mission.html', title="Our Mission")