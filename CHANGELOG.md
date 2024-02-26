# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

The following subsections are used:

- **Added**: new features
- **Fixed**: bug fixes
- **Changed**: other code changes


<!-- ---------------------
      v1.0.0
     --------------------- -->

## [v1.0.0] - XX February 2024

### Added

- Timer interrupt ISR 
- New 3D printed parts 
- New Python interface for the barometer 
- Refuse to arm unless throttle stick is down and switches are at the correct positions
- Motors protocol when receiver gets disconnected 
- Create `ESC_calibration.cpp`
- Read data from Terabee TOF sensor
- Read anemometer data in background; Read and save anemometer data on Pi
- Update logo
- Discord bots and documentation ; run the DiscordBot client and raspberry Pi main script on start-up

### Fixed

- Correct import names
- Documentation issues and typos
- Update `setup.py` and `platformio.ini`
- Update `README.md`
- Fix typos in `ahrs.hpp`

### Changed

- Update SETUP.md for remote access
- Update maximum attitude gains from trimmers and attitude gains
- Improve docs in `read_sbus_from_GPIO_receiver.py`
- Update ESC and buzzer pins 
- Update issue bug_report
- Update PCB's


<!-- ---------------------
      v0.2.0
     --------------------- -->

## [v0.2.0] - 28 August 2023

### Added

- First implementation of altitude hold mode.
- Data logging on Raspberry Pi (data is saved in CSV file).
- A fail-safe to shut down the drone when the receiver connection is timed-out due to a possible loss of connection.
- Yaw rate controller.
- Schematics for electronic board with ESP32.


### Fixed

- Fixed the unnecessary yawing of the drone (the drone now yaws only when commanded)
- Packaged Python code
- Fixed incompatibility between ThreeWaySwitch and bit shift operator

### Changed

- Communication protocol between ESP32 and Raspberry Pi


<!-- ---------------------
      v0.1.0
     --------------------- -->
## [v0.1.0] - 1 June 2023

### Added

- Average initial attitude computed in AHRS (see `averageQuaternion`)
- Calibrate with initial angular velocities
- Check arming switch in setup
- Check kill switch in loop
- Disarm and exit loop if killed
- Clip signals to motors
- Wait for Raspberry Pi to send data over serial

### Fixed

- Removed hard-coded magnetometer and other parameters from `main.cpp`
- Deactivate all printing while flying
- Significant fix for arming issue (new communication protocol between RPi and ESP32)

### Changed

- Change all `Serial.print` to `logSerial`
- Delete `config.cpp`
- Rename `BZZZ_VERBOSITY` to `BZZZ_LOGGING_LEVEL`
- `logSerial`, `setupBuzzer`, `buzz` and `waitForPiSerial` go to `util`
- Update hardware tests

[v0.1.0]: https://github.com/QUB-ASL/bzzz/releases/tag/v0.1.1
[v0.2.0]: https://github.com/QUB-ASL/bzzz/releases/tag/v0.2.0