from flask import render_template
from app import app

@app.route('/')
@app.route('/landing')
def landing():
    
    return render_template('index.html', title="Welcome")

@app.route('/login')
def login():
    return 'Login Page'


@app.route('/register')
def register():
    return 'Register Page'

@app.route('/mission')
def mission():
    return 'Mission Page'