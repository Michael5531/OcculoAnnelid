import statistics as s


def classify_data(data, rate=10000):
    """
    Return 'left', 'right', or None.
    """
    streaming_result = streaming_classifier(data, rate)


def streaming_classifier(wave_data, samp_rate, threshold_events=500):
    window_size = samp_rate

    test_stat = s.stdev(wave_data)

    if test_stat > threshold_events:
        predicted = left_right_detection(wave_data)
        print(predicted)
        return predicted
    else:
        predicted = "None"
        print(predicted)
        return predicted


# This is where ML can replace deterministic heuristic
def left_right_detection(wave_data):
    max_val = wave_data.index(max(wave_data))
    min_val = wave_data.index(min(wave_data))
    if max_val < min_val:
        return 'left'
    else:
        return 'right'
