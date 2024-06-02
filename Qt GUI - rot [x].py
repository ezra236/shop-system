from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget,
    QInputDialog, QMessageBox, QFileDialog, QAction, QLineEdit, QPushButton
)
import sys

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
        products_text = "Available Products:\n"
        for product, info in self.products.items():
            products_text += f"{product.capitalize()}: ${info['price']}, Quantity: {info['quantity']}\n"
        return products_text

    def add_to_cart(self, item):
        if item in self.products:
            if self.products[item]["quantity"] > 0:
                self.shopping_cart.append(item)
                self.products[item]["quantity"] -= 1
                return f"{item.capitalize()} has been added to your cart."
            else:
                return f"Sorry, {item.capitalize()} is out of stock."
        else:
            return "Invalid product. Please choose from the available products."

    def checkout(self):
        total_cost = sum(self.products[item]["price"] for item in self.shopping_cart)
        return (
            [item.capitalize() for item in self.shopping_cart],
            f"Total Cost: ${total_cost:.2f}"
        )

    def save_shopping_cart(self, filename):
        with open(filename, 'w') as file:
            file.write("Shopping Cart:\n")
            for item in self.shopping_cart:
                file.write(f"{item.capitalize()}\n")
            file.write(f"Total Cost: ${sum(self.products[item]['price'] for item in self.shopping_cart):.2f}")

    def add_new_product(self, name, price, quantity):
        new_product_name = name.lower()
        if new_product_name in self.products:
            return f"{new_product_name.capitalize()} already exists in the system. Use 'edit' to modify the product."
        else:
            self.products[new_product_name] = {"price": price, "quantity": quantity}
            return f"{new_product_name.capitalize()} has been added to the system."

class Admin:
    def __init__(self):
        self.admin_password = "123"
        self.rot_x_value = 3  # ROT-X value for encoding

    def authenticate(self):
        password_input, ok = QInputDialog.getText(None, "Admin Password", "Enter the admin password:", QLineEdit.Password)
        password_input = password_input.strip() if ok else ""

        # Apply ROT-X encoding to the entered password
        encoded_password = self.rot_x_encode(password_input)

        return encoded_password

    def rot_x_encode(self, password):
        x = self.rot_x_value
        encoded_password = ""
        for char in password:
            if char.isalpha():
                encoded_char = chr(((ord(char) - ord('a') + x) % 26) + ord('a')) if char.islower() else \
                               chr(((ord(char) - ord('A') + x) % 26) + ord('A'))
            else:
                encoded_char = char
            encoded_password += encoded_char
        return encoded_password

    def add_new_product(self, shop):
        password = self.authenticate()

        if password == self.admin_password:
            new_product_name, ok_name = QInputDialog.getText(None, "New Product", "Enter the name of the new product:")
            new_product_name = new_product_name.strip() if ok_name else ""

            if ok_name:
                new_product_price, ok_price = QInputDialog.getDouble(None, "New Product", f"Enter the price of {new_product_name.capitalize()}:")
                new_product_quantity, ok_quantity = QInputDialog.getInt(None, "New Product", f"Enter the initial quantity of {new_product_name.capitalize()}:")
                
                if ok_price and ok_quantity:
                    result = shop.add_new_product(new_product_name, new_product_price, new_product_quantity)
                    QMessageBox.information(None, "Product Added", result)
                else:
                    QMessageBox.information(None, "Product Not Added", "Invalid price or quantity.")
            else:
                QMessageBox.information(None, "Product Not Added", "No product name provided.")
        else:
            QMessageBox.critical(None, "Authentication Failed", "Incorrect password. Only the admin can add a new product.")

class ShopGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Shopping App")
        self.setGeometry(100, 100, 600, 400)

        self.shop = Shop()
        self.admin = Admin()

        # Main Widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout(central_widget)

        # Label
        label = QLabel("Welcome to the Shopping App!", self)
        label.setStyleSheet("background-color: orange; font-size: 16px;")
        layout.addWidget(label)

        # Admin Button
        admin_button = QPushButton("Add New Product (Admin)", self)
        admin_button.clicked.connect(self.add_new_product)
        layout.addWidget(admin_button)

        # Buttons for Add Product and Finish Shopping
        add_to_cart_button = QPushButton("Add Product to Cart", self)
        add_to_cart_button.clicked.connect(self.add_to_cart)
        layout.addWidget(add_to_cart_button)

        finish_shopping_button = QPushButton("Finish Shopping", self)
        finish_shopping_button.clicked.connect(self.checkout)
        layout.addWidget(finish_shopping_button)

        # Available Products Frame
        products_frame = QWidget(self)
        products_frame.setStyleSheet("background-color: lightgray;")
        layout.addWidget(products_frame)

        # Label to display available products
        self.label_available_products = QLabel("", self)
        self.label_available_products.setStyleSheet("font-size: 10px;")
        layout.addWidget(self.label_available_products)

        # Labels for displaying cart and information
        self.label_cart_info = QLabel("", self)
        self.label_cart_info.setStyleSheet("font-size: 12px;")
        layout.addWidget(self.label_cart_info)

        self.create_widgets()

    def create_widgets(self):
        # Display available products
        self.label_available_products.setText(self.shop.display_available_products())

    def display_available_products(self):
        products_text = self.shop.display_available_products()
        self.label_available_products.setText(products_text)

    def add_to_cart(self):
        self.display_available_products()
        item, ok = QInputDialog.getText(self, "Add to Cart", "Enter a product to add to your cart:")
        while ok and item:
            cart_info = self.shop.add_to_cart(item)
            self.label_cart_info.setText(cart_info)
            item, ok = QInputDialog.getText(self, "Add to Cart", "Enter a product to add to your cart (or press Cancel to finish):")

    def add_new_product(self):
        self.admin.add_new_product(self.shop)
        self.display_available_products()

    def save_shopping_cart(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Shopping Cart", "", "Text files (*.txt);;All Files (*)")
        if filename:
            self.shop.save_shopping_cart(filename)
            QMessageBox.information(self, "Save Successful", f"Shopping cart saved to {filename}")

    def checkout(self):
        cart_items, total_cost = self.shop.checkout()
        cart_info = "\n".join([f"{item}" for item in cart_items])
        cart_info += f"\n{total_cost}"

        QMessageBox.information(self, "Checkout", f"Your Shopping Cart:\n{cart_info}\n\nThank you for shopping with us!")
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    shop_gui = ShopGUI()
    shop_gui.show()
    sys.exit(app.exec_())
