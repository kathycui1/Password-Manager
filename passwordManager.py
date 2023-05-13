import sqlite3
import hashlib
import random
import string
from getpass import getpass
from cryptography.fernet import Fernet

# Define PasswordManager class
# Initializes the database file, database connection, master password, and encryption key
class PasswordManager:
    def __init__(self, db_file):
        self.db_file = db_file
        self.connection = None
        self.master_password = None
        self.key = None

    # Establishes a connection to SQLite database
    # If passwords table does not exist, one is created
    def connect(self):
        self.connection = sqlite3.connect(self.db_file)
        # passwords table has 4 columns: id, service, username, and password
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS passwords (id INTEGER PRIMARY KEY AUTOINCREMENT, service TEXT, username TEXT, password TEXT)"
        )

    # Propts user to enter a master password and verifies it by comparing it with the hashed password
    # Master password is stored as a hashed value
    def create_master_password(self):
        while True:
            password1 = getpass("Enter a master password: ")
            password2 = getpass("Re-enter the master password: ")
            if password1 == password2:
                self.master_password = self._hash_password(password1)
                break
            else:
                print("Passwords do not match. Please try again.")

    # Prompts user to enter master password for authentication and compares it to hashed input
    # 3 attempts total before failed authentication
    def authenticate(self):
        attempts = 3
        while attempts > 0:
            password = getpass("Enter the master password for Authentication: ")
            if self._hash_password(password) == self.master_password:
                print("Authentication successful!")
                return True
            else:
                print("Incorrect password. Please try again.")
                attempts -= 1
        print("Authentication failed. Exiting...")
        return False

    # Converts plain text password into hashed password using SHA256 algorithm
    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    # Generates random strong password of length 12, using uppercase and lowercase letters, digits, and punctuation symbols
    def generate_password(self, length=12):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))

    # Allows user to add a password entry, encrypts the password, and adds it to the database
    # If no password is provided then a random strong password is generated
    def add_password(self):
        service = input("Enter the service name: ")
        username = input("Enter the username: ")
        password = getpass("Enter the password or leave blank to generate a random password: ")

        if not password:
            password = self.generate_password()

        encrypted_password = self._encrypt_password(password)

        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO passwords (service, username, password) VALUES (?, ?, ?)",
                       (service, username, encrypted_password))
        self.connection.commit()
        print("Password added successfully.")

    # Allows user to remove a password entry and deletes it from the database
    def remove_password(self):
        service = input("Enter the service name: ")

        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM passwords WHERE service=?", (service,))
        if cursor.rowcount > 0:
            self.connection.commit()
            print("Password removed successfully.")
        else:
            print("Password not found.")

    # Retrieves all password entries from the database and displays them
    # Passwords are decrypted and displayed with the service and username
    def view_passwords(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT service, username, password FROM passwords")
        passwords = cursor.fetchall()

        if len(passwords) > 0:
            print("\nPasswords:")
            for password in passwords:
                service, username, encrypted_password = password
                decrypted_password = self._decrypt_password(encrypted_password)
                print(f"Service: {service}")
                print(f"Username: {username}")
                print(f"Password: {decrypted_password}")
                print("-" * 20)
        else:
            print("No passwords found.")

    # Encrypts password using the Fernet cipher suite
    # Generates new encryption key and a Fernet instance
    def _encrypt_password(self, password):
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        encrypted_password = cipher_suite.encrypt(password.encode())
        self.key = key  # Store the encryption key for later decryption
        return encrypted_password

    # Decrypts passwords using the stored encryption key and Fernet cipher suite
    def _decrypt_password(self, encrypted_password):
        cipher_suite = Fernet(self.key)
        decrypted_password = cipher_suite.decrypt(encrypted_password)
        return decrypted_password.decode()

    # Connects to the database, prompts the user for master password and authentication,
    # and presents a menu with options to view passwords, add a password, remove a password, or exit the program
    def run(self):
        self.connect()
        self.create_master_password()

        authenticated = self.authenticate()
        if not authenticated:
            return

        while True:
            print("\nMenu:")
            print("1. View passwords")
            print("2. Add password")
            print("3. Remove password")
            print("4. Exit")

            choice = input("Enter your choice (1-4): ")

            if choice == "1":
                self.view_passwords()

            elif choice == "2":
                self.add_password()

            elif choice == "3":
                self.remove_password()

            elif choice == "4":
                self.connection.close()
                print("Exiting...")
                break

            else:
                print("Invalid choice. Please enter a number from 1 to 4.")


# Runs the PasswordManager program
if __name__ == "__main__":
    password_manager = PasswordManager("passwords.db")
    password_manager.run()