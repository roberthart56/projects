from typing import Callable, List, Protocol, TYPE_CHECKING, runtime_checkable
# from ..runtime import Runtime
from ..packets.packets import Packet, packet_from_link 
from ..utils.keys import PacketKeys

if TYPE_CHECKING:
    from ..runtime import Runtime 

# a protocol... an interface, basically, I think 
@runtime_checkable
class LinkImplementation(Protocol):
    def clear_to_send(self) -> bool: ...
    def send(self, data: bytes) -> None: ...
    def is_open(self) -> bool: ...
    def attach(self, on_data) -> None: ... 
    async def run(self) -> None: ... 
    type_name: str
    name: str


class LinkGateway:
    def __init__(self, runtime: 'Runtime', index: int, implementation: LinkImplementation,) -> None:
        self.runtime = runtime
        self.index = index

        # we can typecheck these things, 
        if not isinstance(implementation, LinkImplementation):
            print('the provided implementation is busted (allegedly)')
            return 

        self.clear_to_send: Callable[[], bool] = implementation.clear_to_send
        self.send: Callable[[bytes], None] = implementation.send
        self.is_open: Callable[[], bool] = implementation.is_open
        self.type_name: str = implementation.type_name
        self.run = implementation.run 
        self.name: str = implementation.name
        self.stack: List[Packet] = []

        # hook it up on the rx side, 
        implementation.attach(self.ingest_packet) 

    def ingest_packet(self, pck: bytearray) -> None:
        if (pck[pck[0]] >> 6) != PacketKeys.LFWD.value:
            raise ValueError("Received a poorly formed packet at this link, tossing it!")
        # we stuff our own index in this instruction (for reversal) and increment the pointer 
        pck[pck[0]] = PacketKeys.LFWD.value << 6 | self.index
        pck[0] += 1
        # stick it in our stack, for handling, 
        self.stack.append(packet_from_link(self, pck))
        # haven't had use for it yet, will do when necessary 
        if len(self.stack) > 8:
            print("WARNING: this link's stackLength is > 8, we should implement flowcontrol...")
        # ask for time to handle 
        # self.runtime.request_loop_cycle()

    def get_packets_to_service(self) -> List[Packet]:
        return self.stack

    def dissolve(self) -> None:
        # want to rm ourselves from parent's list, 
        # potentially circular business, beware, idk how this plays in py 
        for l in range(len(self.runtime.links)):
            if self.runtime.links[l] == self:
                # IDK if this works in py yet ? 
                self.runtime.links[l] = None 
                break 