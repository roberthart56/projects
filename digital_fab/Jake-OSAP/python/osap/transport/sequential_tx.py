from typing import List, TYPE_CHECKING
import asyncio

from ..structure.ports import Port
from ..utils.time_utils import get_microsecond_timestamp
from ..packets.routes import Route 
from ..utils.keys import TransportTypeKeys 

if TYPE_CHECKING:
    from ..runtime import Runtime 

class ResolverItem:
    def __init__(self, msg_id: int):
        self.msg_id = msg_id
        self.data: bytearray 
        self.has_returned = False  

# ... we should calculate ttl's from timeouts given by app ?
# how should we deal with awaiting-while waiting for space timeouts vs. network transfer timeout ? 
# we have one of these per port, do we send a key identifying us as a tx'er ? 
# should-do protocol update / osap.tools wipe (!) 

# 2^16 * 2 
retry_time_max = 131071

class SequentialTransmitter:
    def __init__(self, runtime: 'Runtime', name: str, type_name: str = "bare_sqnce_tx"):
        self.port: Port = runtime.port_factory(name, type_name)
        self.port.attach_on_data(self.on_ack)
        self.resolvers: List[ResolverItem] = []
        self.last_id: int = 111

    def _write_new_id(self) -> int:
        self.last_id = (self.last_id + 1) & 255
        return self.last_id
    
    # retry_time_us has MAX = 131072 (two events of max time-to-live length) 
    async def send(self, 
                   destination_route: Route, 
                   destination_port: int, 
                   datagram: bytearray, 
                   retry_time_us = 65000, 
                   retry_attempts_max = 3) -> bytearray | None:

        msg_id = self._write_new_id() 
        resolver = ResolverItem(msg_id)
        # we could / should use this to pick retry times intelligently 
        # num_hops = route.count_hops()

        if retry_time_us > retry_time_max:
            retry_time_us = retry_time_max

        destination_route.time_to_live = min([retry_time_us >> 1, 65535])

        # wait for stack space, 
        await self.port.await_cts(retry_time_us)
        
        # write the message, stuffing our protocol key, id ... application data 
        payload = bytearray(len(datagram) + 2)
        payload[0] = TransportTypeKeys.SEQUENTIAL_TX.value 
        payload[1] = msg_id 
        payload[2:] = datagram 

        # ship it and track it, 
        self.resolvers.append(resolver) 
        send_time = get_microsecond_timestamp() 
        
        # ah shit, we need the port to do some work... 
        retry_attempts = 0 
        self.port.send(payload, destination_route, destination_port)

        while True:
            if resolver.has_returned:
                self.resolvers.remove(resolver)
                return resolver.data 
            elif send_time + retry_time_us < get_microsecond_timestamp():
                if retry_attempts >= retry_attempts_max:
                    raise TimeoutError(f"Timeout after {retry_attempts_max} at {retry_time_us}us each,"\
                                       f"along route: \n{destination_route.print(True)}")
                else:
                    await self.port.await_cts(retry_time_us)
                    retry_attempts += 1 
                    print(f"SEQ_TX RT_ATT: {retry_attempts}")
                    send_time = get_microsecond_timestamp() 
                    self.port.send(payload, destination_route, destination_port) 
            else:
                await asyncio.sleep(0)

    def on_ack(self, data: bytearray, source_route: Route, source_port: int):
        if data[0] != TransportTypeKeys.SEQUENTIAL_RX.value:
            raise Exception(f"received a ... at ...")

        for r in self.resolvers:
            if data[1] == r.msg_id:
                r.data = bytearray(data[2:])
                r.has_returned = True 

        # If we get here, no matching resolver was found
        # raise ValueError(f'resolver was unable to demux msg w/ msg_id {data[offset]}')


# async def request(self, msg_id: int, msg_info: str, timeout_len_ms = 1000) -> bytearray:
#     # we make a new resolver item and push it to our stack, 
#     resolver = ResolverItem(msg_id)
#     self.resolvers.append(resolver)
#     start_time = get_millisecond_timestamp()
#     # now we wait until the bytes become available ? 
#     while True:
#         if resolver.has_returned:
#             self.resolvers.remove(resolver)
#             return resolver.data 
#         elif start_time + timeout_len_ms < get_millisecond_timestamp():
#             raise TimeoutError(f"Timeout: info: '{msg_info}' id: '{msg_id}' len: {timeout_len_ms}ms")
#         else: 
#             await asyncio.sleep(0) 
