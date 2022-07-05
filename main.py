import time
import random

import solver

if __name__ == '__main__':
    # set up game and solver
    random.seed(123456)
    N_rows = 1000
    solver = solver.Solver(60, N_rows, 8 * N_rows)

    # start benchmarking
    t1 = time.time()
    
    # attempt to solve game
    solver.solve()

    # stop benchmarking
    t2 = time.time()
    print("time elapsed during solve: {} s".format(t2 - t1))
