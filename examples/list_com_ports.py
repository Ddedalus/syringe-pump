"""
Print information about available COM ports on the system.
NOTE: you need to install pyserial for this example
```
pip install pyserial
```
"""

import serial.tools.list_ports

if __name__ == "__main__":
    # Print information about each port
    for port in serial.tools.list_ports.comports():
        print(f"Port: {port.device}")
        print(f"Device: {port.name}")
        print(f"Description: {port.description}")
