import hashlib
import secrets
import tkinter as tk
from tkinter import simpledialog, messagebox
import mysql.connector

class Shop:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ShopDB"
        )
        self.cursor = self.connection.cursor()
        self.shopping_cart = []
        self.load_products()

    def load_products(self):
        self.cursor.execute("SELECT name, price, quantity FROM Products")
        rows = self.cursor.fetchall()
        self.products = {row[0]: {"price": row[1], "quantity": row[2]} for row in rows}

    def display_available_products(self):
        available_products = "Available Products:\n"
        return available_products
    
    def display_available_productss(self):
        available_productss = ""
        for product, info in self.products.items():
            available_productss += f"{product.capitalize()}: ${info['price']}, Quantity Available: {info['quantity']}\n"
        return available_productss

    def add_to_cart(self, item, quantity):
        if item in self.products:
            if self.products[item]["quantity"] >= quantity:
                self.shopping_cart.append({"item": item, "quantity": quantity})
                self.products[item]["quantity"] -= quantity
                self._update_product_quantity(item)
                return f"{quantity} {item.capitalize()}{'s' if quantity > 1 else ''} added to your cart."
            else:
                return f"Sorry, we only have {self.products[item]['quantity']} {item.capitalize()}{'s' if self.products[item]['quantity'] == 1 else ''} in stock."
        else:
            return "Invalid product. Please choose from the available products."

    
    def _update_product_quantity(self, item):
        new_quantity = self.products[item]["quantity"]
        self.cursor.execute("UPDATE Products SET quantity = %s WHERE name = %s", (new_quantity, item))
        self.connection.commit()


    def checkout(self):
        total_cost = sum(self.products[item["item"]]["price"] * item["quantity"] for item in self.shopping_cart)
        receipt = "\nYour Shopping Cart:\n"
        for item in self.shopping_cart:
            receipt += f"{item['quantity']} {item['item'].capitalize()}{'s' if item['quantity'] > 1 else ''}\n"
        receipt += f"Total Cost: ${total_cost:.2f}\n\nThank you for shopping with us!"
        return receipt

class Admin:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ShopDB"
        )
        self.cursor = self.connection.cursor()
        self.admin_salt = secrets.token_hex(16)
        self.admin_hashed_password = self._hash_password("123")

    def _hash_password(self, password):
        hashed_password = hashlib.sha256((password + self.admin_salt).encode()).hexdigest()
        return hashed_password

    def check_password(self, password):
        hashed_password = self._hash_password(password)
        return hashed_password == self.admin_hashed_password

    def change_password(self, new_password):
        self.admin_hashed_password = self._hash_password(new_password)
        messagebox.showinfo("Password Changed", "Password changed successfully.")

    def add_new_product(self, shop, new_product_name, new_product_price, new_product_quantity):
        try:
            self.cursor.execute("INSERT INTO Products (name, price, quantity) VALUES (%s, %s, %s)",
                                (new_product_name, new_product_price, new_product_quantity))
            self.connection.commit()
            shop.load_products()  # Reload products after adding a new one
            messagebox.showinfo("Product Added", f"{new_product_name.capitalize()} has been added to the system.")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error: {err}")

def admin_login():
    password = simpledialog.askstring("Admin Login", "Enter the admin password:", show='*')
    if password is None:
        return
    if admin.check_password(password):
        admin_options()
    else:
        messagebox.showerror("Error", "Incorrect password. Access denied.")

def admin_options():
    admin_options_window = tk.Toplevel()
    admin_options_window.title("Admin Options")

    # Set the window size to laptop screen size
    admin_options_window.geometry("1366x768")

    admin_options_window.configure(bg="#eccea5")
    
    # Create a frame for the buttons
    button_frame = tk.Frame(admin_options_window, bg="#eccea5", padx=10, pady=10)
    button_frame.pack(pady=(20, 10))

    # Create a label inside the frame
    hell_label = tk.Label(button_frame, text="PLEASE CHOOSE YOUR OPTION FORMART:", font=("Arial", 16), bg="#eccea5")  
    hell_label.pack(pady=(10, 10))

    # Button for adding a new product
    new_product_button = tk.Button(button_frame, text="Add New Product", command= lambda: add_new_product(admin_options_window), font=("Arial", 12), bg="lightgreen", cursor="hand2")
    new_product_button.pack(pady=(10, 50))

    # Button for changing the password
    change_password_button = tk.Button(button_frame, text="Change Password", command=change_password, font=("Arial", 12), bg="lightgreen", cursor="hand2")
    change_password_button.pack(pady=(10, 0))

    # Optional: Bind events for hover effects
    new_product_button.bind("<Enter>", lambda e: on_enter(e, new_product_button))
    new_product_button.bind("<Leave>", lambda e: on_leave(e, new_product_button))

    change_password_button.bind("<Enter>", lambda e: on_enter(e, change_password_button))
    change_password_button.bind("<Leave>", lambda e: on_leave(e, change_password_button))

