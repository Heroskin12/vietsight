import os

class Config(object):

    # If no environment variable, then the alternative is used.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'