import sqlite3
from tkinter import *
from tkinter import messagebox, ttk

# Database setup
def setup_database():
    conn = sqlite3.connect('management.db')
    cursor = conn.cursor()

    # Check if tables exist before dropping them
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Products';")
    if cursor.fetchone() is not None:
        cursor.execute('DROP TABLE IF EXISTS Products')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='TransactionIn';")
    if cursor.fetchone() is not None:
        cursor.execute('DROP TABLE IF EXISTS TransactionIn')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='TransactionOut';")
    if cursor.fetchone() is not None:
        cursor.execute('DROP TABLE IF EXISTS TransactionOut')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Vendors';")
    if cursor.fetchone() is not None:
        cursor.execute('DROP TABLE IF EXISTS Vendors')
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Customers';")
    if cursor.fetchone() is not None:
        cursor.execute('DROP TABLE IF EXISTS Customers')

    
    # Create table if not exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS Products(
                   Product_name varchar(20) Primary Key,
                   Company varchar(20),
                   Brand varchar(20),
                   Unit_Price float,
                   Quantity integer,
                   CGST decimal(5,2),
                   SGST decimal(5,2),
                   CESS decimal(5,2)
                   )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS TransactionIn(
                   TransactionID integer Primary Key,
                   Company varchar(20),
                   CompanyGSTIN text,
                   Product_Name varchar(20),
                   Contact int,
                   Brand varchar(20),  
                   Quantity integer,  
                   TransactionTime timestamp,  
                   FOREIGN KEY (Product_Name) REFERENCES Products (Product_name)
                   )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS TransactionOut(
                   Bill_Number INTEGER PRIMARY KEY AUTOINCREMENT,
                   Product_Name varchar(20),
                   Quantity INTEGER,
                   Total_Price REAL,
                   Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                   FOREIGN KEY (Product_Name) REFERENCES Products (Product_name)
                   )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Vendors(
                   VendorID integer Primary Key,
                   Name varchar(50),
                   Contact varchar(15),
                   GSTIN varchar(15)
                   )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Customers(
                   CustomerID integer Primary Key,
                   Name varchar(50),
                   Contact varchar(15),
                   GSTIN varchar(15),
                   Address varchar(100)
                   )''')

    conn.commit()
    conn.close()

# Function to add stock
def add_stock(Product_name, Brand, Company, CompanyGSTIN, Contact, Unit_Price, Quantity, CGST, SGST, CESS):
    conn=sqlite3.connect('management.db')
    cursor=conn.cursor()
    try:
        cursor.execute("INSERT into Products(Product_name, Company, Brand, Unit_Price, Quantity, CGST, SGST, CESS) VALUES (?,?,?,?,?,?,?,?)",(Product_name, Company, Brand, Unit_Price, Quantity, CGST, SGST, CESS))

        cursor.execute('INSERT INTO TransactionIn (Product_Name, Brand, Quantity) VALUES (?, ?, ?)', (Product_name, Brand, Quantity))
        conn.commit()
        messagebox.showinfo("Success", "Stock added successfully!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Product already exists!")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        conn.close()


# Function to process sales
def sales(Product_Name, Quantity):
    conn=sqlite3.connect('management.db')
    cursor=conn.cursor()
    try:
        cursor.execute('SELECT Quantity, Unit_Price FROM Products WHERE Product_name=?', (Product_Name,))

        result = cursor.fetchone()
        if result and result[0] >= Quantity:
            total_price = result[1] * Quantity
            cursor.execute('UPDATE Products SET Quantity=Quantity - ? WHERE Product_name=?', (Quantity, Product_Name))
            cursor.execute('INSERT INTO TransactionOut (Product_Name, Quantity, Total_Price) VALUES (?, ?, ?)', (Product_Name, Quantity, total_price))
            conn.commit()
            messagebox.showinfo('Success', "Sale processed successfully!")
        else:
            messagebox.showerror('Error', "Insufficient stock!")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        conn.close()


# Function to add a vendor
def add_vendor(VendorID, Name, Contact, GSTIN):
    conn = sqlite3.connect('management.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Vendors (VendorID, Name, Contact, GSTIN) VALUES (?, ?, ?, ?)", (VendorID, Name, Contact, GSTIN))
        conn.commit()
        messagebox.showinfo("Success", "Vendor added successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        conn.close()


# Function to add a customer
def add_customer(CustomerID, Name, Contact, GSTIN, Address):
    conn = sqlite3.connect('management.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Customers (CustomerID, Name, Contact, GSTIN, Address) VALUES (?, ?, ?, ?, ?)", (CustomerID, Name, Contact, GSTIN, Address))
        conn.commit()
        messagebox.showinfo("Success", "Customer added successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        conn.close()

# Main application window 
def main_window():
    root=Tk()
    root.title('Stock Management App')

    # Treeview to display products
    tree=ttk.Treeview(root, columns=('Product Name', 'Company', 'Brand', 'Unit Price', 'Quantity', 'CGST', 'SGST', 'CESS'), show='headings')
    tree.heading('Product Name', text='Product Name')
    tree.heading('Company', text='Company')
    tree.heading('Brand', text='Brand')
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
    button_frame = Frame(root)
    button_frame.pack(pady=10)

    def open_add_stock_window():
        add_stock_window= Toplevel(root)
        add_stock_window.title('Add Stock')

        Label(add_stock_window, text="Product Name").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        Label(add_stock_window, text="Company").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        Label(add_stock_window, text="Brand").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        Label(add_stock_window, text="Quantity").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        Label(add_stock_window, text="Price").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        Label(add_stock_window, text="Select GST Slab").grid(row=5, column=0, padx=5, pady=5, sticky='w')

        gst_slab_combobox = ttk.Combobox(add_stock_window, values=["5%", "12%", "18%", "28%"], width=10)
        gst_slab_combobox.grid(row=5, column=1, padx=5, pady=5)

        gst_slab_combobox.current(0)  # Set default value to the first slab
        Label(add_stock_window, text="CGST").grid(row=7, column=0, padx=5, pady=5, sticky='w')
        Label(add_stock_window, text="SGST").grid(row=8, column=0, padx=5, pady=5, sticky='w')

        Label(add_stock_window, text="CESS").grid(row=9, column=0, padx=5, pady=5, sticky='w')
        Label(add_stock_window, text="Contact").grid(row=10, column=0, padx=5, pady=5, sticky='w')
        Label(add_stock_window, text="Company GSTIN").grid(row=11, column=0, padx=5, pady=5, sticky='w')

        product_name_entry = Entry(add_stock_window)
        company_entry = Entry(add_stock_window)
        brand_entry = Entry(add_stock_window)
        quantity_entry = Entry(add_stock_window)
        price_entry = Entry(add_stock_window)
        CGST_entry = Entry(add_stock_window)
        SGST_entry = Entry(add_stock_window)
        CESS_entry = Entry(add_stock_window)
        contact_entry = Entry(add_stock_window)
        gstin_entry = Entry(add_stock_window)

        product_name_entry.grid(row=0, column=1, padx=5, pady=5)
        company_entry.grid(row=1, column=1, padx=5, pady=5)
        brand_entry.grid(row=2, column=1, padx=5, pady=5)
        quantity_entry.grid(row=3, column=1, padx=5, pady=5)
        price_entry.grid(row=4, column=1, padx=5, pady=5)
        CGST_entry.grid(row=7, column=1, padx=5, pady=5)
        SGST_entry.grid(row=8, column=1, padx=5, pady=5)
        CESS_entry.grid(row=9, column=1, padx=5, pady=5)
        contact_entry.grid(row=10, column=1, padx=5, pady=5)
        gstin_entry.grid(row=11, column=1, padx=5, pady=5)

        def add_stock_action():
            Product_name = product_name_entry.get()
            Company = company_entry.get()
            Brand = brand_entry.get()
            Quantity = int(quantity_entry.get())
            Price = float(price_entry.get())
            selected_slab = gst_slab_combobox.get()
            slab_value = float(selected_slab[:-1]) if '%' in selected_slab else float(selected_slab)  # Convert to float
            CGST = slab_value / 100 / 2  # Calculate CGST as half of the slab percentage
            SGST = slab_value / 100 / 2  # Calculate SGST as half of the slab percentage

            # Update the entry fields to show calculated values
            CGST_entry.delete(0, END)  # Clear the CGST entry field
            slab_value = float(selected_slab[:-1]) if '%' in selected_slab else float(selected_slab)  # Convert to float
            CGST = (slab_value / 2)  # Calculate CGST
            SGST = (slab_value / 2)  # Calculate SGST
            CGST_entry.insert(0, f"{CGST:.2f}")  # Set the CGST entry field with the calculated value
            SGST_entry.delete(0, END)  # Clear the SGST entry field
            SGST_entry.insert(0, f"{SGST:.2f}")  # Set the SGST entry field with the calculated value

            CESS = float(CESS_entry.get()) if CESS_entry.get() else 0.0

            CompanyGSTIN = gstin_entry.get()
            Contact = int(contact_entry.get())
            add_stock(Product_name, Brand, Company, CompanyGSTIN, Contact, Price, Quantity, CGST, SGST, CESS)
            load_products()
            add_stock_window.destroy()

        Button(add_stock_window, text="Add", command=add_stock_action).grid(row=12, columnspan=2)
    
    def open_process_sale_window():
        process_sale_window=Toplevel(root)
        process_sale_window.title("Billing")
        
        Label(process_sale_window, text="Product Name").grid(row=0, column=0)
        Label(process_sale_window, text="Quantity").grid(row=1, column=0)

        product_name_entry = Entry(process_sale_window)
        quantity_entry = Entry(process_sale_window)
        
        product_name_entry.grid(row=0, column=1)
        quantity_entry.grid(row=1, column=1)

        def process_sale_action():
            Product_Name = product_name_entry.get()
            Quantity = int(quantity_entry.get())
            sales(Product_Name, Quantity)
            load_products()
            process_sale_window.destroy()

        Button(process_sale_window, text='Process Sale', command=process_sale_action).grid(row=2, columnspan=2)

    def open_add_vendor_window():
        add_vendor_window = Toplevel(root)
        add_vendor_window.title("Add Vendor")

        Label(add_vendor_window, text="Vendor ID").grid(row=0, column=0)
        Label(add_vendor_window, text="Name").grid(row=1, column=0)
        Label(add_vendor_window, text="Contact").grid(row=2, column=0)
        Label(add_vendor_window, text="GSTIN").grid(row=3, column=0)

        vendor_id_entry = Entry(add_vendor_window)
        name_entry = Entry(add_vendor_window)
        contact_entry = Entry(add_vendor_window)
        gstin_entry = Entry(add_vendor_window)

        vendor_id_entry.grid(row=0, column=1)
        name_entry.grid(row=1, column=1)
        contact_entry.grid(row=2, column=1)
        gstin_entry.grid(row=3, column=1)

        def add_vendor_action():
            VendorID = int(vendor_id_entry.get())
            Name = name_entry.get()
            Contact = contact_entry.get()
            GSTIN = gstin_entry.get()
            add_vendor(VendorID, Name, Contact, GSTIN)
            add_vendor_window.destroy()

        Button(add_vendor_window, text="Add Vendor", command=add_vendor_action).grid(row=4, columnspan=2)

    def open_add_customer_window():
        add_customer_window = Toplevel(root)
        add_customer_window.title("Add Customer")

        Label(add_customer_window, text="Customer ID").grid(row=0, column=0)
        Label(add_customer_window, text="Name").grid(row=1, column=0)
        Label(add_customer_window, text="Contact").grid(row=2, column=0)
        Label(add_customer_window, text="GSTIN").grid(row=3, column=0)
        Label(add_customer_window, text="Address").grid(row=4, column=0)

        customer_id_entry = Entry(add_customer_window)
        name_entry = Entry(add_customer_window)
        contact_entry = Entry(add_customer_window)
        gstin_entry = Entry(add_customer_window)
        address_entry = Entry(add_customer_window)

        customer_id_entry.grid(row=0, column=1)
        name_entry.grid(row=1, column=1)
        contact_entry.grid(row=2, column=1)
        gstin_entry.grid(row=3, column=1)
        address_entry.grid(row=4, column=1)

        def add_customer_action():
            CustomerID = int(customer_id_entry.get())
            Name = name_entry.get()
            Contact = contact_entry.get()
            GSTIN = gstin_entry.get()
            Address = address_entry.get()
            add_customer(CustomerID, Name, Contact, GSTIN, Address)
            add_customer_window.destroy()

        Button(add_customer_window, text="Add Customer", command=add_customer_action).grid(row=5, columnspan=2)

    # Arrange buttons in an ordered manner
    button_frame = Frame(root)
    button_frame.pack(pady=10)

    Button(button_frame, text="Add Stock", command=open_add_stock_window).grid(row=0, column=0, padx=5)
    Button(button_frame, text="Billing", command=open_process_sale_window).grid(row=0, column=1, padx=5)
    Button(button_frame, text="Add Vendor", command=open_add_vendor_window).grid(row=0, column=2, padx=5)
    Button(button_frame, text="Add Customer", command=open_add_customer_window).grid(row=0, column=3, padx=5)

    root.mainloop()

# Run the application 
if __name__=="__main__":
    setup_database()
    main_window()
