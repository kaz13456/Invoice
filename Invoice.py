#Invoice.py
import tkinter as tk
from tkinter import ttk
import sqlite3

class InvoiceApp:
    def __init__(self, master):
        self.master = master
        print("In the __init__ method")
        self.master.geometry("800x800")
        self.master.title("Invoice Application")

        # Create database connection
        self.conn = sqlite3.connect('invoice.db')
        self.c = self.conn.cursor()

        # Create tables
        self.create_tables()

        # Initialize an empty list to hold the item rows
        self.items = []  # This will hold the items fetched from the database
        self.item_vars = []  # This will hold the StringVars for the Comboboxes
        self.quantity_vars = []  # Add this line. This will hold the StringVars for the Spinboxes.
        self.item_rows = []  # This will hold the widgets for each item row

        # Fetch items from the database
        self.c.execute('SELECT * FROM items')
        self.items = self.c.fetchall()

        # Initialize an empty list for item_vars
        self.item_vars = []

        # Initialize grand_total_var
        self.grand_total_var = tk.StringVar()

        self.sales_tax_var = tk.StringVar()
        self.liquor_tax_var = tk.StringVar()
        self.total_with_tax_var = tk.StringVar()

        # Initialize UI
        self.init_ui()

        # In your init_ui method, after creating the more_button
        self.sales_tax_label = tk.Label(self.totals_frame, text="Sales Tax:")
        self.sales_tax_label.grid(row=9, column=0)

        self.sales_tax_entry = tk.Entry(self.totals_frame, textvariable=self.sales_tax_var, state='readonly')
        self.sales_tax_entry.grid(row=9, column=1)

        self.liquor_tax_label = tk.Label(self.totals_frame, text="Liquor Tax:")
        self.liquor_tax_label.grid(row=10, column=0)

        self.liquor_tax_entry = tk.Entry(self.totals_frame, textvariable=self.liquor_tax_var, state='readonly')
        self.liquor_tax_entry.grid(row=10, column=1)

        self.total_with_tax_label = tk.Label(self.totals_frame, text="Total (including tax):")
        self.total_with_tax_label.grid(row=11, column=0)

        self.total_with_tax_entry = tk.Entry(self.totals_frame, textvariable=self.total_with_tax_var, state='readonly')
        self.total_with_tax_entry.grid(row=11, column=1)

        # Create a new frame for Payment Method
        self.payment_frame = tk.Frame(self.master)
        self.payment_frame.pack(fill='x') # Pack the payment frame

        # Create a label for Payment Method
        payment_method_label = tk.Label(self.payment_frame, text="Payment Method:")
        payment_method_label.grid(row=0, column=0)

        # Create a Combobox for selecting Payment Method
        payment_options = ['Cash', 'Credit Card/Debit Card']
        self.payment_method_combo = ttk.Combobox(self.payment_frame, values=payment_options)
        self.payment_method_combo.grid(row=0, column=1)
        self.payment_method_combo.set(payment_options[0])  # Default to 'Cash'

        # Bind the event here
        self.payment_method_combo.bind('<<ComboboxSelected>>', self.update_transaction_fee)

        # Create a label for Credit Transaction Fee
        credit_trans_fee_label = tk.Label(self.payment_frame, text="Credit Trans. Fee:")
        credit_trans_fee_label.grid(row=1, column=0)

        # Variable to store the credit transaction fee
        self.credit_trans_fee_var = tk.DoubleVar()
        credit_trans_fee_label_value = tk.Label(self.payment_frame, textvariable=self.credit_trans_fee_var)
        credit_trans_fee_label_value.grid(row=1, column=1)


    def init_ui(self):
        try:
            print("In the init_ui method")

            # Create main frames for different sections
            self.customer_info_frame = tk.Frame(self.master)  # Customer info first
            self.item_rows_frame = tk.Frame(self.master)
            self.more_button_frame = tk.Frame(self.master)
            self.totals_frame = tk.Frame(self.master)

            # Pack these frames in the order you want them to appear
            self.customer_info_frame.pack(fill='x')  # Customer info at the top
            self.item_rows_frame.pack(fill='x')
            self.more_button_frame.pack(fill='x')
            self.totals_frame.pack(fill='x')

            # Create widgets
            self.create_widgets()

            # Add item rows
            for _ in range(15):  # Creates 15 item rows initially
                self.add_item_row()

            # Add "More" button
            self.add_more_button = tk.Button(self.more_button_frame, text="More", command=self.add_more_items)
            self.add_more_button.pack(side=tk.TOP, pady=10)

            # Sales Tax
            self.sales_tax_label = tk.Label(self.totals_frame, text="Sales Tax:")
            self.sales_tax_label.grid(row=0, column=0)
            self.sales_tax_entry = tk.Entry(self.totals_frame, textvariable=self.sales_tax_var, state='readonly')
            self.sales_tax_entry.grid(row=0, column=1)

            # Liquor Tax
            self.liquor_tax_label = tk.Label(self.totals_frame, text="Liquor Tax:")
            self.liquor_tax_label.grid(row=1, column=0)
            self.liquor_tax_entry = tk.Entry(self.totals_frame, textvariable=self.liquor_tax_var, state='readonly')
            self.liquor_tax_entry.grid(row=1, column=1)

            # Total including Tax
            self.total_with_tax_var = tk.StringVar()
            self.total_with_tax_label = tk.Label(self.totals_frame, text="Total (including tax):")
            self.total_with_tax_label.grid(row=2, column=0)
            self.total_with_tax_entry = tk.Entry(self.totals_frame, textvariable=self.total_with_tax_var, state='readonly')
            self.total_with_tax_entry.grid(row=2, column=1)

            # Add Grand Total display
            self.grand_total_label = tk.Label(self.totals_frame, text="Grand Total:")
            self.grand_total_label.grid(row=3, column=0)
            self.grand_total_entry = tk.Entry(self.totals_frame, textvariable=self.grand_total_var, state='readonly')
            self.grand_total_entry.grid(row=3, column=1)

            # Create an 'Update' button
            self.update_button = tk.Button(self.totals_frame, text="Update", command=self.calculate_total)
            self.update_button.grid(row=4, column=0, columnspan=2, pady=10)

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
        item_row_frame.grid(sticky='nsew')

        # Create a variable to hold the selected item
        item_var = tk.StringVar()
        self.item_vars.append(item_var) 

        # Create a Combobox for item selection in this row
        item_combo = ttk.Combobox(item_row_frame, values=[item[0] for item in self.items])
        item_combo.grid(column=0, row=len(self.item_rows), padx=10)

        # Create a Spinbox for quantity selection in this row
        quantity_var = tk.StringVar()  
        self.quantity_vars.append(quantity_var)
        quantity_var.trace('w', self.on_quantity_changed)  
        quantity_spin = tk.Spinbox(item_row_frame, from_=0, to=100, width=5, textvariable=quantity_var)
        quantity_spin.grid(column=1, row=len(self.item_rows), padx=10)
        
        # Create an Entry for price display in this row
        price_var = tk.StringVar()
        price_entry = tk.Entry(item_row_frame, textvariable=price_var, state='readonly')
        price_entry.grid(column=2, row=len(self.item_rows), padx=10)
        
        # Create an Entry for row total display in this row
        row_total_var = tk.StringVar()
        row_total_entry = tk.Entry(item_row_frame, textvariable=row_total_var, state='readonly')
        row_total_entry.grid(column=3, row=len(self.item_rows), padx=10)

        # Add a selection handler to the Combobox
        def on_item_selected(event):
            selected_item = item_combo.get()
            for item in self.items:
                if item[0] == selected_item:
                    price_var.set(str(item[1]))
                    update_row_total()
                    break

        item_combo.bind('<<ComboboxSelected>>', on_item_selected)

        # Add the new item row to our list
        self.item_rows.append((item_combo, quantity_spin, price_var, row_total_var))

        def update_row_total():
            # calculate row total (price * quantity)
            if price_var.get() and quantity_var.get():
                row_total = float(price_var.get()) * int(quantity_var.get())
                row_total_var.set(row_total)
            else:
                row_total_var.set(0)

        quantity_var.trace("w", lambda name, index, mode, quantity_var=quantity_var: update_row_total())


    def add_more_items(self):
        self.add_item_row()
        self.calculate_total()  # Calculate total after adding a new item row

    def calculate_total(self):
        print("calculate_total started")
        try:
            print("In the calculate_total method")  # Debug print
            grand_total = 0
            sales_tax = 0
            liquor_tax = 0
            for item_combo, quantity_spin, price_var, row_total_var in self.item_rows:
                print("Processing item row")  # add this line
                # Get the selected item from the Combobox
                item_name = item_combo.get()
                print(f"Item name from item_combo: {item_name}")
                if not item_name:
                    print("Error: Item name is empty!")
                    continue  # Skip to the next iteration if the item name is empty
                
                # Get the quantity from the Spinbox
                quantity = int(quantity_spin.get())
                print(f"Quantity: {quantity}")

                # Fetch the item tax type from the database
                self.c.execute("SELECT taxable, liquor_tax FROM items WHERE name = ?", (item_name,))
                item = self.c.fetchone()
                print("Fetched item from database: ", item)

                # Check if the item is found
                if item is None:
                    print(f"Error: Item {item_name} not found in the database!")
                    continue  # Skip to the next iteration if the item is not found

                # Calculate the total from the row total var
                total = float(row_total_var.get())
                print(f"Row total: {total}")
                grand_total += total
                print(f"Grand total so far: {grand_total}")

                # Calculate taxes
                if item[0]:  # if taxable
                    sales_tax += total * 0.065  # taxable tax
                if item[1]:  # if liquor tax
                    liquor_tax += total * 0.025  # liquor tax

                print(f"Sales tax so far: {sales_tax}")
                print(f"Liquor tax so far: {liquor_tax}")

                # Debug prints
                print(f"item_name: {item_name}, quantity: {quantity}, total: {total}, sales_tax: {sales_tax}, liquor_tax: {liquor_tax}")
                print(f"Item name: {item_name}, Taxable: {item[0]}, Liquor Tax: {item[1]}")

            # Update grand total
            self.grand_total_var.set(f'{grand_total:.2f}')
            print(f"Final grand total: {grand_total}")
            # Update sales tax
            self.sales_tax_var.set(f'{sales_tax:.2f}')
            print(f"Final sales tax: {sales_tax}")
            # Update liquor tax
            self.liquor_tax_var.set(f'{liquor_tax:.2f}')
            print(f"Final liquor tax: {liquor_tax}")
            # Update total with tax
            total_with_tax = grand_total + sales_tax + liquor_tax
            self.total_with_tax_var.set(f'{total_with_tax:.2f}')
            print(f"Final total with tax: {total_with_tax}")
        except Exception as e:
            print("Exception occurred in calculate_total: ", e)


    def create_widgets(self):
        print("Creating widgets...")
        # Create the customer information form at the top
        
        self.customer_info_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='w')
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

        label = tk.Label(parent_frame, text=f"{field_name}:")
        label.grid(row=row, column=0, sticky='w')

        entry = tk.Entry(parent_frame)
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

    def on_item_selected(event):
        print("Item selected event triggered")  # add this line
        selected_item = item_combo.get()
        for item in self.items:
            if item[0] == selected_item:
                price_var.set(str(item[1]))
                self.calculate_total()  # update totals
                break
        self.calculate_total()  # Calculate total when an item is selected

    def on_quantity_changed(self, *args):
        print("Quantity changed, calling calculate_total")  # Debug print
        # When quantity is changed, recalculate the total
        self.calculate_total()
 
    def update_item_total(self, item_var, qty_var, total_var):
        # Get the selected item and quantity
        item = item_var.get()
        qty = qty_var.get()

        # Check if the item is selected and the quantity is not empty
        if item and qty:
            # Find the price of the selected item
            price = next((item_data[2] for item_data in self.items if item_data[1] == item), 0)
            # Calculate the total for the row
            total = price * int(qty)
            # Update the total_var
            total_var.set(total)
        else:
            # If the item is not selected or the quantity is empty, set the total to 0
            total_var.set(0)
    
    # Function to calculate and update the credit transaction fee
    def update_transaction_fee(self, event):
        payment_method = payment_method_combo.get()
        total_with_tax = float(self.total_with_tax_var.get())
        if payment_method == 'Credit Card/Debit Card':
            credit_trans_fee = total_with_tax * 0.015 # 1.50% of the total
        else:
            credit_trans_fee = 0
        self.credit_trans_fee_var.set(f'{credit_trans_fee:.2f}')
        # Update the final total if needed

    # Bind the function to Combobox selection change
    #self.payment_method_combo.bind('<<ComboboxSelected>>', update_transaction_fee)

# Other methods for the application (e.g., for interacting with the database) go here

root = tk.Tk()
app = InvoiceApp(root)
root.mainloop()
