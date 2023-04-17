# read_sbus
[`read_sbus`](https://github.com/VermontCoder/read_sbus) is a module for the Rasperry Pi to read SBus protocol input. SBus is a protocol used by many RC receivers to send data to flight controllers to control RC aircraft,
quadcopters or cars. SBus has an advantage over standard PWM in that up to 16 channels of data can be sent over a single data line.

## Software Requirements
`read_sbus` makes use of two libraries.

- the [pigpio](https://abyz.me.uk/rpi/pigpio/) library. That can be installed as follows

```
sudo apt-get update
sudo apt-get install pigpio python-pigpio python3-pigpio 
```

- the [bitarray](https://pypi.org/project/bitarray/) library. That can be installed as follows 

```
pip install bitarray
```

## Raspberry Pi with ESP32
The raspberry Pi will be used for any high level control, while the ESP32 is used for the low level control (attitude control). 
Currently the Pi is used to receive the radio data and send it to the ESP32. In order to do this the file [`read_sbus_from_GPIO_receiver.py`](https://github.com/QUB-ASL/bzzz/blob/feature/raspberry-readsbus/raspberry/read_sbus/read_sbus_from_GPIO_receiver.py) was created. The radio data is sent from the Pi to the ESP32 via serial.

To receive data from the radio remote control and send it to the ESP32 open a terminal on Raspberry Pi and execute the following 
```
sudo pigpiod
python3 bzzz/raspberry/read_sbus/read_sbus_from_GPIO_receiver.py
```


## Hardware Test
In order to check that the receiver is connected to the Pi correctly and the remote control and reciever are bound properly, the file [`hw_test_receiver.py`](https://github.com/QUB-ASL/bzzz/blob/feature/raspberry-readsbus/hardware/tests/hw_test_receiver.py) was created. The data that is received from the reciever will be printed.

To test the Pi is receiving the correct data open a terminal on Raspberry Pi and execute the following 
```
sudo pigpiod
python3 bzzz/hardware/tests/hw_test_receiver.py
```

## Reference 
For more information on the `read_sbus` module visit https://github.com/VermontCoder/read_sbus
