PATIENT CONNECT
A way to share patient's medical history across healthcare providers and medical facilities

Patient Connect is a web application built using Flask web framework that provides a platform where medical records can be easily shared and accessed by both patients and the medical fraternity.

Here is deployed project, the landing page, my LinkedIn and a blog post about the project.

Installation
The requirements.txt file contains all the dependencies needed to run the app.

Run:

pip install -r requirements.txt

Then to initialize the database start a python interactive environment from the main folder of the project and run:

from patientconnect import db
with app.app_context():
    db.create_all()

and exit the python environment.

You can now run the run.py file to start the app.


