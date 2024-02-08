from patientconnect import app, db, bcrypt, doctor_required, mail
from patientconnect.models import (MedicalProfessional, Patient, TreatmentRecord,
                                   RegisteredDoctors, RegisteredPharmacists,
                                   RegisteredPharmtechs)
from flask import render_template, url_for, flash, redirect, request, session
from patientconnect.forms import (GetPhoneNumber, ContactForm, RequestResetForm,
                                  ResetPasswordForm, MedicalRegistrationForm, PatientRegistrationForm, 
                                  LogInForm, DiagnosisForm, NewRecordForm, VisitStartForm, MedicationForm,
                                  InterventionsForm, InvestgationsForm, UpdateAccountForm)
from flask_login import login_user, current_user, login_required, logout_user
from flask_mail import Message
import pyotp
from datetime import datetime, timedelta
""" Module to handle the different routes functionality
"""

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    """Handle the home view for the app
    """
    # not accessible to logged in users
    if current_user.is_authenticated and current_user.role == 'medic':
        return redirect(url_for('homepage_medic'))
    
    if current_user.is_authenticated and current_user.role == 'patient':
        return redirect(url_for('homepage_patient'))
    
    # complicated way to handle notifying users they have been logged out
    # after a 30min timeout and redirect them to the login page
    if 'expired_final' in session:
        if session.get('expired_final') == 'true':
            flash('Your session has expired after 30 minutes, you have been logged out. Please login again', 'info')
            user = session.get('user_category')
            session.pop('expired_final', None)
            session.pop('user_category', None)
            return redirect(url_for('login', user=user))
    
    form = ContactForm()
    # section is a request parameter for in-page navigation of the home page
    # set by the navigation links on the header of the pages    
    section = request.args.get('section')
    if request.args.get('ms_redir') == 'true':
        if session.get('med_query_details') is not None  and request.method == 'GET':
            form.name.data = session['med_query_details']['name']
            form.email.data = session['med_query_details']['email']
            form.subject.data = session['med_query_details']['subject']
            form.message.data = session['med_query_details']['message']
    if form.validate_on_submit():
        msg = Message(f'Contact Form feedback: {form.subject.data}', sender='patientconnect24@gmail.com',
                  recipients=['patientconnect24@gmail.com'])
        
        msg.body = f'''Sender name: {form.name.data}
Sender Email: {form.email.data}
Message: {form.message.data}'''
        try:
            mail.send(msg)
            session.pop('med_query_details', None)
            flash('Message sent. You will be hearing from us through the email provided. Thank you for your interest.', 'success')
            return redirect(url_for('home', section=''))
        except Exception:
            flash('We had some trouble sending the email. Please try again', 'secondary')
            return redirect(url_for('home', section='contact'))

    return render_template('home.html', section=section, form=form)

