## PATIENT CONNECT
![Patient Connect Homepage](https://github.com/gisconesheri2/Patient-Connect/assets/135016760/8eb929bb-3cb4-4a30-8095-10d1e8749ecd)

A way to share patient's medical history across healthcare providers and medical facilities

Patient Connect is a web application built using Flask web framework that provides a platform where medical records can be easily shared and accessed by both patients and the medical fraternity.

Here is [deployed project](https://gaceripeter.pythonanywhere.com/ ), the [landing page](https://gisconesheri2.github.io/gisconesheri2.gitbub.io/), my [LinkedIn](https://www.linkedin.com/in/peter-gikonyo-9a29491b9/) and a [blog post] about the project.

## INSTALLATION
The requirements.txt file contains all the dependencies needed to run the app.

Run:

```
user@group$ cd Patient-Connect
user@group ~/Patient-Connect$ pip install -r requirements.txt
```
Before using the app, you have to create an .env file in the patientconnect folder with these environment variables defined:
- SECRET_KEY (you can generate one using the python's [secrets](https://www.geeksforgeeks.org/secrets-python-module-generate-secure-random-numbers/) module)
- MAIL_USER (a valid gmail address used to send emails)
- MAIL_PASS (an app password generated within the gmail account settings. See [here](https://www.zdnet.com/article/gmail-app-passwords-what-they-are-how-to-create-one-and-why-to-use-them/)

Alternatively, these can be set as system variables as per your operating system

The next step is to initialize the database. Start a python interactive environment from the main folder of the project and run:

```
user@group ~/Patient-Connect$ python3
Python 3.8.10 (..)
[GCC 9.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from patientconnect import db, app
>>> with app.app_context():
...     db.create_all()
... 
>>> exit()
```

Intialize some databases needed to run the app

```
user@group ~/Patient-Connect$ python3 -m add_medics_to_db_from_json
```

You can now run the run.py file to start the app.

```
user@group ~/Patient-Connect$ python3 -m run
```

Navigate to http://127.0.0.1:5000 on your browser to see the app running locally

## USAGE
The app has two types of users: healthcare professionals and patients. A user's experience will be as show below
 
![Patient Connect Usage Flow](https://github.com/gisconesheri2/Patient-Connect/assets/135016760/afec4014-e560-4132-bee8-e665672e9092)

## CONTRIBUTING
I was the sole contributor to the project

## RELATED PROJECTS
My projects for the ALX software engineering program can be found [here](https://github.com/gisconesheri2).

## LICENSING
MIT Licence
