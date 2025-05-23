import pygame
import random
import pyttsx3
from tkinter import *
import sqlite3
from tkinter import ttk



pygame.font.init()

# GLOBALS VARS
s_width = 800
s_height = 700
play_width = 300  # meaning 300 // 10 = 30 width per block
play_height = 600  # meaning 600 // 20 = 30 height per block
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

# SHAPE FORMATS

S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]


# index 0 - 6 represent shape

# create a piece class that can store some information about each shape.
class Piece(object):  # *
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0

# creating the grid of the game where the shapes descend down
def create_grid(locked_pos={}):  # *
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]

    for x in range(len(grid)):
        for y in range(len(grid[x])):
            if (y, x) in locked_pos:
                c = locked_pos[(y, x)]
                grid[x][y] = c
    return grid

# change the rotation of the shap
def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions

#we need to make sure that we have valid space when we are moving and rotating our shape
def valid_space(shape, grid):
    accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_pos = [j for sub in accepted_pos for j in sub]

    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_pos:
            if pos[1] > -1:
                return False
    return True

#To end the game we need to constantly be checking if the user has lost the game
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True

    return False

# generating a random shape
def get_shape():
    return Piece(5, 0, random.choice(shapes))

# displaying text to the middle of the screen
def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont("Century Gothic", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (
    top_left_x + play_width / 2 - (label.get_width() / 2), top_left_y + play_height / 2 - label.get_height() / 2))

#drawing the grey grid lines in the play area so that we can see which square our pieces are in.
def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y

    for i in range(len(grid)):
        pygame.draw.line(surface, (190, 188, 200), (sx, sy + i * block_size), (sx + play_width, sy + i * block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (190, 188, 200), (sx + j * block_size, sy),
                             (sx + j * block_size, sy + play_height))

#When all of the positions in a row are filled that row is cleared and every row about it is shifted down.
def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue

    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

    return inc

#displaying the next falling shape on the right side of the screen.
def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('Arial Rounded MT Bold', 30)
    label = font.render('Next Shape', 1, (190, 188, 200))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color,
                                 (sx + j * block_size, sy + i * block_size, block_size, block_size), 0)

    surface.blit(label, (sx + 20, sy - 30))

#update score
def update_score(nscore):
    score = max_score()

    with open('C:/Users/EL MAHDY 01007778867/Desktop/tetris/tetris notepad.txt', 'w') as f:
        if int(score) > nscore:
            f.write(str(score))
        else:
            f.write(str(nscore))

#To save the users best score we are going to update a text file
def max_score():
    with open('C:/Users/EL MAHDY 01007778867/Desktop/tetris/tetris notepad.txt', 'r') as f:
        lines = f.readlines()
        score = lines[0].strip()

    return score

# window of the game
def draw_window(surface, grid, score=0, last_score=0):
    surface.fill((0, 0, 0))

    pygame.font.init()
    font = pygame.font.SysFont('Arial Rounded MT Bold', 60)
    label = font.render('Tetris', 1, (190, 188, 200))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    # current score
    font = pygame.font.SysFont('Arial Rounded MT Bold', 30)
    label = font.render('Score: ' + str(score), 1, (190, 188, 200))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100

    surface.blit(label, (sx + 40, sy + 140))
    # last score
    label = font.render('HighScore: ' + last_score, 1, (190, 188, 200))

    sx = top_left_x - 250
    sy = top_left_y + 300

    surface.blit(label, (sx + 30, sy - 100))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j],
                             (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0)

    pygame.draw.rect(surface, (190, 188, 200), (top_left_x, top_left_y, play_width, play_height), 4)

    draw_grid(surface, grid)
    #pygame.display.update()

# the game loop
def main(win):  # *
    last_score = max_score()
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    level_time = 0
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        if level_time / 1000 > 5:
            level_time = 0
            if level_time > 0.12:
                level_time -= 0.005

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not (valid_space(current_piece, grid)):
                        current_piece.rotation -= 1

        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10

        draw_window(win, grid, score, last_score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        if check_lost(locked_positions):
            draw_text_middle(win, "GAME OVER! TRY AGAIN!", 40, (190, 188, 200))
            engine = pyttsx3.init()
            text = "your score is"+str(score) ,"GAME OVER! TRY AGAIN!"
            engine.say(text)
            engine.runAndWait()
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
            update_score(score)

#telling the user they lost and then telling them to play again
def main_menu(win):  # *
    run = True
    while run:
        win.fill((0, 0, 0))

        draw_text_middle(win, 'Press Any Key To Play!', 60, (190, 188, 200))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(win)

    pygame.display.quit()




root = Tk()
root.geometry("300x300")
#opening the window of the game through the form
def open_window():
    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('Tetris')
    root.destroy()
    main_menu(win)



#Heading
Label(root, text="Tetris", font="Helvetica").grid(row=0, column=3)

#Field Names
name = Label(root, text="Name")
email = Label(root, text="E-Mail")
gender = Label(root, text="Gender")
age = Label(root, text="Age")

# creating the database file
def create():
    conn = sqlite3.connect("databasesama.db")
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users(id integer primary key autoincrement,name TEXT,email TEXT, gender TEXT,'
        'age TEXT)')
    conn.commit()
    conn.close()
create()


#Fields Position
name.grid(row=1, column=2)
email.grid(row=2, column=2)
gender.grid(row=3, column=2)
age.grid(row=4, column=2)

#Variable for storing Data
namevalue = StringVar
emailvalue = StringVar
gendervalue = StringVar
agevalue = StringVar
checkvalue = IntVar

#Creating Entry Fields
nameentry = Entry(root, textvariable = namevalue)
emailentry = Entry(root, textvariable = emailvalue)
genderentry = Entry(root, textvariable = gendervalue)
ageentry = Entry(root, textvariable = agevalue)

#Entry Fields Position
nameentry.grid(row=1, column=3)
emailentry.grid(row=2, column=3)
genderentry.grid(row=3, column=3)
ageentry.grid(row=4, column=3)

#save the data of the players
def savedata():
    conn = sqlite3.connect('databasesama.db')
    c = conn.cursor()
    c.execute('insert into users (name , email,gender ,age ) VALUES (?,?,?,?)',
              (nameentry.get(),emailentry.get(),genderentry.get() ,ageentry.get()))
    conn.commit()
    conn.commit()
    conn.close()
    print("saved")



#Submit Button
Button(text="Start Playing", command= open_window).grid(row=8, column=3)
Button(text="save ", command= savedata ).grid(row=7, column=3)


root.mainloop()