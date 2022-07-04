import solver

if __name__ == '__main__':
    # set up game and solver
    N_rows = 100
    solver = solver.Solver(60, N_rows, 8 * N_rows)

    # attempt to solve game
    solver.solve()
