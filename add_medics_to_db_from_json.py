import json
import os
from patientconnect.models import *
from patientconnect import db, app
"""adds registration details to a database from json files"""

current_dir = os.getcwd()

def add_doctors_to_db():
    """populates the Registered Doctors table with data
    """
    with open(os.path.join(current_dir, 'patientconnect', 'registered_medics', 'doctors.json'), 'r') as f:
        with app.app_context():
            doctors = json.load(f)
            try:
                # delete all data within the table
                RegisteredDoctors.query.delete()
                db.session.commit()

                # iterate over the data form the json file and create new 
                # instances of doctors 
                for doctor in doctors[1:]:
                    name_doc = doctor.get('name')
                    if name_doc is not None:
                        name_doc = name_doc.replace('NULL', '')
                        reg = doctor.get('reg')[:3]
                        active = doctor.get('status')
                        doc = RegisteredDoctors(name=name_doc,
                                                reg_no=reg,
                                                active=active)
                        db.session.add(doc)
                db.session.commit()
                print("done adding doctors")
            except Exception as e:
                db.session.rollback()
                print(f'Error adding doctors {e}')


def add_pharmacists_to_db():
    """populates the Registered Pharmacists table with data
    """
    with open(os.path.join(current_dir, 'patientconnect', 'registered_medics', 'pharmacists.json'), 'r') as f:
        with app.app_context():
            pharmacists = json.load(f)
            try:
                RegisteredPharmacists.query.delete()
                db.session.commit()
                for pharmacist in pharmacists[1:]:
                    name_doc = pharmacist.get('name')
                    if name_doc is not None:
                        name_doc = name_doc.replace('NULL', '')
                        reg = pharmacist.get('reg')
                        active = pharmacist.get('status').strip()
                        new_pharmacist = RegisteredPharmacists(name=name_doc,
                                                reg_no=reg,
                                                active=active)
                        db.session.add(new_pharmacist)
                db.session.commit()
                print("done adding pharmacists")
            except Exception as e:
                db.session.rollback()
                print(f'Error adding pharmacists {e}')

def add_pharmtechs_to_db():
    """populates the Registered Pharmtechs table with data
    """
    with open(os.path.join(current_dir, 'patientconnect','registered_medics', 'pharmtechs.json'), 'r') as f:
        with app.app_context():
            pharmtechs = json.load(f)
            try:
                RegisteredPharmtechs.query.delete()
                db.session.commit()
                for pharm_tech in pharmtechs[1:]:
                    name_doc = pharm_tech.get('name')
                    if name_doc is not None:
                        name_doc = name_doc.replace('NULL', '')
                        reg = pharm_tech.get('reg')
                        active = pharm_tech.get('status').strip()
                        new_pharm_tech = RegisteredPharmtechs(name=name_doc,
                                                reg_no=reg,
                                                active=active)
                        db.session.add(new_pharm_tech)
                db.session.commit()
                print("done adding pharmtechs")
            except Exception as e:
                db.session.rollback()
                print(f'Error adding pharmtechs {e}')


add_pharmtechs_to_db()
add_pharmacists_to_db()
add_doctors_to_db()
