import datetime
import time
from bzzz.sensors.evo_time_of_flight import EvoSensor
from bzzz.sensors.pressure_sensor import BMP180Sensor
from bzzz.sensors.filters import AverageFilter, MedianFilter

if __name__ == "__main__":
    EVO_filename = datetime.datetime.now().strftime("Evo-ToF-%d-%m-%y--%H-%M.csv")
    BAR_filename = datetime.datetime.now().strftime("PressureSensor-%d-%m-%y--%H-%M.csv")
    processor = MedianFilter()  # You need to define this class based on your requirements
    keep_running = True
    with (EvoSensor(window_length=3,  
                    data_processor=processor,  
                    log_file=EVO_filename) as tof, 
          BMP180Sensor(log_file=BAR_filename) as barometer):
        
        for i in range(60):
                print("analysing...")
                time.sleep(1)
            
