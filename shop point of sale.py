import hashlib
import getpass
import secrets

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
        print("Available Products:")
        for product, info in self.products.items():
            print(f"{product.capitalize()}: ${info['price']}, Quantity: {info['quantity']}")

    def add_to_cart(self, item, quantity):
        if item in self.products:
            if self.products[item]["quantity"] >= quantity:
                self.shopping_cart.append({"item": item, "quantity": quantity})
                self.products[item]["quantity"] -= quantity
                print(f"{quantity} {item.capitalize()}{'s' if quantity > 1 else ''} added to your cart.")
            else:
                print(f"Sorry, we only have {self.products[item]['quantity']} {item.capitalize()}{'s' if self.products[item]['quantity'] == 1 else ''} in stock.")
        else:
            print("Invalid product. Please choose from the available products.")

    def checkout(self):
        total_cost = sum(self.products[item["item"]]["price"] * item["quantity"] for item in self.shopping_cart)
        print("\nYour Shopping Cart:")
        for item in self.shopping_cart:
            print(f"{item['quantity']} {item['item'].capitalize()}{'s' if item['quantity'] > 1 else ''}")
        print(f"Total Cost: ${total_cost:.2f}")
        print("\nThank you for shopping with us!")

        # Save shopping cart to file
        filename = "shopping_cart.txt"
        with open(filename, 'w') as file:
            file.write("Shopping Cart:\n")
            for item in self.shopping_cart:
                file.write(f"{item['quantity']} {item['item'].capitalize()}{'s' if item['quantity'] > 1 else ''}\n")
            file.write(f"Total Cost: ${total_cost:.2f}")
        print(f"Shopping cart saved to {filename}")

class Admin:
    def __init__(self):
        self.admin_salt = secrets.token_hex(16)  # Generate a random salt for each admin
        self.admin_hashed_password = self._hash_password("123")  # Hash the default password with the salt

    def _hash_password(self, password):
        """Hashes the given password with the admin's salt."""
        hashed_password = hashlib.sha256((password + self.admin_salt).encode()).hexdigest()
        return hashed_password

    def check_password(self, password):
        """Checks if the provided password matches the admin's hashed password."""
        hashed_password = self._hash_password(password)
        return hashed_password == self.admin_hashed_password

    def change_password(self, new_password):
        """Changes the admin's password."""
        self.admin_hashed_password = self._hash_password(new_password)
        print("Password changed successfully.")

    def add_new_product(self, shop, admin_password_input):
        if self.check_password(admin_password_input):
            new_product_name = input("Enter the name of the new product: ").lower()
            new_product_price = float(input(f"Enter the price of {new_product_name.capitalize()}: "))
            new_product_quantity = int(input(f"Enter the initial quantity of {new_product_name.capitalize()}: "))

            if new_product_name in shop.products:
                print(f"{new_product_name.capitalize()} already exists in the system. Use 'edit' to modify the product.")
                return

            shop.products[new_product_name] = {"price": new_product_price, "quantity": new_product_quantity}
            print(f"{new_product_name.capitalize()} has been added to the system.")
        else:
            print("Incorrect password. Only the admin can add a new product or change the password.")

if __name__ == "__main__":
    shop = Shop()
    admin = Admin()

    while True:
        action = input("Enter 'add' to add a product to your cart, 'administrator' for admin actions, or 'done' to finish shopping: ").lower()

        if action == 'done':
            break
        elif action == 'add':
            while action == 'add':
                shop.display_available_products()
                item = input("Enter a product to add to your cart or 'finish': ").lower()
                if item == 'finish':
                    break
                if item in shop.products:
                    quantity = int(input(f"How many {item.capitalize()}{'s' if shop.products[item]['quantity'] > 1 else ''} do you want? "))
                    shop.add_to_cart(item, quantity)
                else:
                    print("Invalid product. Please choose from the available products.")
        elif action == 'administrator':
            admin_password_input = getpass.getpass("Enter the admin password: ")
            if admin.check_password(admin_password_input):
                admin_action = input("Enter 'new' to add a new product or 'change' to change password: ").lower()
                if admin_action == 'new':
                    admin.add_new_product(shop, admin_password_input)
                elif admin_action == 'change':
                    new_password = getpass.getpass("Enter new admin password: ")
                    admin.change_password(new_password)
                else:
                    print("Invalid administrator action. Please enter 'new' or 'change'.")
            else:
                print("Incorrect password. Access denied.")
        else:
            print("Invalid action. Please enter 'add', 'administrator', or 'done'.")

    shop.checkout()
