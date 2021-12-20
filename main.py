# Basics
import serial
import numpy as np
import csv

# Source
from src.occutools import process_byte_data, filter_noise
from src import spikerinfo

# Catch22
from catch22 import catch22_all

# Sklearn
from sklearn.ensemble import RandomForestClassifier

# Snake
from turtle import *
from snake import move

"""
Responsible for controlling the main control loop of the game.
"""

# Set the correct port and buffer size for the serial.
c_port = input('Which port?\n')
input_buffer_size = 40000  # Determines frequency of buffer filling up. 20000 = 1s.
timeout = None

try:
    ser = serial.Serial(port=c_port, baudrate=spikerinfo.baud_rate)
    # ser.set_buffer_size(rx_size=input_buffer_size)  # Seems to be causing bugs on Mac/Linux and redundant on Windows.
    ser.timeout = timeout
except serial.serialutil.SerialException:
    raise Exception(f'Serial exception occurred.')


# Read training data from csv.
print('Training random forest classifier...')
train_X, train_y = None, None
try:
    with open('./data/trainer.csv') as csv_file:
        reader = csv.reader(csv_file)
        train_combined = [row for row in reader]

        train_X = [row[1:] for row in train_combined]
        train_X = np.asarray(train_X, dtype=np.float64)

        train_y = [row[0] for row in train_combined]
        train_y = np.asarray(train_y)
except FileNotFoundError:
    print('Data file not found.')
except IOError:
    print('Data file not accessible.')
assert train_X is not None
assert train_y is not None

ml_object = RandomForestClassifier(n_estimators=100)

# Fit machine learning algorithm to our data.
ml_object.fit(train_X, train_y)
print('Random forest classifier trained.', end='\r')

with ser as s:
    setup(1000, 1000, 370, 0)
    hideturtle()
    tracer(False)
    listen()
    # Set initial snake direction.
    snake_direction = 'Down'

    # Create a buffer for classifying, implement 'treadmill algorithm'.

    # Treadmill algorithm:
    # In the case that we receive a new window with an eye-movement on the window boundary:
    #                   A[------Le]
    # It may be classified as 'Still', since part of the 'Left' waveform is not yet in the classifier.
    #                   A[------Le] --> 'Still'
    # If this is the case, then we wouldn't want to throw away window A, we just classify it as 'Still'.
    # When a new window arrives, it pushes the other windows down the treadmill:
    #       A[------Le] B[ft------]
    # If there are multiple windows on the treadmill, we take their concatenation to the classifier:
    #       A[------Le] B[ft------] --> 'Left'
    # Once we reach a non-'Still' classification, we are satisfied, and also it would interfere with future
    # classifications if we kept it on the treadmill. So we intervene and kick them off the treadmill:
    #                   C[--------] --> 'Still'
    #       C[--------] D[--Right-] --> 'Right'
    #                   E[-Blink--] --> 'Blink'
    prev, curr = None, None

    while True:
        # Read, process and filter data.
        byte_data = s.read(input_buffer_size)
        curr = process_byte_data(
            [int(byte_data[i]) for i in range(len(byte_data))]
        )
        curr = filter_noise(curr)

        # Feed prev and curr into a single array.
        if prev is None:
            data = curr
        else:
            data = np.append(prev, curr)

        # Convert data to feature array.
        features = np.asarray([catch22_all(data)["values"]])

        # Classify feature list with sklearn Random Forest model.
        direction = ml_object.predict(features)

        if direction == 'Left':
            print('Classifier output: Left')
            prev, curr = None, None
        elif direction == 'Right':
            print('Classifier output: Right')
            prev, curr = None, None
        elif direction == 'Still':
            print('Classifier output: Still')
            prev, curr = curr, None
        elif direction == 'Blink':
            print('Classifier output: Blink')
            prev, curr = curr, None

        # Change direction of snake based on the classification.
        snake_direction = move(direction, snake_direction)
        print("")
