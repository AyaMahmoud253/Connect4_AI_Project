 
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

