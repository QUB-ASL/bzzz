import serial

class Anemometer:
    
    def __init__(self, serial_path='/dev/ttyS0', baud=115200):
        self.__ser = serial.Serial(serial_path, baud, timeout=1)
        self.__ser.reset_input_buffer()
        self.__split_data_float = None
    
    def get(self):
        while True:
            if self.__ser.in_waiting > 0:
                sensor_data = self.__ser.readline().decode('utf-8').strip()
                spilt_data = sensor_data.split()    
                self.__split_data_float = [float(x) for x in spilt_data]    
                return  

    @property
    def get_all_sensor_data(self):
        if self.__split_data_float is not None:
            return self.__split_data_float
            
    @property
    def get_3D_wind_speed(self):
        if self.__split_data_float is not None:
            return self.__split_data_float[0]

    @property
    def get_2D_wind_speed(self):
        if self.__split_data_float is not None:
            return self.__split_data_float[1]

    @property
    def get_horizontal_wind_direction(self):
        if self.__split_data_float is not None:
            return self.__split_data_float[2]

    @property
    def get_vertical_wind_direction(self):
        if self.__split_data_float is not None:
            return self.__split_data_float[3]

    @property
    def get_wind_velocities(self):
        if self.__split_data_float is not None:
            return self.__split_data_float[-3:]

    def update_sensor_data(self):
        current_all_sensor_data = self.__split_data_float
        if self.__split_data_float != self.__split_data_float:
            return self.__split_data_float

if __name__ == '__main__':
    sensor = Anemometer()
    for i in range(10):
        sensor.get()
        x = sensor.get_all_sensor_data
        y = sensor.get_wind_velocities
        print(x)
        print(y)

