# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

The following subsections are used:

- **Added**: new features
- **Fixed**: bug fixes
- **Changed**: other code changes

<!-- ---------------------
      v0.2.0
     --------------------- -->

## [v0.2.0] - 14 June 2023

### Added

- A fail-safe to shut down the drone when the receiver connection is timed-out due to a possible loss of connection.
- Yaw rate based controller.

### Fixed

- Fixed the unnecessary Yawing of the drone. The drone now Yaws only when commanded.

### Changed

- Implemented the fail-safe on `fail_safes.hpp` and `fail_safes.cpp`
- Added configurable fail-safe time-out macro to `config.cpp`
- Changed `read_sbus_from_GPIO_receiver.py` to stop sending data to ESP when the radio connection is lost.
- Modified `main.cpp` to utilize the fail-safe.


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