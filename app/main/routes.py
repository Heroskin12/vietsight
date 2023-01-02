from datetime import datetime
from flask import abort, current_app, flash, redirect, render_template, request, url_for, g, jsonify
from app.translate import translate
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import get_locale
import imghdr
import os
from app import db
from app.auth.email import send_password_reset_email
from app.forms import UploadForm, CaptionForm, ProfileForm, CoverForm, PasswordForm, EmptyForm, BucketForm, CommentForm, EditPostForm
from app.models import User, Post, Comment
from langdetect import detect, LangDetectException
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from app.main import bp
import boto3
from io import BytesIO

# Update the 'last seen' time for user each time they make a request.
@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.lastSeen = datetime.utcnow()
        db.session.commit()
        g.locale = str(get_locale())
    
# A function to validate the file type of an image.
def validate_image(stream):
    header = stream.read(512) # Read 512 bytes of the file. This is enough to validate format.
    stream.seek(0) # Reset stream pointer so save function can see all bytes.
    format = imghdr.what(None, header) # Reads img in memory. Returns detected image format or None if format unknown.
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg') # Accounts for jpeg exception where jpg extension used.



# Routes
@bp.route('/', methods=["GET"])
@bp.route('/landing')
def landing():

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    return render_template('index.html', title="Welcome")

@bp.route('/home')
@login_required
def home():
    # Followed_Posts is a function hence why we call it.
    bucketform = BucketForm()
    commentForm = CommentForm()
    emptyForm = EmptyForm()
    followed_users = current_user.followed
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.home', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.home', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('home.html', title='Home',
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url, followed_users=followed_users, BucketForm=bucketform, commentForm=commentForm, emptyForm=emptyForm)

@bp.route('/explore')
@login_required
def explore():
    bucketform = BucketForm()
    commentForm = CommentForm()
    emptyForm = EmptyForm()
    # Get all posts to display on the explore page to hepl users find other people.
    followed_users = current_user.followed
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("home.html", title='Explore', posts=posts.items,
                          next_url=next_url, prev_url=prev_url,BucketForm=bucketform, commentForm=commentForm, emptyForm=emptyForm, followed_users=followed_users)

