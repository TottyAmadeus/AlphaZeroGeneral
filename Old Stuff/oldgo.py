import os
import numpy as np

class Go:

    EMPTY = 0
    BLACK = 1
    WHITE = -1
    BLACKMARKER = 4
    WHITEMARKER = 5
    LIBERTY = 8

    def __init__(self, args: list) -> None:
        '''
        # Description:
        Initializes the game of Go.
        
        # Arguments:
        args: A list containing the board size and the komi. [board_size, komi]
        '''
        self.args = args
        self.board_size = int(args[0])
        self.komi = float(args[1])
        self.board = self.get_initial_state()
        self.color = self.BLACK
        self.history = []
        self.action_size = self.board_size * self.board_size

        self.previous_skipped = False

        self.black_captures = 0
        self.white_captures = 0

        self.liberties = []
        self.block = []
        self.seki_count = 0
        self.seki_liberties = []


    def check_skip_end(self, action: tuple):
        '''
        # Description:
        Checks if the previous move was a skip and if the current move is also a skip.
        If both are skips, returns True, otherwise returns False and sets the previous_skipped variable to True.

        # Returns:
        True if both moves are skips.

        False if either of the moves is not a skip.
        '''
        if action == (-1, -1):
            if self.previous_skipped:
                print("True on check_skip_end")
                return True
            else:
                self.previous_skipped = True
                print("False on check_skip_end")
                return False

    def get_initial_state(self):
        '''
        # Description:
        Returns the initial state of the board.

        # Returns:
        A list of lists representing the board.
        '''
        board = []
        for i in range(self.board_size):
            board.append([])
            for j in range(self.board_size):
                board[i].append(0)
        return board


    def count(self, x, y, state: list, player:int , liberties: list, block: list) -> tuple[list, list]:
        '''
        # Description:
        Counts the number of liberties of a stone and the number of stones in a block.
        Follows a recursive approach to count the liberties of a stone and the number of stones in a block.

        # Returns:
        A tuple containing the number of liberties and the number of stones in a block.
        '''
        
        #initialize piece
        piece = state[y][x]
        #if there's a stone at square of the given player
        if piece == player:
            #save stone coords
            block.append((y,x))
            #mark the stone
            if player == self.BLACK:
                state[y][x] = self.BLACKMARKER
            else:
                state[y][x] = self.WHITEMARKER
            
            #look for neighbours recursively
            if y-1 >= 0:
                liberties, block = self.count(x,y-1,state,player,liberties, block) #walk north
            if x+1 < len(self.board):
                liberties, block = self.count(x+1,y,state,player,liberties, block) #walk east
            if y+1 < len(self.board):
                liberties, block = self.count(x,y+1,state,player,liberties, block) #walk south
            if x-1 >= 0:
                liberties, block = self.count(x-1,y,state,player,liberties, block) #walk west

        #if square is empty
        elif piece == self.EMPTY:
            #mark liberty
            state[y][x] = self.LIBERTY
            #save liberties
            liberties.append((y,x))

        # print("Liberties: " + str(len(self.liberties)) + " in: " + str(x) + "," + str(y))
        # print("Block: " + str(len(self.block)) + " in: " + str(x) + "," + str(y))
        return liberties, block

    #remove captured stones
    def clear_block(self, block: list, state: list) -> list:
        '''
        # Description:
        Clears the block of stones captured by the opponent on the board.

        # Returns:
        The board with the captured stones removed.
        '''

        #clears the elements in the block of elements which is captured
        for i in range(len(block)): 
            y, x = block[i]
            state[y][x] = self.EMPTY
        
        return state

    #restore board after counting stones and liberties
    def restore_board(self, state: list) -> list:
        '''
        # Description:
        Restores the board to its original state after counting liberties and stones.
        This is done by unmarking the stones following bitwise operations with the global class variables.
        
        # Returns:
        The board with the stones unmarked.
        '''

        #unmark stones
        # print("Restore Board")
        # print(state)
        for y in range(len(state)):
            for x in range(len(state)):
                #restore piece
                val = state[y][x]
                if val == self.BLACKMARKER:
                    state[y][x] = self.BLACK
                elif val == self.WHITEMARKER:
                    state[y][x] = self.WHITE
                elif val == self.LIBERTY:
                    state[y][x] = self.EMPTY

        # print("After Restore Board")
        # print(state)
        return state

    def print_board(self, state) -> None:
            '''
            # Description:
            Draws the board in the console.

            # Returns:
            None
            '''

        # Print column coordinates
            print("   ", end="")
            for j in range(len(state[0])):
                print(f"{j:2}", end=" ")
            print("\n  +", end="")
            for _ in range(len(state[0])):
                print("---", end="")
            print()

            # Print rows with row coordinates
            for i in range(len(state)):
                print(f"{i:2}|", end=" ")
                for j in range(len(state[0])):
                    print(f"{str(state[i][j]):2}", end=" ")
                print()

    def captures(self, state: list,player: int) -> tuple[bool, list]:
        '''
        # Description:
        Checks if a move causes a capture of stones of the player passed as an argument.
        If a move causes a capture, the stones are removed from the board.

        # Returns:
        A tuple containing a boolean indicating if a capture has been made and the board with the captured stones removed.
        '''
        check = False

        #loop over the board squares
        for y in range(len(state)):
            for x in range(len(state)):
                
                #init piece
                piece = state[y][x]

                #if stone belongs to given colour
                if piece & player:
                    
                    #count liberties
                    liberties = []
                    block = []
                    liberties, block = self.count(x, y, state, player, liberties, block)

                    #if no liberties remove the stones
                    if len(liberties) == 0: 
                        
                        prisioners = len(block)
                        #clear block
                        state = self.clear_block(block, state)

                        if player == self.BLACK:
                            self.black_captures += prisioners
                        else:
                            self.white_captures += prisioners


                        #if the move is a "ko" move but causes the capture of stones, then it is not allowed, unless it is the second move, in which case it is dealt afterwards
                        if self.seki_count == 0:
                            # print("Seki Found")
                            # returns False, which means that the move has caused a capture (the logic worked out that way in the initial development and i'm not sure what it would affect if it is changed)
                            check = True
                            self.seki_count = 1
                            continue

                    #restore the board
                    state = self.restore_board(state)
        # print("Seki Count: " + str(self.seki_count))
        # print("Captures: " + str(check))
        return check, state

    def change_player(self, player: int) -> int:
        return -player

    def set_stone(self, y: int, x: int, state: list, player: int) -> list:
        '''
        # Description:
        Sets a stone on the board.

        # Returns:
        The board with the stone set.
        '''

        state[y][x] = player
        # print(state)
        return state

    def is_valid_move(self, state: list, action: tuple, player: int) -> bool:
        '''
        # Description:
        Checks if a move is valid.
        If a move repeats a previous state or commits suicide (gets captured without capturing back), it is not valid.
        
        A print will follow explaining the invalid move in case it exists.

        # Returns:
        A boolean confirming the validity of the move.
        '''

        statecopy = np.copy(state)
        a, b = action

        if a >= self.board_size or a < -1 or b < -1 or b >= self.board_size:
            # print("Invalid Move: Out of Bounds")
            return False

        if state[a][b] != self.EMPTY:
            # print("Invalid Move: Space Occupied")
            return False 
        statecopy = self.set_stone(a,b, statecopy, player)

        statecopy = self.captures(statecopy, -player)[1]
        str_board = self.board_to_str(statecopy)

        if str_board in self.history:
            # print("Invalid Move: Repeated State")
            return False

        if self.captures(statecopy, -player)[0] == False and self.captures(statecopy, player)[0] == True:
            # print("Invalid Move: Suicide")
            return False
            
        return True
    
    def board_to_str(self, state: list) -> str:
        '''
        # Description:
        Converts the board to a string representation.

        # Returns
        String representation of the board.
        '''
        return ''.join([''.join(map(str, row)) for row in state])

    def save_state(self, state: list) -> None:
        '''
        # Description:
        Saves the board into a list of string representations of boards.
        
        # Returns:
        None
        '''
        str_board = self.board_to_str(state)
        self.history.append(str_board)  # Save string to history list

    def get_next_state(self, state: list, action: tuple, player: int) -> list:
        '''
        # Description
        Plays the move, verifies and undergoes captures and saves the state to the history.
        
        # Returns:
        New state with everything updated.
        '''
        a, b = action
        # checking if the move is part of is the secondary move to a ko fight
        state = self.set_stone(a, b, state, player)
        print(state)
        state = self.captures(state, -player)[1]
        self.save_state(state)
        return state

    def check_board_full(self, state: list) -> bool:
        '''
        # Description:
        Checks if the board is full.

        # Returns:
        True if the board is full.
        '''

        empty_count = 0
        for row in state:
            for stone in row:
                if stone == 0:
                    empty_count += 1
                if empty_count >= 3:
                    return False
                
        return True

    def check_win_and_over(self, state: list, action: tuple) -> tuple[int, bool]:
        '''
        # Description:
        Checks if the game is over and if there is a winner.

        # Returns:
        A tuple containing the winner and a boolean indicating if the game is over.
        '''
        if self.check_skip_end(action):
            points = self.check_score(state)
            if points > 0:
                return 1, True
            else:
                return -1, True

        if self.check_board_full(state):
            points = self.check_score(state)
            if points > 0:
                return 1, True
            else:
                return -1, True
        
        return 0, False
    
    def check_score(self, state: list) -> float:
        '''
        # Description:
        Checks the score of the game.

        # Returns:
        The score of the game, positive if black is winning, negative if white is winning.
        '''
        black_pieces = 0
        white_pieces = 0
        for row in state:
            for stone in row:
                if stone == 1:
                    black_pieces += 1
                if stone == 2:
                    white_pieces += 1
        
        black_points = black_pieces + self.black_captures
        white_points = white_pieces + self.white_captures + self.komi

        return black_points - white_points
    
    def get_value_and_terminated(self,state: list) -> tuple[float, bool]:
        '''
        # Description:
        Gets the score of the game and if the game is over.

        # Returns:
        A tuple containing the score of the game and a boolean indicating if the game is over.
        '''
        score = self.check_score(state)
        terminated = False
        if self.check_board_full(state) or self.check_available_moves(state, 1) == False or self.check_available_moves(state, -1) == False:
            terminated = True
        
        return score, terminated
    
    def get_valid_moves(self,state: list, player: int) -> set[tuple[int, int]]:
        '''
        # Description:
        Gets the valid moves for a given state, including the skip move.

        # Returns:
        A set containing the valid moves.
        '''

        state = np.array(state)
        return (state.reshape(-1) == 0).astype(np.uint8)
    
    def check_available_moves(self, state: list, player: int) -> bool:
        '''
        # Description:
        Checks if there are any available moves.

        # Returns:
        True if there are available moves.
        '''
        for i in range(len(state)):
            for j in range(len(state)):
                action = (i, j)
                if self.is_valid_move(state, action, player):
                    return True
        return False
    
    def get_encoded_state(self, state):
        layer_1 = np.where(np.array(state) == -1, 1, 0)
        layer_2 = np.where(np.array(state) == 0, 1, 0)
        layer_3 = np.where(np.array(state) == 1, 1, 0)

        result = np.stack([layer_1, layer_2, layer_3])

        return result
    
    def change_perspective(self, state, player):
        return state * player
    
    def get_action_from_index(self, index):
        return index // self.board_size, index % self.board_size

# Default Go Runtime


# args = [9, 5.5]

# go = Go(args)
# state = go.get_initial_state()
# go.print_board(state)

# player = 1
# print("Player: " + str(player))
# print("Input: ")

# while True:
#     a, b = tuple(int(x.strip()) for x in input().split(' '))
#     action = (a, b)
#     if go.is_valid_move(state, action, player):
#         state = go.get_next_state(state, action, player)
#         winner, win = go.check_win_and_over(state, action)
#         if win:
#             print("Winner: " + str(winner))
#             break
#         player = go.change_player(player)
#         go.print_board(state)
#         print("Player: " + str(player))
#         print("Input: ")

        