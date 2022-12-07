from app import app, db, login
from datetime import datetime
from flask_login import UserMixin
from hashlib import md5
from time import time
from werkzeug.security import check_password_hash, generate_password_hash
import jwt

followers = db.Table('followers',
db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

# Represents the relationship between users and the posts they have bucketed.
post_followers = db.Table('post_followers',
db.Column('post_follower_id', db.Integer, db.ForeignKey('user.id')),
db.Column('followed_post_id', db.Integer, db.ForeignKey('post.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String)
    lastName = db.Column(db.String)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    profile_pic = db.Column(db.String)
    cover_pic = db.Column(db.String)
    caption = db.Column(db.String(256))
    lastSeen = db.Column(db.DateTime, default = datetime.utcnow)

    # Creates the one-to-many relationship. 'Posts' is the class of the model where the field is to be added. 'author' is a field added to the 'many' side which points back at the user.
    # E.g. post.author.firstName would return the firstName from the User model.
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    # When followed is queried, you will get the list of users that person follows.
    followed = db.relationship(
        # User is the class on the right side of the relationship.
        # Secondary configures the association table defined above.
        'User', secondary=followers,
        # Indicates the condition that links the left side entity (the follower user) with the association table. The condition is when the user ID matches the follower_id in the association table.
        primaryjoin=(followers.c.follower_id == id),
        # Indicates the condition that links the right side (the followed user) with the association table. The condition is when the user id matches the followed_id.
        secondaryjoin=(followers.c.followed_id == id),
        # Defines how the relationship will be accessed by the right side entity. From the left, it is noamed followed, but the right uses followers.
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )

    # Function below accesses the bucket relationship.
    bucket_list = db.relationship('Post', secondary=post_followers, backref='bucketer_list', lazy='dynamic')

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
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    
    def is_following(self, user):
        # Count the number of users with the same id as the user you want to follow. If it is more than 0 then return True.
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0


    def followed_posts(self):
        followed = Post.query.join(
            # Gets a list of posts by people who the current user follows.
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
            # Also gets post by current user.
        own = Post.query.filter_by(user_id=self.id)
        # Joins both temp tables and orders them by most recent first.
        return followed.union(own).order_by(Post.timestamp.desc())

    def add_to_bucket(self, post):
        if not self.in_bucket(post):
            self.bucket_list.append(post)

    def remove_from_bucket(self, post):
        if self.in_bucket(post):
            self.bucket_list.remove(post)

    def in_bucket(self, post):
        return self.bucket_list.filter(post_followers.c.followed_post_id == post.id).count() > 0

    def bucketed_posts(self):
        # Gets a list of posts followed by the user.
        return self.bucket_list

    def bucketer_users(self, post):
        return post.bucketer_list


    
            

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String)
    body = db.Column(db.String)    
    location = db.Column(db.String)
    directions = db.Column(db.String)
    comments_allowed = db.Column(db.String)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def __repr__(self):
        return '<Post {}, {}, {}>'.format(self.body, self.image, self.comments)

    def count_bucket_list(self, post):
        return post.bucketer_list.count()

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self):
        return '<Comment {}>'.format(self.body)




@login.user_loader
def load_user(id):
    # Get id returns a string so int is called so it can be compared with the user_id.
    return User.query.get(int(id))

