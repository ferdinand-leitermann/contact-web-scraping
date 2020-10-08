from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import pickle
import datetime

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# path for saved dataset
path = ''
dataset_filename = "Lista-Dataset.pickle"

domain = "https://lista.mt"
root = "https://lista.mt"

company_index = 0
employee_index = 0

company_list = []
employee_list = []

src_set = set()


class Company:
    def __init__(self, id, name, industry, email, phone, website, fax,
                 employees, address, src):
        self.id = id
        self.name = name
        self.industry = industry
        self.email = email
        self.phone = phone
        self.website = website
        self.fax = fax
        self.address = address
        self.src = src
        if employees is None:
            employees = []
        self.employees = employees

    def add_employee(self, employee):
        self.employees.append(employee)

    def get_employees_ids(self):
        ids = []
        for employee in self.employees:
            ids.append(employee.id)
        return ids


def generate_company_id():
    global company_index
    new_id = 'Lista-CO.' + '{:0>4}'.format(company_index)
    company_index += 1
    return new_id


class Employee:
    def __init__(self, id, name, position, email, mobile, phone, company):
        self.id = id
        self.name = name
        self.position = position
        self.email = email
        self.mobile = mobile
        self.phone = phone
        self.company = company
        company.add_employee(self)


def generate_employee_id():
    global employee_index
    new_id = 'MP-EE.' + '{:0>4}'.format(employee_index)
    employee_index += 1
    return new_id


class Address:
    def __init__(self, street1, street2, zip, city, country):
        self.street1 = street1
        self.street2 = street2
        self.zip = zip
        self.city = city
        self.country = country


def get_urls(domain, max_page):
    urls = []
    for num in range(max_page):
        param = "/?pagenum=" + str(num + 1) + "&sort%5B1%5D=asc"
        link = domain + param
        print(link)
        html = requests.get(link).text
        soup = BeautifulSoup(html, 'lxml')
        tds = soup.find_all('td', {'data-label': 'More Info'})
        for td in tds:
            try:
                urls.append(td.find('a')['href'])
            except:
                print('no url')

    return urls


def add_company(urls):
    for url in urls:
        try:
            if url not in src_set:
                starttime = datetime.datetime.now()
                src_set.add(url)
                wd = webdriver.Chrome(options=options)
                wd.get(url)
                html = wd.page_source
                soup = BeautifulSoup(html, 'lxml')
                wd.quit()
                # name
                try:
                    name = soup.find('tr', {'class': 'gv-field-1-1'}).find(
                        'td').text
                    # print(name)
                except:
                    name = ''
                # phone
                try:
                    phone = \
                        soup.find('tr', {'class': 'gv-field-1-4'}).find('a')[
                            'href'][4:].replace('%20', '')
                    phone = phone.split('/')[0].split(',')[0]
                    # print(phone)
                except:
                    phone = ''
                # website
                try:
                    website = \
                        soup.find('tr', {'class': 'gv-field-1-5'}).find('a')[
                            'href']
                    # print(website)
                except:
                    website = ''
                # email
                try:
                    email = \
                        soup.find('tr', {'class': 'gv-field-1-6'}).find('a')[
                            'href']
                    # print(email)
                except:
                    email = ''
                # address
                try:
                    address_str = soup.find('tr',
                                            {'class': 'gv-field-1-15'}).find(
                        'td').text[:-6]
                    street1 = address_str
                    address = Address(street1, None, None, None, 'Malta')
                    # print(address)
                except:
                    address = Address(None, None, None, None, 'Malta')
                # industry
                try:
                    industries = soup.find('tr',
                                           {'class': 'gv-field-1-20'}).find_all(
                        'li')
                    industry = ''
                    for i in industries:
                        industry += (i.text + ' ')
                    # print(industry)
                except:
                    industry = ''
                company = Company(generate_company_id(), name, industry, email,
                                  phone, website, None, None, address, url)
                company_list.append(company)
                endtime = datetime.datetime.now()
                duration = endtime - starttime
                print(company.name, 'added in', duration)
        except Exception as e:
            print(e)


urls = get_urls(domain, 1)
add_company(urls)
print(src_set)
print('count', len(src_set))
dataset = [company_list, employee_list]

# save dataset
with open(path + dataset_filename, 'wb') as f:
    pickle.dump(dataset, f, pickle.HIGHEST_PROTOCOL)