def add_new_product(parent_window):
    # Create a new Toplevel window for adding a product
    product_window = tk.Toplevel(parent_window)
    product_window.title("Add New Product")
    product_window.geometry("1366x768")  # Adjust size as needed
    product_window.configure(bg="#eccea5")

    # Create and display product name label and entry
    name_label = tk.Label(product_window, text="Enter the name of the new product:", font=("Arial", 12), bg="#eccea5")
    name_label.pack(pady=(10, 10))

    name_entry = tk.Entry(product_window, font=("Arial", 12))
    name_entry.pack(pady=(5, 10))

    # Create and display price label and entry
    price_label = tk.Label(product_window, text="Enter the price of the product:", font=("Arial", 12), bg="#eccea5")
    price_label.pack(pady=(10, 10))

    price_entry = tk.Entry(product_window, font=("Arial", 12))
    price_entry.pack(pady=(5, 10))

    # Create and display quantity label and entry
    quantity_label = tk.Label(product_window, text="Enter the initial quantity:", font=("Arial", 12), bg="#eccea5")
    quantity_label.pack(pady=(10, 0))

    quantity_entry = tk.Entry(product_window, font=("Arial", 12))
    quantity_entry.pack(pady=(5, 10))

    # Function to handle adding the new product
    def submit_product():
        name = name_entry.get().strip()
        price_str = price_entry.get().strip()
        quantity_str = quantity_entry.get().strip()

        if not name or not price_str or not quantity_str:
            messagebox.showerror("Error", "Please fill in all fields!")
            return

        try:
            price = float(price_str)
            quantity = int(quantity_str)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for price and quantity!")
            return

        admin.add_new_product(shop, name.lower(), price, quantity)
        messagebox.showinfo("Success", f"Product '{name}' added successfully!")
        product_window.destroy()  # Close the product window after adding
        parent_window.destroy()

    # Button to submit the product
    add_button = tk.Button(product_window, text="Add Product", command=submit_product, font=("Arial", 12), bg="lightgreen", cursor="hand2")
    add_button.pack(pady=(20, 0))
    

def change_password():
    new_password = simpledialog.askstring("Change Password", "Enter new admin password:", show='*')
    if new_password is None:
        return
    admin.change_password(new_password)

def customer_login(parent_window):
    # Create and display available products label
    products_label = tk.Label(parent_window, text=shop.display_available_products(), font=("Arial Black", 18), bg="#eccea5")
    products_label.pack(pady=(5, 0))

    products_label = tk.Label(parent_window, text=shop.display_available_productss(), font=("Arial", 14), bg="#eccea5")
    products_label.pack(pady=(0, 15), fill=tk.X)

    # Create a frame to hold the label and entry
    entry_frame = tk.Frame(parent_window, bg="#eccea5")
    entry_frame.pack(pady=(10, 10), fill=tk.X)

    # Label for product entry
    product_label = tk.Label(entry_frame, text="Enter the product you want to add to your cart:", font=("Arial", 12), bg="#eccea5")
    product_label.pack(side=tk.LEFT, fill=tk.X, padx=(25, 0))  # Pack label to the left

    # Entry for product choice
    product_entry = tk.Entry(entry_frame, font=("Arial", 12))
    product_entry.pack(side=tk.LEFT, fill=tk.X, padx=(25, 0))  # Pack entry next to the label


    quantity_frame = tk.Frame(parent_window, bg="#eccea5")
    quantity_frame.pack(pady=(5, 10), fill=tk.X)

    # Label for quantity entry
    quantity_label = tk.Label(quantity_frame, text="Enter quantity:", font=("Arial", 12), bg="#eccea5")
    quantity_label.pack(side=tk.LEFT, padx=(25, 0))

    # Entry for quantity
    quantity_entry = tk.Entry(quantity_frame, font=("Arial", 12))
    quantity_entry.pack(side=tk.LEFT, padx=(25, 0))

    def add_product():
        product_choice = product_entry.get().strip().lower()
        quantity = quantity_entry.get().strip()

        if product_choice in shop.products:
            try:
                quantity = int(quantity)
                message = shop.add_to_cart(product_choice, quantity)
                messagebox.showinfo("Add to Cart", message, parent=parent_window)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity.", parent=parent_window)
        else:
            messagebox.showerror("Error", "Invalid product. Please choose from the available products.", parent=parent_window)

    def on_enter(e):
       # Change the background color for the glow effect on mouse enter
        add_button.config(bg="limegreen")  # Change to a brighter color
        add_button.config(highlightbackground="limegreen")  # Optional: Highlight background

    def on_leave(e):
      # Reset the background color on mouse leave
        add_button.config(bg="lightgreen")


    button_frame = tk.Frame(parent_window, bg="#eccea5")
    button_frame.pack(pady=(10, 0), fill=tk.X)

    # Add button within the button frame
    add_button = tk.Button(button_frame, text="Add to Cart", command=add_product, font=("Arial", 12), bg="lightgreen", cursor="hand2")
    add_button.pack(side=tk.LEFT, padx=(35, 0)) 

    # Bind mouse enter and leave events for the glow effect
    add_button.bind("<Enter>", on_enter)
    add_button.bind("<Leave>", on_leave)

    def finish_shopping():
        display_receipt()
        parent_window.destroy()
    
    def on_enter_finish(e):
        # Change the background color for the glow effect on mouse enter
        finish_button.config(bg="limegreen")  # Change to a brighter color
        finish_button.config(highlightbackground="limegreen")  # Optional: Highlight background

    def on_leave_finish(e):
        # Reset the background color on mouse leave
        finish_button.config(bg="lightgreen")


    # Create a frame for the Finish button
    finish_button_frame = tk.Frame(parent_window, bg="#eccea5")  # Set the background color as needed
    finish_button_frame.pack(pady=(10, 0), fill=tk.X)  # Pack the frame with some vertical padding

    # Create the Finish button and place it in the finish_button_frame
    finish_button = tk.Button(finish_button_frame, text="Finish", command=finish_shopping, font=("Arial", 12), bg="lightgreen", cursor="hand2")
    finish_button.pack(side=tk.LEFT, padx=(35, 0))

    # Bind mouse enter and leave events for the glow effect
    finish_button.bind("<Enter>", on_enter_finish)
    finish_button.bind("<Leave>", on_leave_finish)


