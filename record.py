import sys
import serial
import numpy as np
import matplotlib.pyplot as plt
import datetime
import time
import re
import csv

from src.occutools import process_byte_data, filter_noise, dummy_plug
from src import spikerinfo

from catch22 import catch22_all

# Set the correct buffer size for the serial based on the desired length of the window.
window_length = 2  # Window length in seconds. Set to 0.25 or 0.5, as these are the only possibilities in the game.
input_buffer_size = None  # Determines frequency of buffer filling up. 20000 = 1s.
if window_length == 0.5:
    input_buffer_size = 10000
elif window_length == 0.25:
    input_buffer_size = 5000
elif window_length == 1:
    input_buffer_size = 20000
elif window_length == 2:
    input_buffer_size = 40000
assert input_buffer_size is not None
timeout = None

# Set Dummy Plug flag
dummy_flag = False
if '--dummy' in sys.argv:
    dummy_flag = True

# Save the user's port for 1 minute to save time with repeated data entry.
c_port = None
try:
    with open('./data/log.txt') as log_file:
        log = log_file.read(1000)
        log_lines = log.splitlines()

        then_string = log_lines[1]
        then = float(
            re.fullmatch(r'time:\t(\d*\.\d*)', then_string).group(1)
        )
        now = time.time()

        # If last recording was within the last 1 minute.
        if now - then <= 300:
            port_string = log_lines[2]
            c_port = re.fullmatch(r'port:\t([\w\d/\\]*)', port_string).group(1)
            if not dummy_flag:
                print(f'Using previous port: {c_port}')
        else:
            c_port = None
except FileNotFoundError:
    print('Log file not found.')
except IOError:
    print('File not accessible.')
except IndexError:
    print('Log file is corrupted. Ignoring.')


# Create fake data to act as if it were a spikerbox.
if dummy_flag:
    wave = dummy_plug(input_buffer_size)
    print(f'Using dummy input. Wave resolution: {len(wave)}')

else:
    if c_port is None:
        c_port = input('Which port?\n')

    # Instantiate Serial.
    try:
        ser = serial.Serial(port=c_port, baudrate=spikerinfo.baud_rate)
        # ser.set_buffer_size(rx_size=input_buffer_size)
        ser.timeout = timeout
    except serial.serialutil.SerialException:
        raise Exception(f'Could not open port {c_port}.\nFind port from:\nDevice Manager > Ports (COM & LPT) [Windows]')

    # Read from serial.
    with ser as s:

        # Countdown
        print('2')
        time.sleep(1)
        print('1')
        time.sleep(1)
        print('Recording...')

        byte_data = s.read(input_buffer_size)

    # Process and filter.
    wave = process_byte_data(
        [int(byte_data[i]) for i in range(len(byte_data))]
    )
    wave = filter_noise(wave)
    print(f'Input read, processed and filtered. Wave resolution: {len(wave)}')

# Extract features.
features = catch22_all(wave)['values']
print(f'Features extracted: {features}')


abort_flag = False
classification = None
class_dict = {'l': 'Left', 'r': 'Right', 'b': 'Blink', 's': 'Still'}

# Manually classify the data.
if not abort_flag:
    response = ''
    while response not in {'l', 'r', 'b', 's', 'a'}:
        response = input('What eye movement did you make? [L]eft / [R]ight / [B]link / [S]till / [A]bort\n').lower()
    if response == 'a':
        abort_flag = True
    else:
        classification = response

# Plot wave and confirm from plot that no recording errors have occurred.
if not abort_flag:
    ts = np.linspace(0, len(wave) / spikerinfo.sample_rate, len(wave))
    fig, ax = plt.subplots()
    ax.plot(ts, wave)
    ax.set_xlabel('Time')
    ax.set_ylabel('Amplitude')
    ax.set_title('Recorded Data')
    plt.savefig('./data/waveform.png', format='png')
    plt.show(block=False)

    response = ''
    while response not in {'y', 'a'}:
        response = input('Confirm that the waveform is without any drastic errors. [y] / [A]bort\n').lower()
    if response == 'a':
        while not response.isalnum():
            response = input('Are you sure? Too many false positives can introduce bias into the data. '
                             'Confirm [A]bort or press any other key to cancel.\n').lower()
        if response == 'a':
            abort_flag = True
    if response == 'y':
        pass

    plt.close()

# Final confirmation.
if not abort_flag:
    assert classification is not None

    print(f"Features to be classified as '{class_dict[classification]}.'")

    response = ''
    while response not in {'y', 'a'}:
        response = input('Final chance to [A]bort data. Press [y] to confirm.\n').lower()
    if response == 'a':
        abort_flag = True


# Possible abort.
if abort_flag:
    print('Data acquisition aborted.')
    sys.exit(0)


# Write to output.
try:
    with open('./data/out.csv', 'a') as data_file:
        writer = csv.writer(data_file)
        writer.writerow([class_dict[classification]] + features)
except IOError as err:
    print('Could not write to output due to IOError:')
    print(err)
    sys.exit(0)


# Write to log file.
try:
    with open('./data/log.txt', 'w') as log_file:
        log_file.write(f'datetime:\t{datetime.datetime.now().ctime()}\n')
        log_file.write(f'time:\t{time.time()}\n')
        log_file.write(f'port:\t{c_port}\n')
except IOError as err:
    print('Could not write to log due to IOError:')
    print(err)
    sys.exit(0)
