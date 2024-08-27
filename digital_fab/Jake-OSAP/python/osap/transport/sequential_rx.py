from typing import Callable, TYPE_CHECKING

from ..structure.ports import Port
from ..packets.routes import Route 
from ..utils.keys import TransportTypeKeys 

if TYPE_CHECKING:
    from ..runtime import Runtime

class SequentialReceiver:
    def __init__(self, runtime: 'Runtime', name: str, type_name: str = "bare_sqnce_rx"):
        self.port: Port = runtime.port_factory(name, type_name)
        self.port.attach_on_data(self.on_port_data)

        # confoundingly, our app also has an 'on_data'
        self.on_data_callable: Callable[[bytearray, Route, int], None | bytearray] = self.default_on_data_handler

    def default_on_data_handler(self, data: bytearray, source_route: Route, source_port: int):
        print("rxer default ondata")
        return None 

    def attach_on_data(self, func: Callable[[bytearray, Route, int], None | bytearray]):
        self.on_data_callable = func 

    def on_port_data(self, data: bytearray, source_route: Route, source_port: int):
        if data[0] != TransportTypeKeys.SEQUENTIAL_TX.value:
            raise Exception(f"received an oddball TTK at this sequence rx'er")
        
        msg_num = data[1]

        # call our attached funct, 
        res = self.on_data_callable(data[2:], source_route, source_port)

        # generate an ack-like, 
        if res is not None:
            payload = bytearray(len(res) + 2)
            payload[0] = TransportTypeKeys.SEQUENTIAL_RX.value 
            payload[1] = msg_num 
            payload[2:] = res 
        else:
            payload = bytearray(2)
            payload[0] = TransportTypeKeys.SEQUENTIAL_RX.value 
            payload[1] = msg_num 

        # TODO: AFAIK, race conditions here are still possible 
        # in py, since we donot allocate globally w/in the runtime, 
        # whereas in embedded we have a fixed pool and we know that 
        # (since we are acking) we have one to pop out as we pop this in... 
        # await self.port.await_cts() 
        self.port.send(payload, source_route, source_port)