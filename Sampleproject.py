import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
import mysql.connector
import csv
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class DeliveryTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Delivery Tracking System")
        self.configure(background='#FDFECC')

        # Create a database connection
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="navin123457",
            database="delivery_tracking_system"
        )
        self.table_name = "delivery_record_sys"

        self.geometry("800x600")
        self.configure(background='#FDFECC')

        # Load and resize the background image
        bg_image = Image.open(r"C:\Users\lenovo\Downloads\Image-20230515T060830Z-001\Delivery\delivery-man-with-box-postman-design-isolated-on-white-background-courier-in-hat-and-uniform-with-package-vector.jpg")
        bg_image = bg_image.resize((1800, 1000), Image.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(bg_image)

        # Create a label for the background image and place it at the bottom of the stacking order
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create the GUI components
        self.label = tk.Label(self, text="Enter your Customer ID:", bg='#FDFECC', fg='#333333', font=("Arial", 16))
        self.label.pack(pady=10)

        # Password

        self.label_password = tk.Label(self, text="Enter your Password:", bg='#FDFECC', fg='#333333', font=("Arial", 16))
        self.label_password.pack(pady=10)

        self.password_entry = tk.Entry(self, font=("Arial", 14), show="*")
        self.password_entry.pack(pady=10)


        self.customer_id_entry = tk.Entry(self, font=("Arial", 14))
        self.customer_id_entry.pack(pady=10)

        self.submit_button = tk.Button(self, text="Submit", command=self.display_records, bg='#009688', fg='white', font=("Arial", 14))
        self.submit_button.pack(pady=20)

        # Create a frame for the record display area
        self.record_frame = tk.Frame(self, bg='#FDFECC', bd=5, relief=tk.RIDGE)
        self.record_frame.pack(pady=10)

        self.record_treeview = ttk.Treeview(self.record_frame)
        self.record_treeview["columns"] = ("ID", "Customer Name", "Customer ID", "Product Name", "Product Price", "Delivery Date", "Ordered Date", "Address")
        self.record_treeview.column("#0", width=0, stretch=tk.NO)
        self.record_treeview.column("ID", anchor=tk.CENTER, width=100)
        self.record_treeview.column("Customer Name", anchor=tk.W, width=150)
        self.record_treeview.column("Customer ID", anchor=tk.CENTER, width=100)
        self.record_treeview.column("Product Name", anchor=tk.W, width=150)
        self.record_treeview.column("Product Price", anchor=tk.E, width=100)
        self.record_treeview.column("Delivery Date", anchor=tk.CENTER, width=120)
        self.record_treeview.column("Ordered Date", anchor=tk.CENTER, width=120)
        self.record_treeview.column("Address", anchor=tk.W, width=300)
        self.record_treeview.heading("#0", text="", anchor=tk.W)
        self.record_treeview.heading("ID", text="ID", anchor=tk.CENTER)
        self.record_treeview.heading("Customer Name", text="Customer Name", anchor=tk.W)
        self.record_treeview.heading("Customer ID", text="Customer ID", anchor=tk.CENTER)
        self.record_treeview.heading("Product Name", text="Product Name", anchor=tk.W)
        self.record_treeview.heading("Product Price", text="Product Price", anchor=tk.E)
        self.record_treeview.heading("Delivery Date", text="Delivery Date", anchor=tk.CENTER)
        self.record_treeview.heading("Ordered Date", text="Ordered Date", anchor=tk.CENTER)
        self.record_treeview.heading("Address", text="Address", anchor=tk.W)
        self.record_treeview.pack(pady=10)

        self.generate_bill_button = tk.Button(self, text="Generate Bill", command=self.generate_bill, bg='#FF5722', fg='white', font=("Arial", 14))
        self.generate_bill_button.pack(pady=10)

        self.export_button = tk.Button(self, text="Export Records", command=self.export_records, bg='#607D8B', fg='white', font=("Arial", 14))
        self.export_button.pack(pady=10)

        self.sort_var = tk.StringVar()
        self.filter_var = tk.StringVar()
        self.sort_by_combobox = ttk.Combobox(self, textvariable=self.sort_var, values=["ID", "Customer Name", "Customer ID", "Product Name", "Product Price", "Delivery Date", "Ordered Date", "Address"], state="readonly")
        self.sort_by_combobox.pack(pady=10)
        self.sort_button = tk.Button(self, text="Sort", command=self.sort_records, bg='#607D8B', fg='white', font=("Arial", 14))
        self.sort_button.pack(pady=10)
        self.filter_entry = tk.Entry(self, textvariable=self.filter_var, font=("Arial", 14))
        self.filter_entry.pack(pady=10)
        self.filter_button = tk.Button(self, text="Filter", command=self.filter_records, bg='#607D8B', fg='white', font=("Arial", 14))
        self.filter_button.pack(pady=10)

    def query_records(self, customer_id, password):
       query = f"SELECT * FROM {self.table_name} WHERE customer_id = {customer_id} AND password = '{password}'"
       cursor = self.conn.cursor()
       cursor.execute(query)
       records = cursor.fetchall()
       cursor.close()
       return records


    def display_records(self):
      customer_id = self.customer_id_entry.get()
      password = self.password_entry.get()

      if not customer_id or not password:
         messagebox.showinfo("Error", "Please enter both Customer ID and Password.")
         return

      records = self.query_records(customer_id, password)
      self.record_treeview.delete(*self.record_treeview.get_children())

      if records:
        for record in records:
            self.record_treeview.insert("", tk.END, values=record)
      else:
        self.record_treeview.insert("", tk.END, values=("No Records Found.", "", "", "", "", "", ""))


    def generate_bill(self):
        customer_id = self.customer_id_entry.get()
        records = self.query_records(customer_id)
        self.record_treeview.delete(*self.record_treeview.get_children())

        if records:
            total_price = 0.0
            items = []
            amounts = []

            for record in records:
                self.record_treeview.insert("", tk.END, values=record)
                product_price = float(record[4])
                total_price += product_price
                items.append(record[3])  # Product name
                amounts.append(product_price)  # Product price

            gst = 0.09 * total_price
            product_tax = 0.1 * total_price
            delivery_charge = 100.0
            total_amount = total_price + gst + product_tax + delivery_charge

            bill_frame = tk.Frame(self, bg='#FDFECC', bd=5, relief=tk.RIDGE)
            bill_frame.pack(pady=10)

            bill_label = tk.Label(bill_frame, text="Bill Summary", bg='#FDFECC', fg='#333333', font=("Arial", 16))
            bill_label.pack(pady=10)

            item_frame = tk.Frame(bill_frame, bg='#FDFECC')
            item_frame.pack(pady=10)

            item_label = tk.Label(item_frame, text="Items:", bg='#FDFECC', fg='#333333', font=("Arial", 14))
            item_label.grid(row=0, column=0, padx=5, sticky=tk.W)

            amount_label = tk.Label(item_frame, text="Amount:", bg='#FDFECC', fg='#333333', font=("Arial", 14))
            amount_label.grid(row=0, column=1, padx=5, sticky=tk.W)

            for i in range(len(items)):
                item = tk.Label(item_frame, text=items[i], bg='#FDFECC', fg='#333333', font=("Arial", 12))
                item.grid(row=i + 1, column=0, padx=5, pady=5, sticky=tk.W)

                amount = tk.Label(item_frame, text=f"${amounts[i]}", bg='#FDFECC', fg='#333333', font=("Arial", 12))
                amount.grid(row=i + 1, column=1, padx=5, pady=5, sticky=tk.W)

            total_frame = tk.Frame(bill_frame, bg='#FDFECC')
            total_frame.pack(pady=10)

            total_label = tk.Label(total_frame, text=f"Total Price: ${total_price}", bg='#FDFECC', fg='#333333', font=("Arial", 14))
            total_label.pack(pady=5, anchor=tk.W)

            gst_label = tk.Label(total_frame, text=f"GST (9%): ${gst}", bg='#FDFECC', fg='#333333', font=("Arial", 14))
            gst_label.pack(pady=5, anchor=tk.W)

            tax_label = tk.Label(total_frame, text=f"Product Tax (10%): ${product_tax}", bg='#FDFECC', fg='#333333', font=("Arial", 14))
            tax_label.pack(pady=5, anchor=tk.W)

            delivery_label = tk.Label(total_frame, text="Delivery Charge: $100.0", bg='#FDFECC', fg='#333333', font=("Arial", 14))
            delivery_label.pack(pady=5, anchor=tk.W)

            total_amount_label = tk.Label(total_frame, text=f"Total Amount: ${total_amount}", bg='#FDFECC', fg='#333333', font=("Arial", 14))
            total_amount_label.pack(pady=5, anchor=tk.W)

        else:
            self.record_treeview.insert("", tk.END, values=("No Records Found.", "", "", "", "", "", ""))

    def export_records(self):
        customer_id = self.customer_id_entry.get()
        records = self.query_records(customer_id)

        if records:
            file_path = f"delivery_records_{customer_id}.csv"
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Customer Name", "Customer ID", "Product Name", "Product Price", "Delivery Date", "Ordered Date", "Address"])
                writer.writerows(records)

            messagebox.showinfo("Export Successful", f"Delivery records exported to {file_path} successfully!")
        else:
            messagebox.showinfo("Export Failed", "No records found to export.")

    def sort_records(self):
        sort_column = self.sort_var.get()
        query = f"SELECT * FROM {self.table_name} ORDER BY {sort_column}"
        cursor = self.conn.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()

        self.record_treeview.delete(*self.record_treeview.get_children())
        if records:
            for record in records:
                self.record_treeview.insert("", tk.END, values=record)
        else:
            self.record_treeview.insert("", tk.END, values=("No Records Found.", "", "", "", "", "", ""))

    def filter_records(self):
        filter_text = self.filter_var.get()
        query = f"SELECT * FROM {self.table_name} WHERE customer_id LIKE '%{filter_text}%' OR product_name LIKE '%{filter_text}%' OR delivery_date LIKE '%{filter_text}%'"
        cursor = self.conn.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()

        self.record_treeview.delete(*self.record_treeview.get_children())
        if records:
            for record in records:
                self.record_treeview.insert("", tk.END, values=record)
        else:
            self.record_treeview.insert("", tk.END, values=("No Records Found.", "", "", "", "", "", ""))


if __name__ == "__main__":
    app = DeliveryTracker()
    app.mainloop()
