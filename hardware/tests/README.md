# Hardware tests

## AHRS test
The AHRS hardware test tests the intertial measurement unit's euler angles, 
quaternion angles and angular velocities. Copy and paste the `hw_test_ahrs.cpp` 
code into the main. Follow the instructions provided in the code to complete the hardware test.
## Motor test
The motor test spins has two modes the first of which runs the motors up to speed for 1 second
and then stops them for 1 second, this process is looped. The second test mode throttles the motors sinusoidall.
Copy and paste the `hw_test_motors.cpp` file into the main to run the first test.
To run the second test comment out the first test and then uncomment the second. 
## Motor and kill switch test
