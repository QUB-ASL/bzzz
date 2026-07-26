import read_sbus_from_GPIO
import serial
import time

SBUS_PIN = 25
ESP32_PORT="/dev/ttyUSB0"

reader = read_sbus_from_GPIO.SbusReader(SBUS_PIN)
reader.begin_listen()

print("waiting for  SBUS receiver...")

while not reader.is_connected():
    print("not connected")
    time.sleep(1)

print("Receiver connecte!")

time.sleep(0.1)

ser = serial.Serial(ESP32_PORT,115200)
time.sleep(2)

while True:
    try:
      channel_data = reader.translate_latest_packet()
      print(channel_data)
      
      packet = "S,"

      for i in range(8):
          packet += str(channel_data[i]) + ","
      
      packet += "16,\n"
      
      ser.write(packet.encode())
    
      print("sent: ", packet.strip())

      time.sleep(0.02)

    except keyboardInterrupt:
      reader.end_listening()
      ser.close()
      break

    except Exception as e:
      print(e)
      reader.end_listening()
      ser.close()
      raise

