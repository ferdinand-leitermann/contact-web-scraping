import gspread
from gspread.models import Cell
from oauth2client.client import GoogleCredentials
import pickle

company_ws_file = 'Lista-Company'
employee_ws_file = 'Lista-Employee'

gc = gspread.authorize(GoogleCredentials.get_application_default())


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


class Address:
    def __init__(self, street1, street2, zip, city, country):
        self.street1 = street1
        self.street2 = street2
        self.zip = zip
        self.city = city
        self.country = country


file_path = ''
file_name = 'Lista-Dataset.pickle'

with open(file_path + file_name, 'rb') as f:
    dataset = pickle.load(f)

company_cells = []
employee_cells = []
email_count = 0
email_com = 0
email_ee = 0

for c in dataset[0]:
    print(c.name, c.industry, c.email, c.phone, c.website, c.address.street1)

for index, c in enumerate(dataset[0]):
    company_cells.append(Cell(row=index + 1, col=1, value=c.id))
    company_cells.append(Cell(row=index + 1, col=2, value=c.name))
    company_cells.append(Cell(row=index + 1, col=3, value=c.industry))
    company_cells.append(Cell(row=index + 1, col=4, value=c.email))
    company_cells.append(Cell(row=index + 1, col=5, value=c.phone))
    company_cells.append(Cell(row=index + 1, col=6, value=c.fax))
    company_cells.append(Cell(row=index + 1, col=7, value=c.website))
    company_cells.append(Cell(row=index + 1, col=8, value=c.address.street1))
    company_cells.append(Cell(row=index + 1, col=9, value=c.address.city))
    company_cells.append(Cell(row=index + 1, col=10, value=c.src))
    if '@' in c.email:
        email_com += 1

# for index, e in enumerate(dataset[1]):
#   address = e.company.address.street1 + e.company.address.city
#   employee_cells.append(Cell(row=index+1, col=1, value=e.id))
#   employee_cells.append(Cell(row=index+1, col=2, value=e.name))
#   employee_cells.append(Cell(row=index+1, col=3, value=e.position))
#   employee_cells.append(Cell(row=index+1, col=4, value=e.email))
#   employee_cells.append(Cell(row=index+1, col=5, value=e.mobile))
#   employee_cells.append(Cell(row=index+1, col=6, value=e.phone))
#   employee_cells.append(Cell(row=index+1, col=7, value=e.company.id))
#   employee_cells.append(Cell(row=index+1, col=8, value=e.company.industry))
#   employee_cells.append(Cell(row=index+1, col=9, value=e.company.name))
#   employee_cells.append(Cell(row=index+1, col=10, value=address))
#   if e.email is not None:
#     email_ee += 1

email_count = email_com + email_ee
print(email_count, email_com, email_ee)

company_ws = gc.open(company_ws_file).sheet1
company_ws.update_cells(company_cells)

# employee_ws = gc.open(employee_ws_file).sheet1
# employee_ws.update_cells(employee_cells)
