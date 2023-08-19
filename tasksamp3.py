import tkinter as tk
from tkinter import ttk
import mysql.connector
from ttkthemes import ThemedStyle
from PIL import Image, ImageTk  # Import Image and ImageTk from PIL library
import csv
from tkinter import simpledialog
from tkcalendar import DateEntry
import tkinter.messagebox as messagebox
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib.styles import getSampleStyleSheet


# Create the main application window
root = tk.Tk()
root.title("Task Manager")

# Replace these values with your MySQL credentials
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "navin123457"
MYSQL_DATABASE = "task_manager"


def create_task():
    title = title_entry.get()
    description = description_entry.get("1.0", "end-1c")
    due_date = due_date_entry.get()
    priority = int(priority_var.get())
    status = status_var.get()
    

    # Connect to MySQL database
    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

    # Insert task into the database
    cursor = connection.cursor()
    query = "INSERT INTO tasks (date_added, title, description, due_date, priority, status) VALUES (NOW(), %s, %s, %s, %s, %s)"
    values = (title, description, due_date, priority, status)
    cursor.execute(query, values)
    connection.commit()
    

    # Update task list
    update_task_list()
    
    
    # Clear input fields
    title_entry.delete(0, tk.END)
    description_entry.delete("1.0", tk.END)
    due_date_entry.delete(0, tk.END)
    

def update_task_list():
    # Clear existing tasks from the treeview
    for item in task_tree.get_children():
        task_tree.delete(item)

    # Fetch tasks from the database
    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

    cursor = connection.cursor()
    query = "SELECT id, date_added, title, description, due_date, priority, status FROM tasks ORDER BY priority DESC"
    cursor.execute(query)
    tasks = cursor.fetchall()
    

    # Insert tasks into the treeview
    for task in tasks:
        task_tree.insert("", "end", values=task)
        

def delete_task():
    selected_item = task_tree.selection()
    if not selected_item:
        return

    # Get the task id of the selected item
    task_id = task_tree.item(selected_item)['values'][0]
    

    # Connect to the database
    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

    cursor = connection.cursor()
    query = "DELETE FROM tasks WHERE id = %s"
    cursor.execute(query, (task_id,))
    connection.commit()
    

    # Update task list after deletion
    update_task_list()
    


    

def search_task():
    keyword = search_entry.get()
    priority = int(priority_var_search.get())

    # Connect to the database
    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

    cursor = connection.cursor()

    # Search tasks based on keyword and priority
    query = "SELECT id, date_added, title, description, due_date, priority, status FROM tasks WHERE title LIKE %s AND priority = %s ORDER BY priority DESC"
    cursor.execute(query, (f"%{keyword}%", priority))
    tasks = cursor.fetchall()
    

    # Clear existing tasks from the treeview
    for item in task_tree.get_children():
        task_tree.delete(item)
        

    # Insert searched tasks into the treeview
    for task in tasks:
        task_tree.insert("", "end", values=task)
        

def clear_search():
    search_entry.delete(0, tk.END)
    priority_var_search.set(0)
    update_task_list()


def fetch_tasks_from_database():
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        # Fetch tasks from the database
        cursor = connection.cursor()
        query = "SELECT id, date_added, title, description, due_date, priority, status FROM tasks ORDER BY priority DESC"
        cursor.execute(query)
        tasks = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        return tasks

    except mysql.connector.Error as e:
        print(f"Error fetching tasks from the database: {e}")
        return []



