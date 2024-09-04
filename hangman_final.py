import pygame
import sys
import pygame_gui
import random
import sqlite3
import pathlib

# Paths to make the program run smoothly on any computer
# This line of code was adapted from https://realpython.com/python-pathlib/
base_path = pathlib.Path(__file__).resolve().parent
audio_path = base_path / 'bonk.mp3'
play_button_path = base_path / 'button_play.png'
exit_button_path = base_path / 'button_exit.png'
yes_button_path = base_path / 'button_yes.png'
no_button_path = base_path / 'button_no.png'
leader_board_path = base_path / 'button_score.png'
db_path = base_path/ 'logins.db'
image_folder = base_path/"hangman"
music_path = base_path/''
exit_sound_path = base_path/"exit.mp3"
fail_sign_sound_path = base_path/"wah.mp3"
omg_sound_path = base_path/"omg.mp3"
spiderman_sound_path = base_path/ "spiderman.mp3"

# Word lists/topics for the game
cars = ["BMW", "AUDI", "MERCEDES", "LAMBORGHINI", "NISSAN", "FERRARI", "ASTONMARTIN", "MAZDA", "FORD", "CHEVROLET",
        "PORSCHE", "SUBARU", "MITSUBISHI", "VOLVO", "LEXUS", "RIMAC", "PONTIAC", "DODGE", "TESLA", "RENAULT",
        "MCLAREN", "MASERATI", "HONDA", "SUZUKI"]
car_mods = ["TURBO", "TRANSMISION", "PISTON", "TIRES", "RIMS", "SUSPENSION", "ENGINE", "ROLLCAGE", "NOS", "SHIFTER",
            "WIDEBODY", "OIL", "FILTER", "INTAKE"]

# Colors in RGB
white = (255, 255, 255)
black = (0, 0, 0)
cyan = (204, 255, 255)

# Window for the game
WIDTH, HEIGHT = 800, 500
my_screen = pygame.display.set_mode((WIDTH, HEIGHT))
#Set the caption for the game
pygame.display.set_caption("Hangman")

# setup pygame
#Function to initialeze the pygame module
pygame.init()
#Start the audio mixer
pygame.mixer.init()
#Set timer clock
timer = pygame.time.Clock()
# GUI setup
GUI_MANAGER = pygame_gui.UIManager((WIDTH, HEIGHT))

# Buttons for the hangman
ROWS = 3
COLUMNS = 13
GAP = 20
SIZE = 40
BOXES = []
BUTTONS = []
A = 65

# List to store the image
IMAGES = []
#For loop to change the image and store them into the list automatically instead of doing one at a time
for i in range(7):
    image = pygame.image.load(f"{image_folder}{i}.png")
    #Append the images into the list
    IMAGES.append(image)

#Define a button class
class Button():
    #Funtion to create button. Takes x and y coordintaes, scale to modify the size, and a png image
    def __init__(self, x, y, scale, image):
        #Get the height and width from the image
        width, height = image.get_size()
        self.image = image
        #scale the image
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        #Give the image a rectangle
        self.rect = self.image.get_rect()
        #Set the coordintates
        self.rect.topleft = (x, y)
    #Draws the images into the surface
    def draw(self):
        my_screen.blit(self.image, (self.rect.x, self.rect.y))


# Generate the coordinates x and y for the boxes
for row in range(ROWS):
    for column in range(COLUMNS):
        x = ((column * GAP) + GAP) + (SIZE * column)
        y = ((row * GAP) + GAP) + (SIZE * row) + 360
        box = pygame.Rect(x, y, SIZE, SIZE)
        BOXES.append(box)

for ind, box in enumerate(BOXES):
    letter = chr(A + ind)
    button = [box, letter]
    BUTTONS.append(button)


# Audio
# Adapted from https://stackoverflow.com/questions/43845800/how-do-i-add-background-music-to-my-python-game
doh = pygame.mixer.Sound(audio_path)
exit_sound = pygame.mixer.Sound(exit_sound_path)
fail_sign_sound = pygame.mixer.Sound(fail_sign_sound_path)
omg_sound = pygame.mixer.Sound(omg_sound_path)
spideerman_sound = pygame.mixer.Sound(spiderman_sound_path)
# Font
btn_font = pygame.font.SysFont('arial', 30)
game_font = pygame.font.SysFont('arial', 50)
letter_font = pygame.font.SysFont('arial', 40)
fail_font = pygame.font.SysFont('arial', 20)

# Secret word
WORD = ''
#List to store the letters that the user guessed
GUESS = []

# Username
globalUsername = ""

