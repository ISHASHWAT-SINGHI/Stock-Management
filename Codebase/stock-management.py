import sqlite3
import os
import time

# Current working directory 
curr_directory=os.path.dirname(__file__)
rel_path="Database/management.db"
database_path=os.path.join(curr_directory,rel_path)
conn=sqlite3.connect(database_path)
cursor=conn.cursor()
# Create table if not exist
cursor.execute('''
               CREATE TABLE IF NOT EXISTS Products(
               PID integer Primary Key,
               Company varchar(20)
               Brand varchar(20),
               Product_name varchar(20),
               Unit_Price float,
               Quantity integer,
               Created_At timestamp
               )
               ''')
conn.close()