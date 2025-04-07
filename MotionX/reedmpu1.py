import serial
import time
from collections import deque

# Open Serial connection on COM7 (update if needed)
try:
    ser = serial.Serial("COM7", 115200, timeout=1)
    diagnostics.debug("Serial connected to COM7")
except:
    ser = None
    diagnostics.debug("Error: Unable to open COM7. Check if it's in use.")

if starting and ser:
    vJoy[0].x = 0  # Initialize X-axis (left/right control)
    vJoy[0].y = 0  # Initialize Y-axis (acceleration)

reed_history = deque(maxlen=20)  # Store last 20 reed switch values

def update_vjoy():
    global ser, reed_history
    while True:
        if ser:
            try:
                # Read data from Arduino
                line = ser.readline().decode('utf-8').strip()
                values = line.split(",")  # Expecting "roll,reed_count"

                if len(values) == 2 and values[0] and values[1]:
                    roll = float(values[0])  # Left/Right tilt
                    reed_count = int(values[1])  # Pedaling speed
                    
                    # Update reed history
                    reed_history.append(reed_count)
                    
                    # Check if last 20 values are the same
                    if len(reed_history) == 20 and len(set(reed_history)) == 1:
                        reed_count = 0  # Reset mapped value if no change for 10 readings
                    
                    # Map roll angle (-30° to +30°) to vJoy X-axis (-16384 to 16384)
                    joystick_x = int((roll + 30) * (32768 / 60) - 16384)
                    joystick_x = max(-16384, min(16384, joystick_x))  # Limit range
                    
                    # Map reed count to vJoy Y-axis (acceleration)
                    accel_value = min(16384, reed_count * 1000)  # Adjust scaling if needed

                    # Apply values to vJoy
                    vJoy[0].x = joystick_x
                    vJoy[0].y = accel_value
                    
                    diagnostics.debug("Roll: {}, vJoy X-axis: {} | Reed Count: {}, vJoy Y-axis: {}".format(
                        roll, joystick_x, reed_count, accel_value))
            
            except ValueError:
                diagnostics.debug("Warning: Invalid data received from Arduino")
            except serial.SerialException:
                diagnostics.debug("Error: Serial communication issue")
        
        time.sleep(0.01)  # Small delay to prevent CPU overuse

if starting:
    update_vjoy()  # Start reading sensor data