# Title
title = "Average college student"
title_text = game_font.render(title, True, black)
title_rect = title_text.get_rect(center=(WIDTH // 2, title_text.get_height() // 2))

#Adapted from https://www.sqlite.org/lang_insert.html
def sign_up(username, password):
    """
    This function takes in two parameters: Username and password to store them into a database.
    """
    # Check if either username or password is empty
    if not username or not password:
        print("Username or password cannot be empty")
        return False

    # Establish connection to the database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Command to insert the values into the database
    insert_query = '''
        INSERT INTO logins (username, password)
        VALUES (?, ?)
    '''

    try:
        # Execute the command
        cursor.execute(insert_query, (username, password))
        # Push the data into the database
        conn.commit()
        # If successful, print successful and return True
        print("Sign up successful")
        return True

    except sqlite3.IntegrityError:
        print("Username already exists")

    finally:
        # Close connection to the database
        conn.close()

#Adapted from https://www.sqlite.org/lang_insert.html
def sign_in(username, password):
    #Establish connection to the database
    conn = sqlite3.connect(str(db_path))
    #Create a cursor
    cursor = conn.cursor()
    #Select the logins and password columns
    select_query = '''
        SELECT * FROM logins WHERE username = ? AND password = ?
    '''
    cursor.execute(select_query, (username, password))
    #Select one
    result = cursor.fetchone()
    if result:
        print("Sign in successful")
        global globalUsername
        globalUsername = username
        conn.close()  # Close the connection
        return True
    else:
        print("Invalid username or password")

    conn.close()  # Close the connection

def update_score(score):
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    update_query = "UPDATE logins SET score=? WHERE username=?"
    try:
        cursor.execute(update_query, (score, globalUsername))
        conn.commit()
        print("Score updated successfully")
        return True
    except sqlite3.Error as e:
        print("Error updating score:", e)
    conn.close()


   

def leaderboard_screen():
    #Establish connection to database
    conn = sqlite3.connect(str(db_path))
    #Create a cursor
    cursor = conn.cursor()
    
    #Command query to select from the database the pairs of usernames and score by descending order
    select_query = """
    SELECT username, score FROM logins
    ORDER BY score DESC
    """
    #Execute the sqlite3 command
    cursor.execute(select_query)
    #Select all the rows
    rows = cursor.fetchall()

    conn.close()  # Close the connection

    #Boolean to keep the loop running
    running = True
    while running:
        #Fill the pygame screen with color cyan
        my_screen.fill(cyan)

        #Title text for leaderboard screen
        leaderboard_title_text = game_font.render("Leaderboard", True, black)
        #Rectangle for the title text
        leaderboard_title_rect = leaderboard_title_text.get_rect(center=(WIDTH // 2, 50))
        #Draw the title and the title rectangle
        my_screen.blit(leaderboard_title_text, leaderboard_title_rect)

        y_pos = 150
        #For loop to draw the usernames and scores in the screen
        for row in rows:
            username, score = row
            username_text = pygame.font.SysFont('arial', 20).render(username, True, black)
            score_text = pygame.font.SysFont('arial', 20).render(str(score), True, black)

            username_rect = username_text.get_rect(midleft=(150, y_pos))
            score_rect = score_text.get_rect(midright=(WIDTH - 150, y_pos))

            my_screen.blit(username_text, username_rect)
            my_screen.blit(score_text, score_rect)

            y_pos += 40
        #Create a button to allow the user to exit this screen
        back_button = Button(340, 400, 0.8, pygame.image.load(str(exit_button_path)))
        back_button.draw()
        #Update the screen
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            #Get the coordinates of the clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked_position = event.pos
                #If statement to see if the user clicks the back buttton and end the loop
                if back_button.rect.collidepoint(clicked_position):
                    exit_sound.play()
                    running = False





# Function to draw the buttons on the screen
def draw_buttons():
    for box, letter in BUTTONS:
        btn_txt = btn_font.render(letter, True, black)
        btn_rect = btn_txt.get_rect(center=((box.x + 20), (box.y + 20)))
        my_screen.blit(btn_txt, btn_rect)


# Function that draws the guess. If the letter is in the secret word it will be displayed.Else just a _ will be displayed
def draw_guess():
    display_text = ''
    for letter in WORD:
        if letter in GUESS:
            display_text += f"{letter} "
        else:
            display_text += "_ "
    text = letter_font.render(display_text, True, black)
    my_screen.blit(text, (400, 200))


# Menu 3. In this menu the user can choose the topic between car brands or car modifications for the secret word
def word_choice_menu():
    #Reset the GUI manager to avoid overlapping
    GUI_MANAGER.clear_and_reset()
    #Create a button for the topic using pygame_gui
    car_brands_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((275, 200), (110, 70)),
        text="SUTUTUTU",
        manager=GUI_MANAGER
    )
    #Create a button for the topic using pygame_gui
    mods_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((400, 200), (110, 70)),
        text="MODS",
        manager=GUI_MANAGER
    )
    #Create a title for this screen
    word_choice_title = game_font.render("Choose a topic", True, black)
    word_choice_title_rect = word_choice_title.get_rect(center=(WIDTH // 2, 100))
    #Boolean to keep the loop running
    running = True
    while running:
        #refresh rate to limit the FPS(frames per second) to 60
        refresh_rate = timer.tick(60) / 1000
        my_screen.fill(cyan)
        #For loop to register the pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

         
            GUI_MANAGER.process_events(event)
        #If statement to check if the button is pressed
        if car_brands_button.check_pressed():
            global WORD
            #If the button is pressed, choose a random word from the car brands lists and set it to the secret word
            WORD = random.choice(cars)
            #Run the game
            game()

        ##If the button is pressed, choose a random word from the car parts lists and set it to the secret word
        if mods_button.check_pressed():
            WORD = random.choice(car_mods)
            #Run the game
            game()

        #Update the GUI manager at 60 fps 
        GUI_MANAGER.update(refresh_rate)
        GUI_MANAGER.draw_ui(my_screen)
        my_screen.blit(word_choice_title, word_choice_title_rect)

        pygame.display.update()


# Player score count
SCORE = 0


# Game function
# Adapted from https://www.youtube.com/watch?v=UEO1B_llDnc
def game():
    # lives to keep track of the game
    lives = 0
    game_is_over = False
    # Main loop to keep pygame running
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            # Event type to register the position where the user clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked_position = event.pos

                # Checks if the letter
                for button, letter in BUTTONS:
                    if button.collidepoint(clicked_position):
                        if letter not in WORD:
                            #Play an audio if the letter is not in the secret word
                            doh.play()
                            #add 1 to lives
                            lives += 1

                        # if the lives reach 6, game_is_over will become true and end the game
                        if lives == 6:
                            game_is_over = True

                        GUESS.append(letter)
                        BUTTONS.remove([button, letter])

        my_screen.fill(cyan)
        #Draw the hangman images into the screen. The images are stored in a list. Depending on the lives, the idex changes and moves into the next image.
        my_screen.blit(IMAGES[lives], (150, 100))
        #Draw the title into the screen
        my_screen.blit(title_text, title_rect)
        for box in BOXES:
            pygame.draw.rect(my_screen, black, box, 2)
        #Draws the buttons for the letters
        draw_buttons()
        #Draw the spaces in for the letters in the screen
        draw_guess()


        #Boolean to check when the player wins
        won = True
        #For loop to check if the letter is in the secret word
        for letter in WORD:
            if letter not in GUESS:
                won = False

        #If the player won end the game, add 1 to his score and make the message You won
        if won:
            game_is_over = True
            global SCORE
            SCORE += 1
            omg_sound.play()
            game_message = "You won, play again?"
        #If the player loss end the game and make the message You lost
        elif lives >= 6:
            game_is_over = True
            game_message = "You lost, play again?"

        pygame.display.update()
        timer.tick(60)

        if game_is_over:
            break
    #Create yes and no button to ask the player if he wants to continue playing
    yes_button = Button(280, 320, 0.8, pygame.image.load(str(yes_button_path)))
    no_button = Button(400, 320, 0.8, pygame.image.load(str(no_button_path)))
    #While loop for the end of the game
    while game_is_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            #Register the clicked positons
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked_position = event.pos

                if yes_button.rect.collidepoint(clicked_position):
                    # Reset the game variables
                    GUESS.clear()
                    BUTTONS.clear()
                    for ind, box in enumerate(BOXES):
                        letter = chr(A + ind)
                        button = [box, letter]
                        BUTTONS.append(button)
                    #Reset the game
                    game_is_over = False
                    #Take the user back to the word_choice_menu
                    word_choice_menu()
                # check if the no button is pressed
                if no_button.rect.collidepoint(clicked_position):
                    spideerman_sound.play()
                    #Update the players score
                    update_score(SCORE)
                    #Go back to the main menu
                    main_menu()

        my_screen.fill(cyan)
        game_over_message = game_font.render(game_message, True, black)
        text_rect = game_over_message.get_rect(center=(WIDTH // 2, 200))
        my_screen.blit(game_over_message, text_rect)
        yes_button.draw()
        no_button.draw()

        pygame.display.update()
        timer.tick(60)


# Second menu. In this menu the user can click two buttons. One to start playing and one to exit
def main_menu():
    """
    Function for the second menu. In the main menu two buttons are drawn. A play and exit button
    """
    #Boolean to keep the loop running until its changed to False
    running = True
    #Main loop
    while running:
        
        #Fill the surface with cyan color
        my_screen.fill(cyan)
        #Create the buttons with the Button class previously defined. 
        # The class takes x,y coordinates, scales the image. and loads the image.
        play_button = Button(340, 100, 0.8, pygame.image.load(str(play_button_path)))
        exit_button = Button(340, 200, 0.8, pygame.image.load(str(exit_button_path)))
        leader_board_button = Button(340,300,0.7, pygame.image.load(str(leader_board_path)))
        #Draw the buttons into the screen
        play_button.draw()
        exit_button.draw()
        leader_board_button.draw()
        #Update the screen
        pygame.display.update()
        timer.tick(60)
        
        #Keep the loop running. The program will end if the close button is pressed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            
            #Check if the button is clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                #Gets the coordinates of the click
                clicked_position = event.pos


                #Check if the coordinates of the click collides with the rect of the play button
                if play_button.rect.collidepoint(clicked_position):
                    running = False
                    # Reset the game variables 
                    GUESS.clear()
                    BUTTONS.clear()
                    for ind, box in enumerate(BOXES):
                        letter = chr(A + ind)
                        button = [box, letter]
                        BUTTONS.append(button)
                    #If the play button rect collides with the clicked position move on into the next menu.
                    word_choice_menu()
                # If the leader board buttons is clicked, call the function for the leaderboard screen.
                elif leader_board_button.rect.collidepoint(clicked_position):
                    leaderboard_screen()


                # If the exit button rect collides with the clicked position, the programe ends.
                elif exit_button.rect.collidepoint(clicked_position):
                    exit_sound.play()
                    login()

def login():
    """
    Function for login screen. This function takes a username and a password. The user
    can sign in if he has a user or create a new user.
    """
    fail_sign = False
    #Reset the GUI manager to avoid items to overlap
    GUI_MANAGER.clear_and_reset()
    #Entry line to store the username
    username = pygame_gui.elements.UITextEntryLine(

        relative_rect=pygame.Rect((310, 100), (200, 50)),
        manager=GUI_MANAGER,
        object_id="#username_txt_entry",
        placeholder_text="Enter username"
    )
    #Entry line to store the password
    password = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((310, 250), (200, 50)),
        manager=GUI_MANAGER,
        object_id="#username_txt",
        placeholder_text="Enter password"
    )
    #Sign in button
    sign_in_button = pygame_gui.elements.UIButton(
        #Give the button a rectangle, coordinate, and size
        relative_rect=pygame.Rect((WIDTH / 2 - 100, HEIGHT / 2 + 100), (100, 40)),
        text="Sign In",
        manager=GUI_MANAGER
    )
    #Sign up button 
    sign_up_button = pygame_gui.elements.UIButton(
        #Give the button a rectangle, coordinate, and size
        relative_rect=pygame.Rect((WIDTH / 2 + 10, HEIGHT / 2 + 100), (100, 40)),
        text="Sign Up",
        manager=GUI_MANAGER
    )
    #Boolen to keep the loop running until it changes to False
    running = True
    while running:
        refresh_rate = timer.tick(60) / 1000
        #Set the background color for the surface
        my_screen.fill(cyan)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            GUI_MANAGER.process_events(event)

        #Gets the text that user typed in the username box
        username_txt = username.get_text()
        global globalUsername
        globalUsername = username_txt
        
        #Gets the text that user typed in the password
        password_txt = password.get_text()


        # Check if the sign in button got pressed
        if sign_in_button.check_pressed():
            #If the button is pressed called the sign_in function previuosly defined
            if sign_in(username_txt, password_txt):
                #Change the Boolean to False to stop running the login screen
                
                running = False
                #If the login is succesfull the program will move on into the main menu screen
                main_menu()
            else:
                fail_sign = True
        if fail_sign == True:
                fail_sign_sound.play()
                fail_msg = fail_font.render("Invalid username or password", True, black)
                fail_msg_rect = fail_msg.get_rect(center=(WIDTH // 2, 80))
                my_screen.blit(fail_msg, fail_msg_rect)


        #Check if the sign up button was pressed
        if sign_up_button.check_pressed():
            #If it got pressed the sign up function will be called and store the username and password into the database
            sign_up(username_txt, password_txt)
        #Updates the screen 
        GUI_MANAGER.update(refresh_rate)
        #Draw all the pygame_ui elements into a surface.
        GUI_MANAGER.draw_ui(my_screen)
        pygame.display.update()

login()
