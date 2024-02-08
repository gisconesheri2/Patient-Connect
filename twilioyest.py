from html.parser import HTMLParser
from bs4 import BeautifulSoup
from lxml import html
import requests

html_doc = """ <tr >
                                        <td >PERPETUA WANJIKU KARANJA</td>
                                        <td >2517</td>
                                        <td >P2024D00582</td>
                                        <td ><span class='label label-success'>Status: Active</span> &nbsp; 2024-12-31</td>
                                        <td >
                                        <!--<a href='' class='printable'>View more</a>-->
                                        <a  data-placement="top" title="Click to View Details" class="popStatus" href="#" rel='MzEyNjg=' data-toggle="modal" data-target=".details"    >View Details </a>
                                       
                                       <!-- <a href='#' rel='' class='view_details'>View Details</a>-->
                                        </td>
                                      </tr>
                                                                            <tr >
                                        <td >PETER MWANGI NGUMO</td>
                                        <td >1966</td>
                                        <td >P2024D00175</td>
                                        <td ><span class='label label-success'>Status: Active</span> &nbsp; 2024-12-31</td>
                                        <td >
                                        <!--<a href='' class='printable'>View more</a>-->
                                        <a  data-placement="top" title="Click to View Details" class="popStatus" href="#" rel='MzA4Njc=' data-toggle="modal" data-target=".details"    >View Details </a>
                                       
                                       <!-- <a href='#' rel='' class='view_details'>View Details</a>-->
                                        </td>
                                      </tr>"""

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
print(all)