def send_reset_email(user):
    """Helper function to send a reset password email. Uses Flask Mail.
        @user: A MedicalProfession or Patient instance
        Return: nothing
    """
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@patientconnect.com',
                  recipients=[user.email])
    # url_for generates an absolute url with given parameters
    msg.body = f'''To reset your password, visit this link:
{url_for('reset_token', user=user.role, token=token, _external=True)}

if you did not make this request, ignore this message.
'''
    mail.send(msg)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    """Handles logic for sending a reset password email.
    Must verify the user is registered with the database then send the email
    by the help of the send_reset_email function above
    """
    if current_user.is_authenticated and current_user.role == 'medic':
        return redirect(url_for('homepage_medic'))
    
    if current_user.is_authenticated and current_user.role == 'patient':
        return redirect(url_for('homepage_patient'))
    
    form = RequestResetForm()
    user = request.args.get('user')
    if user is None:
        return redirect(url_for('home'))
    
    if form.validate_on_submit():
        if user == 'patient':
            patient = Patient.query.filter_by(email=form.email.data).first()
            if patient is None:
                flash('There is no account with that email. Please confirm the email.', 'warning')
                return render_template('reset_request.html', title='Reset Password', form=form)
            else:
                try:
                    send_reset_email(patient)
                except Exception:
                    flash('We had some trouble sending the email. Please try again', 'secondary')
                    return render_template('reset_request.html', title='Reset Password', form=form)
                
                flash('Password reset instructions sent to email provided.', 'info')
                return redirect(url_for('login', user='patient'))
            
        if user == 'medic':
            medic = MedicalProfessional.query.filter_by(email=form.email.data).first()
            if medic is None:
                flash('There is no account with that email. Please confirm the email.', 'warning')
                return render_template('reset_request.html', title='Reset Password', form=form)
            else:
                try:
                    send_reset_email(medic)
                except Exception:
                    flash('We had some trouble sending the email. Please try again', 'secondary')
                    return render_template('reset_request.html', title='Reset Password', form=form)
                flash('Password reset instructions sent to email provided.', 'info')
                return redirect(url_for('login', user='medic'))
            
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    """Handles logic for resetting the password.
    Must verify the @token is valid and user id contained therein is
    tied to a registered user
    """
    #Must be logged out to change password
    if current_user.is_authenticated and current_user.role == 'medic':
       return redirect(url_for('homepage_medic'))
    
    if current_user.is_authenticated and current_user.role == 'patient':
        return redirect(url_for('homepage_patient'))

    #user needed to handle authentication logic
    user = request.args.get('user')
    if user is None:
        return redirect(url_for('home'))
    
    if user == 'patient':
        patient = Patient.verify_reset_token(token)
        if patient is None:
            flash('That is an invalid or expired token', 'warning')
            return redirect(url_for('reset_request', user='patient'))
        form = ResetPasswordForm()
        if form.validate_on_submit():
        # hash the password
            hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            #update the password and commit the changes
            patient.password = hashed_pwd
            db.session.commit()
            flash('Your password has been updated.You can now log in.', 'success')
            return redirect(url_for('login', user='patient'))
        return render_template('reset_token.html', title='Reset Password', form=form)
    
    if user == 'medic':
        medic = MedicalProfessional.verify_reset_token(token)
        if medic is None:
            flash('That is an invalid or expired token', 'warning')
            return redirect(url_for('reset_request', user='medic'))
        form = ResetPasswordForm()
        if form.validate_on_submit():
        # hash the password
            hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            medic.password = hashed_pwd
            db.session.commit()
            flash('Your password has been updated.You can now log in.', 'success')
            return redirect(url_for('login', user='medic'))
        return render_template('reset_token.html', title='Reset Password', form=form)
    

def check_name(name1, name2):
    """Helper function to check if names provided for doctors and dentist
    during registration match those in the registered doctors database.
    This is needed because the database only has partial registration numbers
        @name1: name in the registered doctors database
        @name2: name supplied in the form during registration
    Return: True if both names match, False otherwise
    """
    if len(name1) == len(name2):
        x = 1
        names = name1.split()
        for name in names:
            if name in name2:
                if x == len(names):
                    return True
                x += 1
            else:
                return False
    return False

@app.route('/medsignup', methods=['GET', 'POST'])
def medsignup():
    """Handles registration of medical professionals.
    Includes checks to see if the medic's registration status is uptodate
    """
    if current_user.is_authenticated and current_user.role == 'medic':
        return redirect(url_for('homepage_medic'))
    
    if current_user.is_authenticated and current_user.role == 'patient':
        return redirect(url_for('homepage_patient'))
    
    form = MedicalRegistrationForm()
    if form.validate_on_submit():
        # hash the password
        registration_status = False
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        username = f"{form.other_names.data} {form.surname.data}"

        # switch to see if active registration status can be confirmed so that user can be registered
        user_present = False
        if form.profession.data == 'Pharmacist':
            #query the RegisteredPharmacists using the registered id
            user = RegisteredPharmacists.query.filter_by(reg_no=form.registration_number.data).first()
            if user:
                if user.active.strip() == 'Active':
                    registration_status = True
                    username = f'Dr {user.name}'
                    user_present = True
        if form.profession.data == 'Pharmaceutical Technologist':
            user = RegisteredPharmtechs.query.filter_by(reg_no=form.registration_number.data).first()
            if user:
                if user.active.strip() == 'Active':
                    registration_status = True
                    username = user.name
                    user_present = True

        if form.profession.data == 'Dentist' or form.profession.data == 'Medical Officer':
            users = RegisteredDoctors.query.filter_by(reg_no=form.registration_number.data[0:3]).all()
            user_found = False
            for user in users:
                cleaned_name = user.name.lower().replace('dr ', '').replace('prof ', '').replace('  ', ' ').strip()
                username = username.lower().replace('  ', ' ').strip()
                if check_name(cleaned_name, username) == True:
                    user_found = user
                    break
            if user_found is not False:
                    if user_found.active.strip() == 'Active':
                        registration_status = True
                        username = user_found.name
                        user_present = True

        if user_present is True:
            med_user = MedicalProfessional(username=username.title(), email=form.email.data,
                                            password=hashed_pwd, profession=form.profession.data,
                                            registration_number=form.registration_number.data,
                                            facility_name=form.facility_name.data,
                                            registration_status = registration_status)
        
            db.session.add(med_user)
            db.session.commit()
            flash(f'Your account has been created. You can now login!', 'success')
            return(redirect(url_for('login', user='medic')))
        else:
            flash('Registration status could not be confirmed.\n Please confirm details or submit', 'query')
            session['med_query_details'] = {}
            session['med_query_details']['name'] = username
            session['med_query_details']['email'] = form.email.data
            session['med_query_details']['subject'] = 'Confirmation of registration details'
            session['med_query_details']['message'] = f'''Help me with my registration:

                Profession: {form.profession.data}
                Registration number: {form.registration_number.data}
                Facility Name: {form.facility_name.data}'''
    return render_template('medsignup.html', title='Sign Up', form=form)

