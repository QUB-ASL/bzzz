# bzzz python package

This package contains the entire Python code to be running on Raspberry Pi. 
The following features are currently available:

1. Kalman filter estimator for altitude hold dynamics related parameter estimation.
2. Reading RC data and parsing it to ESP.
3. Altitude hold dynamics simulations.

## Installation

If you are setting up a Raspberry Pi from scratch we would recommend following the [SET_UP](docs/SET_UP.md) document.

## Dependencies
There are a few packages that can not be installed in the virtual environment by `pip` therfore should be instaled system wide.

To do this run
```
sudo apt-get install libopenblas-dev libatlas-base-dev
```


## virtual environment
Next a virtual environment can be created by (we have tested this with Python 3.11.2):
```
python -m venv venv_bzzz
```
For older versions of python use:
```
virtualenv -p python3 venv_bzzz
```

Then, activate the virtual environment
```
source  venv_bzzz/bin/activate
```

and install the requaried packages.
```
cd bzzz/raspberry
pip install .
```

Now the `main.py` script can be ran by:
```
sudo pigpiod
python main.py
```


## How to run the main Raspberry Pi code on start-up
After the virtual environment and dependencies have been installed as described above, a script can be used to atuomatically run the main Raspberry
Pi code on start-up.

To do this, the `run_main_on_start_up.sh` can be added to the users crontab by:

```
crontab -e
```
Then add the following:

```
@reboot sleep 10 && ~/bzzz/raspberry/run_main_on_start_up.sh
```
