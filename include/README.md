# Embedded ESP32 C++ code

**About:** This software runs on the ESP32. Its job is
- To receive data from the Serial (provided by the Raspberry Pi) and parse it
- To run the attitude control algorithm
- To implement certain safety mechanisms (arming, killing, etc)

## Contents

The following files are included

| `ahrs.hpp`        | AHRS system (reads IMU measurements, calibrates the IMU, interfaces the Madgwick filter) |
| `config.hpp`      | various constants |
| `controller.hpp`  | attitude control system |
| `fail_safe.hpp`   | checks whether the serial is connected |
| `motors.hpp`      | interface for the four motors |
| `quaternion.hpp`  | quaternion algebra |
| `util.hpp`        | logging, buzzing, and other utils |

The implementations are in [`../src`](../src)
 
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
