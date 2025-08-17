import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient

# ----------------- MongoDB Connection -----------------
client = MongoClient("mongodb://localhost:27017/")
db = client["car_database"]
collection = db["spare_parts"]

# ----------------- Colors & Styles -----------------
BG_COLOR = "#f4f6f8"        # Light background
HEADER_COLOR = "#2c3e50"    # Dark professional header
SIDEBAR_COLOR = "#34495e"   # Sidebar background
BTN_COLOR = "#1abc9c"       # Green buttons
BTN_HOVER = "#16a085"       # Hover green
ENTRY_BG = "#ffffff"
FONT = ("Segoe UI", 10)

# ----------------- Functions -----------------
def create_part():
    part = get_form_data()
    if not all(part.values()):
        messagebox.showerror("Error", "All fields are required.")
        return
    if collection.find_one({"part_id": part["part_id"]}):
        messagebox.showerror("Error", "Part with this ID already exists.")
        return
    try:
        part["price"] = float(part["price"])
        part["stock"] = int(part["stock"])
    except ValueError:
        messagebox.showerror("Error", "Price must be a number and Stock must be an integer.")
        return

    collection.insert_one(part)
    messagebox.showinfo("Success", "Spare part added successfully!")
    clear_entries()
    read_parts()

def read_parts():
    listbox.delete(0, tk.END)
    for part in collection.find():
        listbox.insert(
            tk.END,
            f"{part['part_id']} | {part['name']} | {part['car_model']} | Rs.{part['price']} | Stock: {part['stock']}"
        )

def update_part():
    part_id = entry_id.get()
    if not part_id:
        messagebox.showerror("Error", "Part ID is required for update.")
        return

    updated = get_form_data()
    try:
        updated["price"] = float(updated["price"])
        updated["stock"] = int(updated["stock"])
    except ValueError:
        messagebox.showerror("Error", "Price must be a number and Stock must be an integer.")
        return

    result = collection.update_one({"part_id": part_id}, {"$set": updated})
    if result.modified_count > 0:
        messagebox.showinfo("Success", "Spare part updated successfully!")
    else:
        messagebox.showwarning("Warning", "No changes made or Part not found.")
    clear_entries()
    read_parts()

def delete_part():
    part_id = entry_id.get()
    if not part_id:
        messagebox.showerror("Error", "Part ID is required for deletion.")
        return
    result = collection.delete_one({"part_id": part_id})
    if result.deleted_count > 0:
        messagebox.showinfo("Success", "Spare part deleted successfully!")
    else:
        messagebox.showwarning("Warning", "Part not found.")
    clear_entries()
    read_parts()

def clear_entries():
    for entry in (entry_id, entry_name, entry_model, entry_price, entry_stock):
        entry.delete(0, tk.END)

def get_form_data():
    return {
        "part_id": entry_id.get().strip(),
        "name": entry_name.get().strip(),
        "car_model": entry_model.get().strip(),
        "price": entry_price.get().strip(),
        "stock": entry_stock.get().strip()
    }

def on_listbox_select(event):
    selection = listbox.curselection()
    if selection:
        index = selection[0]
        data = listbox.get(index).split(" | ")
        clear_entries()
        entry_id.insert(0, data[0])
        entry_name.insert(0, data[1])
        entry_model.insert(0, data[2])
        entry_price.insert(0, data[3].replace("Rs.", ""))
        entry_stock.insert(0, data[4].replace("Stock: ", ""))

# ----------------- UI Setup -----------------
root = tk.Tk()
root.title("Car Spare Part Management")
root.geometry("800x600")
root.config(bg=BG_COLOR)

# Header
header = tk.Label(root, text="🚗 Car Spare Part Management", bg=HEADER_COLOR, fg="white",
                  font=("Segoe UI", 14, "bold"), pady=10)
header.pack(fill="x")

# Layout: Sidebar + Main Content
main_frame = tk.Frame(root, bg=BG_COLOR)
main_frame.pack(fill="both", expand=True)

# Sidebar
sidebar = tk.Frame(main_frame, bg=SIDEBAR_COLOR, width=150)
sidebar.pack(side="left", fill="y")

def on_enter(e): e.widget['bg'] = BTN_HOVER
def on_leave(e): e.widget['bg'] = BTN_COLOR

def create_sidebar_btn(text, cmd):
    btn = tk.Button(sidebar, text=text, command=cmd, bg=BTN_COLOR, fg="white",
                    font=("Segoe UI", 10, "bold"), relief="flat", pady=10, width=15)
    btn.pack(pady=5)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

create_sidebar_btn("Add Part", create_part)
create_sidebar_btn("View Parts", read_parts)
create_sidebar_btn("Update Part", update_part)
create_sidebar_btn("Delete Part", delete_part)
create_sidebar_btn("Clear Fields", clear_entries)

# Main Content Area
content = tk.Frame(main_frame, bg=BG_COLOR, padx=20, pady=20)
content.pack(side="left", fill="both", expand=True)

# Form
form_frame = tk.LabelFrame(content, text="Part Details", bg=BG_COLOR, fg=HEADER_COLOR, font=("Segoe UI", 11, "bold"))
form_frame.pack(fill="x", pady=10)

def create_label_entry(frame, text):
    row = tk.Frame(frame, bg=BG_COLOR)
    row.pack(anchor="w", pady=5)
    label = tk.Label(row, text=text, bg=BG_COLOR, fg=HEADER_COLOR, font=FONT, width=20, anchor="w")
    label.pack(side="left")
    entry = tk.Entry(row, bg=ENTRY_BG, fg=HEADER_COLOR, font=FONT, width=30)
    entry.pack(side="left", ipady=3)
    return entry

entry_id = create_label_entry(form_frame, "Part ID")
entry_name = create_label_entry(form_frame, "Part Name")
entry_model = create_label_entry(form_frame, "Compatible Car Model")
entry_price = create_label_entry(form_frame, "Price")
entry_stock = create_label_entry(form_frame, "Stock Quantity")

# Listbox with Scrollbar
list_frame = tk.LabelFrame(content, text="Available Parts", bg=BG_COLOR, fg=HEADER_COLOR, font=("Segoe UI", 11, "bold"))
list_frame.pack(fill="both", expand=True, pady=10)

scrollbar = tk.Scrollbar(list_frame)
scrollbar.pack(side="right", fill="y")

listbox = tk.Listbox(list_frame, width=80, height=15, bg="#ffffff", fg=HEADER_COLOR,
                     font=FONT, selectbackground="#a3e4d7", selectforeground="#000000",
                     yscrollcommand=scrollbar.set)
listbox.pack(fill="both", expand=True, padx=5, pady=5)
scrollbar.config(command=listbox.yview)

listbox.bind("<<ListboxSelect>>", on_listbox_select)

# Initial Load
read_parts()

root.mainloop()
