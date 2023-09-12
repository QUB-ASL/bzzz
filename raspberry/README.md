# bzzz python package

This package contains the entire Python code to be running on Raspberry Pi. 
The following features are currently available:

1. Kalman filter estimator for altitude hold dynamics related parameter estimation.
2. Reading RC data and parsing it to ESP.
3. Altitude hold dynamics simulations.

## Installation

Firstly, you need to install and run the [Pi GPIO daemon](http://abyz.me.uk/rpi/pigpio/pigpiod.html).

Then, create a virtual environment (if you haven't done so already)

```bash
virtualenv -p python3 venv
```

Then, activate the virtual environment

```bash
source venv/bin/activate
```

Next, you need to install this package

```bash
cd raspberry
pip install .
```

You can now run the main file. 

```bash
python main.py
```
