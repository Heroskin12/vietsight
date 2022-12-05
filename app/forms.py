from app.models import User
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import BooleanField, DateField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Account')

    # Will check if username and emails are already in use. These fields must be unique.
    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user is not None:
            raise ValidationError('Username already taken. Please choose another.')
        
    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user is not None:
            raise ValidationError('Email already in use by another account. Please choose another.')

class UploadForm(FlaskForm):
    image = FileField('Upload an Image', validators=[FileRequired()])
    description = TextAreaField('Describe the Post', validators=[DataRequired(), Length(min=1, max=500)])
    location = StringField('Where is this place?', validators=[DataRequired()])
    directions = TextAreaField('How do you get to this place?', validators=[DataRequired(), Length(min=1, max=500)])
    comments_allowed = BooleanField('Allow Comments')
    submit = SubmitField('Upload')

class CaptionForm(FlaskForm):
    new_caption = TextAreaField('Caption', validators=[DataRequired()])
    submit = SubmitField('Confirm Change')

class ProfileForm(FlaskForm):
    new_profile = FileField('Upload a new profile picture', validators=[FileRequired()])
    submit = SubmitField('Change Profile Picture')

class CoverForm(FlaskForm):
    new_cover = FileField('Upload a new cover photo', validators=[FileRequired()])
    submit = SubmitField('Change Cover Photo')

class PasswordForm(FlaskForm):
    oldPassword = PasswordField('Enter current password', validators=[FileRequired()])
    newPassword = PasswordField('Enter new password', validators=[FileRequired()])
    confirmPassword = PasswordField('Confirm new password', validators=[FileRequired()])

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class BucketForm(FlaskForm):
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    body = StringField('Add a comment...')
    submit = SubmitField('Submit')