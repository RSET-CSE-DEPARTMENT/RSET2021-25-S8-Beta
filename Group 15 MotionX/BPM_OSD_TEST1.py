import serial

# Set Arduino COM port (change COM7 if needed)
ser = serial.Serial("COM7", 115200, timeout=1)

if starting:
    plugins.rts.setOSD("RTSS OSD Active...")

def update():
    data = ser.readline().strip()

    try:
        # Decode bytes to string
        data = str(data, 'utf-8')

        # Extract BPM data from MAX30102
        if "BPM=" in data:
            bpm_value = int(data.split("BPM=")[1].split(",")[0])
            calories = bpm_value * 0.14  # Simple formula for calories burned

            # Update RTSS OSD
            plugins.rts.setOSD("❤️ BPM: {} | 🔥 Calories: {:.1f}".format(bpm_value, calories))

    except Exception as e:
        plugins.rts.setOSD("Error: " + str(e))

if starting:
    diagnostics.watch(update)
