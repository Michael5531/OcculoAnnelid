import matplotlib.pyplot as plt
import sys
import wave
import time
import numpy as np
import wave
import pandas as pd
from classifier import classify_data
from classifier import streaming_classifier
from classifier import left_right_detection


### --- Read the wave file ---
wave_file = wave.open('Training Data/periodic_right/periodic_right_damian.wav')
params = wave_file.getparams()
nch = wave_file.getnchannels()

### --- Get samp rate and frame rate ---
samp_rate = wave_file.getframerate() # 10000
frame_rate = wave_file.getnframes() # 316552

### --- Visualize the Wave file --- 
# Extract Raw Audio from Wav File
signal = wave_file.readframes(-1)
signal = np.fromstring(signal, "Int16") # 316552

# If Stereo
if wave_file.getnchannels() == 2:
    print("Error")
    sys.exit(0)

Time = list(np.linspace(0, len(signal) / samp_rate, num=len(signal)))

### --- Iterate wave file and generate a time sequence list ---
a = np.column_stack((Time, signal))
df = pd.DataFrame(a, columns = ['Time','Signal'])

time_use = df["Time"]
signal_use = df["Signal"]

def get_time_seq(frame_rate):
    time_seq = []
    i = 1
    while i < frame_rate + 1:
        time_seq.append(i / samp_rate)
        i += 1
    return time_seq


# def streaming_classifier(wave_data, samp_rate, threshold_events=500):
#     window_size = samp_rate

#     predicted_labesl = []
#     predicted_time = []

#     lower_interval = 1

#     xtime = get_time_seq(frame_rate)
#     max_time = max(xtime)*window_size

    

#     # testStat = sum(interval[1:(len(interval) - 1)] * interval[2:(len(interval))] <= 0)

#     while (max_time > lower_interval + window_size):
#         # upper_interval = lower_interval + window_size
#         # interval = wave_data.loc[lower_interval:upper_interval]

#         # test_stat = wave_data['Time'].std()

#         # testStat = sum(interval[1:len(interval) - 1] * interval[2:(len(interval))] <= 0)
#         # print(testStat)
        


#     if test_stat > threshold_events:
#         predicted = left_right_detection(wave_data)
#         print(predicted)
#         return predicted
#     else:
#         predicted = "None"
#         print(predicted)
#         return predicted

# a = streaming_classifier(df, samp_rate, 5000)
# print(a)


wave_data = df
window_size = samp_rate

lower_interval = 1
upper_interval = lower_interval + window_size
interval = wave_data.loc[lower_interval:upper_interval]

test_stat = wave_data['Time'].std()

# print(interval[1:len(interval) - 1].sum())


# print(interval[2:(len(interval))])

testStat = (interval[1:len(interval) - 1] * interval[2:(len(interval))] <= 0).sum()
print(testStat)