@bp.route('/profile/<username>')
@login_required
def profile(username):
    # Get the posts of the person whose profile you are looking at.
    user = User.query.filter_by(username=username).first_or_404()

    # Page stores the value of the pagination.
    page = request.args.get('page', 1, type=int)

    # Get all posts and divide into page of a quantity defined in POSTS_PER_PAGE.
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    # Add a link for next if there are more posts to show.
    next_url = url_for('main.profile', username=user.username, page=posts.next_num) \
        if posts.has_next else None

    # Add a back link if there are less posts to show.
    prev_url = url_for('main.profile', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    
    # Form for following someone.
    form = EmptyForm()
    return render_template('profile.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form, title="Profile")

                           
@bp.route('/upload', methods=["GET", "POST"])
@login_required
def upload():
    form = UploadForm()    
    if form.validate_on_submit():
        s3 = boto3.resource('s3')
        
        uploaded_file = request.files['image']
        filename = secure_filename(uploaded_file.filename)

        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS'] or \
                file_ext != validate_image(uploaded_file.stream):
                flash("Image type not valid. Must be jpg, gif or png. Please try again.")
                return redirect(url_for('main.upload'))
            unique = current_user.make_unique()
            uploaded_file.save(os.path.join(current_app.config['UPLOAD_PATH'], unique))
            data = open(os.path.join(current_app.config['UPLOAD_PATH'], unique), 'rb')
            s3.Bucket('flask-vietsight').put_object(Key=unique, Body=data)
            os.remove(os.path.join(current_app.config['UPLOAD_PATH'], unique))
            

            # Try detect language of post.
            try:
                language = detect(form.description.data)
            except LangDetectException:
                language = ''

            post = Post( \
                image = filename,
                unique_image = unique,
                body = form.description.data,
                location = form.location.data,
                directions = form.directions.data,
                language = language,
                comments_allowed = form.comments_allowed.data,
                author = current_user
                )
            db.session.add(post)
            db.session.commit()
            flash("Your post is now live!")
            return redirect(url_for('main.profile', username=current_user.username, title="Profile"))
        
        return redirect(url_for('main.login'))

    return render_template('upload.html', title='Upload a Post', form=form)

@bp.route('/delete_post/<id>', methods=["POST"])
@login_required
def delete_post(id):
    form = EmptyForm()

    if form.validate_on_submit():
        post = Post.query.filter_by(id=id).first()
        s3_client = boto3.client('s3')
        s3_client.delete_object(Bucket='flask-vietsight', Key=post.unique_image)
        db.session.delete(post)
        db.session.commit()
        flash('Post Deleted.')
        return redirect(url_for('main.home'))

    flash('Error. Please try again.')
    return redirect(url_for('main.home'))




@bp.route('/settings', methods=["GET", "POST"])
@login_required
def settings():
    
    form = CaptionForm()
    profileForm = ProfileForm()
    coverForm = CoverForm()
    passwordForm = PasswordForm()
    s3 = boto3.resource('s3')

    if form.validate_on_submit():
        newCaption = form.new_caption.data
        current_user.caption = newCaption
        db.session.commit()
        return redirect(url_for('main.profile', username=current_user.username))

    if profileForm.validate_on_submit():
        uploaded_file = request.files['new_profile']
        filename = secure_filename(uploaded_file.filename)

        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS'] or \
                file_ext != validate_image(uploaded_file.stream):
                flash("Image type not valid. Must be jpg, gif or png. Please try again.")
                return redirect(url_for('main.settings'))
            if current_user.unique_profile_pic != None:
                #os.remove(os.path.join(current_app.config['PROFILE_PATH'], current_user.unique_profile_pic))
                s3_client = boto3.client('s3')
                s3_client.delete_object(Bucket='flask-vietsight', Key=current_user.unique_profile_pic)
            current_user.profile_pic = filename
            current_user.unique_profile_pic = current_user.make_unique()
            uploaded_file.save(os.path.join(current_app.config['PROFILE_PATH'], current_user.unique_profile_pic))
            data = open(os.path.join(current_app.config['PROFILE_PATH'], current_user.unique_profile_pic), 'rb')
            s3.Bucket('flask-vietsight').put_object(Key=current_user.unique_profile_pic, Body=data)
            os.remove(os.path.join(current_app.config['PROFILE_PATH'], current_user.unique_profile_pic))
            
            db.session.commit()
            return redirect(url_for('main.profile', username = current_user.username))

    if coverForm.validate_on_submit():
        uploaded_file = request.files['new_cover']
        filename = secure_filename(uploaded_file.filename)

        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS'] or \
                file_ext != validate_image(uploaded_file.stream):
                flash("Image type not valid. Must be jpg, gif or png. Please try again.")
                return redirect(url_for('main.settings'))
            if current_user.unique_cover_pic:
                #os.remove(os.path.join(current_app.config['COVER_PATH'], current_user.unique_cover_pic))
                s3_client = boto3.client('s3')
                s3_client.delete_object(Bucket='flask-vietsight', Key=current_user.unique_cover_pic)

            current_user.cover_pic = filename
            current_user.unique_cover_pic = current_user.make_unique()
            uploaded_file.save(os.path.join(current_app.config['COVER_PATH'], current_user.unique_cover_pic))
            data = open(os.path.join(current_app.config['COVER_PATH'], current_user.unique_cover_pic), 'rb')
            s3.Bucket('flask-vietsight').put_object(Key=current_user.unique_cover_pic, Body=data)
            os.remove(os.path.join(current_app.config['COVER_PATH'], current_user.unique_profile_pic))
            db.session.commit()
            return redirect(url_for('main.profile', username = current_user.username))

    if passwordForm.validate_on_submit():
        print("Form validated.")
        oldPassword = passwordForm.oldPassword.data
        newPassword = passwordForm.newPassword.data
        confirmPassword = passwordForm.confirmPassword.data

        if not current_user.check_password(oldPassword):
            flash("Error. Old password is incorrect.")
        elif newPassword != confirmPassword:
            flash("Error. The new password and confirm password fields do not match.")
        else:
            current_user.set_password(newPassword)
            db.session.commit()
            flash("Password Changed Successfully.")
            return redirect(url_for('main.profile', username=current_user.username))



    return render_template('settings.html', title="Change Settings", form=form, profileForm=profileForm, coverForm=coverForm, passwordForm=passwordForm)

@bp.route('/follow/<username>', methods=["POST"])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        # Get an object of the user you want to follow.
        user = User.query.filter_by(username=username).first()

        # Check that the user exists.
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('main.home'))

        # Check that the user is not trying to follow themselves.
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('main.profile', username=username))

        if current_user.is_following(user):
            flash('Error. You are already following this person.')

        # Call the follow function.
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}'.format(username))
        return redirect(url_for('main.profile', username=username))
    else:
        return redirect(url_for('main.home'))

@bp.route('/unfollow/<username>', methods=["POST"])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        # Get an object of the user you want to follow.
        user = User.query.filter_by(username=username).first()

        # Check that the user exists.
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('main.home'))

        # Check that the user is not trying to follow themselves.
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('main.profile', username=username))

        # Check that the user doesn't already follow this person.
        if not current_user.is_following(user):
            flash('Error. You are not currently following this person.')
            return redirect(url_for('main.profile', username=username))

        # Call the follow function.
        current_user.unfollow(user)
        db.session.commit()
        flash('You have unfollowed {}'.format(username))
        return redirect(url_for('main.profile', username=username))
    else:
        return redirect(url_for('main.home'))


