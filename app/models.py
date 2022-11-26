from app import db
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String)
    lastName = db.Column(db.String)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    # Creates the one-to-many relationship. 'Posts' is the class of the model where the field is to be added. 'author' is a field added to the 'many' side which points back at the user.
    # E.g. post.author.firstName would return the firstName from the User model.
    posts = db.relationship('Posts', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {} {}>'.format(self.firstName, self.lastName)

    # Sets the password on registration.
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    # Checks a password on login.
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))