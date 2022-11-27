from app.models import User
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

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
    # Post Description - TextArea
    location = StringField('Where was this taken?', validators=[DataRequired()])
    # When did you go? - Date Field
    # How do you get there? - TextArea
    # What type of place is this? - Select Menu
    allow_comments = BooleanField('Allow Comments?')
    submit = SubmitField('Upload')
