
#time
import datetime

#import for gspread authentification
import datetime

#import for gspread authentification
from google.colab import auth
auth.authenticate_user()

import gspread
from gspread.models import Cell
from oauth2client.client import GoogleCredentials

#import for html scraping
from bs4 import BeautifulSoup
import requests

#source sheet name
source_sheet = 'whoslist'

#company detination wb
company_destination = 'Contact_Company'

#person detination wb
person_destination = 'Contact_Person'

#open whoiswho source sheet
gc = gspread.authorize(GoogleCredentials.get_application_default())
worksheet = gc.open(source_sheet).sheet1 
urls = worksheet.col_values(2)

#cell arry for update
person_cells = []
company_cells = []

#perso dict {person_dummy: person_extId}
person_dict = {}
#company dict
company_dict = {}

#dict {url:ex_Id}
checked_company_urls = {}
checked_person_urls = {}

#personID
personId_index = 0
#companyID
companyId_index = 0

def get_personId(person_dummy):
  global person_dict
  if person_dummy in person_dict:
    person_exId = ''
    return person_exId

  global personId_index
  person_exId = 'WWCont.' + '{:0>4d}'.format(personId_index)
  person_dict[person_dummy] = person_exId
  personId_index += 1
  return person_exId

def get_companyId(company_dummy):
  global company_dict
  if company_dummy in company_dict:
    comp_exId = company_dict.get(company_dummy)
    return (1,comp_exId)

  global companyId_index
  comp_exId = 'WWComp.' + '{:0>4d}'.format(companyId_index)
  company_dict[company_dummy] = comp_exId
  companyId_index += 1
  return (0,comp_exId)

#person parser
def get_person(url):
  global checked_person_urls
  if url in checked_person_urls:
    #print('duplicate person url')
    return (['',0],[1,0])
  html_content = requests.get(url).text
  soup = BeautifulSoup(html_content, 'lxml')
  try:
    info = soup.find_all("div", {'class':'info'})[0]
    name = info.findAll('h2')[0].text.strip()
    position = info.find_all('h4')[0].text.strip()
    company_name = info.find_all('h4')[1].text.strip()
    industry = info.find('span').text.strip()
  except:
    print('error with url: ', url)
  try:
     website = soup.find('p',{'data-hide':'website'}).find('a')['href']
  except:
     website = " "

  try:
    email = soup.find('p',{'data-hide':'email'}).find('a')['href']
    email = email[7:]
  except:
    email = " "

  try:
    phone = soup.find('p',{'data-hide':'phone'}).find('a').text.strip()
  except:
    phone = " "

  try:
    mobile = soup.find('p',{'data-hide':'mobile'}).find('a').text.strip()
  except:
    mobile = " "

  try:
    com_url_path = soup.find('div',{'class':'job-details'}).find('a').get('href')
    if not com_url_path:
      raise Exception('exception')
    domain = 'https://whoswho.mt'
    com_url = domain + com_url_path
    company = get_company(com_url)
  except:
    print('no linked company for '+ name)
    comp_phone = ''
    comp_email = ''
    address = ''
    latitude = ''
    longitude = ''
    company_dummy = (company_name,industry,website,comp_email,phone,address,latitude,longitude)
    comp_exId = get_companyId(company_dummy)
    company = [comp_exId[0],comp_exId[1], company_name,industry,website,comp_email,comp_phone,address,latitude,longitude]

  person_dummy = (name, position, email,phone,mobile)
  person_exId = get_personId(person_dummy)
  person = [person_exId, name, position, email,phone,mobile,company[1]]

  checked_person_urls.update({url:person_exId})

  return (person , company)

#company parser
def get_company(url):
  global checked_company_urls
  if url in checked_company_urls:
    #print('duplicat company')
    return [1,checked_company_urls[url]]
  html = requests.get(url).text
  soup = BeautifulSoup(html, 'lxml')
  #print(soup.prettify())
  try:
    email = soup.find('p',{'data-hide':'email'}).find('a')['href']
    email = email[7:]																						
  except:
    email = " "

  try:
    phone = soup.find('p',{'data-hide':'phone'}).find('a').text.strip()
  except:
    phone = " "

  try:
    address = soup.find('div',{'class':'address'}).find_all('p')[1].text.strip()
  except:
    address = " "

  try:
    info = soup.find_all("div", {'class':'info'})[0]
    company_name = info.findAll('h2')[0].text.strip()
    industry = info.find('span').text.strip()
  except:
    company_name = 'none'
    industry = 'none'

  try:
    website = soup.find('p',{'data-hide':'website'}).find('a')['href']
  except:
    website = " "

  try:
    coords = soup.find('input',{'id':'mapCoordinatesTxt'})['value']
    coords_obj = [coord.strip() for coord in coords.split(',')]
    longitude = coords_obj[0]
    latitude =coords_obj[1]
  except:
    latitude = ''
    longitude = ''

  company_dummy = (company_name,industry,website,email,phone,address,latitude,longitude)
  comp_exId = get_companyId(company_dummy)
  company = [comp_exId[0],comp_exId[1], company_name,industry,website,email,phone,address,latitude,longitude]

  checked_company_urls.update({url:comp_exId[1]})

  return company

print(datetime.datetime.now())
#iterate through all urls / extract data
for url in urls:

  global personId_index
  global companyId_index

  if '/profile?' in url:
    person_company = get_person(url)

    person = person_company[0]
    company = person_company[1]

    #populate person row
    #person_header [person_exId, name, position, email,phone,mobile,comp_exId]
    if person[0]:
      for index, title in enumerate(person):
        person_cells.append(Cell(row=personId_index, col=index+1,value=title))
      print('added person: ' + person[1])

    #populate company row
    #company header [comp_exId, company_name,industry,website,comp_email,comp_phone,address]
    if company[0] is 0:
      for index, title in enumerate(company):
        company_cells.append(Cell(row=companyId_index, col=index+1,value=title))
      print("added company: " + company[2])


  if "/company?" in url:
    company = get_company(url)

    #populate company row
    #company header [comp_exId, company_name,industry,website,comp_email,comp_phone,address]
    if company[0] is 0:
      for index, title in enumerate(company):
        company_cells.append(Cell(row=companyId_index, col=index+1,value=title))
      print("added company: " + company[2])

print(datetime.datetime.now())
print(person_cells)
print(company_cells)
#update spreadsheet
person_ws = gc.open(person_destination).sheet1
company_ws = gc.open(company_destination).sheet1
person_ws.update_cells(person_cells)
company_ws.update_cells(company_cells)