def export_to_csv():
    tasks = fetch_tasks_from_database()

    # Convert the list of tuples to a list of dictionaries
    task_dicts = []
    for task in tasks:
        task_dict = {
            "ID": task[0],
            "Date Added": task[1],
            "Title": task[2],
            "Description": task[3],
            "Due Date": task[4],
            "Priority": task[5],
            "Status": task[6]
        }
        task_dicts.append(task_dict)

    # Write the list of dictionaries to CSV
    with open("task_manager_export.csv", "w", newline="") as csvfile:
        fieldnames = ["ID", "Date Added", "Title", "Description", "Due Date", "Priority", "Status"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(task_dicts)

def update_task_status(task_id, new_status):
    # Connect to MySQL database
    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

    # Update task status in the database
    cursor = connection.cursor()
    query = "UPDATE tasks SET status = %s WHERE id = %s"
    values = (new_status, task_id)
    cursor.execute(query, values)
    connection.commit()

    # Close the cursor and connection
    cursor.close()
    connection.close()

# ... (your existing code for creating the task_tree)

def mark_as_completed():
    selected_item = task_tree.selection()
    if not selected_item:
        return

    task_id = task_tree.item(selected_item)['values'][0]
    update_task_status(task_id, "Completed")
    update_task_list()

def show_date_picker():
    selected_date = DateEntry(root, date_pattern="yyyy-mm-dd")
    selected_date.grid(row=2, column=2, padx=5, pady=5)
    
    def set_selected_date():
        due_date_entry.delete(0, tk.END)
        due_date_entry.insert(0, selected_date.get())
        selected_date.grid_forget()
    
    ok_button = tk.Button(root, text="OK", command=set_selected_date)
    ok_button.grid(row=2, column=3, padx=5, pady=5)




def calendar_dialog():
    cal = calendar.Calendar()
    selected_date = None

    def set_selected_date(date):
        nonlocal selected_date
        selected_date = date
        calendar_popup.destroy()

    calendar_popup = tk.Toplevel(root)
    calendar_popup.title("Select Due Date")

    year = tk.StringVar()
    month = tk.StringVar()

    year_combobox = ttk.Combobox(calendar_popup, textvariable=year, values=list(range(2021, 2030)))
    year_combobox.set(str(tk.datetime.now().year))
    year_combobox.grid(row=0, column=0, padx=5, pady=5)

    month_combobox = ttk.Combobox(calendar_popup, textvariable=month, values=list(calendar.month_abbr)[1:])
    month_combobox.set(calendar.month_abbr[tk.datetime.now().month])
    month_combobox.grid(row=0, column=1, padx=5, pady=5)

    def update_calendar():
        cal_frame.destroy()
        cal_frame.grid(row=1, columnspan=2)

    def select_date(date):
        selected_date = f"{date}-{month.get()}-{year.get()}"
        set_selected_date(selected_date)

    cal_frame = ttk.Frame(calendar_popup)
    cal_frame.grid(row=1, columnspan=2)

    for week in cal.monthdayscalendar(int(year.get()), list(calendar.month_abbr).index(month.get())):
        for day in week:
            if day == 0:
                ttk.Label(cal_frame, text=" ").grid()
            else:
                ttk.Button(cal_frame, text=str(day), command=lambda day=day: select_date(day)).grid()

    update_button = tk.Button(calendar_popup, text="Update", command=update_calendar)
    update_button.grid(row=0, column=2)

    return selected_date

def delete_task():
    selected_item = task_tree.selection()
    if not selected_item:
        return
    
    # Ask for confirmation
    confirmation = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this task?")
    if confirmation:
        # Get the task id of the selected item
        task_id = task_tree.item(selected_item)['values'][0]
    
        # Connect to the database
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
    
        cursor = connection.cursor()
        query = "DELETE FROM tasks WHERE id = %s"
        cursor.execute(query, (task_id,))
        connection.commit()
    
        # Update task list after deletion
        update_task_list()
        

root.bind("<Control-d>", delete_task)



def mark_as_completed():
    selected_item = task_tree.selection()
    if not selected_item:
        return
    
    # Ask for confirmation
    confirmation = messagebox.askyesno("Confirm Mark as Completed", "Are you sure you want to mark this task as completed?")
    if confirmation:
        task_id = task_tree.item(selected_item)['values'][0]
        update_task_status(task_id, "Completed")
        update_task_list()

root.bind("<Control-c>", mark_as_completed)


def export_to_pdf():
    tasks = fetch_tasks_from_database()

    # Create a PDF document
    doc = SimpleDocTemplate("task_manager_export.pdf", pagesize=letter)
    elements = []

    # Create a table to hold task data
    data = [
        ["ID", "Date Added", "Title", "Description", "Due Date", "Priority", "Status"]
    ]
    for task in tasks:
        data.append(task)

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Add the table to the PDF document
    elements.append(table)

    # Build the PDF document
    doc.build(elements)


def display_statistics():
    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

    cursor = connection.cursor()
    query = "SELECT COUNT(*) FROM tasks"
    cursor.execute(query)
    total_tasks = cursor.fetchone()[0]

    query = "SELECT COUNT(*) FROM tasks WHERE status = 'Completed'"
    cursor.execute(query)
    completed_tasks = cursor.fetchone()[0]

    query = "SELECT COUNT(*) FROM tasks WHERE status = 'In Progress'"
    cursor.execute(query)
    in_progress_tasks = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    statistics_text = f"Total Tasks: {total_tasks}\nCompleted Tasks: {completed_tasks}\nIn Progress Tasks: {in_progress_tasks}"
    messagebox.showinfo("Task Statistics", statistics_text)



def edit_selected_task():
    selected_item = task_tree.selection()
    if not selected_item:
        return

    task_id = task_tree.item(selected_item)['values'][0]

    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

    cursor = connection.cursor()
    query = "SELECT * FROM tasks WHERE id = %s"
    cursor.execute(query, (task_id,))
    task_data = cursor.fetchone()
    cursor.close()
    connection.close()

    if task_data:
        # Open a dialog box for editing task fields
        edit_dialog = tk.Toplevel(root)
        edit_dialog.title("Edit Task")

        # Create and place input fields for each task attribute
        tk.Label(edit_dialog, text="Title:").grid(row=0, column=0, padx=5, pady=5)
        title_entry_edit = tk.Entry(edit_dialog)
        title_entry_edit.insert(0, task_data[2])
        title_entry_edit.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(edit_dialog, text="Description:").grid(row=1, column=0, padx=5, pady=5)
        description_text_edit = tk.Text(edit_dialog, height=5, width=30)
        description_text_edit.insert("1.0", task_data[3])
        description_text_edit.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(edit_dialog, text="Due Date:").grid(row=2, column=0, padx=5, pady=5)
        due_date_entry_edit = tk.Entry(edit_dialog)
        due_date_entry_edit.insert(0, task_data[4])
        due_date_entry_edit.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(edit_dialog, text="Priority:").grid(row=3, column=0, padx=5, pady=5)
        priority_var_edit = tk.StringVar(edit_dialog)
        priority_combobox_edit = ttk.Combobox(edit_dialog, textvariable=priority_var_edit, values=[1, 2, 3])
        priority_combobox_edit.set(task_data[5])
        priority_combobox_edit.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(edit_dialog, text="Status:").grid(row=4, column=0, padx=5, pady=5)
        status_var_edit = tk.StringVar(edit_dialog)
        status_combobox_edit = ttk.Combobox(edit_dialog, textvariable=status_var_edit,
                                            values=["Not Started", "In Progress", "Completed"])
        status_combobox_edit.set(task_data[6])
        status_combobox_edit.grid(row=4, column=1, padx=5, pady=5)

        # Update the task when "Save" button is clicked
        def save_edited_task():
            new_title = title_entry_edit.get()
            new_description = description_text_edit.get("1.0", tk.END)
            new_due_date = due_date_entry_edit.get()
            new_priority = priority_var_edit.get()
            new_status = status_var_edit.get()

            connection = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE
            )

            cursor = connection.cursor()
            query = "UPDATE tasks SET title=%s, description=%s, due_date=%s, priority=%s, status=%s WHERE id=%s"
            cursor.execute(query, (new_title, new_description, new_due_date, new_priority, new_status, task_id))
            connection.commit()
            cursor.close()
            connection.close()

            edit_dialog.destroy()  # Close the edit dialog
            update_task_list()  # Update the task list in the main window

        # Add a "Save" button to save the edited task
        save_button = tk.Button(edit_dialog, text="Save", command=save_edited_task)
        save_button.grid(row=5, columnspan=2, padx=5, pady=10)







