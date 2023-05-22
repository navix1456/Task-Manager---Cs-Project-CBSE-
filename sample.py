import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import mysql.connector

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
        self.table_name = "delivery_records"

        self.geometry("800x600")
        self.configure(background='#FDFECC')

        # Load and resize the background image
        bg_image = Image.open(r"C:\Users\lenovo\Downloads\Image-20230515T060830Z-001\Delivery\online-delivery-service-background-concept-e-commerce-concept-red-scooter-smartphone-and-map-pin-illustration-free-vector.jpg")
        bg_image = bg_image.resize((2000, 1000), Image.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(bg_image)

        # Create a label for the background image and place it at the bottom of the stacking order
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)


        # Create the GUI components
        self.label = tk.Label(self, text="Enter your Customer ID:", bg='#FDFECC', fg='#333333', font=("Arial", 16))
        self.label.pack(pady=10)

        self.customer_id_entry = tk.Entry(self, font=("Arial", 14))
        self.customer_id_entry.pack(pady=10)

        self.submit_button = tk.Button(self, text="Submit", command=self.display_records, bg='#009688', fg='white', font=("Arial", 14))
        self.submit_button.pack(pady=20)

        self.record_treeview = ttk.Treeview(self)
        self.record_treeview["columns"] = ("ID", "Customer Name", "Customer ID", "Product Name", "Product Price", "Delivery Date", "Ordered Date","Address")
        self.record_treeview.column("#0", width=0, stretch=tk.NO)
        self.record_treeview.column("ID", anchor=tk.CENTER, width=50)
        self.record_treeview.column("Customer Name", anchor=tk.W, width=120)
        self.record_treeview.column("Customer ID", anchor=tk.CENTER, width=80)
        self.record_treeview.column("Product Name", anchor=tk.W, width=150)
        self.record_treeview.column("Product Price", anchor=tk.E, width=100)
        self.record_treeview.column("Delivery Date", anchor=tk.CENTER, width=100)
        self.record_treeview.column("Ordered Date", anchor=tk.CENTER, width=100)
        self.record_treeview.heading("#0", text="", anchor=tk.W)
        self.record_treeview.heading("ID", text="ID", anchor=tk.CENTER)
        self.record_treeview.heading("Customer Name", text="Customer Name", anchor=tk.W)
        self.record_treeview.heading("Customer ID", text="Customer ID", anchor=tk.CENTER)
        self.record_treeview.heading("Product Name", text="Product Name", anchor=tk.W)
        self.record_treeview.heading("Product Price", text="Product Price", anchor=tk.E)
        self.record_treeview.heading("Delivery Date", text="Delivery Date", anchor=tk.CENTER)
        self.record_treeview.heading("Ordered Date", text="Ordered Date", anchor=tk.CENTER)
        self.record_treeview.heading("Address", text="Address")
        self.record_treeview.pack(pady=10)

        # Load the delivery box logo image and resize it
        logo_image = Image.open(r"C:\Users\lenovo\Downloads\logo-removebg-preview.png")
        logo_image = logo_image.resize((100, 100))  # Adjust the size as needed
        self.logo_image = ImageTk.PhotoImage(logo_image)

        # Create a label for the logo and place it at the top left corner
        self.logo_label = tk.Label(self, image=self.logo_image, bg='#D3D3D3')
        self.logo_label.place(x=0, y=0)

    def display_records(self):
        customer_id = self.customer_id_entry.get()

        # Retrieve records based on the customer ID
        records = self.query_records(customer_id)

        # Clear previous records from the Treeview
        self.record_treeview.delete(*self.record_treeview.get_children())

        if records:
            total_price = 0.0
            for record in records:
                self.record_treeview.insert("", tk.END, values=record)
                product_price = float(record[4])
                total_price += product_price

            gst = 0.09 * total_price  # Calculate GST (9% of the total price)
            product_tax = 0.1 * total_price  # Calculate product tax (10% of the total price)
            delivery_charge = 100.0  # Delivery charge
            total_amount = total_price + gst + product_tax + delivery_charge

            # Display the bill
            bill_treeview = ttk.Treeview(self)
            bill_treeview["columns"] = ("Item", "Amount")
            bill_treeview.column("#0", width=0, stretch=tk.NO)
            bill_treeview.column("Item", anchor=tk.W, width=200)
            bill_treeview.column("Amount", anchor=tk.E, width=100)
            bill_treeview.heading("#0", text="", anchor=tk.W)
            bill_treeview.heading("Item", text="Item", anchor=tk.W)
            bill_treeview.heading("Amount", text="Amount", anchor=tk.E)
            bill_treeview.pack(pady=10)

            bill_treeview.insert("", tk.END, values=("Product Price", f"{total_price:.2f}"))
            bill_treeview.insert("", tk.END, values=("GST (9%)", f"{gst:.2f}"))
            bill_treeview.insert("", tk.END, values=("Product Tax (10%)", f"{product_tax:.2f}"))
            bill_treeview.insert("", tk.END, values=("Delivery Charge", f"{delivery_charge:.2f}"))
            bill_treeview.insert("", tk.END, values=("Total Amount", f"{total_amount:.2f}"))
        else:
            self.record_treeview.insert("", tk.END, values=("No Records Found.", "", "", "", "", "", ""))

    def query_records(self, customer_id):
        query = f"SELECT id, customer_name, customer_id, product_name, product_price, delivery_date, ordered_date, Address FROM {self.table_name} WHERE customer_id = %s"
        cursor = self.conn.cursor()
        cursor.execute(query, (customer_id,))
        records = cursor.fetchall()
        return records


if __name__ == "__main__":
    app = DeliveryTracker()
    app.mainloop()
