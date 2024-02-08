from flask import Flask, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_apscheduler import APScheduler
from flask_mail import Mail
from functools import wraps
import secrets
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

def doctor_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        print(current_user.is_authenticated)
        print(current_user.role)
        if current_user.is_authenticated and current_user.role != 'medic':
            flash('Access denied. You must be a medic', 'error')
            return redirect(url_for('homepage_patient'))
        return func(*args, **kwargs)
    return decorated_view


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SESSION_TYPE'] = 'filesystem'
app.permanent_session_lifetime = timedelta(minutes=60)
db = SQLAlchemy(app)
app.app_context().push()
bcrypt = Bcrypt(app)
Session(app)
login_manager = LoginManager(app)
login_manager.login_view = 'home'
login_manager.login_message_category = 'info'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USER')
app.config['MAIL_PASSWORD'] =  os.getenv('MAIL_PASS')
mail = Mail(app)

scheduler = APScheduler()
scheduler.init_app(app)

scheduler.start()

@app.before_request
def before_request():
    now = datetime.now()
    if 'user_type' in session:
        if 'last_active' in session:
            last_active = session['last_active']
            delta = now - last_active
            if delta.seconds > 1800:
                session['last_active'] = now
                session['expired'] = True
                return redirect(url_for('logout'))
        session['last_active'] = now

from patientconnect import routes