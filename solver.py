from enum import Enum

import numpy as np

import mineField as mf

# possible states of knowledge of a cell
# using numerical values to simplify math
CELL_MINE = 100
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

def cell_knowledge_as_character(cell_knowledge: int) -> str:
    if cell_knowledge == CELL_MINE:
        return 'X'
    elif 0 <= cell_knowledge <= 8:
        return str(cell_knowledge)
    elif cell_knowledge == CELL_UNKNOWN:
        return '_'
    else:
        print('INVALID CELL KNOWLEDGE VALUE: {}'.format(cell_knowledge))
        assert(False)

class SolverContext:
    def __init__(self, width: int, height: int, number_of_mines: int):
        '''
        initialize the problem and the knowledge state of the solver
        '''

        self.width = width
        self.height = height
        self.number_of_mines = number_of_mines
        
        self.mine_field = mf.MineField(width=width,height=height,number_of_mines=number_of_mines)

        self.knowledge = np.full((width,height), CELL_UNKNOWN)

    def is_in_bounds(self, column: int, row: int):
        return (column >= 0) && (row >= 0) && (column < self.width) && (row < self.height)
        
    def sweep_cell(self, column: int, row: int):
        assert(is_in_bounds(self, column, row))
        
        current_cell_knowledge = self.knowledge[column, row]
        if current_cell_knowledge == CELL_MINE:
            print('SWEEPING A CELL WHERE A MINE SHOULD BE')
            self.mine_field.sweep_cell(column, row)
            print('THIS SHOULD NEVER OCCUR')
            assert(False)
        elif 0 <= current_cell_knowledge <= 8:
            assert(current_cell_knowledge == self.mine_field.sweep_cell(column, row))
        elif current_cell_knowledge == CELL_UNKNOWN:
            print('RISKY SWEEP')
            self.knowledge[column, row] = self.mine_field.sweep_cell(column, row)
            print('sweep succeeded')
        else:
            print('invalid knowledge state of a cell: {}'.format(current_cell_knowledge))
            assert(False)

    def print_grid(self):
        print('-----')
        for row in range(self.height):
            for column in range(self.width):
                print(
                    cell_knowledge_as_character(
                        self.knowledge[column, row]
                    ),
                    end='')
            print('') # newline after end of row
        print('-----')

    def neighbours(column: int, row: int):
        assert(is_in_bounds(self, column, row))

        # all neighbours
        surrounds_list = []
        surrounds_list.push((column + 1, row))     #         east
        surrounds_list.push((column + 1, row - 1)) # north - east
        surrounds_list.push((column,     row - 1)) # north
        surrounds_list.push((column - 1, row - 1)) # north - west
        surrounds_list.push((column - 1, row))     #         west
        surrounds_list.push((column - 1, row + 1)) # south - west
        surrounds_list.push((column,     row + 1)) # south
        surrounds_list.push((column + 1, row + 1)) # south - east

        # filter neighbours for being in bounds
        surrounds_list_2 = list(filter(lambda a: self.is_in_bounds(a.0, a.1), surrounds_list))

        print(surrounds_list_2)
                                
        return surrounds_list_2
        

def check_cell(solver_context: SolverContext, column: int, row: int):
    '''
    check if an implication on the surrounding cells can be made
    '''

    assert(solver_context.is_in_bounds(column, row))
    
    current_cell_knowledge = solver_context.knowledge[column, row]

    if current_cell_knowledge == CELL_MINE:
        # no information to work with
    elif current_cell_knowledge == CELL_UNKNOWN:
        # no information to work with
    elif 0 <= current_cell_knowledge <= 8:
        N_neighbour_mines = current_cell_knowledge

        # count number of surrouning cells that we know have a mine
        # count number of surrounding cells that we don't know the knowledge of; the cells that might still contain a mine
        neighbour_list = solver_context.neighbours(column, row)

        N_unknown_neighbours = 0
        N_found_neighbour_mines = 0

        for neighbour in neithbour_list:
            (current_neighbour_column, current_neighbour_row) = neighbour
            assert(solver_context.is_in_bounds(current_neighbour_column, current_neighbour_row)
            current_neighbour_knowledge = solver_context.knowledge[current_neighbour_column, current_neightbour_row]
            if current_neighbour_knowledge == CELL_MINE:
                N_found_neighbour_mines += 1
            elif current_neighbour_knowledge == CELL_UNKNOWN:
                N_unknown_neighbours += 1
            elif:
                assert(0 <= current_neighbour_knowledge <= 8)

        N_hidden_mines = N_neighbour_mines - N_found_neighbour_mines

        if N_hidden_mines == 0:
            # all unknown neighbours must be safe

            # TODO -------------------------------------------------------------------------------------------------------------------------------------------------
            # sweep all unknown neighbours
            # mark all unknown neighbours and neighbours of newly sweeped neighbours as dirty
                   
        elif N_hidden_mines < N_unknown_neighbours:
            # nothing can be inferred from this information
        elif N_hidden_mines == N_unknown_neighbours:
            # all unknown neighbours contain mines

            # TODO -------------------------------------------------------------------------------------------------------------------------------------------------
            # flag all unknown neighbours as mines
            # mark all neighbours of newly flagged mines as dirty
            
        else:
            print('INVALID STATE')
            assert(False)
                   
    else:
        print('INVALID CELL KNOWLEDGE STATE: {}'.format(current_cell_knowledge))

        
if __name__ == '__main__':

    print('Hello, world')

    solver_context = SolverContext(10, 10, 10)

    solver_context.sweep_cell(1,1)
    print(solver_context.knowledge[1,1])
    solver_context.print_grid()
    
    solver_context.sweep_cell(1,8)
    print(solver_context.knowledge[1,8])
    solver_context.print_grid()
    
    solver_context.sweep_cell(3,1)
    print(solver_context.knowledge[3,1])
    solver_context.print_grid()
    
    solver_context.sweep_cell(4,5)
    print(solver_context.knowledge[4,5])
    solver_context.print_grid()
