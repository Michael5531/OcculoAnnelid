from csv import reader

# diag -> 7 left, 5 right
# original -> left, right, blink, still
# updown -> 5 left, 5 right
# wide -> 5 left, 5 right

with open('./data/raw_signal_diag_Karl_4_6.csv', 'r') as csv_file:
    reader = reader(csv_file)
    for row in reader:
        print(row)
        break

# 1. Determine a threshold for each row, value must be within range to avoid noise
# 2. Find maximum amongst those values
# 3. Find minimum amongst those values
# 4. Max or min index comes first?
#   4.1 max_ind > min_ind == right movement
#   4.2 max_ind < min_ind == left movement

# start end time around the if statement??