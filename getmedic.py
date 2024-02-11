from html.parser import HTMLParser
from bs4 import BeautifulSoup
from lxml import html
import json
import requests

def get_pharmacists():
    url = 'https://practice.pharmacyboardkenya.org/LicenseStatus?register=pharmacists'

    x = requests.get(url)

    html_doc_f = x.text
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
    print(all)
    with open(r'c:\Users\gisconesheri\Desktop\Patient-Connect\patientconnect\registered_medics\pharmacists.json', 'w') as f:
        json.dump(all, f)

def get_pharmtechs():
    url = 'https://practice.pharmacyboardkenya.org/LicenseStatus?register=pharmtechs'

    x = requests.get(url)

    html_doc_f = x.text
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
    with open(r'c:\Users\gisconesheri\Desktop\Patient-Connect\patientconnect\registered_medics\pharmtechs.json', 'w') as f:
        json.dump(all, f)

def get_doctors():
    # have to get the html manually
    with open('medics_register.html', 'r') as f:
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

    with open('doctors.json', 'w') as f:
      json.dump(all, f)