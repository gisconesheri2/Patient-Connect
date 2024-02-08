from patientconnect import app, db, bcrypt, scheduler, doctor_required, mail
from patientconnect.models import MedicalProfessional, Patient, TreatmentRecord
from markupsafe import Markup
from flask import render_template, url_for, flash, redirect, request, session
from patientconnect.forms import *
from flask_login import login_user, current_user, login_required, logout_user
from flask_mail import Message
import pyotp
from datetime import datetime, timedelta

@app.route('/')
@app.route('/home')
def home():
    if current_user.is_authenticated and current_user.role == 'medic':
        return redirect(url_for('homepage_medic'))
    
    if current_user.is_authenticated and current_user.role == 'patient':
        return redirect(url_for('homepage_patient'))
    print(session)
    if 'expired_final' in session:
        if session.get('expired_final') == 'true':
            flash('Your session has expired after 30 minutes, you have been logged out. Please login again', 'info')
            user = session.get('user_category')
            session.pop('expired_final', None)
            session.pop('user_category', None)
            return redirect(url_for('login', user=user))
    return render_template('home.html')

@app.route('/about')
def about():
    return 'about'

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@patientconnect.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit this link:
{url_for('reset_token', user=user.role, token=token, _external=True)}

if you did not make this request, ignore this message.
'''
    mail.send(msg)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():

    if current_user.is_authenticated and current_user.role == 'medic':
        return redirect(url_for('homepage_medic'))
    
    if current_user.is_authenticated and current_user.role == 'patient':
        return redirect(url_for('homepage_patient'))
    
    form = RequestResetForm()
    user = request.args.get('user')

    if form.validate_on_submit():
        if user == 'patient':
            patient = Patient.query.filter_by(email=form.email.data).first()
            if patient is None:
                flash('There is no account with that email. You must register first.', 'warning')
                return redirect(url_for('ptsignup'))
            else:
                send_reset_email(patient)
                flash('Password reset instructions sent to email provided.', 'info')
                return redirect(url_for('login', user='patient'))
            
        if user == 'medic':
            medic = MedicalProfessional.query.filter_by(email=form.email.data).first()
            if medic is None:
                flash('There is no account with that email. You must register first.', 'warning')
                return redirect(url_for('medsignup'))
            else:
                send_reset_email(medic)
                flash('Password reset instructions sent to email provided.', 'info')
                return redirect(url_for('login', user='medic'))
            
    print(request.args.get('user'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated and current_user.role == 'medic':
       return redirect(url_for('homepage_medic'))
    
    if current_user.is_authenticated and current_user.role == 'patient':
        return redirect(url_for('homepage_patient'))

    user = request.args.get('user')
    if user == 'patient':
        patient = Patient.verify_reset_token(token)
        if patient is None:
            flash('That is an invalid or expired token', 'warning')
            return redirect(url_for('reset_request', user='patient'))
        form = ResetPasswordForm()
        if form.validate_on_submit():
        # hash the password
            hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
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
    
@app.route('/contact_us')
def contact_us():
    return 'number'

@app.route('/medsignup', methods=['GET', 'POST'])
def medsignup():
    if current_user.is_authenticated and current_user.role == 'medic':
        return redirect(url_for('homepage_medic'))
    
    if current_user.is_authenticated and current_user.role == 'patient':
        return redirect(url_for('homepage_patient'))
    
    form = MedicalRegistrationForm()
    if form.validate_on_submit():
        # hash the password
        hashed_pwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        username = f"{form.surname.data} {form.other_names.data}"
        med_user = MedicalProfessional(username=username.title(), email=form.email.data,
                                   password=hashed_pwd, profession=form.profession.data,
                                   registration_number=form.registration_number.data,
                                   facility_name=form.facility_name.data)
        db.session.add(med_user)
        db.session.commit()
        flash(f'Your account has been created. You can now login!', 'success')
        return(redirect(url_for('login', user='medic')))
    return render_template('medsignup.html', title='Sign Up', form=form)

@app.route('/ptsignup', methods=['GET', 'POST'])
def ptsignup():

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

    if current_user.is_authenticated and current_user.role == 'medic':
        return redirect(url_for('homepage_medic'))
    
    if current_user.is_authenticated and current_user.role == 'patient':
        return redirect(url_for('homepage_patient'))
    print(session)
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
    phone = session.get('phone')
    user = session.get('user_type')
    q_phone = request.args.get('phone')
    if user == 'patient':
        records = current_user.treatment_records
        username = current_user.username
        return render_template('homepage_patient.html', title='Patient Homepage',
                            records=records, username=username)
    
    if user == 'medic' and phone is None:
        return redirect(url_for('homepage_medic'))
    elif user == 'medic' and phone is not None:
        patient = Patient.query.filter_by(phone_number=phone).first()
        records = patient.treatment_records
        username= patient.username
        return render_template('homepage_patient.html', title='Patient Homepage',
                            records=records, username=username)


def send_otp_email(patient):
    msg = Message('Visit Authorization Code', sender='patientconnect24@gmail.com',
                  recipients=[patient.email])
    msg.body = f'''To authorize the visit, share this code with your doctor:
{patient.current_otp}
if you did not make this request, ignore this message.
'''
    mail.send(msg)

@app.route('/homepage_medic', methods=['GET', 'POST'])
@login_required
@doctor_required
def homepage_medic():
    form = GetPhoneNumber()
    # form.country_code.data = '254'
    # code_expired generated by an automatic redirect from the otp_confirmation page
    # used to generate an alert on the template that the code expired
    code_expired = request.args.get('code_expired')
    if code_expired == 'true':
        patient = Patient.query.filter_by(phone_number=session.get('phone')).first()
        if patient:
            patient.current_otp = None
            patient.otp_expired = True
            db.session.commit()
    print(session)
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
        session['phone'] = patient.phone_number
        print(otp)
        db.session.commit()

        send_otp_email(patient)
        # TODO send otp
        flash('Enter the OTP code sent to the patient. It is valid for 5 minutes', 'primary')
        return redirect(url_for('otp_confirmation', phone=phone))
    return render_template('homepage_medic.html',
                            get_phone_form=form,
                            title='Medic DashBoard',
                            code_expired=code_expired)


@app.route('/otp_confirmation', methods=['GET', 'POST'])
def otp_confirmation():
    form = VisitStartForm()

    # phone number needed to access the patient database's and their otp
    phone = request.args.get('phone')
    if phone is None:
        flash('Enter Phone Number', 'warning')
        return redirect (url_for('homepage_medic'))
    print(request.form)
    # set a timer for 180 seconds to delete the patient's otp from database
    date = datetime.now() + timedelta(seconds=300)

    def remove_code():
        """Removes the user's otp from the database"""
        with scheduler.app.app_context():
            patient = Patient.query.filter_by(phone_number=phone).first()
            patient.current_otp = None
            patient.otp_expired = True
            db.session.commit()
            print('code expired')
            scheduler.remove_all_jobs()

    patient = Patient.query.filter_by(phone_number=phone).first()
    
    if form.validate_on_submit():
        if patient.current_otp == form.authorization_code.data:
            patient.current_otp = None
            patient.otp_expired = True
            db.session.commit()
            scheduler.remove_all_jobs()
            session['phone'] = patient.phone_number
            return redirect(url_for('homepage_patient', phone=phone))
        elif patient.otp_expired == True:
            flash('Code expired. Request a new one.', 'warning')
            patient.otp_expired = False
            db.session.commit()
            return redirect (url_for('homepage_medic'))
        else:
            flash("Invalid Code. Confirm the code or ", 'redirect')

    # set up the scheduler to delete the patient's otp
    if scheduler.get_job(id='testtime3') is None:
        scheduler.add_job(id='testtime3', func=remove_code, trigger='date', run_date=date)
    
    return render_template('otp-confirmation.html', title='confirm-otp', confirm_opt_form=form)


@app.route('/create_record')
@app.route('/create_record/<field>', methods=['GET','POST'])
@login_required
@doctor_required
def create_record(field):
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
    r_id = request.args.get('id')
    record = TreatmentRecord.query.filter_by(id=r_id).first()
    return render_template('show_record.html', record=record)

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    print(form.errors)
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

    print(form.errors)
    return render_template('account.html', title='Account', form=form)


@app.route('/logout')
@login_required
def logout():
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

