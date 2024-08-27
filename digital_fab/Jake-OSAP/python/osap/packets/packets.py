from typing import Union, TYPE_CHECKING
from .routes import Route
from ..utils.keys import PacketKeys
from ..utils.serdes import serialize_tight_u16, deserialize_tight_u16
from ..utils.time_utils import get_microsecond_timestamp

if TYPE_CHECKING:
    from ..runtime import Runtime
    from ..structure.ports import Port
    from ..structure.links import LinkGateway


# local ute, stuffs routes into packets
def packet_stuff_route(pck: bytearray, route: Route):
    # pck[0] is the pointer, which starts at 5th byte (where 1st instruct is)
    pck[0] = 5
    serialize_tight_u16(route.time_to_live, pck, 1)
    serialize_tight_u16(route.max_segment_size, pck, 3)
    pck[5:5+len(route.encoded_path)] = route.encoded_path
    return len(route.encoded_path) + 5


# build a packet for runtime-to-runtime
def packet_system_message(source: 'Runtime', route: 'Route', data: bytearray) -> 'Packet':
    packet_length = 5 + len(route.encoded_path) + len(data)
    if packet_length > route.max_segment_size:
        raise ValueError(f"Attempt to write packet of length "
                         f"{packet_length} along a route with maximum "
                         f"{route.max_segment_size}")
    pck = bytearray(packet_length)
    route_end = packet_stuff_route(pck, route)
    pck[route_end:] = data
    # print("authored system msg", [byte for byte in pck])
    return Packet(source, pck, route.time_to_live)


# build a Packet for a port-to-port trip
def packet_port_to_port(source: 'Port', route: 'Route', destination_port: int, data: bytearray) -> 'Packet':
    packet_length = 5 + len(route.encoded_path) + 5 + len(data)
    if packet_length > route.max_segment_size:
        raise ValueError(f"Attempt to write packet of length {
                         packet_length} along a route with maximum {route.max_segment_size}")
    pck = bytearray(packet_length)
    route_end = packet_stuff_route(pck, route)
    pck[route_end] = PacketKeys.DGRM.value << 6 | source.get_index() >> 6
    pck[route_end + 1] = source.get_index() << 2 | destination_port >> 8
    pck[route_end + 2] = destination_port & 255
    pck[route_end + 3:] = data
    return Packet(source, pck, route.time_to_live)


# build / ingest a packet from an external source
def packet_from_link(source: 'LinkGateway', pck: bytearray) -> 'Packet':
    time_to_live, _ = deserialize_tight_u16(pck, 1)
    return Packet(source, pck, time_to_live)


# base class, basically just a struct innit ?
class Packet:
    source: Union['Port', 'Runtime', 'LinkGateway']
    data: bytearray
    service_deadline: int

    def __init__(self, source: Union['Port', 'Runtime', 'LinkGateway'], data: bytearray, time_to_live: int):
        self.source = source
        self.data = data
        self.service_deadline = time_to_live + get_microsecond_timestamp()

    def delete(self):
        if self in self.source.stack:
            self.source.stack.remove(self)
        else:
            raise ValueError(
                "A likely double-deletion of this packet has occurred... check runtime...")
