from patientconnect import db, login_manager, app
from datetime import datetime
from flask_login import UserMixin
from flask import session
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    if 'user_type' in session:
        if session['user_type'] == 'patient':
            return Patient.query.get(int(user_id))
        if session['user_type'] == 'medic':
            return MedicalProfessional.query.get(int(user_id))
    return None

class MedicalProfessional(db.Model, UserMixin):
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
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=1800)['user_id']
        except:
            return None
        return MedicalProfessional.query.get(user_id)
    
    def __repr__(self):
        return f"Medic('{self.username}', '{self.profession}')"

class Patient(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), unique=True, nullable=False)
    phone_number = db.Column(db.Integer, unique=True, nullable=False)
    treatment_records = db.relationship('TreatmentRecord', backref='patient')
    current_otp = db.Column(db.String)
    # age = db.Column(db.Integer)
    otp_expired = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(30), nullable=False, default='patient')

    def get_reset_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=1800)['user_id']
        except:
            return None
        return Patient.query.get(user_id)
    
    def __repr__(self):
        return f"Patient('{self.username}', '{self.email}')"
    
class TreatmentRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    facility_name = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    diagnosis = db.Column(db.String(200), nullable=False)
    case_notes = db.Column(db.Text, nullable=False)
    investigations_done = db.Column(db.Text)
    medication_given = db.Column(db.Text)
    interventions_done = db.Column(db.Text)