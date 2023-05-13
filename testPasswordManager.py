import unittest
from unittest.mock import patch
from passwordManager import PasswordManager

# Define test case class
class TestPasswordManager(unittest.TestCase):
    # Create instance of PasswordManager class with an in-memory database to establish a connection
    # Set master password and ecryption key manually
    def setUp(self):
        self.password_manager = PasswordManager(":memory:")
        self.password_manager.connect()
        self.password_manager.master_password = self.password_manager._hash_password("test123")
        self.password_manager.key = b'KJvI96do_buk9KaibXxV0mp4YSuRzeDNh4l7AW6XCWY='

    # Close database connection after each test case
    def tearDown(self):
        self.password_manager.connection.close()

    # Test to check if hashed password is equivalent to the expected value of the hashed password
    def test_hash_password(self):
        hashed_password = self.password_manager._hash_password("test123")
        expected_hash = "ecd71870d1963316a97e3ac3408c9835ad8cf0f3c1bc703527c30265534f75ae"
        self.assertEqual(hashed_password, expected_hash)

    # Test to check if the generated password length is 12
    def test_generate_password(self):
        password = self.password_manager.generate_password()
        self.assertEqual(len(password), 12)

    # Test to check if encryption and decryption process is functioning correctly
    def test_encrypt_decrypt_password(self):
        password = "test123"
        encrypted_password = self.password_manager._encrypt_password(password)
        decrypted_password = self.password_manager._decrypt_password(encrypted_password)
        self.assertEqual(decrypted_password, password)
    
    # Test to verify behaviour of adding a password without providing a password
    @patch("builtins.input", side_effect=["Service 1", "User 1", ""])
    def test_add_password_random(self, mock_input):
        self.password_manager.add_password()
        cursor = self.password_manager.connection.cursor()
        cursor.execute("SELECT * FROM passwords")
        result = cursor.fetchone()
        self.assertEqual(result[1], "Service 1")
        self.assertEqual(result[2], "User 1")

    # Test to verify behaviour of adding a password by providing a password
    @patch("builtins.input", side_effect=["Service 2", "User 2", "password"])
    def test_add_password_with_password(self, mock_input):
        self.password_manager.add_password()
        cursor = self.password_manager.connection.cursor()
        cursor.execute("SELECT * FROM passwords")
        result = cursor.fetchone()
        self.assertEqual(result[1], "Service 2")
        self.assertEqual(result[2], "User 2")

    # Test to verify behaviour of removing a password from the database
    @patch("builtins.input", return_value="Service 1")
    def test_remove_password(self, mock_input):
        self.password_manager.remove_password()
        cursor = self.password_manager.connection.cursor()
        cursor.execute("SELECT * FROM passwords WHERE service=?", ("Service 1",))
        result = cursor.fetchone()
        self.assertIsNone(result)

    # Test to verify overall behaviour of the run method
    @patch("builtins.input", side_effect=["test123", "4"])
    def test_run(self, mock_input):
        with patch("builtins.print") as mock_print:
            self.password_manager.run()
            mock_print.assert_called_with("Exiting...")

if __name__ == "__main__":
    unittest.main()
