from enum import Enum
import random

import numpy as np

import mineField


'''
The Solver object contains both the mineField.MineField object and its own knowledge state of the game.

The main lifting of the solving is done in the "check_cell" function.
This function checks the knowledge state of a cell, and those of the directly neighbouring cells.
If all mines adjacent to the cell have been found before, the others cells are safe to sweep.
If all of the neighbouring cells without knowledge must contain a mine, we can flag those cells.

Solving runs "check_cell" in a loop untill no progress can be made any more, at which point a random cell with unknown state will be sweeped.

To make the solution linear time in the number of cells that are covered,
we track the set of cells that are interesting for "check_cell" to evaluate:
when the knowledge of a cell or the knowledge of an adjacent cell changes the new information might give "check_cell" enough to make a new inference.
We call a cell that has new information 'dirty'.

This set is tracked both by a queue (so it's quick & simple to find a cell to check and to see that we are finished), and an array marking every cell as either dirty or not.
If a cell is flagged as dirty, its coordinates are pushed to the "dirty_queue" and the value in the "is_dirty" array is set to TRUE.

After a cell is evaluated by "check_cell", it will mark the cell as not dirty in the "is_dirty" array, such it can sometimes be discarded early when it is marked as dirty multiple times.
'''


# Possible states of knowledge of a cell; the possible values of the "knowledge" array
# using numerical values to simplify math
CELL_FLAGGED = 100 # cells that are inferred to contain a mine
# 0  no mines in the adjacent cells
# 1
# 2
# 3
# 4
# 5
# 6
# 7
# 8  all adjacent cells have mines
CELL_UNKNOWN = 200


# boolean values for using numpy arrays as a grid of booleans
TRUE = 1
FALSE = 0


def cell_knowledge_as_character(cell_knowledge: int) -> str:
    '''
    Used for printing of the board state
    '''
    if cell_knowledge == CELL_FLAGGED:
        # red "X"
        return '\033[0;31m' + 'X' + '\033[0;37m'
    elif cell_knowledge == 0:
        # green "0"
        return '\033[0;32m' + '0' + '\033[0;37m'
    elif 0 < cell_knowledge <= 8:
        # white number
        return str(cell_knowledge)
    elif cell_knowledge == CELL_UNKNOWN:
        # white "_"
        return '_'
    else:
        print('INVALID CELL KNOWLEDGE VALUE: {}'.format(cell_knowledge))
        assert(False)

