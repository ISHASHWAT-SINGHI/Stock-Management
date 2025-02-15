import sqlite3
from tkinter import *
from tkinter import messagebox, ttk

class StockManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Stock Management App')

        # Main container
        self.main_container = Frame(self.root)
        self.main_container.pack(fill=BOTH, expand=True)

        # Content Frame
        self.content_frame = Frame(self.main_container)
        self.content_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        # Hamburger Menu Frame
        self.menu_frame = Frame(self.main_container, width=200, bg='lightgray')
        
        # Hamburger Button
        self.hamburger_button = Button(self.main_container, text="☰", command=self.toggle_menu)
        self.hamburger_button.pack(side=LEFT, anchor=NW)

        # Menu Items
        self.add_vendor_button = Button(self.menu_frame, text="Add Vendor", command=self.open_add_vendor_window)
        self.add_vendor_button.pack(fill=X)

        self.add_customer_button = Button(self.menu_frame, text="Add Customer", command=self.open_add_customer_window)
        self.add_customer_button.pack(fill=X)

        # Initially hide the menu
        self.menu_visible = True
        self.menu_frame.pack_forget()

        # Initialize form visibility states
        self.vendor_form_visible = False
        self.customer_form_visible = False

    def toggle_menu(self):
        if self.menu_visible:
            self.menu_frame.pack_forget()
        else:
            self.menu_frame.pack(side=LEFT, fill=Y)
        self.menu_visible = not self.menu_visible

    def open_add_vendor_window(self):
        # Toggle visibility
        if self.vendor_form_visible:
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            self.vendor_form_visible = False
            return

        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Create form in content frame
        self.vendor_form_visible = True
        
        Label(self.content_frame, text="Vendor ID").pack()
        vendor_id_entry = Entry(self.content_frame)
        vendor_id_entry.pack()

        Label(self.content_frame, text="Name").pack()
        name_entry = Entry(self.content_frame)
        name_entry.pack()

        Label(self.content_frame, text="Contact").pack()
        contact_entry = Entry(self.content_frame)
        contact_entry.pack()

        Label(self.content_frame, text="GSTIN").pack()
        gstin_entry = Entry(self.content_frame)
        gstin_entry.pack()

        def add_vendor_action():
            VendorID = int(vendor_id_entry.get())
            Name = name_entry.get()
            Contact = contact_entry.get()
            GSTIN = gstin_entry.get()
            add_vendor(VendorID, Name, Contact, GSTIN)
            # Clear entries after adding
            vendor_id_entry.delete(0, END)
            name_entry.delete(0, END)
            contact_entry.delete(0, END)
            gstin_entry.delete(0, END)

        Button(self.content_frame, text="Add Vendor", command=add_vendor_action).pack()

    def open_add_customer_window(self):
        # Toggle visibility
        if self.customer_form_visible:
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            self.customer_form_visible = False
            return

        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Create form in content frame
        self.customer_form_visible = True
        
        Label(self.content_frame, text="Customer ID").pack()
        customer_id_entry = Entry(self.content_frame)
        customer_id_entry.pack()

        Label(self.content_frame, text="Name").pack()
        name_entry = Entry(self.content_frame)
        name_entry.pack()

        Label(self.content_frame, text="Contact").pack()
        contact_entry = Entry(self.content_frame)
        contact_entry.pack()

        Label(self.content_frame, text="GSTIN").pack()
        gstin_entry = Entry(self.content_frame)
        gstin_entry.pack()

        Label(self.content_frame, text="Address").pack()
        address_entry = Entry(self.content_frame)
        address_entry.pack()

        def add_customer_action():
            CustomerID = int(customer_id_entry.get())
            Name = name_entry.get()
            Contact = contact_entry.get()
            GSTIN = gstin_entry.get()
            Address = address_entry.get()
            add_customer(CustomerID, Name, Contact, GSTIN, Address)
            # Clear entries after adding
            customer_id_entry.delete(0, END)
            name_entry.delete(0, END)
            contact_entry.delete(0, END)
            gstin_entry.delete(0, END)
            address_entry.delete(0, END)

        Button(self.content_frame, text="Add Customer", command=add_customer_action).pack()

