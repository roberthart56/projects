from .cobs_usbserial_asyncio import CobsUsbSerial
import serial.tools.list_ports 

# we have unique PIDs for different boards... 
# we should basically just maintain a list of 'em 

device_product_ids = {
    "000A": "RP2040",
    "802F": "XIAO_D21",
    "0483": "TEENSY_4P0",
    "80CB": "QTPY_D21"
}

class AutoUSBPorts:
    def __init__(self):
        self.ports = [] 
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # some .comports() are *real* comports, and don't have a PID 
            if port.pid is None:
                continue 
            try:
                type_name = device_product_ids[f"{port.pid:04X}"]
                print(f"AUTO_USB: adding a port as {type_name}")
                self.add_port(port)
            except KeyError as err:
                print(f"AUTO_USB: no entry in our table for this device w/ pid {port.pid:04X}")

    def add_port(self, port):
        print(f"auto_usb_serial found {port.device}, id: {port.pid:04X}, "\
              f"type: {device_product_ids[f"{port.pid:04X}"]}")
        self.ports.append(CobsUsbSerial(port.device))