def display_receipt():
    receipt = shop.checkout()
    messagebox.showinfo("Receipt", receipt)

def start_customer_login(root):
    # Create a new top-level window with laptop screen size
    customer_window = tk.Toplevel(root)
    customer_window.title("Customer Interaction")
    customer_window.config(bg="#eccea5")
    # Set the window size to laptop screen size
    customer_window.geometry("1366x768")

    # Call the customer login function with customer_window as parent
    customer_login(customer_window)

def on_enter(e, button):
    # Change the background color for the glow effect on mouse enter
    button.config(bg="limegreen")  # Change to a brighter color
    button.config(highlightbackground="limegreen")  # Optional: Highlight background

def on_leave(e, button):
    # Reset the background color on mouse leave
    button.config(bg="lightgreen")

def display_gui():
    root = tk.Tk()
    root.title("Online Shop")
    
    # Set the root window size to laptop screen size
    root.geometry('1600x850+0+0')

    root.configure(bg="#eccea5") 

    # Create a function to exit fullscreen mode (optional)
    def exit_fullscreen(event=None):
        root.destroy()

    root.bind("<Escape>", exit_fullscreen)  # Bind the Escape key to close the application

    hello_frame = tk.Frame(root, bg="#eccea5", padx=10, pady=10)  # Frame with background color and padding
    hello_frame.pack(padx=20, pady=10)  # Pack the frame with some external padding

    # Create a label inside the frame
    hello_label = tk.Label(hello_frame, text="Welcome To Ezra Shopping Mall APPLICATION!", font=("Arial", 24), bg="#eccea5")  
    hello_label.pack()

    hell_frame = tk.Frame(root, bg="#eccea5", padx=5, pady=5)  # Frame with background color and padding
    hell_frame.pack(pady=(10, 10))  # Pack the frame with some external padding

    # Create a label inside the frame
    hell_label = tk.Label(hello_frame, text="PLEASE CHOOSE YOUR LOGIN FORMART:", font=("Arial", 16), bg="#eccea5")  
    hell_label.pack()
    
    admin_button_frame = tk.Frame(root, bg="#eccea5")  # Frame with the same background color
    admin_button_frame.pack(pady=(5, 10))  # Pack the frame with some padding

    # Create the admin button and pack it into the frame
    admin_button = tk.Button(admin_button_frame, text="Admin", command=admin_login, font=("Arial", 12), bg="lightgreen", cursor="hand2")
    admin_button.pack(pady=10)
    
    admin_button.bind("<Enter>", lambda e: on_enter(e, admin_button))
    admin_button.bind("<Leave>", lambda e: on_leave(e, admin_button))

    customer_button_frame = tk.Frame(root, bg="#eccea5")  # Frame with the same background color
    customer_button_frame.pack(pady=(40, 20))  # Pack the frame with some padding

    # Create the customer button and pack it into the frame
    customer_button = tk.Button(customer_button_frame, text="Customer", command=lambda: start_customer_login(root), font=("Arial", 12), bg="lightgreen", cursor="hand2")
    customer_button.pack(pady=10)

    customer_button.bind("<Enter>", lambda e: on_enter(e, customer_button))
    customer_button.bind("<Leave>", lambda e: on_leave(e, customer_button))
    
    root.mainloop()

if __name__ == "__main__":
    shop = Shop()
    admin = Admin()
    display_gui()
