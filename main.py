import tkinter as tk
from tkinter import ttk
import sqlite3
import pandas as pd
from functools import partial
import os
from tkinter import PhotoImage


def fetch_data(order_by=None, filters=None):
    conn = sqlite3.connect('new.db')
    cursor = conn.cursor()
    query = 'SELECT * FROM STUDENTS'
    if filters:
        conditions = ' AND '.join(filters)
        query += ' WHERE ' + conditions
    if order_by:
        query += f' ORDER BY {order_by}'
    print("Query:", query)  # Print the query for debugging
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["NAME", "CLASS", "SECTION"])
    conn.close()
    return df

# Function to map section data to image paths
def map_section_to_image(section):
    image_path = f"images/{section.upper()}.png"
    if os.path.exists(image_path):
        return image_path
    else:
        return "Unknown"


# Define a dictionary to store PhotoImage objects
section_images = {}


# Fetch and display data
def show_data(order_by=None, filters=None):
    df = fetch_data(order_by, filters)
    for i in tree.get_children():
        tree.delete(i)

    for index, row in df.iterrows():
        name, class_, section = row["NAME"], row["CLASS"], row["SECTION"]
        section_image_path = map_section_to_image(section)
        print("Image Path:", section_image_path)  # Print the image path for debugging

        if section_image_path != "Unknown":
            try:
                if section_image_path not in section_images:
                    # Open the image file and resize it to fit within the Treeview row
                    section_image = PhotoImage(file=section_image_path).subsample(2)
                    section_images[section_image_path] = section_image
                else:
                    section_image = section_images[section_image_path]
                print("Image Object:", section_image)  # Print the image object for debugging
                tree.insert("", "end", values=(name, class_, ""), image=section_image)
            except Exception as e:
                print("Error loading image:", e)  # Print any error that occurs during image loading
                tree.insert("", "end", values=(name, class_, "Image Error"))
        else:
            tree.insert("", "end", values=(name, class_, "Unknown"))

def sort_column(column):
    show_data(order_by=column)

def update_filter(column, event=None):
    filter_text = event.widget.get().strip()  # Get text from the widget that triggered the event
    if filter_text:
        filters[column] = f'{column} LIKE "%{filter_text}%"'
    else:
        if column in filters:
            del filters[column]
    show_data(order_by=None, filters=list(filters.values()))

def on_configure(event):
    # Calculate the width of each filter entry based on the width of the filter frame and the number of columns
    frame_width = filter_frame.winfo_width()
    entry_width = (frame_width - 10) // len(columns)  # Adjust 10 according to your preference
    for entry in filter_entries.values():
        entry.config(width=entry_width)

root = tk.Tk()
root.title("Student Data")

# Set initial window size
root.geometry("800x250")  # Set initial width to 800 pixels and height to 600 pixels

# Dark theme colors
bg_color = "#1E1E1E"
fg_color = "#FFFFFF"
header_color = "#212121"
selected_bg_color = "#37474F"
selected_fg_color = "#FFFFFF"
tree_bg_color = "#37474F"
tree_fg_color = "#FFFFFF"

# Set dark theme colors
root.config(bg=bg_color)
root.tk_setPalette(background=bg_color, foreground=fg_color)

# Create a frame to contain filter widgets
filter_frame = tk.Frame(root, bg=bg_color)
filter_frame.grid(row=0, column=0, columnspan=3, sticky="ew")

# Create Treeview with columns and set height
tree = ttk.Treeview(root, columns=("Name", "Class", "Section"), show="tree headings", selectmode="browse")
tree.heading("Name", text="Name", command=lambda: sort_column("NAME"))
tree.heading("Class", text="Class", command=lambda: sort_column("CLASS"))
tree.heading("Section", text="Section", command=lambda: sort_column("SECTION"))

# Configure column anchor to center the text
tree.column("Name", anchor="center")
tree.column("Class", anchor="center")
tree.column("Section", anchor="center")

tree.grid(row=1, column=0, columnspan=3, sticky="nsew")

# Set Treeview colors
style = ttk.Style()
style.theme_use("clam")  # Use "clam" theme to override default colors
# Set Treeview colors and adjust row height
style.configure("Treeview",
                background=tree_bg_color,
                foreground=tree_fg_color,
                fieldbackground=bg_color,
                rowheight=50)  # Adjust row height to accommodate images
style.map("Treeview",
          background=[("selected", selected_bg_color)],
          foreground=[("selected", selected_fg_color)])

# Set row and column weights for resizing
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)

# Fetch and display data
show_data()

# Create filter entry widgets for each column
filter_entries = {}
filters = {}
placeholders = ["Filter Name", "Filter Class", "Filter Section"]  # Placeholders for filter entries
columns = ["Name", "Class", "Section"]  # Corresponding columns for filter entries
for i, column in enumerate(columns):
    filter_entry = ttk.Entry(filter_frame, width=20)  # Set a default width
    filter_entry.grid(row=1, column=i, sticky="ew")
    filter_entry.insert(0, placeholders[i])  # Insert the placeholder text
    filter_entry.bind("<FocusIn>", lambda event, col_index=i: on_entry_click(event, columns[col_index]))  # Bind event for placeholder behavior
    filter_entry.bind("<FocusOut>", lambda event, col_index=i: on_focus_out(event, columns[col_index]))  # Bind event for placeholder behavior
    filter_entry.bind("<KeyRelease>", lambda event, col=columns[i]: update_filter(col, event))  # Bind event for filtering as you type
    filter_entries[column] = filter_entry

def on_entry_click(event, column):
    """Function to handle placeholder behavior when entry widget gets focus."""
    entry = event.widget
    if entry.get() == placeholders[columns.index(column)]:
        entry.delete(0, "end")
        entry.config(style="Placeholder.TEntry")  # Apply placeholder style when entry gets focus

def on_focus_out(event, column):
    """Function to handle placeholder behavior when entry widget loses focus."""
    entry = event.widget
    if not entry.get():
        entry.insert(0, placeholders[columns.index(column)])
        entry.config(style="Placeholder.TEntry")  # Apply placeholder style when entry loses focus

# Define a placeholder style
style.configure("Placeholder.TEntry", foreground="grey")  # Set the text color to grey for placeholder text

# Set weight for button row to allow resizing
root.grid_rowconfigure(2, weight=0)

# Bind the configure event of the filter frame to adjust the width of the filter entries
filter_frame.bind("<Configure>", on_configure)

# Configure columns in the filter frame to resize proportionally
for i in range(len(columns)):
    filter_frame.grid_columnconfigure(i, weight=1)

root.mainloop()
