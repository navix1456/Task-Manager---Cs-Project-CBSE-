import tkinter as tk
from tkinter import ttk
import mysql.connector
from ttkthemes import ThemedStyle
from PIL import Image, ImageTk  # Import Image and ImageTk from PIL library



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
    

def edit_task():
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
    query = "SELECT title, description, due_date, priority, status FROM tasks WHERE id = %s"
    cursor.execute(query, (task_id,))
    task_data = cursor.fetchone()
    

    # Set the task data to the input fields for editing
    title_entry.delete(0, tk.END)
    title_entry.insert(0, task_data[0])
    

    description_entry.delete("1.0", tk.END)
    description_entry.insert("1.0", task_data[1])
    

    due_date_entry.delete(0, tk.END)
    due_date_entry.insert(0, task_data[2])
    

    priority_var.set(task_data[3])
    status_var.set(task_data[4])
    

    # Update the task list after editing
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
    

# Create the main application window
root = tk.Tk()
root.title("Task Manager")


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
background_image = Image.open("event-management-wedding-planner-online-manager-planning-event-conference-or-party-professional-organizer-schedule-modern-flat-cartoon-style-illustration-on-white-background-vector.jpg")
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


# Task Deletion and Edit Buttons
delete_button = tk.Button(root, text="Delete Task", command=delete_task)
delete_button.grid(row=7, column=0, padx=5, pady=5)


edit_button = tk.Button(root, text="Edit Task", command=edit_task)
edit_button.grid(row=7, column=1, padx=5, pady=5)


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



# Set window icon
window_icon = Image.open("download (1).png")
window_icon = ImageTk.PhotoImage(window_icon)
root.iconphoto(True, window_icon)


# Set window background color
root.configure(bg="#f0f0f0")


# Update task list when the application starts
update_task_list()

root.mainloop()
