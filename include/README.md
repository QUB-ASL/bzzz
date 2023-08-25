# Embedded ESP32 C++ code

**About:** This software runs on the ESP32. Its job is
- To receive data from the Serial (provided by the Raspberry Pi) and parse it
- To run the attitude control algorithm
- To implement certain safety mechanisms (arming, killing, etc)

## Contents

The following files are included

| File              | Description |
| ----------------- | ----------- |
| `ahrs.hpp`        | AHRS system (reads IMU measurements, calibrates the IMU, interfaces the Madgwick filter) |
| `config.hpp`      | various constants |
| `controller.hpp`  | attitude control system |
| `fail_safe.hpp`   | checks whether the serial is connected |
| `motors.hpp`      | interface for the four motors |
| `quaternion.hpp`  | quaternion algebra |
| `util.hpp`        | logging, buzzing, and other utils |

The implementations are in [`../src`](../src)


## Communication protocol

### Raspberry Pi to ESP32

The EPS32 receives over the serial the following message

```
S, yaw_rate_reference, pitch_reference_rad, roll_reference_rad, throttle_reference, trimmer_a_prcnt, trimmer_b_prcnt, trimmer_c_prcnt, trimmer_e_prcnt, encoded_switches
```

where `yaw_rate_reference` is the yaw reference rate (left stick, horizontal) in rad/sec, `pitch_reference_rad` is the pitch reference angle in rad (right stick, vertical), `roll_reference_rad` is the roll reference angle in rad (right stick, horizontal), `throttle_reference` is the throttle reference (left stick, vertical), `trimmer_a_prcnt`, `trimmer_b_prcnt` and `trimmer_c_prcnt` are the positions of the three trimmers as a number between 0 and 1, `trimmer_e_prcnt` is the position of trimmer E (right side of the RC), and lastly `encoded_switches` are the switches A, B, C, and D encoded as follows:

- bit-4 (MSB): 1-bit info of Switch B: 1 if armed else 0
- bit-3: 1-bit info of Switch A: 1 if kill_on else 0
- bits 2 and 1: 2-bit info of switch C: 00 for position DOWN, 01 for position MID, 10 for position UP
- bit-0: 1-bit info of switch D: 1 if D_on else 0

### ESP32 to Raspberry Pi

The ESP sends the following message over the serial

```
FD: q1 q2 q3 ax ay az motorFL motorFR motorBL motorBR
```

where `q1`, `q2`, `q3` are the vector part of the quaternion, `ax`, `ay`, `az` are the acceleration measurements from the IMU, `motorFL`, `motorFR`, `motorBL`, and `motorBR` are the PWM signals to the four motors.
 
## Headers 

This directory is intended for project header files.

A header file is a file containing C declarations and macro definitions
to be shared between several project source files. You request the use of a
header file in your project source file (C, C++, etc) located in `src` folder
by including it, with the C preprocessing directive `#include'.

```c++
// File: src/main.c

#include "header.h"

int main (void)
{
 ...
}
```

Including a header file produces the same results as copying the header file
into each source file that needs it. Such copying would be time-consuming
and error-prone. With a header file, the related declarations appear
in only one place. If they need to be changed, they can be changed in one
place, and programs that include the header file will automatically use the
new version when next recompiled. The header file eliminates the labor of
finding and changing all the copies as well as the risk that a failure to
find one copy will result in inconsistencies within a program.

In C, the usual convention is to give header files names that end with `.h'.
It is most portable to use only letters, digits, dashes, and underscores in
header file names, and at most one dot.

Read more about using header files in official GCC documentation:

* Include Syntax
* Include Operation
* Once-Only Headers
* Computed Includes

https://gcc.gnu.org/onlinedocs/cpp/Header-Files.html
