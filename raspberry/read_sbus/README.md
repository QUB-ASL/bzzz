# read_sbus
[`read_sbus`](https://github.com/VermontCoder/read_sbus) is a module for the Rasperry Pi to read SBus protocol input. SBus is a protocol used by many RC receivers to send data to flight controllers to control RC aircraft,
quadcopters or cars. SBus has an advantage over standard PWM in that up to 16 channels of data can be sent over a single data line.

`read_sbus` makes use of two libraries.

- the [pigpio](https://abyz.me.uk/rpi/pigpio/) library. That can be installed as follows

```
sudo apt-get update
sudo apt-get install pigpio python-pigpio python3-pigpio. That can be installed as follows 
```

- the [bitarray](https://pypi.org/project/bitarray/) library. That can be installed as follows 

```
pip install bitarray
```

## Test

To test the Pi is receiving the correct data open terminal on Raspberry Pi and execute the following 
```
sudo pigpiod
```
```
python bzzz/hardware/tests/hw_test_receiver.py
```

## Reference 

For more information on the `read_sbus` module visit https://github.com/VermontCoder/read_sbus
