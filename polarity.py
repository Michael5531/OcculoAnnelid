import serial
import matplotlib.pyplot as plt
import numpy as np
from src.occutools import process_byte_data, filter_noise
from src import spikerinfo

"""
A handy user-interfaced way to check the polarity of the electrodes are correctly attached.
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

polarity_confirmed_flag = False

while not polarity_confirmed_flag:
    input('Confirm electrodes polarity (any key to start recording).\n')
    print('Recording...')
    with ser as s:
        byte_data = s.read(input_buffer_size)
    wave = process_byte_data(
        [int(byte_data[i]) for i in range(len(byte_data))]
    )
    wave = filter_noise(wave)
    ts = np.linspace(0, len(wave) / spikerinfo.sample_rate, len(wave))
    fig, ax = plt.subplots()
    ax.plot(ts, wave)
    ax.set_xlabel('Time')
    ax.set_ylabel('Amplitude')
    ax.set_title('Recorded Data.')
    plt.savefig('./polarity.png', format='png')
    plt.show(block=False)

    response = ''
    while response not in {'y', 'n'}:
        response = input('Confirm that looking left produces a positive spike. [y]/[n]\n').lower()
    if response == 'y':
        polarity_confirmed_flag = True
    if response == 'n':
        print('Reverse attachment of electrodes.')
        polarity_confirmed_flag = False
