import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import mysql.connector
from mysql.connector import Error
import os
import keyring
import time

def get_db_credentials():
    """ Get database credentials from keyring or prompt user """
    credentials = {
        'host': keyring.get_password('stock_management', 'host'),
        'user': keyring.get_password('stock_management', 'user'),
        'password': keyring.get_password('stock_management', 'password'),
        'database': keyring.get_password('stock_management', 'database')
    }
    
    # If credentials are not stored, use defaults
    if not all(credentials.values()):
        credentials = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'database': 'stock_management'
        }
    
    # If any credentials are missing, show input dialog
    if not all(credentials.values()):
        cred_window = tk.Toplevel()
        cred_window.title("Database Credentials")
        
        ttk.Label(cred_window, text="Host:").grid(row=0, column=0, padx=5, pady=5)
        host_entry = ttk.Entry(cred_window)
        host_entry.grid(row=0, column=1, padx=5, pady=5)
        host_entry.insert(0, credentials['host'])
        
        ttk.Label(cred_window, text="User:").grid(row=1, column=0, padx=5, pady=5)
        user_entry = ttk.Entry(cred_window)
        user_entry.grid(row=1, column=1, padx=5, pady=5)
        user_entry.insert(0, credentials['user'])
        
        ttk.Label(cred_window, text="Password:").grid(row=2, column=0, padx=5, pady=5)
        password_entry = ttk.Entry(cred_window, show="*")
        password_entry.grid(row=2, column=1, padx=5, pady=5)
        password_entry.insert(0, credentials['password'])
        
        ttk.Label(cred_window, text="Database:").grid(row=3, column=0, padx=5, pady=5)
        db_entry = ttk.Entry(cred_window)
        db_entry.grid(row=3, column=1, padx=5, pady=5)
        db_entry.insert(0, credentials['database'])
        
        def save_credentials():
            credentials['host'] = host_entry.get()
            credentials['user'] = user_entry.get()
            credentials['password'] = password_entry.get()
            credentials['database'] = db_entry.get()
            cred_window.destroy()
            
        ttk.Button(cred_window, text="Save", command=save_credentials).grid(row=4, column=0, columnspan=2, pady=10)
        
        cred_window.grab_set()
        cred_window.wait_window()
        
    return credentials


def create_connection():
    """ Create a database connection to the MySQL database """
    connection = None
    credentials = get_db_credentials()
    
    if not all(credentials.values()):
        messagebox.showwarning("Input Error", "All database credentials are required")
        return None
        
    try:
        connection = mysql.connector.connect(
            host=credentials['host'],
            user=credentials['user'],
            password=credentials['password'],
            database=credentials['database'],
            autocommit=False
        )
        
        # Store credentials in keyring on successful connection
        if connection.is_connected():
            keyring.set_password('stock_management', 'host', credentials['host'])
            keyring.set_password('stock_management', 'user', credentials['user'])
            keyring.set_password('stock_management', 'password', credentials['password'])
            keyring.set_password('stock_management', 'database', credentials['database'])
            
        return connection
    except Error as e:
        messagebox.showerror("Connection Error", f"The error '{e}' occurred")
        return None

