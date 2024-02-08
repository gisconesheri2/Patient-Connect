from flask import Flask, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_migrate import Migrate
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
import os
from flask_wtf.csrf import CSRFProtect
""" Set the flask's app configuration variables, 
link the different flask extensions and initialize the app
"""

load_dotenv()

def doctor_required(func):
    """Restricts the homepage_medic route to 
    users with the medic role
    """
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
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://gaceripeter:Zp#DoAWmxVxx2y@gaceripeter.mysql.pythonanywhere-services.com/gaceripeter$patientconnect'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
# app.config['SERVER_NAME'] = 'gaceripeter.pythonanywhere.com'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USER')
app.config['MAIL_PASSWORD'] =  os.getenv('MAIL_PASS')

with app.app_context():

    # app.permanent_session_lifetime = timedelta(minutes=60)
    db = SQLAlchemy(app)
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 280

    bcrypt = Bcrypt(app)
    Session(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'home'
    login_manager.login_message_category = 'info'


    mail = Mail(app)
    csrf = CSRFProtect(app)

    migrate = Migrate(app, db)

    @app.before_request
    def before_request():
        """Keep track of last access time to the application
        and if it exceeds 30 minutes, prompt for new login
        """
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
from patientconnect import models