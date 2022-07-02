from enum import Enum
from random import randrange
from typing import Tuple

BEGINNER_FIELD = {'width': 10, 'height': 10, 'number_of_mines': 10}
INTERMEDIATE_FIELD = {'width': 16, 'height': 16, 'number_of_mines': 40}
EXPERT_FIELD = {'width': 30, 'height': 16, 'number_of_mines': 99}


class ExplosionException(Exception):
    pass


class CellStatus(Enum):
    SAFE = 0
    MINE = 1


class MineField:
    '''The mine field for the mine sweeper'''
    def __init__(self, *, width: int, height: int, number_of_mines: int):
        '''Init of the class
        
        Keyword arguments:
        width -- the width of the mine field
        height -- the height of the mine field
        number_of_mines -- hoe many mines will be generated'''

        # Check inputs
        if not isinstance(width, int) or not isinstance(height, int) or not isinstance(number_of_mines, int):
            raise TypeError("All inputs must be of type int")
        if width <= 0:
            raise ValueError("Width must be greather than 0")
            
        if height <= 0:
            raise ValueError("Height must be greather than 0")
            
        if number_of_mines < 0:
            raise ValueError("Number of mines must be greather than or equal to 0")

        if number_of_mines >= (width * height):
            raise ValueError("Number of mines may not be larger than or equal to width * height")

        # Empty field
        self.__field = None
        self.__width = width
        self.__height = height
        self.__number_of_mines = number_of_mines

    def __fill_mine_field(self, first_row, first_column) -> None:
        '''Fill the mine field, but keep the first hit cell mine-free
        
        Arguments:
        first_row -- The cell on this row shall not have a mine
        first_column -- The cell on this column shall not have a mine
        '''
        self.__field = [ [ CellStatus.SAFE] * self.__width for _ in range(self.__height) ]

        # Fill with mines
        mines_left = self.__number_of_mines
        while mines_left > 0:
            # get a random number
            random_index = randrange(0, self.__width * self.__height)
            column = random_index % self.__width
            row = random_index // self.__width
            if (row, column) != (first_row, first_column) and self.__field[row][column] == CellStatus.SAFE:
                self.__field[row][column] = CellStatus.MINE
                mines_left -= 1
        
    def sweep_cell(self, column: int, row: int) -> int:
        '''Sweep a cell at column, row
        
        Arguments:
        column -- the column of the cell to sweep
        row --- the row of the cell to sweep
        
        Returns:
        number of adjacent mines
        
        Throws:
        ExplosionException
        '''

        if (0 > row) or (row >= self.__height):
            raise ValueError("0 < row >= self.__height")
        if (0 > column) or (column >= self.__width):
            raise ValueError("0 < column >= self.__width")

        # Fill the mine field if it is not created yet
        if not self.__field:
            self.__fill_mine_field(first_row=row, first_column=column)

        # Stepped on mine?
        if self.__field[row][column] == CellStatus.MINE:
            raise ExplosionException()

        adjacent_mines = 0

        # Look into the adjacent cells
        # N
        if (row > 0) and (self.__field[row - 1][column] == CellStatus.MINE):
            adjacent_mines += 1
        # S
        if (row < (self.__height - 1)) and (self.__field[row + 1][column] == CellStatus.MINE):
            adjacent_mines += 1
        # W
        if (column > 0) and (self.__field[row][column - 1] == CellStatus.MINE):
            adjacent_mines += 1
        # E
        if (column < (self.__width - 1)) and (self.__field[row][column + 1] == CellStatus.MINE):
            adjacent_mines += 1
        # NW
        if (row > 0) and (column > 0) and (self.__field[row - 1][column - 1] == CellStatus.MINE):
            adjacent_mines += 1
        # NE
        if (row > 0) and (column < (self.__width - 1)) and (self.__field[row - 1][column + 1] == CellStatus.MINE):
            adjacent_mines += 1
        # SE
        if (row < (self.__height - 1)) and (column < (self.__width - 1)) and (self.__field[row + 1][column + 1] == CellStatus.MINE):
            adjacent_mines += 1
        # SW
        if (row < (self.__height - 1)) and (column > 0) and (self.__field[row + 1][column - 1] == CellStatus.MINE):
            adjacent_mines += 1

        return adjacent_mines
