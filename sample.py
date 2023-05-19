import tkinter as tk
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

        # Create the GUI components
        self.label = tk.Label(self, text="Enter your Customer ID:", bg='#FDFECC', fg='#333333', font=("Arial", 16))
        self.label.pack()

        self.customer_id_entry = tk.Entry(self, font=("Arial", 14))
        self.customer_id_entry.pack(pady=10)

        self.submit_button = tk.Button(self, text="Submit", command=self.display_records, bg='#009688', fg='white', font=("Arial", 14))
        self.submit_button.pack(pady=20)

        self.record_label = tk.Label(self, text="", bg='#FDFECC', fg='#333333', font=("Arial", 14))
        self.record_label.pack()

    def display_records(self):
        customer_id = self.customer_id_entry.get()

        # Retrieve records based on the customer ID
        records = self.query_records(customer_id)

        if records:
            self.record_label.config(text="Records Found:")
            for record in records:
                self.record_label.config(text=self.record_label.cget("text") + f"\n{record}")
        else:
            self.record_label.config(text="No Records Found.")

    def query_records(self, customer_id):
        query = f"SELECT * FROM {self.table_name} WHERE customer_id = %s"
        cursor = self.conn.cursor()
        cursor.execute(query, (customer_id,))
        records = cursor.fetchall()
        return records


if __name__ == "__main__":
    app = DeliveryTracker()
    app.mainloop()


