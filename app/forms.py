from app.models import User
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField
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
    # Upload File - File Upload
    description = TextAreaField('Describe the Post', validators=[DataRequired(), Length(min=1, max=500)])
    location = StringField('Where was this taken?', validators=[DataRequired()])
    # When did you go? - Date Field
    directions = TextAreaField('How do you get there', validators=[DataRequired(), Length(min=1, max=500)])
    # What type of place is this? - Select Menu
    allow_comments = BooleanField('Allow Comments?')
    submit = SubmitField('Upload')

class CaptionForm(FlaskForm):
    new_caption = TextAreaField('Caption', validators=[Length(min=0, max=256)])
    submit = SubmitField('Confirm Change')
