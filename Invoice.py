#Invoice.py
import tkinter as tk
from tkinter import ttk
import sqlite3

class InvoiceApp:
    def __init__(self, master):
        print("In the __init__ method")
        self.master = master
        self.master.geometry("800x800")
        self.master.title("Invoice Application")

        # Create database connection
        self.conn = sqlite3.connect('invoice.db')
        self.c = self.conn.cursor()

        # Create tables
        self.create_tables()

        # Initialize an empty list to hold the item rows
        self.item_rows = []

        # Fetch items from the database
        self.c.execute('SELECT * FROM items')
        self.items = self.c.fetchall()

        # Initialize an empty list for item_vars
        self.item_vars = []

        # Initialize grand_total_var
        self.grand_total_var = tk.StringVar()

        # Initialize UI
        self.init_ui()

        self.sales_tax_var = tk.StringVar()
        self.liquor_tax_var = tk.StringVar()
        self.total_with_tax_var = tk.StringVar()

        # In your init_ui method, after creating the more_button
        self.sales_tax_label = tk.Label(self.master, text="Sales Tax:")
        self.sales_tax_label.pack(side=tk.TOP)

        self.sales_tax_entry = tk.Entry(self.master, textvariable=self.sales_tax_var, state='readonly')
        self.sales_tax_entry.pack(side=tk.TOP)

        self.liquor_tax_label = tk.Label(self.master, text="Liquor Tax:")
        self.liquor_tax_label.pack(side=tk.TOP)

        self.liquor_tax_entry = tk.Entry(self.master, textvariable=self.liquor_tax_var, state='readonly')
        self.liquor_tax_entry.pack(side=tk.TOP)

        self.total_with_tax_label = tk.Label(self.master, text="Total (including tax):")
        self.total_with_tax_label.pack(side=tk.TOP)

        self.total_with_tax_entry = tk.Entry(self.master, textvariable=self.total_with_tax_var, state='readonly')
        self.total_with_tax_entry.pack(side=tk.TOP)

    def init_ui(self):
        try:
            print("In the init_ui method")

            # Create widgets
            self.create_widgets()

            # Add item rows
            for _ in range(15):  # Creates 15 item rows initially
                self.add_item_row()

            # Add "More" button
            self.add_more_button = tk.Button(self.master, text="More", command=self.add_more_items)
            self.add_more_button.pack(side=tk.TOP)

            # Create a frame for totals
            self.totals_frame = tk.Frame(self.master)
            self.totals_frame.pack(side=tk.TOP, padx=5, pady=5)

            # Sales Tax
            self.sales_tax_label = tk.Label(self.totals_frame, text="Sales Tax:")
            self.sales_tax_label.pack(side=tk.TOP)
            self.sales_tax_entry = tk.Entry(self.totals_frame, textvariable=self.sales_tax_var, state='readonly')
            self.sales_tax_entry.pack(side=tk.TOP)

            # Liquor Tax
            self.liquor_tax_label = tk.Label(self.totals_frame, text="Liquor Tax:")
            self.liquor_tax_label.pack(side=tk.TOP)
            self.liquor_tax_entry = tk.Entry(self.totals_frame, textvariable=self.liquor_tax_var, state='readonly')
            self.liquor_tax_entry.pack(side=tk.TOP)

            # Total including Tax
            self.total_with_tax_var = tk.StringVar()
            self.total_with_tax_label = tk.Label(self.totals_frame, text="Total (including tax):")
            self.total_with_tax_label.pack(side=tk.TOP)
            self.total_with_tax_entry = tk.Entry(self.totals_frame, textvariable=self.total_with_tax_var, state='readonly')
            self.total_with_tax_entry.pack(side=tk.TOP)

            # Add Grand Total display
            self.grand_total_label = tk.Label(self.totals_frame, text="Grand Total:")
            self.grand_total_label.pack(side=tk.TOP)
            self.grand_total_entry = tk.Entry(self.totals_frame, textvariable=self.grand_total_var, state='readonly')
            self.grand_total_entry.pack(side=tk.TOP)

            # Create an 'Update' button
            self.update_button = tk.Button(self.totals_frame, text="Update", command=self.calculate_total)
            self.update_button.pack(side=tk.TOP)

        except Exception as e:
            print("Exception occurred in init_ui: ", e)

    def create_tables(self):
        try:
            print("In the create_tables method")
            
            self.c.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    name TEXT,
                    address TEXT,
                    city TEXT,
                    state TEXT,
                    zip TEXT,
                    phone TEXT
                )
            ''')

            self.c.execute('''
                CREATE TABLE IF NOT EXISTS invoices (
                    invoice_number INTEGER PRIMARY KEY,
                    customer_name TEXT,
                    total REAL,
                    tax REAL,
                    grand_total REAL
                )
            ''')

            self.c.execute('''
                CREATE TABLE IF NOT EXISTS invoice_items (
                    invoice_number INTEGER,
                    item_name TEXT,
                    quantity INTEGER,
                    FOREIGN KEY (invoice_number) REFERENCES invoices (invoice_number)
                )
            ''')

            self.conn.commit()
        except Exception as e:
            print("Exception occurred in create_tables: ", e)


    def add_item_row(self):
        # Create a new item row frame
        item_row_frame = tk.Frame(self.item_rows_frame)
        item_row_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Create a variable to hold the selected item
        item_var = tk.StringVar()
        self.item_vars.append(item_var) 

        # Create a Combobox for item selection in this row
        item_combo = ttk.Combobox(item_row_frame, values=[item[0] for item in self.items])
        item_combo.pack(side=tk.LEFT)

        # Create a Spinbox for quantity selection in this row
        quantity_spin = tk.Spinbox(item_row_frame, from_=0, to=100, width=5)
        quantity_spin.pack(side=tk.LEFT)

        # Create an Entry for price display in this row
        price_var = tk.StringVar()
        price_entry = tk.Entry(item_row_frame, textvariable=price_var, state='readonly')
        price_entry.pack(side=tk.LEFT)
        
        # Add a selection handler to the Combobox
        def on_item_selected(event):
            selected_item = item_combo.get()
            for item in self.items:
                if item[0] == selected_item:
                    price_var.set(str(item[1]))
                    break
        item_combo.bind('<<ComboboxSelected>>', on_item_selected)

        # Add a quantity change handler to the Spinbox
        #def on_quantity_changed(event):
        #    self.calculate_total()
        quantity_spin.bind('<KeyRelease>', self.on_quantity_changed)

        # Create an Entry for row total display in this row
        row_total_var = tk.StringVar()
        row_total_entry = tk.Entry(item_row_frame, textvariable=row_total_var, state='readonly')
        row_total_entry.pack(side=tk.LEFT)

        # Add the new item row to our list
        self.item_rows.append((item_combo, quantity_spin, price_var, row_total_var))

    def add_more_items(self):
        self.add_item_row()
        self.calculate_total()  # Calculate total after adding a new item row

    def calculate_total(self):
        print("calculate_total started")
        try:
            print("In the calculate_total method")  # Debug print
            print("Item rows: ", self.item_rows)  # add this line
            grand_total = 0
            sales_tax = 0
            liquor_tax = 0
            for item_combo, quantity_spin, price_var, row_total_var in self.item_rows:
                # Get the selected item from the Combobox
                item_name = item_combo.get()

                # Get the quantity from the Spinbox
                quantity = int(quantity_spin.get())

                # Fetch the item price and tax type from the database
                self.c.execute("SELECT price, tax_type FROM items WHERE name = ?", (item_name,))
                item = self.c.fetchone()
                print("Fetched item from database: ", item)

                if item is not None:
                    # Calculate the total
                    price = item[0]
                    total = price * quantity
                    grand_total += total
                            
                    # Update the total in the Entry
                    price_var.set(f'{price:.2f}')  # Update the price
                    row_total_var.set(f'{total:.2f}')  # Update the total for the row
                    
                    # Calculate taxes based on tax type
                    if item[1] == 'general':
                        sales_tax += total * 0.065
                    elif item[1] == 'liquor':
                        sales_tax += total * 0.065
                        liquor_tax += total * 0.025

                    # Debug prints
                    print(f"item_name: {item_name}, quantity: {quantity}, price: {price}, total: {total}, sales_tax: {sales_tax}, liquor_tax: {liquor_tax}")
                    
            # Update grand total
            self.grand_total_var.set(f'{grand_total:.2f}')
            # Update sales tax
            self.sales_tax_var.set(f'{sales_tax:.2f}')
            # Update liquor tax
            self.liquor_tax_var.set(f'{liquor_tax:.2f}')
            # Update total with tax
            total_with_tax = grand_total + sales_tax + liquor_tax
            self.total_with_tax_var.set(f'{total_with_tax:.2f}')
        except Exception as e:
            print("Exception occurred in calculate_total: ", e)


    def create_widgets(self):
        print("Creating widgets...")
        # Create the customer information form at the top
        self.customer_info_frame = tk.Frame(self.master)
        self.customer_info_frame.pack(side=tk.TOP, fill=tk.X)
        print("Customer info frame created")

        self.create_customer_info_field(self.customer_info_frame, "Name", 0)
        print("Name field created")
        self.create_customer_info_field(self.customer_info_frame, "Address", 1)
        print("Address field created")
        self.create_customer_info_field(self.customer_info_frame, "City", 2)
        print("City field created")
        self.create_customer_info_field(self.customer_info_frame, "State", 3)
        print("State field created")
        self.create_customer_info_field(self.customer_info_frame, "Zip", 4)
        print("Zip field created")
        self.create_customer_info_field(self.customer_info_frame, "Phone", 5)
        print("Phone field created")

    def create_customer_info_field(self, parent_frame, field_name, row):
        print(f"Creating {field_name} field...")
        field_frame = tk.Frame(parent_frame)
        field_frame.pack(side=tk.TOP, fill=tk.X)

        label = tk.Label(field_frame, text=f"{field_name}:")
        label.grid(row=row, column=0, sticky='w')

        entry = tk.Entry(field_frame)
        entry.grid(row=row, column=1, sticky='w')
        print(f"{field_name} field created")

    def get_items(self):
        try:
            self.c.execute("SELECT name FROM items")
            items = [item[0] for item in self.c.fetchall()]
            return items
        except Exception as e:
            print("Exception occurred in get_items: ", e)
            return []

    def init_ui(self):
        try:
            print("In the init_ui method")

            # Create widgets
            self.create_widgets()

            # Fetch items from the database
            self.c.execute('SELECT * FROM items')
            self.items = self.c.fetchall()

            # Create a frame for the items
            self.items_frame = tk.Frame(self.master)
            self.items_frame.pack(side=tk.TOP, fill=tk.X)

            # Create the invoice form below the customer information
            self.invoice_frame = tk.Frame(self.master)
            self.invoice_frame.pack(side=tk.TOP, fill=tk.X)

            # Create a frame to hold the item rows
            self.item_rows_frame = tk.Frame(self.master)
            self.item_rows_frame.pack(side=tk.TOP, fill=tk.X)

            # Create 15 item rows
            for _ in range(15):
                self.add_item_row()

            # Create the 'More' button
            self.more_button = tk.Button(self.master, text="More", command=self.add_item_row)
            self.more_button.pack(side=tk.TOP)

            # Create an Entry for displaying grand total
            total_label = tk.Label(self.totals_frame, text="Total:")
            total_label.pack(side=tk.LEFT)
            total_entry = tk.Entry(self.totals_frame, textvariable=self.grand_total_var, state='readonly')
            total_entry.pack(side=tk.LEFT)

            # Create a label and an entry for the grand total
            self.grand_total_label = tk.Label(self.master, text="Grand Total:")
            self.grand_total_label.pack(side=tk.TOP)
            self.grand_total_entry = tk.Entry(self.master, textvariable=self.grand_total_var, state='readonly')
            self.grand_total_entry.pack(side=tk.TOP)

        except Exception as e:
            print("Exception occurred in init_ui: ", e)

    def on_item_selected(event):
        print("Item selected event triggered")  # add this line
        selected_item = item_combo.get()
        for item in self.items:
            if item[0] == selected_item:
                price_var.set(str(item[1]))
                self.calculate_total()  # update totals
                break
        self.calculate_total()  # Calculate total when an item is selected

    def on_quantity_changed(self, event):
        print("Quantity changed, calling calculate_total")  # Debug print
        # When quantity is changed, recalculate the total
        self.calculate_total()
 
    # Other methods for the application (e.g., for interacting with the database) go here

root = tk.Tk()
app = InvoiceApp(root)
root.mainloop()
