import sqlite3
from tkinter import *
from tkinter import messagebox, ttk

# Database setup
def setup_database():    
    conn=sqlite3.connect('management.db')
    cursor=conn.cursor()
    
    # Drop the transactions table if it exists
    cursor.execute('DROP TABLE IF EXISTS Products')
    cursor.execute('DROP TABLE IF EXISTS TransactionIn')
    cursor.execute('DROP TABLE IF EXISTS TransactionOut')
    
    # Create table if not exist
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Products(
                   PID integer Primary Key,
                   Company varchar(20),
                   Brand varchar(20),
                   Product_name varchar(20),
                   Unit_Price float,
                   Quantity integer,
                   CGST decimal(5,2),
                   SGST decimal(5,2),
                   CESS decimal(5,2)
                   )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS TransactionIn(
                   TransactionID integer Primary Key,
                   Company varchar(20),
                   CompanyGSTIN text,
                   Product_ID integer,
                   Contact int,
                   Brand varchar(20),  
                   Quantity integer,  
                   TransactionTime timestamp,  
                   FOREIGN KEY (Product_ID) REFERENCES Products (PID)
                   )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS TransactionOut(
                   Bill_Number INTEGER PRIMARY KEY AUTOINCREMENT,
                   Product_Id INTEGER,
                   Quantity INTEGER,
                   Total_Price REAL,
                   Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                   FOREIGN KEY (Product_Id) REFERENCES Products (PID)  -- Ensure correct column name
                   )
    ''')

    conn.commit()
    conn.close()

# Function to add stock
def add_stock(PID, Brand, Company, CompanyGSTIN, Contact, Product_name, Unit_Price, Quantity, CGST, SGST, CESS):
    conn=sqlite3.connect('management.db')
    cursor=conn.cursor()
    cursor.execute("INSERT into Products(PID, Company, Brand, Product_name, Unit_Price, Quantity, CGST, SGST, CESS) VALUES (?,?,?,?,?,?,?,?,?)",(PID, Company, Brand, Product_name, Unit_Price, Quantity, CGST, SGST, CESS))
    PID=cursor.lastrowid
    cursor.execute('INSERT INTO TransactionIn (Product_Id, Brand, Quantity) VALUES (?, ?, ?)', (PID, Brand, Quantity))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Stock added successfully!")

# Function to process sales
def sales(Product_Id, Quantity):
    conn=sqlite3.connect('management.db')
    cursor=conn.cursor()
    cursor.execute('SELECT Quantity, Price FROM Products WHERE PID=?', (Product_Id,))
    result=cursor.fetchone()
    if result and result[0]>= Quantity:
        total_price= result[1]*Quantity
        cursor.execute('UPDATE Products SET Quantity=Quantity - ? WHERE PID=?', (Quantity, Product_Id))
        cursor.execute('INSERT INTO TransactionOut (Product_Id, Quantity, Total_Price) VALUES (?, ?, ?)', (Product_Id, Quantity, total_price))
        conn.commit()
        messagebox.showinfo('Success', "Sale processed successfully!")
    else:
        messagebox.showerror('Error', "Insufficient stock!")
    conn.close()

# Main application window 
def main_window():
    root=Tk()
    root.title('Stock Management App')

    # Treeview to display products
    tree=ttk.Treeview(root, columns=('PID', 'Company', 'Brand', 'Product Name', 'Unit Price', 'Quantity', 'CGST', 'SGST', 'CESS'), show='headings')
    tree.heading('PID', text='PID')
    tree.heading('Company', text='Company')
    tree.heading('Brand', text='Brand')
    tree.heading('Product Name', text='Product Name')
    tree.heading('Unit Price', text='Unit Price')
    tree.heading('Quantity', text='Quantity')
    tree.heading('CGST', text='CGST')
    tree.heading('SGST', text='SGST')
    tree.heading('CESS', text='CESS')
    tree.pack()

    # Load products into treeview
    def load_products():
        for row in tree.get_children():
            tree.delete(row)
        conn=sqlite3.connect('management.db')
        cursor=conn.cursor()
        cursor.execute('SELECT * FROM Products')
        for row in cursor.fetchall():
            tree.insert('', 'end', values=row)
        conn.close()
    
    load_products()

    # Buttons for adding stock and processing sales 
    def open_add_stock_window():
        add_stock_window= Toplevel(root)
        add_stock_window.title('Add Stock')

        Label(add_stock_window, text="PID").grid(row=0, column=0)
        Label(add_stock_window, text="Company").grid(row=1, column=0)
        Label(add_stock_window, text="Brand").grid(row=2, column=0)
        Label(add_stock_window, text="Product Name").grid(row=3, column=0)
        Label(add_stock_window, text="Quantity").grid(row=4, column=0)
        Label(add_stock_window, text="Price").grid(row=5, column=0)
        Label(add_stock_window, text="CGST").grid(row=6, column=0)
        Label(add_stock_window, text="SGST").grid(row=7, column=0)
        Label(add_stock_window, text="CESS").grid(row=8, column=0)
        Label(add_stock_window, text="Contact").grid(row=9, column=0)
        Label(add_stock_window, text="Company GSTIN").grid(row=10, column=0)

        pid_entry = Entry(add_stock_window)
        company_entry = Entry(add_stock_window)
        brand_entry = Entry(add_stock_window)
        name_entry = Entry(add_stock_window)
        quantity_entry = Entry(add_stock_window)
        price_entry = Entry(add_stock_window)
        CGST_entry = Entry(add_stock_window)
        SGST_entry = Entry(add_stock_window)
        CESS_entry = Entry(add_stock_window)
        contact_entry = Entry(add_stock_window)
        gstin_entry = Entry(add_stock_window)

        pid_entry.grid(row=0, column=1)
        company_entry.grid(row=1, column=1)
        brand_entry.grid(row=2, column=1)
        name_entry.grid(row=3, column=1)
        quantity_entry.grid(row=4, column=1)
        price_entry.grid(row=5, column=1)
        CGST_entry.grid(row=6, column=1)
        SGST_entry.grid(row=7, column=1)
        CESS_entry.grid(row=8, column=1)
        contact_entry.grid(row=9, column=1)
        gstin_entry.grid(row=10, column=1)

        def add_stock_action():
            PID = int(pid_entry.get())
            Product_name = name_entry.get()
            Company = company_entry.get()
            Brand = brand_entry.get()
            Quantity = int(quantity_entry.get())
            Price = float(price_entry.get())
            CGST = float(CGST_entry.get())
            SGST = float(SGST_entry.get())
            CESS = float(CESS_entry.get())
            CompanyGSTIN = gstin_entry.get()
            Contact = int(contact_entry.get())
            add_stock(PID, Brand, Company, CompanyGSTIN, Contact, Product_name, Price, Quantity, CGST, SGST, CESS)
            load_products()
            add_stock_window.destroy()

        Button(add_stock_window, text="Add", command=add_stock_action).grid(row=11, columnspan=2)
    
    def open_process_sale_window():
        process_sale_window=Toplevel(root)
        process_sale_window.title("Billing")
        
        Label(process_sale_window, text="Product ID").grid(row=0, column=0)
        Label(process_sale_window, text="Quantity").grid(row=1, column=0)

        id_entry = Entry(process_sale_window)
        quantity_entry = Entry(process_sale_window)
        
        id_entry.grid(row=0, column=1)
        quantity_entry.grid(row=1, column=1)

        def process_sale_action():
            Product_id = id_entry.get()
            Quantity = int(quantity_entry.get())
            sales(Product_id, Quantity)
            load_products()
            process_sale_window.destroy()

        Button(process_sale_window, text='Process Sale', command=process_sale_action).grid(row=2, columnspan=2)
    
    Button(root, text="Add Stock", command=open_add_stock_window).pack()
    Button(root, text="Billing", command=open_process_sale_window).pack()

    root.mainloop()

# Run the application 
if __name__=="__main__":
    setup_database()
    main_window()
