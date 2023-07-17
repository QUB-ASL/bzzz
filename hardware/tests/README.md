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
The motors in this test respond to throttle commands from the RC remote. Test requires the kill switch to be armed.
In this test the operator will hear a series of beeps from the buzzer:
- 2 beeps = AHRS setup complete.
- 4 beeps = RC and RaspberryPi connected.
- 2 long beeps = Prepered for arming.
- 6 beeps = Motors armed.
  
[comment]: <> (This is a comment, it will not be included)
To run the test, copy and paste the `hw_test_motors_with_arm_kill.cpp` into main.

## Motor test with RC
In this test the motors respond to the throttle commands from the RC.
To run the test copy and paste the `hw_test_motors_with_receiver.cpp` into main.
