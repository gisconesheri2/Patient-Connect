import json
from patientconnect.models import *
from patientconnect import db

def add_doctors_to_db():
    with open(r'C:\Users\gisconesheri\Desktop\Patient-Connect\patientconnect\registered_medics\doctors.json', 'r') as f:
        doctors = json.load(f)
        for d in doctors[1:]:
            # print(d)
            name_doc = d.get('name')
            if name_doc is not None:
                name_doc = name_doc.replace('NULL', '')
                reg = d.get('reg')[:3]
                active = d.get('status')
                doc = RegisteredDoctors(name=name_doc,
                                        reg_no=reg,
                                        active=active)
                db.session.add(doc)
        db.session.commit()

def add_pharmacists_to_db():
    with open(r'C:\Users\gisconesheri\Desktop\Patient-Connect\patientconnect\registered_medics\pharmacists.json', 'r') as f:
        doctors = json.load(f)
        for d in doctors[1:]:
            # print(d)
            name_doc = d.get('name')
            if name_doc is not None:
                name_doc = name_doc.replace('NULL', '')
                reg = d.get('reg')
                active = d.get('status').strip()
                doc = RegisteredPharmacists(name=name_doc,
                                        reg_no=reg,
                                        active=active)
                db.session.add(doc)
        db.session.commit()

def add_pharmtechs_to_db():
    with open(r'C:\Users\gisconesheri\Desktop\Patient-Connect\patientconnect\registered_medics\pharmtechs.json', 'r') as f:
        doctors = json.load(f)
        for d in doctors[1:]:
            name_doc = d.get('name')
            if name_doc is not None:
                name_doc = name_doc.replace('NULL', '')
                reg = d.get('reg')
                active = d.get('status').strip()
                doc = RegisteredPharmtechs(name=name_doc,
                                        reg_no=reg,
                                        active=active)
                db.session.add(doc)
        db.session.commit()

