# Hardware tests

## AHRS test
The AHRS hardware test tests the inertial measurement unit's Euler angles, 
quaternion angles and angular velocities. Copy and paste the `hw_test_ahrs.cpp` 
code into the `main.cpp`. Follow the instructions provided in the code to complete the hardware test.

## Motor test
The motor test has two modes the first of which runs the motors up to speed for 1 second
and then stops them for 1 second, this process is looped. The second test changes the PWM signal following a sinusoidal waveform.
Copy and paste the `hw_test_motors.cpp` file into the `main.cpp` to run the first test.
To run the second test comment out the first test and then uncomment the second one. 

## Motor and kill switch test
The motors in this test respond to throttle commands from the RC remote. Test requires the kill switch to be armed.
In this test the operator will hear a series of beeps from the buzzer:

| Beeps | Meaning |
| ----- | --------|
| 2 short | AHRS setup complete |
| 4 short | RC and Raspberry Pi connected |
| 2 long | preparation for arming |
| 6 short | Motors armed |
  
To run the test, copy and paste the `hw_test_motors_with_arm_kill.cpp` into `main.cpp`.

## Motor test with RC
In this test the motors respond to the throttle commands from the RC.
To run the test copy and paste the `hw_test_motors_with_receiver.cpp` into `main.cpp`.
