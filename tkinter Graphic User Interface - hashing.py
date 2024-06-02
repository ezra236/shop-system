import hashlib
import getpass
import secrets
import tkinter as tk
from tkinter import simpledialog, messagebox

class Shop:
    def __init__(self):
        self.products = {
            "apple": {"price": 0.5, "quantity": 10},
            "banana": {"price": 0.25, "quantity": 10},
            "orange": {"price": 0.75, "quantity": 10},
            "grape": {"price": 1.0, "quantity": 10},
        }
        self.shopping_cart = []

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
                return f"{quantity} {item.capitalize()}{'s' if quantity > 1 else ''} added to your cart."
            else:
                return f"Sorry, we only have {self.products[item]['quantity']} {item.capitalize()}{'s' if self.products[item]['quantity'] == 1 else ''} in stock."
        else:
            return "Invalid product. Please choose from the available products."

    def checkout(self):
        total_cost = sum(self.products[item["item"]]["price"] * item["quantity"] for item in self.shopping_cart)
        receipt = "\nYour Shopping Cart:\n"
        for item in self.shopping_cart:
            receipt += f"{item['quantity']} {item['item'].capitalize()}{'s' if item['quantity'] > 1 else ''}\n"
        receipt += f"Total Cost: ${total_cost:.2f}\n\nThank you for shopping with us!"
        return receipt

class Admin:
    def __init__(self):
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
        shop.products[new_product_name] = {"price": new_product_price, "quantity": new_product_quantity}
        messagebox.showinfo("Product Added", f"{new_product_name.capitalize()} has been added to the system.")

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

def customer_login():
    while True:
        product_choice = simpledialog.askstring("Customer", shop.display_available_products() + "\nEnter the product you want to add to your cart:")
        if product_choice is None:
            break
        if product_choice.lower() in shop.products:
            quantity = simpledialog.askinteger("Quantity", f"How many {product_choice.capitalize()}{'s' if shop.products[product_choice.lower()]['quantity'] > 1 else ''} do you want?")
            if quantity is not None:
                message = shop.add_to_cart(product_choice.lower(), quantity)
                messagebox.showinfo("Add to Cart", message)
        else:
            messagebox.showerror("Error", "Invalid product. Please choose from the available products.")
        add_or_finish = messagebox.askyesno("Continue", "Do you want to add more products?")
        if not add_or_finish:
            break
    display_receipt()

def display_receipt():
    receipt = shop.checkout()
    messagebox.showinfo("Receipt", receipt)

def display_gui():
    root = tk.Tk()
    root.title("Online Shop")

    admin_button = tk.Button(root, text="Admin", command=admin_login)
    admin_button.pack(pady=10)

    customer_button = tk.Button(root, text="Customer", command=customer_login)
    customer_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    shop = Shop()
    admin = Admin()
    display_gui()
