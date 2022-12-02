import sqlite3

#Open database
conn = sqlite3.connect('database.db')

#Create table
conn.execute('''CREATE TABLE manager 
		(mgrId INTEGER PRIMARY KEY, 
		password TEXT,
		email TEXT,
		firstName TEXT,
		lastName TEXT,
		address1 TEXT,
		address2 TEXT,
		zipcode TEXT,
		city TEXT,
		state TEXT,
		country TEXT, 
		phone TEXT
		)''')
        
conn.execute('''CREATE TABLE customers
(customer_id INTEGER NOT NULL AUTOINCREMENT PRIMARY KEY , 
password TEXT,
email TEXT,
firstName TEXT,
lastName TEXT,
address1 TEXT,
address2 TEXT,
zipcode TEXT,
city TEXT,
state TEXT,
country TEXT, 
phone TEXT,
Kind TEXT,
business category TEXT,
company gross annual income TEXT,
marriage status TEXT,
gender TEXT,
age TEXT,
income TEXT)
''')

conn.execute('''CREATE TABLE product_kind
(productKindId INTEGER PRIMARY KEY,
name TEXT)
''')

conn.execute('''CREATE TABLE products
(productId INTEGER PRIMARY KEY,
name TEXT,
inventory amount REAL,
price REAL,
description TEXT,
image TEXT,
stock INTEGER,
productKindId INTEGER,
FOREIGN KEY(productKindId) REFERENCES product_kind(productKindId))
''')

conn.execute('''CREATE TABLE salesperson
(name TEXT, 
address1 TEXT,
address2 TEXT,
zipcode TEXT,
city TEXT,
state TEXT,
country TEXT, 
email TEXT, 
jobTitle TEXT, 
store_assigned TEXT, 
salary REAL)
''')

conn.execute('''CREATE TABLE cart
(userId INTEGER,
productId INTEGER,
FOREIGN KEY(userId) REFERENCES users(userId),
FOREIGN KEY(productId) REFERENCES products(productId)
)
''')

conn.execute('''CREATE TABLE store
(store ID INTEGER, 
address1 TEXT,
address2 TEXT,
zipcode TEXT,
city TEXT,
state TEXT,
country TEXT, manager TEXT, 
number_of_salespersons INTEGER, 
region TEXT)
''')

conn.execute('''CREATE TABLE region
(region_ID INTEGER, 
region_name TEXT, 
region_manager TEXT
)
''')

conn.execute('''CREATE TABLE Transactions
(record_of_product_purchased INTEGER, 
including_order_number INTEGER, 
date TEXT, 
salesperson_name TEXT, 
product_ price TEXT, 
product_quantity INTEGER,
customer_information TEXT)
''')




conn.close()

