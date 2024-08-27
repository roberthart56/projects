import serial.tools.list_ports

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"Port: {port.device}")
        print(f" - Description: {port.description}")
        if port.serial_number:
            print(f" - Serial Number: {port.serial_number}")
        if port.manufacturer:
            print(f" - Manufacturer: {port.manufacturer}")
        if port.product:
            print(f" - Product: {port.product}")
        if port.vid is not None:
            print(f" - VID: {port.vid:04X}")
        if port.pid is not None:
            print(f" - PID: {port.pid:04X}")
        print()

list_serial_ports()
