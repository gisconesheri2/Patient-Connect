from patientconnect.models import MedicalProfessional, Patient
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField, SubmitField, IntegerField,\
    BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, InputRequired,\
    ValidationError, Optional, NumberRange
from flask_login import current_user
import phonenumbers
"""Defination of classes to model the WTF forms and handle validation
of details entered in the forms
"""

class RegistrationForm(FlaskForm):
    """ Registration form template containing common fields
    for both patient and medical professionals users
    Will be inherited by the respective classes
    """
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
                                     validators=[InputRequired(),
                                                 EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')

medprof = ['Medical Officer', 'Pharmacist', 'Dentist', 'Pharmaceutical Technologist',]
others_medprof = ['Clinical Officer', 'Registered Nurse','Physiotherapist']
class MedicalRegistrationForm(RegistrationForm):
    """Template form for fields specific to the medical professional users
    """
    profession = SelectField(label='Medical Profession',
                             choices=medprof,
                             validators=[DataRequired()])
    facility_name = StringField('Current Facility',
                                      validators=[DataRequired()])
    registration_number = StringField('Registration Number',
                                      validators=[DataRequired()])
        
    def validate_email(self, email):
        """Validates if an email exists in the professional's database as it must be unique
        """
        email = MedicalProfessional.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Email exists. Please choose another')
        
    def validate_registration_number(self, registration_number):
        """Validates that a profession of a specific cadre is
        not performing a double registration with another email
        """
        user = MedicalProfessional.query.filter_by(registration_number=registration_number.data).first()
        if user and user.profession == self.profession.data:
            raise ValidationError("That registration number already has an account")

        
class PatientRegistrationForm(RegistrationForm):
    """Template and validation for unique fields in patient registration
    """
    phone = StringField('Phone', validators=[DataRequired()])
    
        
    def validate_email(self, email):
        """Validate that email supplied is unique an registered to another account
        """
        email = Patient.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Email exists. Please choose another')
        
    def validate_phone(self, phone):
        """Validate that phone number supplied is 
            1. A valid format - uses the phonenumbers module to do the validation
            2. Does not exist in the database- must be unique
        """
        valid_phone = 0
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')
        print(type(phone.data))
        valid_phone = int(phone.data)
        patient = Patient.query.filter_by(phone_number=valid_phone).first()
        if patient:
            raise ValidationError('Phone Number exists. Please choose another')
        
class LogInForm(FlaskForm):
    """"Template for the log in form. It is the same for both type of users
    """
    email = EmailField('Email',
                         validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('LogIn')

class GetPhoneNumber(FlaskForm):
    """Template to get and validate a patient's phone number
    by the medical professional. This is needed to gain access to patient's records
    """
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Request OTP Code')
    
    def validate_phone(self, phone):
        """Validate that phone number supplied is 
            1. A valid format - uses the phonenumbers module to do the validation
            2. Exists in the database and is registered to a patient
        """
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
    """Template to facilitate verification of the otp number sent to a patient
    """
    authorization_code = StringField('Authentication Code',
                                      validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Start Visit')



class UpdateAccountForm(FlaskForm):
    """Template to facilitate updating of account details
    The same for both user types. Different views are handled by the Jinja template
    """
    username = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    facility_name = StringField('Current Facility', validators=[Optional()])

    submit = SubmitField('Update Account Details')

    def validate_username(self, username):
        """Validate that the name is unique and not being used by another
        """
        if username.data != current_user.username:
            if current_user.role == 'medic':
                user = MedicalProfessional.query.filter_by(username=username.data).first()
            elif current_user.role == 'patient':
                user = Patient.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')
            
    def validate_phone(self, phone):
        """Validate that phone number supplied is 
            1. A valid format - uses the phonenumbers module to do the validation
            2. Does not exist in the database- must be unique
        """
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
        """Validate that the email supplied is unique and does not
        already exist in the database
        """
        if email.data != current_user.email:
            if current_user.role == 'medic':
                user = MedicalProfessional.query.filter_by(email=email.data).first()
            elif current_user.role == 'patient':
                user = Patient.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class DiagnosisForm(FlaskForm):
    """Template to get diagnosis details by the doctor when creating a new treatment record
    """
    diagnosis = StringField('Diagnosis',
                           validators=[DataRequired()])
    submit = SubmitField('Next')

class CaseDetails(FlaskForm):
    """Template to get the case details by the doctor when creating a new treatment record
    """
    bp_systolic = IntegerField('BP(Systolic)', validators=[DataRequired(), NumberRange(min=100, max=300)])
    bp_diastolic = IntegerField('BP(Diastolic)', validators=[DataRequired(), NumberRange(min=40, max=200)])
    presenting_illness_history = TextAreaField('History of Presenting Illness',
                        validators=[DataRequired()])
    submit = SubmitField('Next')

class InvestgationsForm(FlaskForm):
    """Template to get investigations details by the doctor when creating a new treatment record
    """
    investigations = TextAreaField('Investigation',
                           validators=[DataRequired()])
    submit = SubmitField('Next')

class MedicationForm(FlaskForm):
    """Template to get medication details by the doctor when creating a new treatment record
    """
    medications = TextAreaField('Medications',
                           validators=[DataRequired()])
    submit = SubmitField('Next')

class InterventionsForm(FlaskForm):
    """Template to get interventions/procedures details by the doctor when creating a new treatment record
    """
    interventions = TextAreaField('Interventions',
                           validators=[DataRequired()])
    submit = SubmitField('Finish')
    
class NewRecordForm(FlaskForm):
    """Template to provide a summary of the details by the doctor
    when creating a new treatment record and allow last minute edits before creating a record.
    """
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
    """Template to facilitate resetting of passwords for users.
    Used to get the email registered in the account
    """
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    """Template to facilitate resetting of passwords for users.
    Used to actually change the password
    """
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class ContactForm(FlaskForm):
    """Template to facilitate sending of feedback and request manual registration
    of healthcare professionals
    """
    name = StringField('Full Name', validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired()])
    email = EmailField('Email Address', validators=([DataRequired(), Email()]))
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')

