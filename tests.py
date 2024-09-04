import unittest
from unittest.mock import patch
from io import StringIO
import sys
from pathlib import Path
import pygame
import sqlite3

# Import the functions from the main code
from hangman_final import login, sign_up, main_menu, word_choice_menu, game, leaderboard_screen, draw_buttons, draw_guess, Button

class HangmanGameTest(unittest.TestCase):
    def setUp(self):
        # Initialize pygame
        pygame.init()
        pygame.display.set_mode((800, 600))
        pygame.mixer.init()

    def test_login(self):
        # Create a temporary database for testing
        db_path = Path("test_database.db")
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE logins (username TEXT, password TEXT)")
        conn.commit()

        # Simulate input
        with patch('builtins.input', side_effect=['username', 'password']):
            # Redirect stdout to capture printed output
            sys.stdout = StringIO()

            # Call the login function
            login()

            sys.stdout = sys.__stdout__

            # Assert that the expected output is printed
            self.assertIn('Sign in successful', sys.stdout.getvalue())

        # Remove the temporary database file
        db_path.unlink()

    def test_sign_up(self):
        # Create a temporary database for testing
        db_path = Path("test_database.db")
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE logins (username TEXT PRIMARY KEY, password TEXT)")
        conn.commit()

        # Call the sign_up function
        result = sign_up('newuser', 'password', db_path)

        # Assert that the user is successfully signed up
        self.assertTrue(result)

        # Try to sign up with the same username again
        result = sign_up('newuser', 'password', db_path)

        # Assert that the sign up fails due to duplicate username
        self.assertFalse(result)

        # Remove the temporary database file
        db_path.unlink()

    def test_main_menu(self):
        # Create user for testing
        db_path = Path("test_database.db")
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE logins (username TEXT PRIMARY KEY, password TEXT)")
        cursor.execute("INSERT INTO logins (username, password) VALUES ('testuser', 'password')")
        conn.commit()

        # Simulate user input for main menu selection
        with patch('builtins.input', side_effect=['1']):
            # Redirect stdout to capture printed output
            sys.stdout = StringIO()

            # Call the main_menu function
            main_menu(db_path)

            # Restore stdout
            sys.stdout = sys.__stdout__

            # Assert that the expected output is printed
            self.assertIn('Play button clicked', sys.stdout.getvalue())

        # Remove the temporary database file
        db_path.unlink()

    def test_word_choice_menu(self):
        # Simulate user input for word choice menu
        with patch('builtins.input', side_effect=['1']):
            # Redirect stdout to capture printed output
            sys.stdout = StringIO()

            # Call the word_choice_menu function
            word_choice_menu()

            sys.stdout = sys.__stdout__

            # Assert that the expected output is printed
            self.assertIn('Game started', sys.stdout.getvalue())


    def tearDown(self):
        # Quit pygame
        pygame.quit()

if __name__ == '__main__':
    unittest.main()
