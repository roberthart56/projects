from typing import Optional, TYPE_CHECKING

# Assuming Packet and the deserializeTight utility functions are defined elsewhere
from ..utils.serdes import deserialize_tight_u16
from ..utils.keys import PacketKeys

if TYPE_CHECKING:
    from .packets import Packet

def route_get_key_increment(key: int) -> int:
    return key >> 6


def route_end_scan(packet: 'Packet') -> int:
    end = 5
    while True:
        increment = route_get_key_increment(packet.data[end])
        if not increment or increment == 3:
            return end
        end += increment
        if end > len(packet.data):
            return len(packet.data)


def route_equality(a: 'Route', b: 'Route') -> bool:
    if len(a.encoded_path) != len(b.encoded_path):
        return False
    for i in range(len(a.encoded_path)):
        if a.encoded_path[i] != b.encoded_path[i]:
            return False
    return True


def route_build(existing: Optional['Route'] = None) -> 'RouteBuilder':
    path = bytearray(256)
    wptr = 0
    if existing:
        path[0:len(existing.encoded_path)] = existing.encoded_path
        wptr = len(existing.encoded_path)
    return RouteBuilder(path, wptr)


def route_from_packet(packet: 'Packet') -> 'Route':
    time_to_live, _ = deserialize_tight_u16(packet.data, 1)
    max_segment_size, _ = deserialize_tight_u16(packet.data, 3)
    path_end = route_end_scan(packet)
    return Route(bytearray(packet.data[5:path_end]), max_segment_size, time_to_live)


class Route:
    def __init__(self, encoded_path: bytearray, max_segment_size: int, time_to_live: int) -> None:
        self.encoded_path: bytearray = encoded_path
        self.max_segment_size: int = max_segment_size
        self.time_to_live: int = time_to_live

    def reverse(self) -> None:
        old_path = self.encoded_path[:]
        rptr = 0
        wptr = len(old_path)
        while wptr > 0:
            increment = route_get_key_increment(old_path[rptr])
            if not increment or increment == 3:
                raise ValueError('Route reversal error')
            wptr -= increment
            self.encoded_path[wptr:wptr+increment] = old_path[rptr:rptr+increment]
            rptr += increment

    def count_hops(self) -> int:
        # no busses yet, so this is easy... 
        return len(self.encoded_path) 

    def print(self, return_string = False) -> None | str:
        msg = "ROUTE: -------------\n"
        rptr = 0
        while rptr < len(self.encoded_path):
            key = self.encoded_path[rptr] >> 6
            if key == PacketKeys.LFWD.value:
                msg += f"LINKF: {self.encoded_path[rptr] & 0b00011111}\n"
            elif key == PacketKeys.BFWD.value:
                msg += f"BUSF: {self.encoded_path[rptr] & 0b00011111}, {self.encoded_path[rptr + 1]}\n"
            else:
                msg += "BROKEN !\n"
                break
            rptr += route_get_key_increment(self.encoded_path[rptr])
        msg += "ENDROUTE: ----------"
        if return_string:
            return msg 
        else: 
            print(msg)


# utility class 
class RouteBuilder:
    def __init__(self, path: bytearray, wptr: int) -> None:
        self.path = path
        self.wptr = wptr

    def end(self, max_segment_size: int = 256, time_to_live: int = 65000) -> Route:
        return Route(bytearray(self.path[:self.wptr]), max_segment_size, time_to_live)

    def link(self, index: int) -> 'RouteBuilder':
        self.path[self.wptr] = (PacketKeys.LFWD.value << 6) | (index & 0b00011111)
        self.wptr += 1
        return self

    def bus(self, index: int, rx_address: int) -> 'RouteBuilder':
        self.path[self.wptr] = (PacketKeys.BFWD.value << 6) | (index & 0b00011111)
        self.wptr += 1
        self.path[self.wptr] = rx_address
        self.wptr += 1
        return self
