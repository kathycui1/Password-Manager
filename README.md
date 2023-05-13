# Password-Manager
Simple password manager that uses SQLite and Python to store and manage passwords.

# How to use
1. Have Python installed and ‘cryptography’ library:
```
pip install cryptography
```
3. Run the program:
```
python passwordManager.py
```
5. Set up your master password
    - Choose a strong and memorable master password as it will be used to authenticate and access your stored passwords
6. Authenticate
    - Enter the master password
7. Menu
    1. Option 1: View Passwords (Lists all stored passwords with associated service names and usernames)
    2. Option 2: Add Password (Allows you to add a new password entry)
    3. Option 3: Remove Password (Allows you to remove an existing password entry)
    4. Option 4: Exit (Terminates the program and closes the database connection)