@app.route('/ptsignup', methods=['GET', 'POST'])
def ptsignup():
    """Handles the logic registering patients
    """
    if current_user.is_authenticated and current_user.role == 'medic':
        return redirect(url_for('homepage_medic'))
    
    if current_user.is_authenticated and current_user.role == 'patient':
        return redirect(url_for('homepage_patient'))
    
    form = PatientRegistrationForm()
    if form.validate_on_submit():
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        full_phone = int(form.phone.data)
        username = f"{form.surname.data} {form.other_names.data}"
        patient = Patient(username=username.title(), email=form.email.data,
                                   password=hashed_pwd, phone_number=full_phone)
        db.session.add(patient)
        db.session.commit()
        flash(f'Your account has been created. You can now login!', 'success')
        return(redirect(url_for('login', user='patient')))
    return render_template('ptsignup.html', title="Sign Up", form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    """Handle login of users. Utilises the Flask Login extension.
    """
    if current_user.is_authenticated and current_user.role == 'medic':
        return redirect(url_for('homepage_medic'))
    
    if current_user.is_authenticated and current_user.role == 'patient':
        return redirect(url_for('homepage_patient'))
    
    # user needed to know which database to get the login details
    user = request.args.get('user')
    if user is None:
        return redirect(url_for('home'))
    form = LogInForm()

    if form.validate_on_submit():
        email = form.email.data
        pwd = form.password.data

        if user == 'patient':
            patient = Patient.query.filter_by(email=email).first()
            if patient and bcrypt.check_password_hash(patient.password, pwd):
                # add key user_type to the flask session so that flask login can generate its login id
                session['user_type'] = 'patient'
                login_user(patient, remember=form.remember.data)
                return redirect(url_for('homepage_patient'))
            else:
                flash('Please check your login details and try again', 'danger')
        
        if user == 'medic':
            medic = MedicalProfessional.query.filter_by(email=email).first()
            if medic and bcrypt.check_password_hash(medic.password, pwd):
                session['user_type'] = 'medic'
                login_user(medic, remember=form.remember.data)
                return redirect(url_for('homepage_medic'))
            else:
                flash('Please check your login details and try again', 'danger')
                
    return render_template('login.html', title="Log In", form=form, user=user)


@app.route('/homepage_patient')
@login_required
def homepage_patient():
    """Handle logic for the patient homepage
    """
    user = session.get('user_type')

    if user == 'patient':
        records = current_user.treatment_records
        username = current_user.username
        return render_template('homepage_patient.html', title='Patient Homepage',
                            records=records, username=username)
    
    phone = session.get('phone')
    if user == 'medic' and phone is None:
        # handle invalid access by a medic
        return redirect(url_for('homepage_medic'))
    elif user == 'medic' and phone is not None:
        patient = Patient.query.filter_by(phone_number=phone).first()
        records = patient.treatment_records
        username= patient.username
        return render_template('homepage_patient.html', title='Patient Homepage',
                            records=records, username=username)


def send_otp_email(patient):
    """Helper function to send an one time password(otp) email. Uses Flask Mail.
        @patient: A Patient Class instance
        Return: nothing
    """
    msg = Message('Visit Authorization Code', sender='patientconnect24@gmail.com',
                  recipients=[patient.email])
    msg.body = f'''To begin the current visit, please share this code with your doctor:
{patient.current_otp}

if you did not authorize this request, kindly ignore this message.
'''
    mail.send(msg)

@app.route('/homepage_medic', methods=['GET', 'POST'])
@login_required
@doctor_required
def homepage_medic():
    """Handles the homepage for the medic
    Includes logic to generate a time-based OTP by help of the pyotp module
    """
    form = GetPhoneNumber()
    # code_expired generated by an automatic redirect from the otp_confirmation page
    # used to generate an alert on the template that the code expired
    code_expired = request.args.get('code_expired')
    if code_expired == 'true':
        # remove the otp from the patient's records
        patient = Patient.query.filter_by(phone_number=session.get('phone')).first()
        if patient:
            patient.current_otp = None
            patient.otp_expired = True
            db.session.commit()
            session.pop('phone', None)

    end_visit = request.args.get('end_visit')
    if end_visit == 'true':
        session.pop('phone', None)
        flash('Visit Ended', 'info')
    
    if form.validate_on_submit():
        phone = form.phone.data
        patient = Patient.query.filter_by(phone_number=form.phone.data).first()

        # generate a time based otp and save it in the patient's database
        totp = pyotp.TOTP(pyotp.random_base32())
        otp = totp.now()
        patient.current_otp = otp
        patient.otp_expired = False
        patient.otp_creation_time = datetime.now()
        session['phone'] = patient.phone_number
        db.session.commit()


        try:
            send_otp_email(patient)
        except Exception as e:
            flash(f'We had some trouble sending the otp code. Please enter number again {e}', 'secondary')
            return render_template('homepage_medic.html',
                            get_phone_form=form,
                            title='Medic DashBoard',
                            code_expired=code_expired)
        # TODO send otp
        flash('Enter the OTP code sent to the patient. It is valid for 5 minutes', 'primary')
        return redirect(url_for('otp_confirmation', phone=phone))
    return render_template('homepage_medic.html',
                            get_phone_form=form,
                            title='Medic DashBoard',
                            code_expired=code_expired)


@app.route('/otp_confirmation', methods=['GET', 'POST'])
def otp_confirmation():
    """Handle the the logic for otp confirmation and invalidation
    Includes starting up a background task to delete the patient opt within
    five minutes if code is not used with that time
    """
    form = VisitStartForm()

    # phone number needed to access the patient database's and their otp
    phone = request.args.get('phone')
    if phone is None:
        flash('Enter Phone Number', 'warning')
        return redirect (url_for('homepage_medic'))

    patient = Patient.query.filter_by(phone_number=phone).first()
    if form.validate_on_submit():
        time_lapsed = (datetime.now() - patient.otp_creation_time).total_seconds()
        if (patient.current_otp == form.authorization_code.data and
            time_lapsed < 300):

            patient.current_otp = None
            patient.otp_expired = True
            patient.otp_creation_time = None
            db.session.commit()
            scheduler.remove_all_jobs()
            session['phone'] = patient.phone_number
            return redirect(url_for('homepage_patient', phone=phone))
        elif time_lapsed > 300:
            flash('Code expired. Kindly request a new one.', 'warning')
            patient.current_otp = None
            patient.otp_expired = True
            patient.otp_creation_time = None
            db.session.commit()
            session.pop('phone', None)
            return redirect (url_for('homepage_medic'))
        else:
            flash("Invalid Code. Confirm the code or ", 'redirect')
    
    return render_template('otp-confirmation.html', title='confirm-otp', confirm_opt_form=form)


@app.route('/create_record')
@app.route('/create_record/<field>', methods=['GET','POST'])
@login_required
@doctor_required
def create_record(field):
    """Handle creation of a new tretment record
    """
    if session.get('s_record_data') is None:
        session['s_record_data'] = {}


    if field == 'diagnosis':
        form = DiagnosisForm()
        if  form.validate_on_submit():
            session['s_record_data']['diagnosis'] = form.diagnosis.data
            return redirect(url_for('create_record',field='casenotes'))
        return render_template('diagnosis_new_record.html', title='New Record-Diagnosis', form=form)
    if field == 'casenotes':
        form = CaseDetails()
        if form.validate_on_submit():
            bp  = f"Blood Pressure was {form.bp_systolic.data}/{form.bp_diastolic.data}\n"
            session['s_record_data']['case_notes']= f"{bp}HPI: {form.presenting_illness_history.data}"
            return redirect(url_for('create_record', field='investigations'))
        return render_template('casenotes_new_record.html', title='New Record-Casenotes', form=form)
    if field == 'investigations':
        form = InvestgationsForm()
        if  form.validate_on_submit():
            session['s_record_data']['investigations'] = form.investigations.data
            return redirect(url_for('create_record',field='medications'))
        return render_template('investigations_new_record.html', title='New Record-Investigations', form=form)
    if field == 'medications':
        form = MedicationForm()
        if  form.validate_on_submit():
            session['s_record_data']['medications'] = form.medications.data
            return redirect(url_for('create_record',field='interventions'))
        return render_template('medications_new_record.html', title='New Record-Medications', form=form)
    if field == 'interventions':
        form = InterventionsForm()
        if  form.validate_on_submit():
            session['s_record_data']['interventions'] = form.interventions.data
            return redirect(url_for('create_record',field='save_record'))
        return render_template('interventions_new_record.html', title='New Record-Interventions', form=form)
    if field == 'save_record':
        form = NewRecordForm()
        if request.method == 'GET':
            form.diagnosis.data =  session['s_record_data']['diagnosis']
            form.casenotes.data =  session['s_record_data']['case_notes']
            form.investigations.data =  session['s_record_data']['investigations']
            form.medications.data =  session['s_record_data']['medications']
            form.interventions.data =  session['s_record_data']['interventions']
            return render_template('new_record_save.html', title='New Record-Save', form=form)
        if form.validate_on_submit():
            pt =Patient.query.filter_by(phone_number=session['phone']).first()
            record = TreatmentRecord(patient_id = pt.id,
                                     facility_name = current_user.facility_name,
                                     diagnosis = form.diagnosis.data,
                                     case_notes = form.casenotes.data,
                                     investigations_done = form.investigations.data,
                                     medication_given = form.medications.data,
                                     interventions_done=form.interventions.data)
            db.session.add(record)
            db.session.commit()
            return redirect(url_for('homepage_patient'))
        return redirect(url_for('create_record', field='save_record'))
        
@app.route('/records')
def records():
    """Handle display of an indivual treament record
    """
    r_id = request.args.get('id')

    if r_id is None:
        flash("Invalid record.", 'warning')
        return redirect(url_for('homepage_patient'))
    record = TreatmentRecord.query.filter_by(id=r_id).first()
    return render_template('show_record.html', record=record)

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    """Handle account updates and view logic
    """
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if current_user.role == 'patient':
            current_user.phone_number = int(form.phone.data)
        if current_user.role == 'medic':
            current_user.facility_name = form.facility_name.data
        db.session.commit()
        flash('Details Changed!', 'success')
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        if current_user.role == 'patient':
            phone_string = '0' + str(current_user.phone_number)[3:]
            form.phone.data= phone_string
        if current_user.role == 'medic':
            form.facility_name.data = current_user.facility_name

    return render_template('account.html', title='Account', form=form)


@app.route('/logout')
@login_required
def logout():
    """Logs out a user and clears a session's values
    """
    logout_user()
    expired = 'false'
    user_category = None
    if 'phone' in session:
        patient = Patient.query.filter_by(phone_number=session.get('phone')).first()
        if patient:
            patient.code_expired = False
            db.session.commit()
    if 'expired' in session:
        if session.get('expired') is True:
            expired = 'true'
            user_category = session['user_type']
    session.clear()
    session['expired_final'] = expired
    session['user_category'] = user_category
    return redirect(url_for('home'))


@app.route('/delete_account', methods=['GET'])
@login_required
def delete_account():
    """Handles deletion of all records associated with an account
    """
    if current_user.role == 'patient':
        Patient.query.filter_by(id=current_user.id).delete()
        db.session.commit()
    if current_user.role == 'medic':
        MedicalProfessional.query.filter_by(id=current_user.id).delete()
        db.session.commit()
    flash('Account has been successfully deleted', 'success')
    session.clear()
    return redirect(url_for('home'))