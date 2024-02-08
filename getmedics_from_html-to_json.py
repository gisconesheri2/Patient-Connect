from bs4 import BeautifulSoup
import json
import requests

""" Gets registration details for medics from html files and saves then to
JSON files for easy manipulation into an sql database
"""
def get_pharmacists():
    """From the pharmacist's register html (obtained form copying and
    pasting the html from https://practice.pharmacyboardkenya.org/LicenseStatus?register=pharmacists)
    parse the included tables and extract the names, registration number and registration status
    """

    with open(r'patientconnect\registered_medics\pharmacists_register.html', 'r') as f:
      html_doc_f = f.read()

    soup = BeautifulSoup(html_doc_f, 'html.parser')
    headers = ['name', 'reg']

    all = []

    for tag in soup.find_all('tr'):
        name = {}
        n = 0
        for td in tag.find_all('td'):
            if n < 2:
                name[headers[n]] = td.string
                n += 1
            if td.find('span') is not None:
                name['status'] = tag.find('span').string.split(':')[1]
        all.append(name)
    with open(r'patientconnect\registered_medics\pharmacists.json', 'w') as f:
        json.dump(all, f)

def get_pharmtechs():
    """From the pharmtechs register html (obtained form copying and
    pasting the html from https://practice.pharmacyboardkenya.org/LicenseStatus?register=pharmtechs)
    parse the included tables and extract the names, registration number and registration status
    """

    with open(r'patientconnect\registered_medics\pharmtechs_register.html', 'r') as f:
        html_doc_f = f.read()
    soup = BeautifulSoup(html_doc_f, 'html.parser')
    headers = ['name', 'reg']

    all = []

    for tag in soup.find_all('tr'):
        name = {}
        n = 0
        for td in tag.find_all('td'):
            if n < 2:
                name[headers[n]] = td.string
                n += 1
            if td.find('span') is not None:
                name['status'] = tag.find('span').string.split(':')[1]
        all.append(name)
    with open(r'patientconnect\registered_medics\pharmtechs.json', 'w') as f:
        json.dump(all, f)

def get_doctors():
    """From the doctors register html (obtained form copying and
    pasting the html from https://kmpdc.go.ke/Registers/practitioners.php)
    parse the included tables and extract the names, registration number and registration status
    """
      
    with open(r'patientconnect\registered_medics\medics_register.html', 'r') as f:
      html_doc_f = f.read()
    soup = BeautifulSoup(html_doc_f, 'html.parser')
    headers = ['name', 'reg']
    all = []
    for tag in soup.find_all('tr'):
        name = {}
        n = 0
        for td in tag.find_all('td'):
            if n < 2:
              name[headers[n]] = td.string
              n += 1
            if td.find('span') is not None:
              name['status'] = tag.find('span').string
        all.append(name)
        # name['status'] = tag.find('span').string.split(':')[1]

    with open(r'patientconnect\registered_medics\doctors.json', 'w') as f:
      json.dump(all, f)

get_doctors()
get_pharmacists()
get_pharmtechs()