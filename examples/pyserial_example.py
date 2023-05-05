import serial
import time

# Configure serial connection
ser = serial.Serial(
    port="COM4",
    baudrate=9600,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.SEVENBITS,
)

ser.isOpen()

input = b"run"
out = b""

# Send the input to the device
# Note the carriage return and line feed characters \r\n will depend on the device
ser.write(input + b"\r\n")

# Wait 1 sec before reading output

time.sleep(1)
while ser.inWaiting():
    out += ser.read(1)

# Print the response
print(out)

ser.write(b"stop\r\n")