def view_bills():
    """ View and print previous bills """
    bills_window = tk.Toplevel()
    bills_window.title("Previous Bills")
    
    def print_bill():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a bill to print")
            return
            
        # Get bill details
        bill_values = tree.item(selected[0], 'values')
        
        # Format bill text with explicit Unicode symbols
        bill_text = f"Pradayini Enterprise\n"
        bill_text += f"Transaction ID: {bill_values[0]}\n"
        bill_text += f"Customer: {bill_values[1]}\n"
        bill_text += f"Phone: {bill_values[2]}\n"
        bill_text += f"Address: {bill_values[3]}\n\n"
        bill_text += f"Subtotal: \u20B9{bill_values[4]}\n"
        bill_text += f"GST: \u20B9{bill_values[5]}\n"
        bill_text += f"Grand Total: \u20B9{bill_values[6]}\n"
        bill_text += f"Date: {bill_values[7]}\n"
        bill_text += f"\nBrands Purchased:\n"
        
        # Fetch product information for this bill
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("""
                    SELECT p.Product_name, p.Brand, bi.quantity, p.Unit_Price 
                    FROM bill_items bi
                    JOIN products p ON bi.product_id = p.ID
                    WHERE bi.transaction_id = %s
                """, (bill_values[0],))
                products = cursor.fetchall()
                
                if not products:
                    bill_text += "\nNo product details found for this bill.\n"
                else:
                    # Add product details
                    bill_text += "\nProducts Purchased:\n"
                    for product in products:
                        bill_text += f"- {product[0]} ({product[1]}) x {product[2]} @ ₹{product[3]:.2f}\n"
                    
                    # Add brand summary
                    unique_brands = set(product[1] for product in products)
                    bill_text += "\nBrands Purchased:\n"
                    for brand in unique_brands:
                        bill_text += f"- {brand}\n"
            except Error as e:
                bill_text += f"\nError fetching product details: {str(e)}\n"
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        bill_text += f"\nThank you for your business!"
        
        # Print the bill
        import os
        
        # Create a PDF file in the Documents folder
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        # Create a PDF file path in a Bills folder on Desktop
        from pathlib import Path
        bills_folder = Path.home() / "Desktop" / "Bills"
        bills_folder.mkdir(exist_ok=True)  # Create folder if it doesn't exist
        pdf_path = str(bills_folder / f"bill_{bill_values[0]}.pdf")
        
        # Create PDF with embedded DejaVuSans font
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import os
        font_path = os.path.join(os.path.dirname(__file__), 'DejaVuSans.ttf')
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
        
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter
        
        # Set font and starting position with Unicode support
        c.setFont("DejaVuSans", 14)
        # Add company logo or header
        c.drawString(50, height - 50, "Pradayini Enterprise")
        c.setFont("DejaVuSans", 12)
        x = 50
        y = height - 80  # Start below the header
        line_height = 15
        margin = 50
        
        # Add text to PDF with proper spacing and UTF-8 encoding
        for line in bill_text.split('\n'):
            # Ensure text is properly encoded as UTF-8
            encoded_line = line.encode('utf-8').decode('utf-8')
            c.drawString(x, y, encoded_line)
            y -= line_height
            if y < margin:  # Create new page if we reach the bottom
                c.showPage()
                y = height - margin
                c.setFont("DejaVuSans", 12)
        
        c.save()
        temp_path = pdf_path
        
        # Try to print the PDF with error handling
        try:
            if os.name == 'nt':  # Windows
                os.startfile(temp_path, 'print')
            elif os.name == 'posix':  # macOS/Linux
                os.startfile(temp_path)
            
            # Wait a moment for the print dialog to appear
            time.sleep(2)
            
            # Clean up after printing
            os.unlink(temp_path)
            
        except OSError as e:
            # If printing fails, save the PDF with transaction ID as name in Bills folder
            save_path = str(bills_folder / f"bill_{bill_values[0]}.pdf")
            if os.path.exists(save_path):
                # If file already exists, add timestamp to make it unique
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                save_path = str(bills_folder / f"bill_{bill_values[0]}_{timestamp}.pdf")
            os.rename(temp_path, save_path)
            messagebox.showinfo("Print Failed", 
                f"Could not print directly. The bill has been saved to:\n{save_path}\n\n"
                f"Please print it manually. Error: {str(e)}")
    
    # Create treeview to display bills
    columns = ("Transaction ID", "Customer Name", "Phone", "Address", "Total", "GST", "Grand Total", "Date")
    tree = ttk.Treeview(bills_window, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.grid(row=0, column=0, padx=5, pady=5)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(bills_window, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky='ns')
    

    def view_transaction():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a transaction to view")
            return
            
        # Get transaction details
        transaction_id = tree.item(selected[0], 'values')[0]
        
        # Create view window
        view_window = tk.Toplevel()
        view_window.title(f"Transaction Details - {transaction_id}")
        
        # Create text widget to display bill
        bill_text = tk.Text(view_window, wrap=tk.WORD, height=30, width=60)
        bill_text.grid(row=0, column=0, padx=10, pady=10)
        
        # Fetch and display transaction details
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                
                # Get main transaction details
                cursor.execute("""
                    SELECT customer_name, customer_phone, customer_address, 
                           total_amount, gst_amount, grand_total, created_at 
                    FROM bills 
                    WHERE transaction_id = %s
                """, (transaction_id,))
                bill_details = cursor.fetchone()
                
                if bill_details:
                    # Format bill text
                    bill_text.insert(tk.END, f"Pradayini Enterprise\n")
                    bill_text.insert(tk.END, f"Transaction ID: {transaction_id}\n")
                    bill_text.insert(tk.END, f"Customer: {bill_details[0]}\n")
                    bill_text.insert(tk.END, f"Phone: {bill_details[1]}\n")
                    bill_text.insert(tk.END, f"Address: {bill_details[2]}\n\n")
                    bill_text.insert(tk.END, "Products:\n")
                    
                    # Get product details
                    cursor.execute("""
                        SELECT p.Product_name, p.Brand, bi.quantity, p.Unit_Price 
                        FROM bill_items bi
                        JOIN products p ON bi.product_id = p.ID
                        WHERE bi.transaction_id = %s
                    """, (transaction_id,))
                    products = cursor.fetchall()
                    
                    for product in products:
                        bill_text.insert(tk.END, 
                            f"- {product[0]} ({product[1]}) x {product[2]} @ ₹{product[3]:.2f}\n")
                    
                    bill_text.insert(tk.END, f"\nSubtotal: ₹{bill_details[3]:.2f}\n")
                    bill_text.insert(tk.END, f"GST (18%): ₹{bill_details[4]:.2f}\n")
                    bill_text.insert(tk.END, f"Grand Total: ₹{bill_details[5]:.2f}\n")
                    bill_text.insert(tk.END, f"\nDate: {bill_details[6]}\n")
                    bill_text.insert(tk.END, f"\nThank you for your business!")
                    
                    # Make text read-only
                    bill_text.config(state=tk.DISABLED)
                    
            except Error as e:
                messagebox.showerror("Database Error", f"Error fetching transaction details: {e}")
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    # Add buttons
    button_frame = ttk.Frame(bills_window)
    button_frame.grid(row=1, column=0, columnspan=2, pady=10)
    
    ttk.Button(button_frame, text="Print Selected Bill", command=print_bill).grid(row=0, column=0, padx=5)
    ttk.Button(button_frame, text="View Details", command=view_transaction).grid(row=0, column=1, padx=5)

    
    # Fetch and display bills
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT b.transaction_id, b.customer_name, b.customer_phone, b.customer_address, 
                   b.total_amount, b.gst_amount, b.grand_total, b.created_at 
            FROM bills b
            ORDER BY b.Created_At DESC
        """)
        bills = cursor.fetchall()
        for bill in bills:
            tree.insert("", tk.END, values=bill)
        connection.close()

def generate_bill():
    """ Generate a bill with GST calculation """
    bill_window = tk.Toplevel()
    bill_window.title("Billing")
    
    # Customer Details
    def load_customers():
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT DISTINCT customer_name, customer_phone, customer_address FROM bills ORDER BY customer_name")
                customers = cursor.fetchall()
                # Return customers with name and address combined for display
                return [f"{customer[0]} - {customer[2]}" for customer in customers]
            except Error as e:
                messagebox.showerror("Database Error", f"Error loading customers: {e}")
                return []
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        return []

    def on_customer_select(event):
        selected = customer_select.get()
        if selected:
            # Extract just the customer name from the selected value
            customer_name = selected.split(' - ')[0]
            
            # Fetch customer details from database using the extracted name
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("SELECT customer_phone, customer_address FROM bills WHERE customer_name = %s LIMIT 1", (customer_name,))
                result = cursor.fetchone()
                connection.close()
                
                if result:
                    customer_phone.delete(0, tk.END)
                    customer_address.delete(0, tk.END)
                    customer_phone.insert(0, result[0])
                    customer_address.insert(0, result[1])
                    # Set just the name in the customer name field
                    customer_select.set(customer_name)

    
    # Create customer details frame
    customer_frame = ttk.LabelFrame(bill_window, text="Customer Details", padding=10)
    customer_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
    
    # Customer Select Combobox
    ttk.Label(customer_frame, text="Customer Name*:").grid(row=0, column=0, padx=5, pady=5)
    customer_select = ttk.Combobox(customer_frame, state="normal", width=30)
    customer_select.grid(row=0, column=1, padx=5, pady=5)
    customer_select.bind("<<ComboboxSelected>>", on_customer_select)
    customer_select.bind("<KeyRelease>", lambda e: [customer_phone.delete(0, tk.END), customer_address.delete(0, tk.END)])
    # Populate customers when window opens
    customer_select['values'] = load_customers()
    
    # Refresh customer list button
    ttk.Button(
        customer_frame, 
        text="Refresh List", 
        command=lambda: customer_select.configure(values=load_customers())
    ).grid(row=0, column=2, padx=5)
    
    # Customer Phone
    ttk.Label(customer_frame, text="Customer Phone:").grid(row=2, column=0, padx=5, pady=5)
    customer_phone = ttk.Entry(customer_frame)
    customer_phone.grid(row=2, column=1, padx=5, pady=5)
    
    # Customer Address
    ttk.Label(customer_frame, text="Customer Address*:").grid(row=3, column=0, padx=5, pady=5)
    customer_address = ttk.Entry(customer_frame)
    customer_address.grid(row=3, column=1, padx=5, pady=5)
    
    # Show All Customers button
    ttk.Button(
        customer_frame,
        text="Show All Customers",
        command=lambda: show_all_customers()
    ).grid(row=1, column=2, padx=5, pady=5)

    # Proceed button
    ttk.Button(
        customer_frame, 
        text="Proceed →", 
        command=lambda: validate_and_proceed(),
        style='Accent.TButton'
    ).grid(row=3, column=2, padx=5, pady=5)

    def show_all_customers():
        """ Show all customer details in a new window """
        customers_window = tk.Toplevel()
        customers_window.title("All Customers")
        
        # Create treeview to display customers
        columns = ("Name", "Phone", "Address")
        tree = ttk.Treeview(customers_window, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
        tree.grid(row=0, column=0, padx=5, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(customers_window, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Fetch and display customers
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT DISTINCT customer_name, customer_phone, customer_address FROM bills")
            customers = cursor.fetchall()
            for customer in customers:
                tree.insert("", tk.END, values=customer)
            connection.close()
    
    def validate_and_proceed():
        if not customer_select.get().strip():
            messagebox.showwarning("Input Error", "Customer name is required")
            return
        if not customer_address.get().strip():
            messagebox.showwarning("Input Error", "Customer address is required")
            return
        customer_frame.grid_forget()
        product_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
    
    # Configure styles for better visibility
    style = ttk.Style()
    style.configure('Accent.TButton', font=('Arial', 10, 'bold'), padding=5)
    
    # Product Selection Frame
    product_frame = ttk.Frame(bill_window)
    product_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
    
    # Create filter frame
    filter_frame = ttk.Frame(product_frame)
    filter_frame.grid(row=0, column=0, columnspan=2, sticky='e', pady=(0, 10))
    
    # Brand filter
    ttk.Label(filter_frame, text="Filter by Brand:", font=('Arial', 9, 'bold')).grid(row=0, column=0, padx=(0, 5))
    brand_filter = ttk.Combobox(filter_frame, state="readonly", width=20)
    brand_filter.grid(row=0, column=1, padx=(0, 5))
    
    # Clear filter button
    clear_filter_btn = ttk.Button(filter_frame, text="Clear Filter", 
                                command=lambda: [brand_filter.set(''), populate_products()])
    clear_filter_btn.grid(row=0, column=2)
    
    # Create treeview for products with quantity selection
    columns = ("Product", "Price", "Quantity")
    product_tree = ttk.Treeview(product_frame, columns=columns, show="headings", height=5)
    product_tree.grid(row=1, column=0, columnspan=2, sticky='nsew')
    
    # Add sorting functionality
    for col in columns:
        product_tree.heading(col, text=col, 
                           command=lambda c=col: sort_treeview(product_tree, c, False))
    
    # Add scrollbar to product treeview
    scrollbar = ttk.Scrollbar(product_frame, orient=tk.VERTICAL, command=product_tree.yview)
    product_tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=1, column=2, sticky='ns')
    
    # Function to sort treeview
    def sort_treeview(tree, col, reverse):
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        data.sort(reverse=reverse)
        for index, (val, child) in enumerate(data):
            tree.move(child, '', index)
        tree.heading(col, command=lambda: sort_treeview(tree, col, not reverse))
    
    # Function to populate products
    def populate_products(brand=None):
        product_tree.delete(*product_tree.get_children())
        connection = create_connection()
        if connection:
            cursor = connection.cursor()
            query = "SELECT ID, Product_name, Unit_Price, Brand FROM products"
            if brand and brand != "All":
                query += f" WHERE Brand = '{brand}'"
            cursor.execute(query)
            products = cursor.fetchall()
            
            # Get unique brands for filter
            brands = set(product[3] for product in products)
            brand_filter['values'] = ["All"] + sorted(brands)
            
            for product in products:
                product_tree.insert("", tk.END, 
                                 values=(product[1], f"₹{product[2]:.2f}", 0), 
                                 tags=(product[0],))
            connection.close()
    
    # Initial population
    populate_products()
    
    # Bind brand filter change
    brand_filter.bind("<<ComboboxSelected>>", 
                     lambda e: populate_products(brand_filter.get()))
    
    # Function to update quantities
    def update_quantity(event):
        item = product_tree.selection()[0]
        current_values = product_tree.item(item, 'values')
        new_quantity = simpledialog.askinteger("Quantity", f"Enter quantity for {current_values[0]}:", 
                                            parent=bill_window, minvalue=0)
        if new_quantity is not None:
            product_tree.item(item, values=(current_values[0], current_values[1], new_quantity))
    
    # Bind double click to update quantity
    product_tree.bind("<Double-1>", update_quantity)
    
    # GST Rate
    gst_rate = 18  # 18% GST
    
    def calculate_bill():
        try:
            total = 0
            items = []
            for item in product_tree.get_children():
                values = product_tree.item(item, 'values')
                quantity = int(values[2])
                if quantity > 0:
                    product_id = product_tree.item(item, 'tags')[0]
                    price = float(values[1].replace('₹', ''))
                    total += price * quantity
                    # Get brand information from database
                    connection = create_connection()
                    if connection:
                        cursor = connection.cursor()
                        cursor.execute("SELECT Brand FROM products WHERE ID = %s", (product_id,))
                        brand = cursor.fetchone()[0]
                        connection.close()
                    
                    items.append({
                        'name': values[0],
                        'price': price,
                        'quantity': quantity,
                        'product_id': product_id,
                        'brand': brand
                    })
            
            if not items:
                messagebox.showwarning("Selection Error", "Please select at least one product with quantity > 0")
                return
                
            # Validate customer details
                
            # Calculate GST
            gst_rate = 18  # 18% GST
            gst_amount = (total * gst_rate) / 100
            grand_total = total + gst_amount
            
            # Generate sequential transaction ID
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("SELECT MAX(transaction_id) FROM bills")
                last_id = cursor.fetchone()[0]
                if last_id:
                    next_id = int(last_id.split('TXN')[1]) + 1
                else:
                    next_id = 1
                transaction_id = f"TXN{next_id:04d}"
                connection.close()
            
            # Display bill
            # Extract just the customer name from the combobox
            customer_name = customer_select.get().split(' - ')[0]
            
            bill_text = f"Pradayini Enterprise\n"
            bill_text += f"Transaction ID: {transaction_id}\n"
            bill_text += f"Customer: {customer_name}\n"
            bill_text += f"Phone: {customer_phone.get()}\n\n"
            bill_text += "Products:\n"
            for item in items:
                bill_text += f"- {item['name']} ({item['brand']}) x {item['quantity']} @ ₹{item['price']:.2f}\n"
            bill_text += f"\nSubtotal: ₹{total:.2f}\n"
            bill_text += f"GST ({gst_rate}%): ₹{gst_amount:.2f}\n"
            bill_text += f"Grand Total: ₹{grand_total:.2f}\n"
            bill_text += f"\nBrands Purchased:\n"
            # Get unique brands
            unique_brands = set(item['brand'] for item in items)
            for brand in unique_brands:
                bill_text += f"- {brand}\n"
            bill_text += f"\nThank you for your business!"
            
            # Save bill to database
            connection = create_connection()
            if connection:
                try:
                    cursor = connection.cursor()
                    insert_bill_query = """
                    INSERT INTO bills (transaction_id, customer_name, customer_phone, customer_address, total_amount, gst_amount, grand_total)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """
                    # First insert the bill
                    cursor.execute(insert_bill_query, (transaction_id, customer_name, customer_phone.get(), customer_address.get(), total, gst_amount, grand_total))
                    
                    # Save bill items and update product quantities
                    for item in items:
                        # Insert bill item details
                        insert_item_query = """
                        INSERT INTO bill_items (transaction_id, product_id, quantity)
                        VALUES (%s, %s, %s)
                        """
                        cursor.execute(insert_item_query, 
                            (transaction_id, item['product_id'], item['quantity']))
                        
                        # Update product quantity
                        update_query = """
                        UPDATE products 
                        SET Quantity = Quantity - %s 
                        WHERE ID = %s AND Quantity >= %s
                        """
                        cursor.execute(update_query, (item['quantity'], item['product_id'], item['quantity']))
                        if cursor.rowcount == 0:
                            connection.rollback()
                            messagebox.showerror("Stock Error", f"Insufficient stock for product: {item['name']}")
                            return
                    
                    connection.commit()
                    messagebox.showinfo("Bill Generated", bill_text)
                    bill_window.destroy()
                    view_products()  # Refresh product list after bill generation
                except Error as e:
                    connection.rollback()
                    messagebox.showerror("Database Error", f"Error saving bill: {e}")
                finally:
                    if connection.is_connected():
                        cursor.close()
                        connection.close()
        except ValueError:
            messagebox.showwarning("Input Error", "Please enter a valid quantity")
            
    # Create generate bill button
    ttk.Button(bill_window, text="Generate Bill", command=calculate_bill).grid(row=5, column=0, columnspan=2, pady=(10, 20))

def logout():
    """ Logout and clear stored credentials """
    confirm = messagebox.askyesno("Confirm Logout", "Are you sure you want to logout? This will clear stored credentials.")
    if confirm:
        keyring.delete_password('stock_management', 'host')
        keyring.delete_password('stock_management', 'user')
        keyring.delete_password('stock_management', 'password')
        keyring.delete_password('stock_management', 'database')
        messagebox.showinfo("Logout Successful", "Credentials cleared successfully")

def add_product():
    """ Add a new product to the products table """
    product_name = entry_product_name.get().strip()
    brand = entry_brand.get().strip()
    quantity = entry_quantity.get()
    price = entry_price.get()

    if not product_name or not brand or not quantity or not price:
        messagebox.showwarning("Input Error", "All fields are required")
        return

    try:
        quantity = int(quantity)
        price = float(price)
        if quantity <= 0 or price <= 0:
            raise ValueError("Values must be positive")
    except ValueError:
        messagebox.showwarning("Input Error", "Quantity and Price must be valid positive numbers")
        return

    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            add_product_query = """
            INSERT INTO products (Product_name, Brand, Unit_Price, Quantity)
            VALUES (%s, %s, %s, %s);
            """
            cursor.execute(add_product_query, (product_name, brand, price, quantity))
            connection.commit()
            messagebox.showinfo("Success", f"Product '{product_name}' added successfully")
            clear_entries()
            view_products()
        except Error as e:
            connection.rollback()
            messagebox.showerror("Database Error", f"Error adding product: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

def update_product():
    """ Update an existing product's quantity and price """
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select a product to update")
        return
        
    # Get actual ID from tag
    product_id = tree.item(selected[0], 'tags')[0]
    
    # Use the pre-filled price from the entry field
    price = entry_price.get()
    quantity = entry_quantity.get()
    operation = update_operation.get()

    if not quantity or not price:
        messagebox.showwarning("Input Error", "Quantity and Price are required")
        return

    try:
        quantity = int(quantity)
        price = float(price)
        if quantity <= 0 or price <= 0:
            raise ValueError("Values must be positive")
    except ValueError:
        messagebox.showwarning("Input Error", "Quantity and Price must be valid positive numbers")
        return

    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Get current quantity
            cursor.execute("SELECT Quantity FROM products WHERE ID = %s", (int(product_id),))
            current_quantity = cursor.fetchone()[0]
            
            # Calculate new quantity based on operation
            if operation == "remove":
                new_quantity = current_quantity - quantity
                if new_quantity < 0:
                    messagebox.showwarning("Invalid Operation", "Cannot remove more than available quantity")
                    return
            else:  # add
                new_quantity = current_quantity + quantity
                
            update_product_query = """
            UPDATE products
            SET Quantity = %s, Unit_Price = %s
            WHERE ID = %s;
            """
            cursor.execute(update_product_query, (new_quantity, price, int(product_id)))
            connection.commit()
            messagebox.showinfo("Success", f"Product ID '{product_id}' updated successfully")
            clear_entries()
            view_products()
        except Error as e:
            connection.rollback()
            messagebox.showerror("Database Error", f"Error updating product: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

def delete_product():
    """ Delete a product from the products table """
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select a product to delete")
        return
        
    # Get actual ID from tag
    product_id = tree.item(selected[0], 'tags')[0]
    
    # Add confirmation dialog
    confirm = messagebox.askyesno("Confirm Delete", 
        f"Are you sure you want to delete product ID {product_id}?")
    if not confirm:
        return

    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()
            delete_product_query = "DELETE FROM products WHERE ID = %s;"
            cursor.execute(delete_product_query, (int(product_id),))
            connection.commit()
            messagebox.showinfo("Success", f"Product ID '{product_id}' deleted successfully")
            clear_entries()
            view_products()
        except Error as e:
            connection.rollback()
            messagebox.showerror("Database Error", f"Error deleting product: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

def view_products():
    """ Retrieve and display all products from the products table """
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT ID, Product_name, Brand, Unit_Price, Quantity, (Unit_Price * Quantity) AS Total_price FROM products;")
        products = cursor.fetchall()
        connection.close()

        # Clear the treeview
        for row in tree.get_children():
            tree.delete(row)

        # Display serial numbers while maintaining actual IDs
        for index, product in enumerate(products, start=1):
            tree.insert("", tk.END, values=(index, product[0], product[1], product[2], f"{product[3]:.2f}", product[4], f"{product[5]:.2f}"), tags=(product[0],))
        
        # Store actual IDs in tag for reference
        tree.tag_configure('id', background='white')
        
        # Add selection event handler to pre-fill price
        def on_product_select(event):
            selected = tree.selection()
            if selected:
                # Get the unit price from the selected product
                Unit_Price = tree.item(selected[0], 'values')[4]
                # Pre-fill the price entry field
                entry_price.delete(0, tk.END)
                entry_price.insert(0, Unit_Price)
                # Calculate total price
                calculate_total()
        
        # Bind the selection event
        tree.bind('<<TreeviewSelect>>', on_product_select)

def clear_entries():
    """ Clear all input fields """
    entry_product_name.delete(0, tk.END)
    entry_brand.delete(0, tk.END)
    entry_quantity.delete(0, tk.END)
    entry_price.delete(0, tk.END)
    total_price_label.config(text="0.00")

# Create the main window
root = tk.Tk()
root.title("Pradayini Enterprise")

# Create input fields
ttk.Label(root, text="Product Name").grid(row=0, column=0, padx=5, pady=5)
entry_product_name = ttk.Entry(root)
entry_product_name.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(root, text="Brand").grid(row=1, column=0, padx=5, pady=5)
entry_brand = ttk.Entry(root)
entry_brand.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(root, text="Quantity").grid(row=3, column=0, padx=5, pady=5)
entry_quantity = ttk.Entry(root)
entry_quantity.grid(row=3, column=1, padx=5, pady=5)

ttk.Label(root, text="Price").grid(row=4, column=0, padx=5, pady=5)
entry_price = ttk.Entry(root)
entry_price.grid(row=4, column=1, padx=5, pady=5)

def calculate_total(*args):
    try:
        quantity = int(entry_quantity.get())
        price = float(entry_price.get())
        total = quantity * price
        total_price_label.config(text=f"Total: ₹{total:.2f}", foreground="green", font=("Arial", 10, "bold"))
    except (ValueError, AttributeError):
        total_price_label.config(text="Total: ₹0.00", foreground="red", font=("Arial", 10, "bold"))

# Total Price Display
total_price_label = ttk.Label(root, text="Total: ₹0.00", foreground="red", font=("Arial", 10, "bold"))
total_price_label.grid(row=5, column=0, columnspan=2, pady=10)

# Bind calculation to quantity and price changes
entry_quantity.bind("<KeyRelease>", calculate_total)
entry_price.bind("<KeyRelease>", calculate_total)

# Update operation selection
update_operation = tk.StringVar(value="add")
ttk.Label(root, text="Update Operation:").grid(row=2, column=0, padx=5, pady=5)
ttk.Radiobutton(root, text="Add Stock", variable=update_operation, value="add").grid(row=2, column=1, padx=5, pady=5)
ttk.Radiobutton(root, text="Remove Stock", variable=update_operation, value="remove").grid(row=2, column=2, padx=5, pady=5)

# Create buttons
ttk.Button(root, text="Add New Product", command=add_product).grid(row=5, column=0, padx=5, pady=5)
ttk.Button(root, text="Update Stock", command=update_product).grid(row=5, column=1, padx=5, pady=5)
ttk.Button(root, text="Delete Product", command=delete_product).grid(row=6, column=0, padx=5, pady=5)
ttk.Button(root, text="View Products", command=view_products).grid(row=6, column=1, padx=5, pady=5)
ttk.Button(root, text="Generate Bill", command=generate_bill).grid(row=8, column=0, padx=5, pady=5)
ttk.Button(root, text="View Bills", command=view_bills).grid(row=8, column=1, padx=5, pady=5)
ttk.Button(root, text="Change Credentials", command=get_db_credentials).grid(row=9, column=0, padx=5, pady=5)
ttk.Button(root, text="Logout", command=logout).grid(row=9, column=1, padx=5, pady=5)

# Create treeview to display products
columns = ("Serial No.", "ID", "Product_name", "Brand", "Unit_Price", "Quantity", "Total_price")
tree = ttk.Treeview(root, columns=columns, show="headings")
tree.heading("Serial No.", text="Serial No.")
tree.heading("ID", text="Product ID")
tree.heading("Product_name", text="Product Name")
tree.heading("Brand", text="Brand")
tree.heading("Unit_Price", text="Unit Price")
tree.heading("Quantity", text="Quantity")
tree.heading("Total_price", text="Total Price")
tree.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

# Add scrollbar
scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.grid(row=7, column=2, sticky='ns')

# Populate products when application starts
view_products()

# Run the application
root.mainloop()
