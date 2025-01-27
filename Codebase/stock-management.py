import sqlite3
import os
import time

# Create a database if not exist 
conn=sqlite3.connect('management.db')
cursor=conn.cursor()
# Create table if not exist
cursor.execute('''
               CREATE TABLE IF NOT EXISTS Products(
               PID integer Primary Key,
               Company varchar(20),
               Brand varchar(20),
               Product_name varchar(20),
               Unit_Price float,
               Quantity integer,
               Created_At timestamp
               )
               ''')
cursor.execute('''
               CREATE TABLE IF NOT EXISTS TransactionIn(
               TransactionID integer Primary Key,
               Company varchar(20),
               CompanyGSTIN int,
               Contact int,
               PID integer,
               TransactionTime timestamp
               )
               ''')

# View Products
def view_products():

    # Retrieve and display all the products from the products table
    cursor.execute("SELECT PID, Company, Brand, Product_name, Unit_Price, Quantity, (Unit_Price*Quantity) AS Total_Price FROM Products")
    products=cursor.fetchall()
    print(products)

# View Transactions
def view_transactions():

    # Retrieve and display all the transactions from the transactionin table
    cursor.execute("SELECT TransactionID, Company, CompanyGSTIN, Contact, PID, TransactionTime FROM TransactionIn")
    transaction=cursor.fetchall()
    print(transaction)

# def add_product():
    # Add products through transactions 

# Main 
view_products()
view_transactions()
conn.close()