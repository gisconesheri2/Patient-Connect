from patientconnect import db, login_manager, app
from datetime import datetime
from flask_login import UserMixin
from flask import session
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    """User loader function for Flask Login.
    Use of session variables needed to differentiate between the two types of users.
    """
    if 'user_type' in session:
        if session['user_type'] == 'patient':
            return Patient.query.get(int(user_id))
        if session['user_type'] == 'medic':
            return MedicalProfessional.query.get(int(user_id))
    return None

class MedicalProfessional(db.Model, UserMixin):
    """Sqlalchemy model for Medical Professionals.
    Also inherits the USerMixin class from Flask Login
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    profession = db.Column(db.String(120), nullable=False)
    registration_number = db.Column(db.String(20), nullable=False)
    facility_name = db.Column(db.String(200), nullable=False)
    registration_status = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(30), nullable=False, default='medic')

    def get_reset_token(self):
        """Used to generate a time bound sequence of random letters
        that will be used to facilitate changing the password.
        Uses the itsdangerous module.
        """
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        """decodes the token to:
        1. verify its is still within 30 minutes of being sent/generated
        2. get the user id and return a MedicalProfession Instance to the change password view

        Return: A MedicalProfession instance or None otherwise
        """
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=1800)['user_id']
        except:
            return None
        return MedicalProfessional.query.get(user_id)
    
    def __repr__(self):
        return f"Medic('{self.username}', '{self.profession}')"

class Patient(db.Model, UserMixin):
    """Sqlalchemy model for Patients.
    Also inherits the USerMixin class from Flask Login
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), unique=True, nullable=False)
    phone_number = db.Column(db.Integer, unique=True, nullable=False)
    current_otp = db.Column(db.String)
    # age = db.Column(db.Integer)
    otp_expired = db.Column(db.Boolean, default=False)
    otp_creation_time = db.Column(db.DateTime)
    role = db.Column(db.String(30), nullable=False, default='patient')
    treatment_records = db.relationship('TreatmentRecord', backref='patient', cascade="all, delete-orphan")

    def get_reset_token(self):
        """Used to generate a time bound sequence of random letters
        that will be used to facilitate changing the password.
        Uses the itsdangerous module.
        """
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        """decodes the token to:
        1. verify its is still within 30 minutes of being sent/generated
        2. get the user id and return the Patient instance to the change password view

        Return: A Patient instance or None otherwise
        """
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=1800)['user_id']
        except:
            return None
        return Patient.query.get(user_id)
    
    def __repr__(self):
        return f"Patient('{self.username}', '{self.email}')"
    
class TreatmentRecord(db.Model):
    """SQLAlchemy model for treatment records
    """
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    facility_name = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    diagnosis = db.Column(db.String(200), nullable=False)
    case_notes = db.Column(db.Text, nullable=False)
    investigations_done = db.Column(db.Text)
    medication_given = db.Column(db.Text)
    interventions_done = db.Column(db.Text)


class RegisteredDoctors(db.Model):
    """SQLAlchemy model for the table storing registered doctors and dentists.
    Used to verify that the registration status of the above is current and can
    access patient records.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    reg_no = db.Column(db.String)
    active = db.Column(db.String)

class RegisteredPharmacists(db.Model):
    """SQLAlchemy model for the table storing pharmacists.
    Used to verify that the registration status of the above is current and can
    access patient records.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    reg_no = db.Column(db.String)
    active = db.Column(db.String)

class RegisteredPharmtechs(db.Model):
    """SQLAlchemy model for the table storing pharmaceutical technologists.
    Used to verify that the registration status of the above is current and can
    access patient records.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    reg_no = db.Column(db.String)
    active = db.Column(db.String)