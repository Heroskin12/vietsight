from app import db, login
from datetime import datetime
from flask_login import UserMixin
from hashlib import md5
from werkzeug.security import check_password_hash, generate_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String)
    lastName = db.Column(db.String)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    # Creates the one-to-many relationship. 'Posts' is the class of the model where the field is to be added. 'author' is a field added to the 'many' side which points back at the user.
    # E.g. post.author.firstName would return the firstName from the User model.
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {} {}>'.format(self.firstName, self.lastName)

    # Sets the password on registration.
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    # Checks a password on login.
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        # Encode the email before making the Gravatar request.
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        # Request the gravatar for this user.
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

@login.user_loader
def load_user(id):
    # Get id returns a string so int is called so it can be compared with the user_id.
    return User.query.get(int(id))