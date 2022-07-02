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

    def sweep_cell(self, column: int, row: int):
        assert(column >= 0)
        assert(row >= 0)
        assert(column < self.width)
        assert(row < self.height)

        
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
