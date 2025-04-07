#include <Arduino.h>
#include <Servo.h>

Servo esc;  // Create an ESC control object

#define ESC_PIN 25  // Change this if needed (currently set to GPIO 25)

// Define PWM signal limits
const int minPWM = 1000;  // ESC minimum throttle (Off)
const int maxPWM = 2000;  // ESC maximum throttle (Full speed)
const int step = 5;       // Step size for throttle increase
const int delayTime = 20; // Time between steps (smooth acceleration)

void setup() {
    Serial.begin(115200);
    esc.attach(ESC_PIN, minPWM, maxPWM);  // Attach ESC to the correct pin

    Serial.println("Arming ESC...");
    esc.writeMicroseconds(minPWM);  // Send lowest throttle (1000 µs)
    delay(5000);  // Wait for ESC to initialize and arm

    Serial.println("ESC armed and ready.");
}

void loop() {
    Serial.println("Increasing throttle...");
    for (int pwm = minPWM; pwm <= maxPWM; pwm += step) {
        esc.writeMicroseconds(pwm);
        delay(delayTime);
    }

    Serial.println("Decreasing throttle...");
    for (int pwm = maxPWM; pwm >= minPWM; pwm -= step) {
        esc.writeMicroseconds(pwm);
        delay(delayTime);
    }

    Serial.println("Sweep complete. Pausing...");
    delay(2000);
}
