def median_filter(data_list: list, window_length = 5):
    """Applies median filter of given window length.

    :param data_list: Data list on which the filter is to be applied.
    :param window_length: filter window length, must be and int, defaults to 5
    :return: retruns the median of the given data.
    """
    data_list = data_list[-window_length:]  # take the latest values
    data_list.sort()
    idx = window_length//2
    return (data_list[idx] + data_list[-idx - 1])/2