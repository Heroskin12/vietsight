import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    # If no environment variable, then the alternative is used.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # Database Config | Fallback location set if no DB address known.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')

    # No signal sent to app if DB is changed.
    SQLALCHEMY_TRACK_MODIFICATIONS = False