# [Rest of the file remains unchanged...]
# Database setup
def setup_database():
    conn = sqlite3.connect('management.db')
    cursor = conn.cursor()

    # Check if tables exist before dropping them
    # cursor.execute('DROP TABLE IF EXISTS Products')
    # cursor.execute('DROP TABLE IF EXISTS TransactionIn')
    # cursor.execute('DROP TABLE IF EXISTS TransactionOut')
    # cursor.execute('DROP TABLE IF EXISTS Vendors')
    # cursor.execute('DROP TABLE IF EXISTS Customers')

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
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS GSTSlabs(
                   SlabID integer Primary Key AUTOINCREMENT,
                   SlabPercentage decimal(5,2)
                   )''')  # Create GSTSlabs table

    conn.commit()
    conn.close()

# Function to add a new GST slab
def add_gst_slab(slab_percentage):
    conn = sqlite3.connect('management.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO GSTSlabs (SlabPercentage) VALUES (?)", (slab_percentage,))

    conn.commit()
    conn.close()

# Function to fetch GST slabs
def fetch_gst_slabs():
    conn = sqlite3.connect('management.db')
    cursor = conn.cursor()
    cursor.execute('SELECT SlabPercentage FROM GSTSlabs ORDER BY SlabPercentage ASC')

    gst_slabs = [row[0] for row in cursor.fetchall()]
    conn.close()
    return gst_slabs


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
    root = Tk()
    root.title('Stock Management App')
    
    # Create the main app instance
    app = StockManagementApp(root)
    
    # Buttons for adding stock and processing sales 
    button_frame = Frame(root)
    button_frame.pack(pady=10)

    # Function to open the manage gst slabs section 
    def open_manage_gst_slabs_window():

        manage_gst_slabs_window = Toplevel(root)
        manage_gst_slabs_window.title("Manage GST Slabs")

        # Function to add new gst slabs 
        Label(manage_gst_slabs_window, text="Add GST Slab").grid(row=0, column=0)
        gst_slab_entry = Entry(manage_gst_slabs_window)
        gst_slab_entry.grid(row=0, column= 1)

        def add_gst_slab_action():
            slab_percentage = float(gst_slab_entry.get()) if gst_slab_entry.get() else 0
            add_gst_slab(slab_percentage)
            messagebox.showinfo("Success", "GST slab added successfully!")

            manage_gst_slabs_window.destroy()
        
        Button(manage_gst_slabs_window, text="Add Slab", command=add_gst_slab_action).grid(row=0, column=4)

        # Function to view gst slabs 
        gst_slabs = fetch_gst_slabs()
        Label(manage_gst_slabs_window, text="GST Slabs").grid(row=2, column=0, columnspan=2)

        # Create a treeview to display GST slabs
        tree = ttk.Treeview(manage_gst_slabs_window, columns=('SlabPercentage'), show='headings')

        tree.heading('SlabPercentage', text='Slab Percentage')

        tree.grid(row=3, column=0, columnspan=2, sticky='nsew')

        for slab in gst_slabs:
            tree.insert('', 'end', values=(slab,))

        # Function to delete selected GST slab
        def delete_selected_slab():
            selected_item = tree.selection()
            if selected_item:
                slab_percentage = tree.item(selected_item, 'values')[0]
                conn = sqlite3.connect('management.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM GSTSlabs WHERE SlabPercentage=?", (slab_percentage,))
                conn.commit()
                conn.close()
                tree.delete(selected_item)  # Remove from treeview
                messagebox.showinfo("Success", "GST slab deleted successfully!")
        
        Button(manage_gst_slabs_window, text="Delete Slab", command=delete_selected_slab).grid(row=4, column=0, columnspan=2)

        manage_gst_slabs_window.mainloop() 

    Button(button_frame, text="Manage GST Slabs", command=open_manage_gst_slabs_window).grid(row=0, column=5, padx=5)
    
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

    def open_add_stock_window():
        add_stock_window= Toplevel(root)
        add_stock_window.title('Add Stock')

        Label(add_stock_window, text="Product Name").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        Label(add_stock_window, text="Company").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        Label(add_stock_window, text="Brand").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        Label(add_stock_window, text="Quantity").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        Label(add_stock_window, text="Price").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        Label(add_stock_window, text="Select GST Slab").grid(row=5, column=0, padx=5, pady=5, sticky='w')

        gst_slabs = fetch_gst_slabs()
        gst_slab_combobox = ttk.Combobox(add_stock_window, values=gst_slabs, width=10)
        gst_slab_combobox.grid(row=5, column=1, padx=5, pady=5)

        if gst_slabs:
            gst_slab_combobox.current(int(0))  # Set default value to the first slab

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
            slab_value = float(selected_slab[:-1]) if '%' in selected_slab and selected_slab else 0  # Convert to float

            CGST = slab_value / 100 / 2  # Calculate CGST as half of the slab percentage
            SGST = slab_value / 100 / 2  # Calculate SGST as half of the slab percentage

            # Update the entry fields to show calculated values
            CGST_entry.delete(0, END)  # Clear the CGST entry field
            # slab_value = float(selected_slab[:-1]) if '%' in selected_slab else float(selected_slab)  # Convert to float
            # CGST = (slab_value / 2)  # Calculate CGST
            # SGST = (slab_value / 2)  # Calculate SGST
            # CGST_entry.delete(0,END)
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

    # Arrange buttons in an ordered manner
    button_frame = Frame(root)
    button_frame.pack(pady=10)

    Button(button_frame, text="Add Stock", command=open_add_stock_window).grid(row=0, column=0, padx=5)
    Button(button_frame, text="Billing", command=open_process_sale_window).grid(row=0, column=1, padx=5)
    # Button(button_frame, text="Add Vendor", command=open_add_vendor_window).grid(row=0, column=2, padx=5)
    # Button(button_frame, text="Add Customer", command=open_add_customer_window).grid(row=0, column=3, padx=5)
    root.mainloop()

# Run the application 
if __name__ == "__main__":
    setup_database()
    main_window()