class Solver:
    '''
    Tracks the knowledge obtained during the sweeping process and has some additional internal state for efficiency of sweeping.
    '''
    def __init__(self, width: int, height: int, number_of_mines: int):
        '''
        Initializes the problem and the knowledge state of the solver.
        '''

        # properties of the game
        self.width = width
        self.height = height
        self.number_of_mines = number_of_mines

        # external minesweeper game
        self.mine_field = mineField.MineField(width=width,height=height,number_of_mines=number_of_mines)

        # tracks what information has been obtained while playing the game
        # allowed values of this array are shown on top of file
        # start with all cells being unknown
        self.knowledge = np.full((width,height), CELL_UNKNOWN)

        # tracks if information regarding cells has been changed since they were last checked
        # start with non of the cells marked as dirty
        self.is_dirty = np.full((width,height), FALSE)

        # queue of dirty cells to make checking them simpler
        self.dirty_queue = []

        
    def is_in_bounds(self, column: int, row: int):
        return (column >= 0) and (row >= 0) and (column < self.width) and (row < self.height)


    def print_grid(self, cursor_column: int = -1, cursor_row: int = -1):
        '''
        Prints the knowledge array to the terminal.
        Optional to give a cursor position marking one of the unknown cells.
        '''
        assert(
            (cursor_column == -1 and cursor_row == -1)
            or
            self.is_in_bounds(cursor_column, cursor_row)
            )
        
        print('-----')
        for row in range(self.height):
            for column in range(self.width):
                if row == cursor_row and column == cursor_column:
                    assert(self.knowledge[column, row] == CELL_UNKNOWN)
                    print('\033[0;34m' + '@' + '\033[0;37m', end = ' ')
                else:
                    print(
                        cell_knowledge_as_character(
                            self.knowledge[column, row]
                        ),
                        end=' ')
            print('') # newline after end of row
        print('-----')

        
    def neighbours(self, column: int, row: int) -> [int]:
        '''
        Gives a list of all neighbours of the cell at (column, row) that are in the bounds of the game board
        '''
        assert(self.is_in_bounds(column, row))

        # all neighbours, even if they aren't in bounds
        neighbour_list = []
        neighbour_list.append((column + 1, row))     #         east
        neighbour_list.append((column + 1, row - 1)) # north - east
        neighbour_list.append((column,     row - 1)) # north
        neighbour_list.append((column - 1, row - 1)) # north - west
        neighbour_list.append((column - 1, row))     #         west
        neighbour_list.append((column - 1, row + 1)) # south - west
        neighbour_list.append((column,     row + 1)) # south
        neighbour_list.append((column + 1, row + 1)) # south - east

        # filter to keep only the neighbours that are in bounds
        neighbour_list_filtered = list(filter(lambda coordinate: self.is_in_bounds(coordinate[0], coordinate[1]), neighbour_list))

        return neighbour_list_filtered

    
    def count_neighbours(self, column: int, row: int) -> (int, int):
        '''
        Count number of surrounding cells that we don't know the knowledge of; the cells that might still contain a mine.
        Count number of surrouning cells that we know have a mine.
        Returns a tuple of the two above numbers in that order.
        '''
        assert(self.is_in_bounds(column, row))
        
        neighbour_list = self.neighbours(column, row)

        N_unknown_neighbours = 0
        N_found_neighbour_mines = 0

        for current_neighbour in neighbour_list:
            (current_neighbour_column, current_neighbour_row) = current_neighbour
            assert(self.is_in_bounds(current_neighbour_column, current_neighbour_row))

            current_neighbour_knowledge = self.knowledge[current_neighbour_column, current_neighbour_row]
            
            if current_neighbour_knowledge == CELL_FLAGGED:
                N_found_neighbour_mines += 1
            elif current_neighbour_knowledge == CELL_UNKNOWN:
                N_unknown_neighbours += 1
            else:
                assert(0 <= current_neighbour_knowledge <= 8)

        return (N_unknown_neighbours, N_found_neighbour_mines)


    def sweep_unknown_cell(self, column: int, row: int):
        '''
        Will try to sweep the cell.
        Assumes that previous code has made sure that this cell has not been sweeped before.
        Will update the knowledge state with the new information.
        Will flag all adjacent cells as dirty as they might be affected by the new knowledge.
        
        Will throw an exception when the cell contains a mine.
        '''
        assert(self.is_in_bounds(column, row))
        assert(self.knowledge[column, row] == CELL_UNKNOWN)

        # PERFORM THE SWEEP
        self.knowledge[column, row] = self.mine_field.sweep_cell(column, row)

        # mark this and surrounding cells as dirty
        self.mark_neighbourhood_dirty(column, row)

        
    def flag_unknown_cell(self, column: int, row: int):
        '''
        Flags the cell for containing a mine.
        Assumes that previous code has made sure that this cell has not been sweeped before.
        Will flag all adjacent cells as dirty as they might be affected by the new knowledge.
        '''
        assert(self.is_in_bounds(column, row))
        assert(self.knowledge[column, row] == CELL_UNKNOWN)

        self.knowledge[column, row] = CELL_FLAGGED

        self.mark_neighbourhood_dirty(column, row)

        
    def sweep_unknown_neighbours(self, column: int, row: int):
        '''
        Sweeps all neighbours of the cell at (column, row) that are currently unknown.
        '''
        assert(self.is_in_bounds(column, row))

        neighbour_list = self.neighbours(column, row)
        for current_neighbour in neighbour_list:
            (current_neighbour_column, current_neighbour_row) = current_neighbour
            current_neighbour_knowledge = self.knowledge[current_neighbour_column, current_neighbour_row]

            if current_neighbour_knowledge == CELL_UNKNOWN:
                self.sweep_unknown_cell(current_neighbour_column, current_neighbour_row)


    def flag_unknown_neighbours(self, column: int, row: int):
        '''
        Sweeps all neighbours of the cell at (column, row) that are currently unknown.
        '''
        assert(self.is_in_bounds(column, row))

        neighbour_list = self.neighbours(column, row)
        for current_neighbour in neighbour_list:
            (current_neighbour_column, current_neighbour_row) = current_neighbour
            current_neighbour_knowledge = self.knowledge[current_neighbour_column, current_neighbour_row]

            if current_neighbour_knowledge == CELL_UNKNOWN:
                self.flag_unknown_cell(current_neighbour_column, current_neighbour_row)

        
    def mark_dirty(self, column: int, row: int):
        '''
        Set this cell to dirty such that it will be checked later.
        '''
        assert(self.is_in_bounds(column, row))

        self.is_dirty[column, row] = TRUE
        self.dirty_queue.append((column, row))

        
    def mark_neighbourhood_dirty(self, column: int, row: int):
        '''
        Set the neighbouring cells to dirty such that they will be checked soon.
        Usefull to call this funtion when knowledge about some cell has been filled in
        '''
        assert(self.is_in_bounds(column, row))
        
        self.mark_dirty(column, row)

        neighbour_list = self.neighbours(column, row)
        for neighbour in neighbour_list:
            (current_neighbour_column, current_neighbour_row) = neighbour
            self.mark_dirty(current_neighbour_column, current_neighbour_row)

        
    def check_cell(self, column: int, row: int):
        '''
        Check if an implication on the content of surrounding cells can be made.
        Does not assume anything about the previous knowledge of the cell.

        Strategy: by checking the state of the surrounding cells we can find how many mines are still "hidden" in the adjacent cells.
        If all of the surrounding cells that we have no knowledge of must have a mine we can flag them.
        If none of the surrounding cells that we have no knowledge of must have a mine we can safely sweep them.

        Should never sweep a mine, so shouldn't throw an exception.
        '''
        assert(self.is_in_bounds(column, row))

        # check if the cell has been checked more recently than it had been added to the queue
        # in that case no need to be checked at this moment
        if self.is_dirty[column, row] == FALSE:
            return

        current_cell_knowledge = self.knowledge[column, row]

        if current_cell_knowledge == CELL_FLAGGED:
            pass # no information to work with
        elif current_cell_knowledge == CELL_UNKNOWN:
            pass # no information to work with
        elif 0 <= current_cell_knowledge <= 8:
            # cell has information
            N_neighbour_mines = current_cell_knowledge

            # find information on the neighbouring cells
            (N_unknown_neighbours, N_found_neighbour_mines) = self.count_neighbours(column, row)
            
            N_hidden_mines = N_neighbour_mines - N_found_neighbour_mines
            if N_hidden_mines == 0:
                # all unknown neighbours must be safe
                # note that this will also be triggered when the state of all neighbouring cells is known, but not a problem
                self.sweep_unknown_neighbours(column, row)
            elif N_hidden_mines < N_unknown_neighbours:
                pass # nothing can be inferred from this information
            elif N_hidden_mines == N_unknown_neighbours:
                # all unknown neighbours contain mines
                self.flag_unknown_neighbours(column, row)
            else:
                print('INVALID STATE')
                assert(False)
        
        else:
            print('INVALID CELL KNOWLEDGE STATE: {}'.format(current_cell_knowledge))

        self.is_dirty[column, row] = FALSE

        
    def process_queue(self):
        '''
        Will check all cells that are in the queue (including new ones that will be added to the queue in the process).

        Should never step on a mine, so never throws an exception
        '''

        # walk through the queue
        # note that new items might be appended to the queue in the process
        # as any cell can only be flagged 8x (8 neighbours) and the board is finite, the process must terminate
        while len(self.dirty_queue) > 0:
            (column, row) = self.dirty_queue.pop()
            self.check_cell(column, row)

        # check if the self.is_dirty array is indeed "cleared" to everything being clean
        # abuses the fact that FALSE is set to the numeric value of 0
        total = np.sum(self.is_dirty)
        if total != 0:
            print('problem, total is: {}'.format(total))
            assert(False)

            
    def sample_random_unknown(self) -> (bool, int, int):
        '''
        Chooses a random cell with currently unknown state
        If this occurs it will return (True, column, row)
        If no cell has unknown state, the game is finished and the return value is (False, -1, -1)
        '''
        # makes a list of all the cells of which the current knowledge state is CELL_UNKNOWN
        unknown_list = []
        for row in range(self.height):
            for column in range(self.width):
                if self.knowledge[column, row] == CELL_UNKNOWN:
                    unknown_list.append((column, row))

        N_unknown_cells = len(unknown_list)

        if N_unknown_cells == 0:
            # no unknown cells -> game is finished!
            return (False, -1, -1)
        else:
            # pick and return a randon one in the list
            random_index = random.randrange(0, len(unknown_list))
            return (True, unknown_list[random_index][0], unknown_list[random_index][1])


    def solve(self, print_knowledge: bool = True):
        '''
        Plays the game.
        '''
        is_running = True

        while is_running:
            (found_unknown, guess_column, guess_row) = self.sample_random_unknown()
            if found_unknown:
                # print current state
                if print_knowledge:
                    self.print_grid(guess_column, guess_row)

                # make a guess, could raise an exception when sweeping a mine
                try:
                    self.sweep_unknown_cell(guess_column, guess_row)
                except mineField.ExplosionException:
                    print("BOOM!")
                    return

                # make as many possible inferences
                # safe from throwing exceptions
                self.process_queue()
            else:
                is_running = False

        if print_knowledge:
            self.print_grid()
        print("SOLVED THE GAME!")        
