import numpy as np
import abc


class DataProcessor(abc.ABC):
    """Abstract data processor"""

    def __init__(self):
        pass

    @abc.abstractmethod
    def process(self, data, cursor=0):
        """
        Data processing method (abstract; no implementation)

        :param data: numpy array of data  
        :param cursor: index of the *current* measurement 
        """
        pass


class AverageFilter(DataProcessor):
    """Moving average filter"""

    def __init__(self):
        super().__init__()

    def process(self, data, cursor=0):
        return np.nanmean(data, axis=0)


class MedianFilter(DataProcessor):
    """
    Median filter

    The median filter is recommended to be used when the window size is odd.
    """

    def __init__(self):
        super().__init__()

    def process(self, data, cursor=0):
        return np.nanmedian(data, axis=0)


class NoFilter(DataProcessor):
    """No filter: the latest data point is returned"""

    def __init__(self):
        super().__init__()

    def process(self, data, cursor):
        return data[cursor]
