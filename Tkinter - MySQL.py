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
        for product, info in self.products.items():
            available_products += f"{product.capitalize()}: ${info['price']}, Quantity: {info['quantity']}\n"
        return available_products

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

    # Set the window to fullscreen
    screen_width = admin_options_window.winfo_screenwidth()
    screen_height = admin_options_window.winfo_screenheight()
    admin_options_window.geometry(f"{screen_width}x{screen_height}")
    admin_options_window.attributes('-fullscreen', True)

    new_product_button = tk.Button(admin_options_window, text="Add New Product", command=add_new_product)
    new_product_button.pack(pady=10)

    change_password_button = tk.Button(admin_options_window, text="Change Password", command=change_password)
    change_password_button.pack(pady=10)

def add_new_product():
    name = simpledialog.askstring("Add New Product", "Enter the name of the new product:")
    if name is None:
        return
    price = float(simpledialog.askstring("Add New Product", f"Enter the price of {name.capitalize()}:"))
    quantity = int(simpledialog.askstring("Add New Product", f"Enter the initial quantity of {name.capitalize()}:"))
    admin.add_new_product(shop, name.lower(), price, quantity)

def change_password():
    new_password = simpledialog.askstring("Change Password", "Enter new admin password:", show='*')
    if new_password is None:
        return
    admin.change_password(new_password)

def customer_login(fullscreen_window):
    while True:
        product_choice = simpledialog.askstring("Customer", shop.display_available_products() + "\nEnter the product you want to add to your cart:", parent=fullscreen_window)
        if product_choice is None:
            break
        if product_choice.lower() in shop.products:
            quantity = simpledialog.askinteger("Quantity", f"How many {product_choice.capitalize()}{'s' if shop.products[product_choice.lower()]['quantity'] > 1 else ''} do you want?", parent=fullscreen_window)
            if quantity is not None:
                message = shop.add_to_cart(product_choice.lower(), quantity)
                messagebox.showinfo("Add to Cart", message, parent=fullscreen_window)
        else:
            messagebox.showerror("Error", "Invalid product. Please choose from the available products.", parent=fullscreen_window)
        
        add_or_finish = messagebox.askyesno("Continue", "Do you want to add more products?", parent=fullscreen_window)
        if not add_or_finish:
            break
    
    # Destroy the fullscreen window when done
    fullscreen_window.destroy()
    
    display_receipt()

def display_receipt():
    receipt = shop.checkout()
    messagebox.showinfo("Receipt", receipt)

def start_customer_login(root):
    # Create a fullscreen top-level window
    fullscreen_window = tk.Toplevel(root)
    fullscreen_window.title("Customer Interaction")
    
    # Set the window size to the screen size
    screen_width = fullscreen_window.winfo_screenwidth()
    screen_height = fullscreen_window.winfo_screenheight()
    
    # Set the window size and make it fullscreen
    fullscreen_window.geometry(f"{screen_width}x{screen_height}")
    fullscreen_window.attributes('-fullscreen', True)

    # Call the customer login function with fullscreen_window as parent
    customer_login(fullscreen_window)

def display_gui():
    root = tk.Tk()
    root.title("Online Shop")
    
    # Set the root window to fullscreen
    root.attributes('-fullscreen', True)
    
    # Create a function to exit fullscreen mode (optional)
    def exit_fullscreen(event=None):
        root.attributes('-fullscreen', False)
        root.destroy()

    root.bind("<Escape>", exit_fullscreen)  # Bind the Escape key to exit fullscreen mode
    
    admin_button = tk.Button(root, text="Admin", command=admin_login)
    admin_button.pack(pady=100)
    
    customer_button = tk.Button(root, text="Customer", command=lambda: start_customer_login(root))
    customer_button.pack(pady=50)
    
    root.mainloop()

if __name__ == "__main__":
    shop = Shop()
    admin = Admin()
    display_gui()
