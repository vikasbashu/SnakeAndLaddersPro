import tkinter as tk
from tkinter import messagebox
import random
import pygame

# Initialize pygame
pygame.init()
root = tk.Tk()
root.title("Snake & Ladder Go Pro 🚀")

# Load assets
board_bg_img = tk.PhotoImage(file='assets/board_bg.png')
snake_img = tk.PhotoImage(file='assets/snake.png')
ladder_img = tk.PhotoImage(file='assets/ladder.png')
player_imgs = {
    1: tk.PhotoImage(file='assets/player1.png'),
    2: tk.PhotoImage(file='assets/player2.png')
}
dice_images = [tk.PhotoImage(file=f'assets/dice{i}.png') for i in range(1, 7)]
dice_roll_sound = pygame.mixer.Sound('assets/dice_roll.wav')
move_sound = pygame.mixer.Sound('assets/move.wav')

# Board config
BOARD_SIZE = 600
CELL_SIZE = BOARD_SIZE // 10

# Game elements
game_snakes = {}
dynamic_snakes = {}
ladders = {}
player_positions = {1: 1, 2: 1}
current_player = 1
move_count = 0

# Window

canvas = tk.Canvas(root, width=BOARD_SIZE, height=BOARD_SIZE)
canvas.grid(row=0, column=0, columnspan=3)
dice_label = tk.Label(root)
dice_label.grid(row=1, column=1)

# Position → coord
def position_to_coord(pos):
    row = (pos - 1) // 10
    col = (pos - 1) % 10
    if row % 2 == 1:
        col = 9 - col
    x = col * CELL_SIZE + CELL_SIZE // 2
    y = (9 - row) * CELL_SIZE + CELL_SIZE // 2
    return x, y

# Draw board
def draw_board():
    canvas.delete("all")
    canvas.create_image(0, 0, anchor=tk.NW, image=board_bg_img)

    # Draw ladders
    for start, end in ladders.items():
        draw_ladder(start, end)

    # Draw snakes
    for start, end in game_snakes.items():
        draw_snake(start, end)
    for start, end in dynamic_snakes.items():
        draw_snake(start, end)

    # Draw players
    for p, pos in player_positions.items():
        draw_player(p, pos)

# Draw snake
def draw_snake(start, end):
    x1, y1 = position_to_coord(start)
    x2, y2 = position_to_coord(end)
    canvas.create_image(x1, y1, image=snake_img)

# Draw ladder
def draw_ladder(start, end):
    x1, y1 = position_to_coord(start)
    x2, y2 = position_to_coord(end)
    canvas.create_image(x1, y1, image=ladder_img)

# Draw player avatar
def draw_player(player_num, pos):
    x, y = position_to_coord(pos)
    canvas.create_image(x, y, image=player_imgs[player_num])

# Roll dice
def roll_dice():
    global current_player, move_count

    roll_button.config(state='disabled')
    dice_value = random.randint(1, 6)
    move_count += 1
    dice_roll_sound.play()

    dice_label.config(image=dice_images[dice_value-1])
    print(f"Player {current_player} rolls {dice_value}")

    old_pos = player_positions[current_player]
    target_pos = old_pos + dice_value
    if target_pos > 100:
        target_pos = 100

    animate_move(current_player, old_pos, target_pos, lambda: after_move_logic(current_player))

# Animate move
def animate_move(player, start, end, callback):
    step = 1 if end >= start else -1
    def move_one(pos):
        player_positions[player] = pos
        draw_board()
        move_sound.play()

        if pos != end:
            canvas.after(150, lambda: move_one(pos + step))
        else:
            callback()
    move_one(start + step)

# After move logic
def after_move_logic(player):
    global current_player

    pos = player_positions[player]

    if pos in ladders:
        print(f"Player {player} climbs ladder from {pos} to {ladders[pos]}")
        animate_move(player, pos, ladders[pos], lambda: after_move_logic(player))
        return
    if pos in game_snakes:
        print(f"Player {player} bitten by snake from {pos} to {game_snakes[pos]}")
        animate_move(player, pos, game_snakes[pos], lambda: after_move_logic(player))
        return
    if pos in dynamic_snakes:
        print(f"Player {player} bitten by dynamic snake from {pos} to {dynamic_snakes[pos]}")
        animate_move(player, pos, dynamic_snakes[pos], lambda: after_move_logic(player))
        return

    if move_count % 5 == 0 and len(dynamic_snakes) < 3:
        add_dynamic_snake()

    if player_positions[player] == 100:
        messagebox.showinfo("Game Over", f"Player {player} wins!")
        reset_game()
        return

    current_player = 2 if current_player == 1 else 1
    roll_button.config(state='normal')
    root.title(f"Player {current_player}'s Turn - Go Pro Game")

# Add dynamic snake
def add_dynamic_snake():
    while True:
        start = random.randint(21, 99)
        end = random.randint(1, start - 1)
        occupied_positions = set(game_snakes.keys()) | set(game_snakes.values()) | \
                             set(ladders.keys()) | set(ladders.values()) | \
                             set(dynamic_snakes.keys()) | set(dynamic_snakes.values())
        if start not in occupied_positions and end not in occupied_positions:
            dynamic_snakes[start] = end
            print(f"Dynamic Snake Added: {start} → {end}")
            break

# Generate snakes and ladders
def generate_game_snakes():
    global game_snakes
    game_snakes = {}
    while len(game_snakes) < 7:
        start = random.randint(21, 99)
        end = random.randint(1, start - 1)
        occupied_positions = set(game_snakes.keys()) | set(game_snakes.values()) | \
                             set(ladders.keys()) | set(ladders.values())
        if start not in occupied_positions and end not in occupied_positions:
            game_snakes[start] = end

def generate_ladders():
    global ladders
    ladders = {}
    while len(ladders) < 8:
        start = random.randint(1, 80)
        end = random.randint(start + 1, 100)
        occupied_positions = set(game_snakes.keys()) | set(game_snakes.values()) | \
                             set(ladders.keys()) | set(ladders.values())
        if start not in occupied_positions and end not in occupied_positions:
            ladders[start] = end

# Reset
def reset_game():
    global player_positions, current_player, move_count, dynamic_snakes
    player_positions = {1: 1, 2: 1}
    current_player = 1
    move_count = 0
    dynamic_snakes = {}
    generate_game_snakes()
    generate_ladders()
    draw_board()
    dice_label.config(image='')
    root.title("Player 1's Turn - Go Pro Game")

# Buttons
roll_button = tk.Button(root, text="Roll Dice", command=roll_dice, font=("Arial", 16))
roll_button.grid(row=1, column=0, sticky="ew")

reset_button = tk.Button(root, text="Reset Game", command=reset_game, font=("Arial", 16))
reset_button.grid(row=1, column=2, sticky="ew")

# Start
generate_game_snakes()
generate_ladders()
draw_board()
root.title("Player 1's Turn - Go Pro Game")
root.mainloop()