@bp.route('/bucket/<username>', methods=["GET", "POST"])
@login_required
def bucket(username):

    # Get the posts of the person whose profile you are looking at.
    user = User.query.filter_by(username=username).first_or_404()

    # Page stores the value of the pagination.
    page = request.args.get('page', 1, type=int)

    # Get all posts and divide into page of a quantity defined in POSTS_PER_PAGE.
    # Can I organize these by most recently added?
    posts = user.bucket_list.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    # Add a link for next if there are more posts to show.
    next_url = url_for('main.bucket', username=user.username, page=posts.next_num) \
        if posts.has_next else None

    # Add a back link if there are less posts to show.
    prev_url = url_for('main.bucket', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    
    # Form for following someone.
    form = EmptyForm()
    return render_template('bucket.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)

@bp.route('/add_bucket/<id>', methods=["POST"])
@login_required
def add_bucket(id):
    form = BucketForm()
    if form.validate_on_submit():
        # Get an object of the post you want to follow.
        post = Post.query.filter_by(id=id).first()
        

        # Check that the user exists.
        if post is None:
            flash('Post not found.')
            return redirect(url_for('main.home'))

        # Call the follow function.
        current_user.add_to_bucket(post)
        db.session.commit()
        flash('You have added this post to your bucket list!')
        return redirect(url_for('main.bucket', username=current_user.username))
    else:
        flash("Error. Could not add post to bucket list.")
        return redirect(url_for('main.post', id=id))

@bp.route('/remove_bucket/<id>', methods=["POST"])
@login_required
def remove_bucket(id):
    form = BucketForm()
    if form.validate_on_submit():
    # Get an object of the post you want to unfollow.
        post = Post.query.filter_by(id=id).first()

        # Check that the user exists.
        if post is None:
            flash('Post not found.')
            return redirect(url_for('main.home'))

        # Call the remove from bucket function.
        current_user.remove_from_bucket(post)
        db.session.commit()
        flash('You have removed this post from your bucket list.')
        return redirect(url_for('main.bucket', username=current_user.username))
    else:
        flash("Error. Could not remove post from your bucket list.")
        return redirect(url_for('main.bucket', username=current_user.username))

@bp.route('/add_comment/<id>', methods=["POST"])
@login_required
def add_comment(id):
    form = CommentForm()

    if form.validate_on_submit():
        try:
            language = detect(form.body.data)
        except LangDetectException:
            language = ''
        comment = Comment(
            body = form.body.data,
            author = current_user,
            language=language,
            post = Post.query.filter_by(id=id).first())

        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('main.post', id=id))
    
    flash("Error. Please try again.")
    return redirect(url_for('main.post', id=id))

@bp.route('/delete_comment/<id>', methods=["POST"])
@login_required
def delete_comment(id):


    comment = Comment.query.filter_by(id=id).first()
    if comment.author == current_user:
        db.session.delete(comment)
        db.session.commit()
        flash("Comment successfully deleted!")
        return redirect(url_for('main.post', id=id))
    
    flash("Error. Couldn't delete comment. Please try again!")
    return redirect(url_for('main.post', id=id))

@bp.route('/edit_comment/<id>', methods=["POST"])
@login_required
def edit_comment(id):
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment.query.filter_by(id=id).first()
        if comment.author == current_user:
            try:
                language = detect(form.body.data)
            except LangDetectException:
                language = ''
            comment.body = form.body.data
            db.session.commit()
            flash("Comment successfully edited.")
            return redirect(url_for('main.post', id=comment.post_id))

    flash("Error. Please try again.")
    return redirect(url_for('main.post', id=id))


@bp.route('/post/<id>', methods=["GET"])
@login_required
def post(id):
    commentForm = CommentForm()
    bucket = BucketForm()
    empty = EmptyForm()
    post = Post.query.filter_by(id=id).first()
    return render_template('post.html', post=post, commentForm=commentForm, BucketForm=bucket, empty=empty)


@bp.route('/edit_post/<id>', methods=["GET", "POST"])
@login_required
def edit_post(id):

    form = EditPostForm()
    post = Post.query.filter_by(id=id).first()
    print('Boo')

    if form.validate_on_submit():
        print('Boo Boo')
        if current_user != post.author:
            flash("Error. This is not your post.")
            return redirect(url_for('main.post'))
        elif post is None:
            flash("Error. Post doesn't exist.")
            return redirect(url_for('main.home'))
        else:
            try:
                language = detect(form.description.data)
            except LangDetectException:
                language = ''
            post.body = form.description.data
            post.location = form.location.data
            post.directions = form.directions.data
            post.language = language
            post.comments_allowed = form.comments_allowed.data
            
            db.session.commit()
            return redirect(url_for('main.post', id=post.id))

    return render_template('edit_post.html', form=form, post=post)

@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})



