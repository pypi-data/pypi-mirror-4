import random
from os.path import abspath, join, dirname



__title__ = 'InfoGen'
__version__ = '1.0.0'
__author__ = 'Jinesh Patel'
__license__ = 'MIT'


file_location = lambda filename: abspath(join(dirname(__file__), filename))



FILES = {
    'first_name' : file_location('fname'),
    'last_name'  : file_location('lname'),
    'address'    : file_location('address'),
    'company'      : file_location('company')
}

def first_name(filename=FILES['first_name']):
    _temp1=[]
    f= open(filename)
    for i in f.readlines():
        _temp1.append(str(i).split('\r'))
    _fname = random.choice(random.choice(_temp1))
    return str(_fname)
        
def last_name(filename=FILES['last_name']):
    _temp2=[]
    f= open(filename)
    for i in f.readlines():
        _temp2.append(str(i).split('\r'))
    _lname = random.choice(random.choice(_temp2))
    return str(_lname)


def company(filename=FILES['company']):
    _temp4 = []
    f= open(filename)
    for i in f.readlines():
        _temp4.append(str(i).split('\r'))
    _company = random.choice(random.choice(_temp4))
    return _company

def address(filename=FILES['address']):
    _temp3=[]
    f= open(filename)
    for i in f.readlines():
        _temp3.append(str(i).split('\r'))
    _add = random.choice(random.choice(_temp3))
    return _add
    

def telephone_number():
    telephone_number  = str(random.randint(200,980))+'-'+str(random.randint(100,999))+'-'+str(random.randint(1000,9999))
    return telephone_number
    
def social_security_number():
    ssn = str(random.randint(100,999))+'-'+str(random.randint(10,99))+'-'+str(random.randint(1000,9999))
    return ssn
    



    
        
    
    
def personal_data():
    fname = first_name()
    lname = last_name()
    company_ = company()
    address_ = address()
    no = telephone_number()
    ssn = social_security_number()
    return "First Name: %s"%str(fname) +"Last Name: %s"%str(lname)+"Company: %s"%company_+"Address: %s"%str(address_) +"Telephone: %s"%str(no)+"\nSSN: %s"%str(ssn)



if __name__ == '__main__':
#    print personal_data()
    print first_name()
    print last_name()
    print company()
    print address()
    print telephone_number()
    print social_security_number()
    


