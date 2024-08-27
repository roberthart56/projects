from typing import List, Callable, TYPE_CHECKING
import asyncio

from ..packets.packets import Packet, Route, packet_port_to_port
from ..utils.time_utils import get_microsecond_timestamp

if TYPE_CHECKING:
    from ..runtime import Runtime
    from ..packets.routes import Route


class Port:
    def __init__(self, runtime: 'Runtime', index: int, type_name: str, name: str) -> None:
        self.runtime = runtime
        self.index = index
        self.stack: List[Packet] = []
        self.stack_max_length = 4
        self.type_name = type_name
        self.name = name
        self.on_data_callable: Callable[[bytearray, Route, int], None] = self.default_on_data_handler

    def set_max_stack_length(self, length: int) -> None:
        if length < 1:
            length = 1
        elif length > 64:
            length = 64
        self.stack_max_length = length

    def get_max_stack_length(self) -> int:
        return self.stack_max_length

    def send(self, data: bytearray, route: Route, destination_port: int) -> None:
        if not self.clear_to_send():
            raise Exception(f"port.send() called on over-full port"\
                            f" w/ max {self.stack_max_length}")
        self.stack.append(packet_port_to_port(self, route, destination_port, data))

    def clear_to_send(self) -> bool:
        return len(self.stack) < self.stack_max_length

    async def await_cts(self, timeout_len_us = 1000000) -> None:
        start_time = get_microsecond_timestamp() 
        while not self.clear_to_send():
            if start_time + timeout_len_us < get_microsecond_timestamp():
                raise TimeoutError(f"{self.type_name} '{self.name}'timed out at await_cts")
            else:
                await asyncio.sleep(0)

    def attach_on_data(self, func: Callable[[bytearray, Route, int], None]) -> None:
        self.on_data_callable = func

    def default_on_data_handler(self, data: bytearray, source_route: Route, source_port: int) -> None:
        print(f'firing the default onDataHandler for port {self.name} with {len(data)} bytes')

    def get_packets_to_service(self) -> List[Packet]:
        return self.stack

    def get_index(self) -> int:
        return self.index
