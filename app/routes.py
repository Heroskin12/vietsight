from datetime import datetime
from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user, login_required
import imghdr
import os
from app import app, db
from app.forms import LoginForm, RegisterForm, UploadForm
from app.models import User, Post
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

# Update the 'last seen' time for user each time they make a request.
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.lastSeen = datetime.utcnow()
        db.session.commit()
    
# A function to validate the file type of an image.
def validate_image(stream):
    header = stream.read(512) # Read 512 bytes of the file. This is enough to validate format.
    stream.seek(0) # Reset stream pointer so save function can see all bytes.
    format = imghdr.what(None, header) # Reads img in memory. Returns detected image format or None if format unknown.
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg') # Accounts for jpeg exception where jpg extension used.

# Routes
@app.route('/')
@app.route('/landing')
def landing():
    
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

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    return render_template('index.html', title="Welcome")

@app.route('/login', methods=["GET", "POST"])
def login():

    # If the user is already logged in.
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    #Post Method
    if form.validate_on_submit():
        # Returns the first result of any matching username.
        user = User.query.filter_by(username = form.username.data).first()

        # If there is no matching username, or if the password doesn't match the one stored in the user object.
        if user is None or not user.check_password(form.password.data):
            flash('Invaid username or password.')
            return redirect(url_for('login'))
        
        # If all good, log the user in. If they reached login from an inauthenticated view, send them back there. If not, send them to home page.
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
        

    return render_template('login.html', title='Log In', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))


@app.route('/register', methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('home'))

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
        return redirect(url_for('login'))
        
    return render_template('register.html', title='Register', form=form)

@app.route('/mission')
def mission():
    return render_template('mission.html', title="Our Mission")

@app.route('/home')
@login_required
def home():
    return render_template('home.html', title='Home')

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    print(user.lastSeen)
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]

    return render_template('profile.html', user=user, posts=posts, title="Profile")

@app.route('/upload', methods=["GET", "POST"])
@login_required
def upload():
    form = UploadForm()    
    if form.validate_on_submit():
        print('Hello!')
        print(form.image.data, form.description.data, form.location.data, form.directions.data, form.comments.data)
        uploaded_file = request.files['image']
        filename = secure_filename(uploaded_file.filename)
        print("Hello" + filename)

        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            print("Goodbye" + file_ext)
            if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
                file_ext != validate_image(uploaded_file.stream):
                flash("Image type not valid. Must be jpg, gif or png. Please try again.")
                return redirect(url_for('upload'))
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

            post = Post( \
                image = filename,
                body = form.description.data,
                location = form.location.data,
                directions = form.directions.data,
                comments = form.comments.data
                )
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('profile', username=current_user.username))
        
        return redirect(url_for('login'))

    print('This is a get request')
    return render_template('upload.html', title='Upload a Post', form=form)

@app.route('/settings', methods=["GET", "POST"])
@login_required
def settings():
    
    return render_template('settings.html', title="Change Settings")