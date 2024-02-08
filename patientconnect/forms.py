from flask import flash, request
from patientconnect.models import MedicalProfessional, Patient
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, IntegerField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, InputRequired, ValidationError, Optional, NumberRange
from flask_login import current_user
import phonenumbers


class RegistrationForm(FlaskForm):
    username = StringField('Full Name',
                            validators=[Optional(), Length(min=5, max=50)])
    surname = StringField('Surname',
                            validators=[DataRequired(), Length(min=5, max=30)])
    other_names = StringField('Other Names',
                            validators=[DataRequired(), Length(min=5, max=30)])
    email = EmailField('Email', 
                       validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[InputRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')

medprof = ['Medical Officer', 'Pharmacist','Clinical Officer',
           'Pharmaceutical Technologist','Registered Nurse','Physiotherapist']
class MedicalRegistrationForm(RegistrationForm):
    profession = SelectField(label='Medical Profession',
                             choices=medprof,
                             validators=[DataRequired()])
    facility_name = StringField('Current Facility',
                                      validators=[DataRequired()])
    registration_number = StringField('Registration Number',
                                      validators=[DataRequired()])
        
    def validate_email(self, email):
        email = MedicalProfessional.query.filter_by(email=email.data).first()
        print(email)
        if email:
            raise ValidationError('Email exists. Please choose another')
        
class PatientRegistrationForm(RegistrationForm):
    phone = StringField('Phone', validators=[DataRequired()])
    
        
    def validate_email(self, email):
        email = Patient.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Email exists. Please choose another')
        
    def validate_phone(self, phone):
        valid_phone = 0
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')
        valid_phone = phone.data
        patient = Patient.query.filter_by(phone_number=valid_phone).first()
        if patient:
            raise ValidationError('Phone Number exists. Please choose another')
        
class LogInForm(FlaskForm):
    email = EmailField('Email',
                         validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('LogIn')

class GetPhoneNumber(FlaskForm):
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Request OTP Code')
    
    def validate_phone(self, phone):
        valid_phone = 0
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number') 
        valid_phone = phone.data
        patient = Patient.query.filter_by(phone_number=valid_phone).first()
        if not patient:
            raise ValidationError('Patient is not registered with the service.')    

class VisitStartForm(FlaskForm):
    authorization_code = StringField('Authentication Code',
                                      validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Start Visit')



class UpdateAccountForm(FlaskForm):
    username = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    facility_name = StringField('Current Facility', validators=[Optional()])

    submit = SubmitField('Update')

    def validate_username(self, username):
        print(current_user.role)
        if username.data != current_user.username:
            if current_user.role == 'medic':
                user = MedicalProfessional.query.filter_by(username=username.data).first()
            elif current_user.role == 'patient':
                user = Patient.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')
            
    def validate_phone(self, phone):
        valid_phone = 0
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number') 
        valid_phone = phone.data
        patient = Patient.query.filter_by(phone_number=valid_phone).first()
        if patient:
            raise ValidationError('Phone Number exists. Please choose another')
            
        

    def validate_email(self, email):
        if email.data != current_user.email:
            if current_user.role == 'medic':
                user = MedicalProfessional.query.filter_by(email=email.data).first()
            elif current_user.role == 'patient':
                user = Patient.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class DiagnosisForm(FlaskForm):
    diagnosis = StringField('Diagnosis',
                           validators=[DataRequired()])
    submit = SubmitField('Next')

class CaseDetails(FlaskForm):
    bp_systolic = IntegerField('BP(Systolic)', validators=[DataRequired(), NumberRange(min=100, max=300)])
    bp_diastolic = IntegerField('BP(Diastolic)', validators=[DataRequired(), NumberRange(min=40, max=200)])
    presenting_illness_history = TextAreaField('History of Presenting Illness',
                        validators=[DataRequired()])
    submit = SubmitField('Next')

class InvestgationsForm(FlaskForm):
    investigations = TextAreaField('Investigation',
                           validators=[DataRequired()])
    submit = SubmitField('Next')

class MedicationForm(FlaskForm):
    medications = TextAreaField('Medications',
                           validators=[DataRequired()])
    submit = SubmitField('Next')

class InterventionsForm(FlaskForm):
    interventions = TextAreaField('Interventions',
                           validators=[DataRequired()])
    submit = SubmitField('Finish')


    
class NewRecordForm(FlaskForm):
    diagnosis = StringField('Diagnosis',
                           validators=[DataRequired()])
    casenotes = TextAreaField('Casenotes')
    investigations = TextAreaField('Investigations done',
                        validators=[DataRequired()])
    medications = TextAreaField('Medication Given',
                        validators=[DataRequired()])
    interventions = TextAreaField('Interventions Done',
                        validators=[DataRequired()])
    
    submit = SubmitField('Update')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
