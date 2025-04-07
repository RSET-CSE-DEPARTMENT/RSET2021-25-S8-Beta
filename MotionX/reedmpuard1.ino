#include <Wire.h>
#include <MPU6050.h>

#define REED_SWITCH_PIN 2  // Reed switch connected to digital pin 2

MPU6050 mpu;
volatile int magnetCount = 0;

void reedSwitchInterrupt() {
    magnetCount++;  // Increase count when magnet passes
}

void setup() {
    Serial.begin(115200);  // Set baud rate to 115200
    Wire.begin();
    mpu.initialize();
    
    if (!mpu.testConnection()) {
        Serial.println("MPU6050 connection failed");
        while (1);
    }
    
    pinMode(REED_SWITCH_PIN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(REED_SWITCH_PIN), reedSwitchInterrupt, FALLING);
}

void loop() {
    int16_t ax, ay, az, gx, gy, gz;
    mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

    float roll = atan2(ay, az) * 180.0 / PI;  // Calculate roll angle

    Serial.print(roll);
    Serial.print(",");
    Serial.println(magnetCount);  // Send roll and magnet count as "roll,reed_count"

    delay(20);
}
