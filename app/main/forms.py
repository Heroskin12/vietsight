from app.models import User
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

class UploadForm(FlaskForm):
    image = FileField('Upload an Image', validators=[FileRequired()])
    description = TextAreaField('Describe the Post', validators=[DataRequired(), Length(min=1, max=500)])
    location = StringField('Where is this place?', validators=[DataRequired()])
    directions = TextAreaField('How do you get to this place?', validators=[DataRequired(), Length(min=1, max=500)])
    comments_allowed = BooleanField('Allow Comments')
    submit = SubmitField('Upload')

class EditPostForm(FlaskForm):
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
    oldPassword = PasswordField('Enter current password', validators=[DataRequired()])
    newPassword = PasswordField('Enter new password', validators=[DataRequired()])
    confirmPassword = PasswordField('Confirm new password', validators=[DataRequired()])
    submit = SubmitField('Confirm Change')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class BucketForm(FlaskForm):
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    body = TextAreaField('Add a comment...', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Submit')