import numpy as np
import datetime
import csv


class DataLogger:
    """A data logger to be used with a sensor"""

    def __init__(self, num_features, max_samples=10000, feature_names=None):
        """
        Construct a new instance of DataLogger

        :param num_features: number of features
        :param max_samples: buffer size (maximum number of samples); default: 10000
        :param feature_names: list of feature names (str)
        """
        self.__data_vault = np.zeros(
            (max_samples, num_features), dtype=np.float64)
        self.__timestamps_vault = np.array(
            [datetime.datetime.now()] * max_samples)
        self.__feature_names = feature_names
        self.__cursor = 0

    def record(self, timespamp, datum):
        """
        Record/log data in memory

        :param timestamp: timestamp of measurement(s)
        :param datum: measurement (float or numpy array)
        """
        self.__data_vault[self.__cursor, :] = datum
        self.__timestamps_vault[self.__cursor:] = timespamp
        self.__cursor = self.__cursor + 1

    def save_to_csv(self, filename):
        """
        Save the data to a CSV file

        :param filename: file name (relative or absolute path)
        """
        with open(filename, "w") as fh:
            writer = csv.writer(fh)
            writer.writerow(self.__feature_names)
        with open(filename, "a+") as fh:
            writer = csv.writer(fh)
            data_to_record = np.hstack((np.reshape(self.__timestamps_vault[:self.__cursor], (
                self.__cursor, 1)), self.__data_vault[:self.__cursor, :]))
            writer.writerows(data_to_record)
