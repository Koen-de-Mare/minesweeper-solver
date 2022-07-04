from enum import Enum
import random

import numpy as np

import mineField as mf

# possible states of knowledge of a cell
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

# boolean values for mis-using numpy arrays
TRUE = 1
FALSE = 0

def cell_knowledge_as_character(cell_knowledge: int) -> str:
    if cell_knowledge == CELL_FLAGGED:
        return '\033[91mX\033[00m'
    elif cell_knowledge == 0:
        return '\033[92m0\033[00m'
    elif 0 < cell_knowledge <= 8:
        return str(cell_knowledge)
    elif cell_knowledge == CELL_UNKNOWN:
        return '_'
    else:
        print('INVALID CELL KNOWLEDGE VALUE: {}'.format(cell_knowledge))
        assert(False)

class Solver:
    def __init__(self, width: int, height: int, number_of_mines: int):
        '''
        initialize the problem and the knowledge state of the solver
        '''

        # properties of the board
        self.width = width
        self.height = height
        self.number_of_mines = number_of_mines

        # external minesweeper game
        self.mine_field = mf.MineField(width=width,height=height,number_of_mines=number_of_mines)

        # tracks what information has been obtained while playing the game
        self.knowledge = np.full((width,height), CELL_UNKNOWN)

        # tracks if information regarding cells has been changed since they were last checked
        self.is_dirty = np.full((width,height), FALSE)

        # queue of dirty cells to make checking them simpler
        self.dirty_queue = []

        
    def is_in_bounds(self, column: int, row: int):
        return (column >= 0) and (row >= 0) and (column < self.width) and (row < self.height)


    def print_grid(self):
        print('-----')
        for row in range(self.height):
            for column in range(self.width):
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
        neighbour_list_filtered = list(filter(lambda a: self.is_in_bounds(a[0], a[1]), neighbour_list))

        return neighbour_list_filtered

    
    def count_neighbours(self, column: int, row: int) -> (int, int):
        '''
        Count number of surrouning cells that we know have a mine.
        Count number of surrounding cells that we don't know the knowledge of; the cells that might still contain a mine.
        '''
        assert(self.is_in_bounds(column, row))
        
        neighbour_list = self.neighbours(column, row)

        N_unknown_neighbours = 0
        N_found_neighbour_mines = 0

        for neighbour in neighbour_list:
            (current_neighbour_column, current_neighbour_row) = neighbour
            assert(self.is_in_bounds(current_neighbour_column, current_neighbour_row))

            current_neighbour_knowledge = self.knowledge[current_neighbour_column, current_neighbour_row]
            
            if current_neighbour_knowledge == CELL_FLAGGED:
                N_found_neighbour_mines += 1
            elif current_neighbour_knowledge == CELL_UNKNOWN:
                N_unknown_neighbours += 1
            else:
                assert(0 <= current_neighbour_knowledge <= 8)

        return (N_unknown_neighbours, N_found_neighbour_mines)


    # functions that modify the knowledge state of the solver
    # Because new knowledge has been obtained they are responsible for marking adjacent cells as dirty
    def sweep_unknown_cell(self, column: int, row: int):
        '''
        Will try to sweep the cell.
        Assumes that previous code has made sure that this cell has not been sweeped before and does not contain a mine.
        '''
        assert(self.is_in_bounds(column, row))
        assert(self.knowledge[column, row] == CELL_UNKNOWN)

        # PERFORM THE SWEEP
        self.knowledge[column, row] = self.mine_field.sweep_cell(column, row)

        # mark this and surrounding cells as dirty
        self.mark_neighbourhood_dirty(column, row)

        
    def flag_unknown_cell(self, column: int, row: int):
        '''
        Flags the cell for containing mine
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
        for neighbour in neighbour_list:
            (current_neighbour_column, current_neighbour_row) = neighbour
            current_neighbour_knowledge = self.knowledge[current_neighbour_column, current_neighbour_row]

            if current_neighbour_knowledge == CELL_UNKNOWN:
                self.sweep_unknown_cell(current_neighbour_column, current_neighbour_row)


    def flag_unknown_neighbours(self, column: int, row: int):
        '''
        Sweeps all neighbours of the cell at (column, row) that are currently unknown.
        '''
        assert(self.is_in_bounds(column, row))

        neighbour_list = self.neighbours(column, row)
        for neighbour in neighbour_list:
            (current_neighbour_column, current_neighbour_row) = neighbour
            current_neighbour_knowledge = self.knowledge[current_neighbour_column, current_neighbour_row]

            if current_neighbour_knowledge == CELL_UNKNOWN:
                self.flag_unknown_cell(current_neighbour_column, current_neighbour_row)

        
    def mark_dirty(self, column: int, row: int):
        '''
        Set this cell to dirty such that it will be checked soon
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
        Does not assume anything about the previous logic of the cell.
        '''
        assert(self.is_in_bounds(column, row))

        if self.is_dirty[column, row] == FALSE:
            # the cell has been checked in the mean while: no need to check it again
            return
        
        current_cell_knowledge = self.knowledge[column, row]

        if current_cell_knowledge == CELL_FLAGGED:
            pass # no information to work with
        elif current_cell_knowledge == CELL_UNKNOWN:
            pass # no information to work with
        elif 0 <= current_cell_knowledge <= 8:
            N_neighbour_mines = current_cell_knowledge
            
            (N_unknown_neighbours, N_found_neighbour_mines) = self.count_neighbours(column, row)
            
            N_hidden_mines = N_neighbour_mines - N_found_neighbour_mines
            if N_hidden_mines == 0:
                # all unknown neighbours must be safe
                # note the special case where there are no unknown neighbours, making N_hidden_mines == 0 vacuously true
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
        Will check all cells that are in the queue (including new ones that will be added to the queue in the process)
        '''
        while len(self.dirty_queue) > 0:
            (column, row) = self.dirty_queue.pop(0)
            self.check_cell(column, row)

        # check if the self.is_dirty array is indeed "cleared" to everything being clean
        total = np.sum(self.is_dirty)
        if total != 0:
            print('problem, total is: {}'.format(total))
            assert(False)

            
    def sample_random_unknown(self) -> (int, int):
        unknown_list = []
        for row in range(self.height):
            for column in range(self.width):
                if self.knowledge[column, row] == CELL_UNKNOWN:
                    unknown_list.append((column, row))

        random_index = random.randrange(0, len(unknown_list))

        return unknown_list[random_index]


    def solve(self):
        pass
        # TODO
        
        
if __name__ == '__main__':
    # set up game and solver
    N = 1000
    solver = Solver(90, N, 10 * N)

    # initial guess
    solver.sweep_unknown_cell(3,3)
    solver.print_grid()

    # solve direct implications of first guess
    solver.process_queue()
    solver.print_grid()
