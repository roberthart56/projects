import asyncio
from cobs import cobs
import serial


class CobsUsbSerial:
    def __init__(self, port, baudrate=115200):
        self.port = port
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=0)
        self.buffer = bytearray()
        self.on_data_callable = None
        self.name = port
        self.type_name = "cobsUSBSerial"

    def send(self, data: bytes):
        data_enc = cobs.encode(data) + b"\x00"
        self.ser.write(data_enc)

    def read(self):
        byte = self.ser.read(1)
        if not byte:
            return
        if byte == b"\x00":
            if len(self.buffer) > 0:
                data = cobs.decode(self.buffer)
                self.buffer = bytearray()
                return bytearray(data)
            else:
                return
        else:
            self.buffer += byte

    def is_open(self):
        return True

    def clear_to_send(self):
        return True

    def attach(self, on_data):
        self.on_data_callable = on_data

    # loops forever,
    async def run(self):
        while True:
            bts = self.read()
            if bts and self.on_data_callable is not None:
                self.on_data_callable(bts)
            await asyncio.sleep(0)
