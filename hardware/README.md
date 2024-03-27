## Tests

## ESC_calibration.cpp
This to to calibrate Hobbywing Skywalker ESC only. If another ESC is being used it may require recoding.

The signal to the ESC is set high before the power is provided to the ESC. 
This sets it to calibration mode.
After a particular delay the signal to the ESC is set back to low which completes the calibration. 

### Step to calibrate ESC
${\color{red}REMOVE \space PROPELLERS \space FROM \space QUADCOPTER}$
* Take the code from `ESC_calibration.cpp` and paste it to the `main.cpp`
* Flash it to the ESP32
* Power on the ESC
* 2 short beeps (from ESCs) would confirm that the ESC is in calibration mode
* 3 short beeps (from ESCs) and 1 long beep would confirm that the ESC is calibrated.