# Apply the themed style
style = ThemedStyle(root)
style.set_theme("plastik")  # Choose the "plastik" theme


# Set custom fonts
font_title = ("Helvetica", 18, "bold")
font_label = ("Helvetica", 12)
font_button = ("Helvetica", 12, "bold")


# Center the window on the screen
window_width = 800
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Load and set the background image
background_image = Image.open("Untitled design (6).jpg")
background_image = ImageTk.PhotoImage(background_image)
background_label = tk.Label(root, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)




# Task Input Section

input_frame = ttk.Frame(root)
input_frame.place(relx=0.5, rely=0.1, anchor=tk.CENTER)


title_label = tk.Label(root, text="Title:")
title_label.grid(row=0, column=0, padx=5, pady=5)
title_entry = tk.Entry(root)
title_entry.grid(row=0, column=1, padx=5, pady=5)


description_label = tk.Label(root, text="Description:")
description_label.grid(row=1, column=0, padx=5, pady=5)
description_entry = tk.Text(root, height=5, width=30)
description_entry.grid(row=1, column=1, padx=5, pady=5)


due_date_label = tk.Label(root, text="Due Date:")
due_date_label.grid(row=2, column=0, padx=5, pady=5)
due_date_entry = tk.Entry(root)
due_date_entry.grid(row=2, column=1, padx=5, pady=5)


priority_label = tk.Label(root, text="Priority:")
priority_label.grid(row=3, column=0, padx=5, pady=5)
priority_var = tk.StringVar(root)
priority_combobox = ttk.Combobox(root, textvariable=priority_var, values=[1, 2, 3])
priority_combobox.grid(row=3, column=1, padx=5, pady=5)


