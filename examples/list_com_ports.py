import serial.tools.list_ports

# Get a list of all available serial ports
ports = list(serial.tools.list_ports.comports())

# Print information about each port
for port in ports:
    print(
        "Port: {}\nDevice: {}\nDescription: {}\n".format(
            port.device, port.name, port.description
        )
    )
