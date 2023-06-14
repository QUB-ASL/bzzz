def median_filter(data_list: list, window_length: int = 5):
    data_list = data_list[-window_length:]  # take the latest values
    data_list.sort()
    idx = window_length//2
    return (data_list[idx] + data_list[-idx - 1])/2