status_label = tk.Label(root, text="Status:")
status_label.grid(row=4, column=0, padx=5, pady=5)
status_var = tk.StringVar(root)
status_combobox = ttk.Combobox(root, textvariable=status_var, values=["Not Started", "In Progress", "Completed"])
status_combobox.grid(row=4, column=1, padx=5, pady=5)


add_button = tk.Button(root, text="Add Task", command=create_task)
add_button.grid(row=5, column=0, columnspan=2, padx=5, pady=10)


mark_as_completed_button = tk.Button(root, text="Mark as Completed", command=mark_as_completed)
mark_as_completed_button.grid(row=7, column=1, padx=5, pady=5)

date_picker_button = tk.Button(root, text="Select Due Date", command=show_date_picker)
date_picker_button.grid(row=2, column=2, padx=5, pady=5)

# Add a button to export tasks to PDF
export_pdf_button = tk.Button(root, text="Export to PDF", command=export_to_pdf)
export_pdf_button.grid(row=12, column=0, padx=5, pady=5)

#show statistics
stats_button = tk.Button(root, text="Show Statistics", command=display_statistics)
stats_button.grid(row=13, column=2, padx=5, pady=5)

# Add "Edit Task" Button
edit_task_button = tk.Button(root, text="Edit Task", command=edit_selected_task)
edit_task_button.grid(row=14, column=1, padx=5, pady=5)







# Task List View Section

list_frame = ttk.Frame(root)
list_frame.place(relx=0.5, rely=0.35, anchor=tk.CENTER)


task_tree = ttk.Treeview(root, columns=("ID", "Date Added", "Title", "Description", "Due Date", "Priority", "Status"))
task_tree.heading("#1", text="ID")
task_tree.heading("#2", text="Date Added")
task_tree.heading("#3", text="Title")
task_tree.heading("#4", text="Description")
task_tree.heading("#5", text="Due Date")
task_tree.heading("#6", text="Priority")
task_tree.heading("#7", text="Status")
task_tree.column("#1", anchor="center", width=40)
task_tree.column("#2", anchor="center", width=80)
task_tree.column("#3", anchor="w", width=120)
task_tree.column("#4", anchor="w", width=200)
task_tree.column("#5", anchor="center", width=80)
task_tree.column("#6", anchor="center", width=60)
task_tree.column("#7", anchor="center", width=100)
task_tree.grid(row=6, column=0, columnspan=2, padx=5, pady=5)


# Task Deletion Buttons
delete_button = tk.Button(root, text="Delete Task", command=delete_task)
delete_button.grid(row=7, column=0, padx=5, pady=5)





# Search Functionality Section
search_frame = ttk.Frame(root)
search_frame.place(relx=0.5, rely=0.92, anchor=tk.CENTER)



search_label = tk.Label(root, text="Search Keyword:")
search_label.grid(row=8, column=0, padx=5, pady=5)
search_entry = tk.Entry(root)
search_entry.grid(row=8, column=1, padx=5, pady=5)



priority_label_search = tk.Label(root, text="Priority:")
priority_label_search.grid(row=9, column=0, padx=5, pady=5)
priority_var_search = tk.StringVar(root)
priority_combobox_search = ttk.Combobox(root, textvariable=priority_var_search, values=[0, 1, 2, 3])
priority_combobox_search.grid(row=9, column=1, padx=5, pady=5)



search_button = tk.Button(root, text="Search", command=search_task)
search_button.grid(row=10, column=0, columnspan=2, padx=5, pady=5)



clear_search_button = tk.Button(root, text="Clear Search", command=clear_search)
clear_search_button.grid(row=11, column=0, columnspan=2, padx=5, pady=5)

#export csv
export_csv_button = tk.Button(root, text="Export to CSV", command=export_to_csv)
export_csv_button.grid(row=12, column=0, columnspan=2, padx=5, pady=5)







# Delete Task Shortcut (Ctrl + D)
def delete_selected(event):
    delete_task()

root.bind("<Control-d>", delete_selected)

# Mark as Completed Shortcut (Ctrl + C)
def mark_completed(event):
    mark_as_completed()

root.bind("<Control-c>", mark_completed)

# Set window icon
window_icon = Image.open("download (1).png")
window_icon = ImageTk.PhotoImage(window_icon)
root.iconphoto(True, window_icon)



# Set window icon
window_icon = Image.open("download (1).png")
window_icon = ImageTk.PhotoImage(window_icon)
root.iconphoto(True, window_icon)


# Set window background color
root.configure(bg="#f0f0f0")


# Update task list when the application starts
update_task_list()

root.mainloop()
