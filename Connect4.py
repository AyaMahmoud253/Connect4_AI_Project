import numpy as np
import pygame 
import sys
import math 
from threading import Timer
import random


#game cosntants
ROWS = 6
COLS = 7
 
PLAYER_TURN = 0
AI_TURN = 1

 
PLAYER_PIECE = 1
AI_PIECE = 2

 
Orange = (255, 165, 0)
White = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)


def create_board():
    board = np.zeros((ROWS, COLS))
    return board


 
def drop_piece(board, row, col, piece):
    board[row][col] = piece


# check that top row in a column is empty
def is_valid_location(board, col):
    return board[0][col] == 0


#find the place the the piece will settle 
def get_next_open_row(board, col):
    for r in range(ROWS-1, -1, -1):
        if board[r][col] == 0:
            return r


# checking if one of the player will win
def winning_move(board, piece):

    #check horizontally
    for c in range(COLS-3):
        for r in range(ROWS):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    # check vertically
    for c in range(COLS):
        for r in range(ROWS-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    # checking positive diagonal
    for c in range(COLS-3):
        for r in range(3, ROWS):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

    # checking negative diagonal for win
    for c in range(3,COLS):
        for r in range(3, ROWS):
            if board[r][c] == piece and board[r-1][c-1] == piece and board[r-2][c-2] == piece and board[r-3][c-3] == piece:
                return True


# draw the board
def draw_board(board):
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(screen, Orange, (c * sq_size, r * sq_size + sq_size, sq_size, sq_size ))
            if board[r][c] == 0:
                pygame.draw.circle(screen, White, (int(c * sq_size + sq_size/2), int(r* sq_size + sq_size + sq_size/2)), circle_radius)
            elif board[r][c] == 1:
                pygame.draw.circle(screen, RED, (int(c * sq_size + sq_size/2), int(r* sq_size + sq_size + sq_size/2)), circle_radius)
            else :
                pygame.draw.circle(screen, YELLOW, (int(c * sq_size + sq_size/2), int(r* sq_size + sq_size + sq_size/2)), circle_radius)

    pygame.display.update()


# evaluate a 'window' of 4 locations in a row based on what pieces it contains
# the values used can be experimented with
def evaluate_window(window, piece):
    # by default the oponent is the player
    opponent_piece = PLAYER_PIECE

    # if we are checking from the player's perspective, then the oponent is AI
    if piece == PLAYER_PIECE:
        opponent_piece = AI_PIECE

    # initial score of a window is 0
    score = 0

    # based on how many friendly pieces there are in the window, we increase the score
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2

    # or decrese it if the oponent has 3 in a row
    if window.count(opponent_piece) == 3 and window.count(0) == 1:
        score -= 4 

    return score    


# scoring the overall attractiveness of a board after a piece has been droppped
def score_position(board, piece):

    score = 0

    # score center column --> we are prioritizing the central column because it provides more potential winning windows
    center_array = [int(i) for i in list(board[:,COLS//2])]
    center_count = center_array.count(piece)
    score += center_count * 6

    # below we go over every single window in different directions and adding up their values to the score
    # score horizontal
    for r in range(ROWS):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLS - 3):
            window = row_array[c:c + 4]
            score += evaluate_window(window, piece)

    # score vertical
    for c in range(COLS):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROWS-3):
            window = col_array[r:r+4]
            score += evaluate_window(window, piece)

    # score positively sloped diagonals
    for r in range(3,ROWS):
        for c in range(COLS - 3):
            window = [board[r-i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    # score negatively sloped diagonals
    for r in range(3,ROWS):
        for c in range(3,COLS):
            window = [board[r-i][c-i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

# checking if the given turn or in other words node in the alpha_beta tree is terminal
# a terminal node is player winning, AI winning or board being filled up
def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0



# minmax algo
def minimax1(board, depth, maximizing_player):

    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return None, 10000000
            elif winning_move(board, PLAYER_PIECE):
                return None, -10000000
            else:
                return None, 0
        else:
            return None, score_position(board, AI_PIECE)

    if maximizing_player:
        best_value = -math.inf
        best_column = random.choice(valid_locations)

        for col in valid_locations:
            row = get_next_open_row(board, col)
            if row is None:
                continue

            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            _, value = minimax1(b_copy, depth - 1, False)

            if value > best_value:
                best_value = value
                best_column = col

        return best_column, best_value

    else:
        best_value = math.inf
        best_column = random.choice(valid_locations)

        for col in valid_locations:
            row = get_next_open_row(board, col)
            if row is None:
                continue

            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            _, value = minimax1(b_copy, depth - 1, True)

            if value < best_value:
                best_value = value
                best_column = col

        return best_column, best_value


# alpha_beta
def alpha_beta(board, depth, alpha, beta, maximizing_player):

    # all valid locations on the board
    valid_locations = get_valid_locations(board)

    # boolean that tells if the current board is terminal
    is_terminal = is_terminal_node(board)

    # if the board is terminal or depth == 0
    # we score the win very high and a draw as 0
    if depth == 0 or is_terminal:
        if is_terminal: # winning move 
            if winning_move(board, AI_PIECE):
                return (None, 10000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000)
            else:
                return (None, 0)
        # if depth is zero, we simply score the current board
        else: # depth is zero
            return (None, score_position(board, AI_PIECE))

    # if the current board is not rerminal and we are maximizing
    if maximizing_player:

        # initial value is what we do not want - negative infinity
        value = -math.inf

        # this will be the optimal column. Initially it is random
        column = random.choice(valid_locations)

        # for every valid column, we simulate dropping a piece with the help of a board copy
        # and run the alpha_beta on it with decresed depth and switched player
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            # recursive call
            new_score = alpha_beta(b_copy, depth-1, alpha, beta, False)[1]
            # if the score for this column is better than what we already have
            if new_score > value:
                value = new_score
                column = col
            # alpha is the best option we have overall
            alpha = max(value, alpha) 
            # if alpha (our current move) is greater (better) than beta (opponent's best move), then 
            # the oponent will never take it and we can prune this branch
            if alpha >= beta:
                break

        return column, value
    
    # same as above, but for the minimizing player
    else: # for thte minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = alpha_beta(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(value, beta) 
            if alpha >= beta:
                break
        return column, value



def get_valid_locations(board):
    valid_locations = []
    
    for column in range(COLS):
        if is_valid_location(board, column):
            valid_locations.append(column)

    return valid_locations



def end_game():
    global game_over
    game_over = True
    print(game_over)



board = create_board()


game_over = False


not_over = True


turn = random.randint(PLAYER_TURN, AI_TURN)


pygame.init()

# size of one game location
sq_size = 100

# dimensions for pygame GUI
width = COLS * sq_size
height = (ROWS + 1) * sq_size
circle_radius = int(sq_size/2 - 5)
size = (width, height)
screen = pygame.display.set_mode(size)


my_font = pygame.font.SysFont("monospace", 75)


draw_board(board)
pygame.display.update()



x=1
while not game_over and x==1:
    if turn == PLAYER_TURN and not game_over and not_over:
        
        
       # Generate a random column
       
       valid_loc  = get_valid_locations(board)
       col = random.choice(valid_loc)

       if is_valid_location(board, col):
           
           
           
           pygame.time.wait(500)
           row = get_next_open_row(board, col)
           drop_piece(board, row, col, PLAYER_PIECE)
           if winning_move(board, PLAYER_PIECE):
               
               
            
               print("PLAYER 2 WINS!")
               label = my_font.render("PLAYER 2 WINS!", 1, YELLOW)
               screen.blit(label, (40, 10))
               not_over = False
               t = Timer(3.0, end_game)
               t.start()
       draw_board(board)

    # increment turn by 1
    turn += 1
    # this will alternate between 0 and 1 with every turn
    turn = turn % 2
                     
    # if its the AI's turn
    if turn == AI_TURN and not game_over and not_over:

        # the column to drop in is found using minmax
        col, minimax_score = minimax1(board, 5, True)

        if is_valid_location(board, col):
            pygame.time.wait(500)
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)
            if winning_move(board, AI_PIECE):
                print("PLAYER 2 WINS!")
                label = my_font.render("PLAYER 2 WINS!", 1, YELLOW)
                screen.blit(label, (40, 10))
                not_over = False
                t = Timer(3.0, end_game)
                t.start()
        draw_board(board)    

        # increment turn by 1
        turn += 1
        # this will alternate between 0 and 1 withe very turn
        turn = turn % 2
