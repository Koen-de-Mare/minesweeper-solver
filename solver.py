import mineField as mf

print("Hello, world")

mine_field = mf.MineField(width=10,height=10,number_of_mines=10)

print(mine_field.sweep_cell(1,1))
print(mine_field.sweep_cell(3,5))
print(mine_field.sweep_cell(0,9))
print(mine_field.sweep_cell(9,0))

